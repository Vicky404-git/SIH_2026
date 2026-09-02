import os
from typing import Optional

try:
    import ollama
except ImportError:
    ollama = None

from .config import get_ollama_options, get_rag_params
from .rag import search, add_chat_memory, DB_PATH
from .agent import Agent, Tool, ToolResult
from .doc_gen import docgen_tool

MODEL_MAP = {
    "coding": "ssfdre38/gemma4-turbo:latest",
    "vision": "ssfdre38/gemma4-turbo:latest",
    "reasoning": "ssfdre38/gemma4-turbo:latest",
    "general": "ssfdre38/gemma4-turbo:latest",
}


def classify_task(prompt: str, has_image: bool = False):
    if has_image:
        return "vision", "image attached → routed to vision model"

    prompt_lower = prompt.lower()
    code_keywords = {"code", "python", "script", "function", "bug", "error", "refactor", "sql", "exec"}
    matched = [kw for kw in code_keywords if kw in prompt_lower]

    if matched:
        return "coding", f"matched keywords {matched} → routed to coding model"

    return "reasoning", "no code/image signals → routed to general reasoning model"


def kb_search_tool(query: str, db_path: str = DB_PATH) -> ToolResult:
    rag_params = get_rag_params()
    hits = search(query, top_k=rag_params["top_k"], db_path=db_path)
    if not hits:
        return ToolResult(ok=False, output="No relevant SOPs/manuals found in local knowledge base.")

    lines = []
    for score, doc in hits:
        if score < 0.3:
            confidence = "strong match"
        elif score < 0.6:
            confidence = "weak match"
        else:
            confidence = "low relevance"
        lines.append(f"[{doc['file']}] ({confidence}, distance={score:.3f}) {doc['content'][:300]}")

    return ToolResult(ok=True, output="\n".join(lines))


kb_tool = Tool(
    "search_knowledge_base",
    kb_search_tool,
    "Search internal SOPs/manuals for relevant grounded context. Returns matches with confidence labels."
)


def build_llm_call(persona: str = "default", db_path: str = DB_PATH):
    """Returns a callable(prompt)->raw_text, bound to a specific model per task type.
    This is what gets passed into Agent(llm_call=...).
    """
    def llm_call(agent_prompt: str) -> str:
        # crude but cheap re-classification per call, since the agent loop
        # may touch multiple task types across its steps
        task_type, reason = classify_task(agent_prompt)
        model_name = MODEL_MAP.get(task_type, MODEL_MAP["general"])
        ollama_opts = get_ollama_options()

        response = ollama.generate(
            model=model_name,
            prompt=agent_prompt,
            options=ollama_opts,
        )
        return response.get("response", "")

    return llm_call


def run_agent(prompt: str, image_path: Optional[str] = None, persona: str = "default", db_path: str = DB_PATH) -> dict:
    if ollama is None:
        return {"error": "Ollama package is not installed."}

    tools = [kb_tool, docgen_tool]  # sandbox tool gets added here once Docker wrapper is ready

    llm_call = build_llm_call(persona=persona, db_path=db_path)
    agent = Agent(llm_call=llm_call, tools=tools, max_steps=6)

    result = agent.run(prompt)

    # write to chat memory regardless of completed/incomplete status
    add_chat_memory(prompt, str(result["result"]), persona=persona, db_path=db_path)

    # ── AUDIT LOG: append the full trace to disk, one line per run ──
    _write_audit_log(prompt, result)

    return result


def _write_audit_log(prompt: str, result: dict, log_path: str = "memory/audit_log.jsonl"):
    import json, time
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    entry = {
        "timestamp": time.time(),
        "prompt": prompt,
        "status": result["status"],
        "trace": result["trace"],
        "final_result": result["result"],
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
