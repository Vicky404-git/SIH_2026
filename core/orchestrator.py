import os
from typing import Dict, Any, Optional

try:
    import ollama
except ImportError:
    ollama = None

from .config import get_ollama_options, get_rag_params
from .rag import search, add_chat_memory, DB_PATH

# Model registry mapped by capability
MODEL_MAP = {
    "coding": "ssfdre38/gemma4-turbo:latest",
    "vision": "ssfdre38/gemma4-turbo:latest",
    "reasoning": "ssfdre38/gemma4-turbo:latest",
    "general": "ssfdre38/gemma4-turbo:latest"
}

def classify_task(prompt: str, has_image: bool = False) -> str:
    """Keyword-based intent classifier for zero-latency routing."""
    if has_image:
        return "vision"
    
    prompt_lower = prompt.lower()
    code_keywords = {"code", "python", "script", "function", "bug", "error", "refactor", "sql", "exec"}
    
    if any(kw in prompt_lower for kw in code_keywords):
        return "coding"
    
    return "reasoning"


def run_agent(
    prompt: str, 
    image_path: Optional[str] = None, 
    persona: str = "default",
    db_path: str = DB_PATH
) -> Dict[str, Any]:
    """
    Main agent pipeline:
    1. Route task to specific model
    2. Retrieve local knowledge (RAG)
    3. Call local Ollama model with system/RAM limits
    4. Save conversation memory
    """
    if ollama is None:
        return {"error": "Ollama package is not installed."}

    # 1. Classify & Select Model
    task_type = classify_task(prompt, has_image=bool(image_path))
    model_name = MODEL_MAP.get(task_type, MODEL_MAP["general"])
    
    # 2. Get Resource Throttling Options & RAG Params
    ollama_opts = get_ollama_options()
    rag_params = get_rag_params()

    # 3. Retrieve RAG Context (for non-vision tasks)
    context_chunks = []
    sources = []
    if task_type != "vision":
        hits = search(prompt, top_k=rag_params["top_k"], db_path=db_path)
        for score, doc in hits:
            context_chunks.append(doc["content"])
            sources.append(doc["file"])

    context_str = "\n---\n".join(context_chunks) if context_chunks else "No internal SOPs or reference docs found."

    # 4. Construct System Prompt
    system_prompt = (
        f"You are a sovereign, air-gapped industrial AI assistant.\n"
        f"Task Type: {task_type.upper()}\n"
        f"Grounded Context:\n{context_str}\n\n"
        f"Answer the user's request accurately using the grounded context provided if relevant."
    )

    # 5. Call Model via Ollama
    try:
        if task_type == "vision" and image_path and os.path.exists(image_path):
            response = ollama.generate(
                model=model_name,
                prompt=prompt,
                images=[image_path],
                options=ollama_opts
            )
        else:
            response = ollama.generate(
                model=model_name,
                prompt=prompt,
                system=system_prompt,
                options=ollama_opts
            )

        output_text = response.get("response", "")

        # 6. Append to Chat Memory
        add_chat_memory(prompt, output_text, persona=persona, db_path=db_path)

        return {
            "response": output_text,
            "task_type": task_type,
            "model_used": model_name,
            "sources": list(set(sources))
        }

    except Exception as e:
        return {
            "error": f"Model execution failed: {str(e)}",
            "task_type": task_type,
            "model_used": model_name
        }
