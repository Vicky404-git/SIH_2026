import streamlit as st
import os
import tempfile
from pathlib import Path

from core.orchestrator import run_agent
from core.rag import ingest_text

st.set_page_config(page_title="Sovereign AI Workbench", layout="wide", page_icon="🔒")

# ── Load external CSS + HTML fragments ──────────────────────────────
BASE_DIR = Path(__file__).parent

def load_file(path: str) -> str:
    p = BASE_DIR / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")

css = load_file("static/style.css")
header_html = load_file("static/index.html")

if css:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning("style.css not found — using default Streamlit theme.")

if header_html:
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.title("🔒 Sovereign On-Premise Agentic AI")
    st.caption("Air-gapped industrial AI assistant — zero external network calls")

# ── Sidebar: tool status ────────────────────────────────────────────
with st.sidebar:
    st.header("System Status")
    st.success("Network Egress: 0 Bytes")
    st.info("Vector DB: sqlite-vec (Local)")
    st.divider()
    st.markdown("**Active Tools:**")
    st.checkbox("Local RAG Search", value=True, disabled=True)
    st.checkbox("Document Generation (docx)", value=True, disabled=True)
    st.checkbox("Docker Sandbox (Code)", value=False, disabled=True)

    st.divider()
    st.markdown("**Add to Knowledge Base**")
    uploaded_doc = st.file_uploader(
        "Upload a text/code file (no OCR needed)",
        type=["txt", "md", "py", "json", "csv", "log"],
        key="doc_uploader",
    )

    if "consumed_doc_id" not in st.session_state:
        st.session_state["consumed_doc_id"] = None

    if uploaded_doc is not None and uploaded_doc.file_id != st.session_state["consumed_doc_id"]:
        content = uploaded_doc.read().decode("utf-8", errors="ignore")
        chunk_count = ingest_text(content, source_name=uploaded_doc.name, source_type="doc")
        st.session_state["consumed_doc_id"] = uploaded_doc.file_id
        st.success(f"Added {chunk_count} chunks from '{uploaded_doc.name}' to memory.")

# ── Chat state & UI ──────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 1. Render existing conversation history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Render Suggestion Buttons ONLY if conversation is empty
selected_prompt = None
if len(st.session_state["messages"]) == 0:
    st.markdown("**Try asking:**")
    cols = st.columns(2)
    suggestions = [
        "Search the knowledge base for memory throttling and summarize it.",
        "Generate a technical report about the C-204 compressor.",
    ]
    for col, p in zip(cols, suggestions):
        if col.button(p, key=f"btn_{p[:10]}"):
            selected_prompt = p

# 3. Vision Upload Widget
uploaded_image = st.file_uploader(
    "Attach scanned document / image (optional)",
    type=["png", "jpg", "jpeg", "pdf"],
)

def confidence_badge_html(confidence: str) -> str:
    conf = (confidence or "unknown").lower()
    css_class = {
        "high": "confidence-high",
        "medium": "confidence-medium",
        "low": "confidence-low",
    }.get(conf, "confidence-medium")
    return f'<span class="confidence-badge {css_class}">{conf.upper()}</span>'

# 4. SINGLE Chat Input
typed_prompt = st.chat_input("Ask a question or request a task...")
prompt = typed_prompt or selected_prompt
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    image_path = None
    if uploaded_image is not None:
        suffix = os.path.splitext(uploaded_image.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_image.read())
            image_path = tmp.name

    with st.spinner("Agent is reasoning (local inference)..."):
        res = run_agent(prompt, image_path=image_path)

    with st.expander("📋 Agent Activity", expanded=True):
        for i, step in enumerate(res.get("trace", []), 1):
            icon = "✅" if step.get("result_ok", True) else "❌"
            action = step.get("tool") or step.get("error") or "reasoning"
            st.markdown(f"{icon} **Step {i}:** {action}")

    with st.chat_message("assistant"):
        result_text = res.get("result", "")

        # Handle .docx file downloads
        if isinstance(result_text, str) and result_text.strip().endswith(".docx") and os.path.exists(result_text.strip()):
            st.markdown("✅ Document generated:")
            with open(result_text.strip(), "rb") as f:
                st.download_button(
                    "Download .docx",
                    f,
                    file_name=os.path.basename(result_text.strip()),
                )
        else:
            st.markdown(result_text)

        confidence = res.get("confidence", "unknown")
        st.markdown(f"**Confidence:** {confidence_badge_html(confidence)}", unsafe_allow_html=True)

        with st.expander("🧠 Agent reasoning"):
            st.write(res.get("reasoning", "No reasoning provided."))

        with st.expander("🔀 Routing decision"):
            st.write(f"Task type: `{res.get('task_type', 'unknown')}`")
            st.write(res.get("routing_reason", "No routing info available."))

        with st.expander("📋 Full step trace"):
            for step in res.get("trace", []):
                st.json(step)

        if res.get("status") == "incomplete":
            st.warning("⚠️ Agent stopped before finishing — see progress above.")

    st.session_state["messages"].append({
        "role": "assistant",
        "content": result_text if isinstance(result_text, str) else str(result_text),
    })
