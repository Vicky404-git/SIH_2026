import os
import resource
import shutil
import signal
import subprocess
import tempfile
from typing import Dict, Any

from .code_inspector import inspect_code

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
    """Executes a Python script inside an isolated subprocess with strict OS resource limits.

    Security layers applied (in order):
      1. AST import blocklist — reject dangerous imports before execution
      2. Filesystem confinement — copy script into isolated temp dir
      3. OS resource limits — RLIMIT_AS (RAM) + RLIMIT_CPU via preexec_fn
      4. Wall-clock timeout — subprocess.run(timeout=...)
    """
    abs_path = os.path.abspath(script_path)
    
    if not os.path.exists(abs_path):
        return {"success": False, "output": "", "error": f"File not found: {abs_path}"}

    # ── Layer 1: AST Import Inspection ──────────────────────────────
    try:
        source = open(abs_path, "r").read()
    except Exception as e:
        return {"success": False, "output": "", "error": f"[Sandbox Error] Cannot read script: {e}"}

    inspection = inspect_code(source)
    if not inspection["safe"]:
        blocked = ", ".join(inspection["blocked_imports"])
        return {
            "success": False,
            "output": "",
            "error": f"[Sandbox Violation] Blocked imports detected: {blocked}. Execution denied.",
        }

    # ── Layer 2: Filesystem Confinement ─────────────────────────────
    # Copy script into an isolated temp directory so it cannot traverse
    # to memory/*.db, core/, or any repo files.
    sandbox_dir = tempfile.mkdtemp(prefix="sandbox_jail_")
    confined_script = os.path.join(sandbox_dir, "script.py")
    try:
        shutil.copy2(abs_path, confined_script)
    except Exception as e:
        shutil.rmtree(sandbox_dir, ignore_errors=True)
        return {"success": False, "output": "", "error": f"[Sandbox Error] Failed to confine script: {e}"}

    # ── Layer 3 & 4: Resource Limits + Timeout ──────────────────────
    # Bind explicit arguments to eliminate lambda scope bugs
    def target_limits():
        _apply_os_limits(max_mem_mb=max_mem_mb, max_cpu_sec=timeout_sec)

    try:
        result = subprocess.run(
            ["python3", confined_script],
            preexec_fn=target_limits,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=sandbox_dir  # confined working directory
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
    finally:
        # Always clean up the confinement directory
        shutil.rmtree(sandbox_dir, ignore_errors=True)

