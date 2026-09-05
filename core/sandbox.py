import os
import resource
import signal
import subprocess
from typing import Dict, Any

def _apply_os_limits(max_mem_mb: int, max_cpu_sec: int) -> None:
    """Child process callback: Enforces OS kernel limits before execution begins."""
    # 1. Convert RAM limit to Bytes
    mem_bytes = max_mem_mb * 1024 * 1024
    
    # Restrict Virtual Memory (RLIMIT_AS)
    try:
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    except Exception:
        pass  # Fallback if OS restricts lower limit adjustment
    
    # 2. Restrict CPU Time (RLIMIT_CPU)
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_sec, max_cpu_sec))
    except Exception:
        pass

def execute_sandboxed_code(script_path: str, timeout_sec: int = 5, max_mem_mb: int = 256) -> Dict[str, Any]:
    """Executes a Python script inside an isolated subprocess with strict OS resource limits."""
    abs_path = os.path.abspath(script_path)
    
    if not os.path.exists(abs_path):
        return {"success": False, "output": "", "error": f"File not found: {abs_path}"}

    # Bind explicit arguments to eliminate lambda scope bugs
    def target_limits():
        _apply_os_limits(max_mem_mb=max_mem_mb, max_cpu_sec=timeout_sec)

    try:
        result = subprocess.run(
            ["python3", abs_path],
            preexec_fn=target_limits,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=os.path.dirname(abs_path)
        )
        
        # Check OS termination signals
        if result.returncode < 0:
            sig_num = abs(result.returncode)
            sig_name = signal.Signals(sig_num).name if sig_num in signal.__dict__.values() else f"Signal {sig_num}"
            return {
                "success": False,
                "output": result.stdout,
                "error": f"[Sandbox Violation] Process killed by OS kernel ({sig_name}). Exceeded memory/CPU limit."
            }

        if result.returncode == 0:
            return {"success": True, "output": result.stdout, "error": ""}
        else:
            return {"success": False, "output": result.stdout, "error": result.stderr}

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"[Sandbox Violation] Execution timed out: Exceeded {timeout_sec}s wall-clock limit."
        }
    except Exception as e:
        return {"success": False, "output": "", "error": f"[Sandbox Error] Execution failed: {str(e)}"}
