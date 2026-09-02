import streamlit as st
from core.orchestrator import run_agent

st.set_page_config(page_title="Sovereign AI Workbench", layout="wide", page_icon="🔒")
# --- 2000s GEN X SOFT CLUB UI INJECTION ---
st.markdown("""
<style>
/* Deep dark background with soft system monospace font */
.stApp {
    background-color: #0a0a0f; 
    color: #a3a3b5; 
    font-family: 'Courier New', Consolas, monospace;
}

/* Soft glowing headers */
h1, h2, h3 {
    color: #d8d8e6 !important; 
    text-shadow: 0px 0px 8px rgba(216, 216, 230, 0.3);
    font-weight: normal;
    letter-spacing: -1px;
}

/* Translucent, dashed-border chat bubbles */
.stChatMessage {
    background: rgba(255, 255, 255, 0.02);
    border: 1px dashed #3a3a52; 
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.5);
}

/* Cyber-soft chat input */
.stChatInputContainer textarea {
    background-color: #12121a !important;
    color: #00ffcc !important; /* Soft cyan text */
    border: 1px solid #2a2a3d !important;
    border-radius: 6px;
}
.stChatInputContainer textarea:focus {
    border-color: #00ffcc !important;
    box-shadow: 0 0 8px rgba(0, 255, 204, 0.2) !important;
}

/* Dimmed, brutalist sidebar */
[data-testid="stSidebar"] {
    background-color: #0d0d12;
    border-right: 1px solid #1a1a24;
}

/* Checkboxes and accents */
.stCheckbox label {
    color: #dda0dd !important; /* Soft plum */
}
hr {
    border-color: #2a2a3d;
}
</style>
""", unsafe_allow_html=True)

st.title("🔒 Sovereign On-Premise Agentic AI")
st.markdown("Air-gapped industrial AI assistant. Zero external network calls.")

# Sidebar for Air-Gap Proof / Status
with st.sidebar:
    st.header("System Status")
    st.success("Network Egress: 0 Bytes")
    st.info("Vector DB: sqlite-vec (Local)")
    st.info("Models: ssfdre38/gemma4-turbo")
    
    st.divider()
    st.markdown("**Active Tools:**")
    st.checkbox("Local RAG Search", value=True, disabled=True)
    st.checkbox("Docker Sandbox (Code)", value=False, disabled=True) # Next step!

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question about your documents or request a task..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call Orchestrator
    with st.spinner("Agent is reasoning (Local Inference)..."):
        res = run_agent(prompt)
        
        if "error" in res:
            full_response = f"🚨 **ERROR:** {res['error']}"
        else:
            sources_str = ", ".join(res.get("sources", [])) if res.get("sources") else "None"
            
            # Format the output beautifully
            full_response = (
                f"{res.get('response')}\n\n"
                f"---\n"
                f"**Task Type:** `{res.get('task_type')}` | "
                f"**Model:** `{res.get('model_used')}` | "
                f"**Sources:** `{sources_str}`"
            )
        
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
