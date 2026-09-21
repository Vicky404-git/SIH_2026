from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from core.orchestrator import run_agent
import shutil, tempfile, os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory map: uploaded filename -> saved server-side path.
# Fine for a single-user demo; not meant to survive a real restart.
_uploaded_files: dict[str, str] = {}

@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    suffix = "." + file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        saved_path = tmp.name

    _uploaded_files[file.filename] = saved_path

    # text/code files get ingested into the KB immediately (matches your
    # existing ingest_text flow); images are left as-is for the vision path
    if suffix.lower() in (".txt", ".md", ".py", ".json", ".csv", ".log"):
        from core.rag import ingest_text
        content = open(saved_path, "r", errors="ignore").read()
        ingest_text(content, source_name=file.filename, source_type="doc")

    return {
        "id": f"doc_{file.filename}",
        "name": file.filename,
        "status": "Indexed",
    }

@app.post("/chat")
async def chat(payload: dict):
    message = payload.get("message", "")
    attachments = payload.get("attachments", [])

    # if the last attachment is an image, resolve it to the real saved path
    image_path = None
    for name in reversed(attachments):
        saved = _uploaded_files.get(name)
        if saved and saved.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")):
            image_path = saved
            break

    result = run_agent(message, image_path=image_path)

    # map your real fields onto exactly what workbench.js expects
    return {
        "result": result.get("result"),
        "reasoning": result.get("reasoning"),
        "confidence": result.get("confidence"),
        "status": result.get("status"),
        "trace": [
            {"step": i + 1, "action": s.get("tool", s.get("error", "reasoning")), "status": "success" if s.get("result_ok", True) else "failed"}
            for i, s in enumerate(result.get("trace", []))
        ],
        "sources": result.get("sources", []),
    }

@app.get("/reports/{filename}/download")
async def download_report(filename: str):
    # your docgen_tool already writes real .docx files to a temp path;
    # this just serves whatever path was returned as the chat result
    if not os.path.exists(filename):
        return {"error": "File not found"}
    return FileResponse(filename, filename=os.path.basename(filename))
