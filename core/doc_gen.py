# doc_gen_tool.py
import subprocess, tempfile
from core.agent import Tool, ToolResult

def generate_docx(markdown_content: str) -> ToolResult:
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
        f.write(markdown_content)
        md_path = f.name
    out_path = md_path.replace(".md", ".docx")

    result = subprocess.run(["pandoc", md_path, "-o", out_path], capture_output=True, text=True)
    if result.returncode != 0:
        return ToolResult(ok=False, output=result.stderr)
    return ToolResult(ok=True, output=out_path)

docgen_tool = Tool("generate_docx", generate_docx, "Convert markdown content into a Word document, returns file path")
