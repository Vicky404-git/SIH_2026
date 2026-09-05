import streamlit as st
import os, tempfile
from core.orchestrator import run_agent

st.set_page_config(page_title="Sovereign AI Workbench", layout="wide", page_icon="🔒")

st.markdown("""<style> ... (keep your existing 2000s Gen X CSS block unchanged) ... </style>""", unsafe_allow_html=True)

st.title("🔒 Sovereign On-Premise Agentic AI")
st.markdown("Air-gapped industrial AI assistant. Zero external network calls.")

with st.sidebar:
    st.header("System Status")
    st.success("Network Egress: 0 Bytes")
    st.info("Vector DB: sqlite-vec (Local)")
    st.divider()
    st.markdown("**Active Tools:**")
    st.checkbox("Local RAG Search", value=True, disabled=True)
    st.checkbox("Document Generation (docx)", value=True, disabled=True)
    st.checkbox("Docker Sandbox (Code)", value=False, disabled=True)  # flip once built

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_image = st.file_uploader("Attach scanned document / image (optional)", type=["png", "jpg", "jpeg", "pdf"])

if prompt := st.chat_input("Ask a question or request a task..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    image_path = None
    if uploaded_image is not None:
        suffix = os.path.splitext(uploaded_image.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_image.read())
            image_path = tmp.name

    with st.spinner("Agent is reasoning (local inference)..."):
        res = run_agent(prompt, image_path=image_path)

    with st.chat_message("assistant"):
        result_text = res.get("result", "")

        # If the agent produced a real file (docx), offer it as a download
        if isinstance(result_text, str) and result_text.endswith(".docx") and os.path.exists(result_text):
            st.markdown("✅ Document generated:")
            with open(result_text, "rb") as f:
                st.download_button("Download .docx", f, file_name=os.path.basename(result_text))
        else:
            st.markdown(result_text)

        confidence = res.get("confidence", "unknown")
        badge_color = {"high": "green", "medium": "orange", "low": "red"}.get(confidence, "gray")
        st.markdown(f"**Confidence:** :{badge_color}[{confidence.upper()}]")

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

    st.session_state.messages.append({"role": "assistant", "content": result_text if isinstance(result_text, str) else str(result_text)})
