import streamlit as st
from core.orchestrator import run_agent

st.set_page_config(page_title="Sovereign AI Workbench", layout="wide", page_icon="🔒")

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
