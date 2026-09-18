# doc_gen_tool.py
import subprocess, tempfile
from core.agent import Tool, ToolResult
from core.config import get_sandbox_limits
from core.sandbox import _apply_os_limits

def generate_docx(markdown_content: str) -> ToolResult:
    limits = get_sandbox_limits()

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
        f.write(markdown_content)
        md_path = f.name
    out_path = md_path.replace(".md", ".docx")

    def _pandoc_limits():
        _apply_os_limits(max_mem_mb=limits["max_mem_mb"], max_cpu_sec=limits["timeout_sec"])

    try:
        result = subprocess.run(
            ["pandoc", md_path, "-o", out_path],
            preexec_fn=_pandoc_limits,
            capture_output=True,
            text=True,
            timeout=limits["timeout_sec"],
        )
    except subprocess.TimeoutExpired:
        return ToolResult(ok=False, output=f"[Sandbox Violation] pandoc timed out after {limits['timeout_sec']}s.")

    if result.returncode < 0:
        return ToolResult(ok=False, output=f"[Sandbox Violation] pandoc killed by OS (signal {abs(result.returncode)}).")
    if result.returncode != 0:
        return ToolResult(ok=False, output=result.stderr)
    return ToolResult(ok=True, output=out_path)

docgen_tool = Tool(
    "generate_docx", 
    generate_docx, 
    "ONLY use this tool if the user explicitly asks to 'generate a document', 'create a report', or 'make a .docx file'. Do NOT use this for code."
)

