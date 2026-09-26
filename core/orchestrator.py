import os
import tempfile
from typing import Optional

try:
    import ollama
except ImportError:
    ollama = None

from .config import get_ollama_options, get_rag_params, get_sandbox_limits
from .rag import search, add_chat_memory, DB_PATH
from .agent import Agent, Tool, ToolResult
from .doc_gen import docgen_tool
from .sandbox import execute_sandboxed_code

from .config import load_config
from .model_registry import discover_models, get_best_model
from .memory_manager import check_and_consolidate

def get_model_map():
    config = load_config()
    user_map = config.get("model_map", {})
    discovered = discover_models()

    fallback = {}
    for cap in ("coding", "vision", "reasoning", "general"):
        match = next((m["name"] for m in discovered if m["guessed_capability"] == cap), None)
        fallback[cap] = match  # None if nothing found — don't silently misassign

    return {**fallback, **user_map}

def classify_task(prompt: str, has_image: bool = False):
    if has_image:
        return "vision", "image attached → routed to vision model"

    prompt_lower = prompt.lower()
    code_keywords = {"code", "python", "script", "function", "bug", "error", "refactor", "sql", "exec"}
    matched = [kw for kw in code_keywords if kw in prompt_lower]

    if matched:
        return "coding", f"matched keywords {matched} → routed to coding model"

    return "reasoning", "no code/image signals → routed to general reasoning model"




_last_sources = []  # reset per run — fine for single-user demo, not thread-safe for concurrent users

def kb_search_tool(query: str, db_path: str = DB_PATH) -> ToolResult:
    global _last_sources
    rag_params = get_rag_params()
    hits = search(query, top_k=rag_params["top_k"], source_types=("doc", "code"), db_path=db_path)
    if not hits:
        return ToolResult(ok=False, output="No relevant SOPs/manuals found in local knowledge base.")

    lines = []
    for score, doc in hits:
        confidence = "strong match" if score < 14 else "weak match" if score < 18 else "low relevance"
        lines.append(f"[{doc['file']}] ({confidence}, distance={score:.3f}) {doc['content'][:300]}")
        _last_sources.append({
            "id": doc["file"], "title": doc["file"], "page": "", "excerpt": doc["content"][:200],
        })
    return ToolResult(ok=True, output="\n".join(lines))


kb_tool = Tool(
    "search_knowledge_base",
    kb_search_tool,
    "Search internal SOPs/manuals for relevant grounded context. Returns matches with confidence labels."
)


def execute_code_tool_fn(code_string: str) -> ToolResult:
    """Agent tool wrapper: writes code to a temp file, executes it inside
    the OS-level sandbox (resource-limited subprocess), and returns output.
    Limits are pulled from centralized config (sandbox_timeout_sec, sandbox_max_mem_mb).
    """
    limits = get_sandbox_limits()
    tmp_file = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix="sandbox_", dir=None,  # None → system /tmp
            delete=False
        )
        tmp_file.write(code_string)
        tmp_file.close()

        result = execute_sandboxed_code(
            script_path=tmp_file.name,
            timeout_sec=limits["timeout_sec"],
            max_mem_mb=limits["max_mem_mb"],
        )

        if result["success"]:
            return ToolResult(ok=True, output=result["output"])
        else:
            return ToolResult(ok=False, output=result["error"])

    except Exception as e:
        return ToolResult(ok=False, output=f"[Sandbox Tool Error] {e}")
    finally:
        if tmp_file and os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)


code_exec_tool = Tool(
    "execute_code",
    execute_code_tool_fn,
    "Execute a Python script inside an isolated, resource-limited sandbox. "
    "Pass the FULL Python source code as a single string argument. "
    "Use ONLY when the task requires running or testing code. "
    "The sandbox enforces strict CPU and memory limits."
)


def build_llm_call(persona: str = "default", db_path: str = DB_PATH):
    def llm_call(agent_prompt: str, has_image: bool = False, image_path: str = None) -> str:
        task_type, reason = classify_task(agent_prompt, has_image=has_image)
        current_map = get_model_map()

        # BYOM: Use get_best_model() for graceful local fallback
        model_name, warning = get_best_model(task_type, model_map=current_map)

        if warning:
            print(f"[BYOM Warning] {warning}")

        if not model_name:
            return ('{"action": "finish", "result": "ERROR: No local models found. '
                    'Run `ollama pull <model>` to install one.", '
                    '"reasoning": "System error", "confidence": "high"}')

        if task_type == "vision":
            if not model_name:
                return '{"action": "finish", "result": "ERROR: No vision-capable model installed. Please run `ollama pull llava:7b`.", "reasoning": "System error", "confidence": "high"}'
            if not image_path:
                return '{"action": "finish", "result": "ERROR: Vision task classified but no image was provided.", "reasoning": "System error", "confidence": "high"}'
            response = ollama.generate(
                model=model_name,
                prompt=agent_prompt,
                images=[image_path],
                options=get_ollama_options(),
            )
            return response.get("response", "")

        response = ollama.generate(
            model=model_name,
            prompt=agent_prompt,
            options=get_ollama_options(),
        )
        return response.get("response", "")

    return llm_call


def run_agent(prompt, project_id="workbench", image_path=None, persona="default") -> dict:
    global _last_sources
    _last_sources = []

    if ollama is None:
        return {"error": "Ollama package is not installed."}

    dynamic_db_path = f"memory/{project_id}.db"
    project_kb_tool = Tool(
        "search_knowledge_base",
        lambda query: kb_search_tool(query, db_path=dynamic_db_path),
        kb_tool.description,
    )
    tools = [project_kb_tool, docgen_tool, code_exec_tool]

    llm_call = build_llm_call(persona=persona, db_path=dynamic_db_path)
    agent = Agent(llm_call=llm_call, tools=tools, max_steps=6)          # <-- agent created FIRST

    task_type, routing_reason = classify_task(prompt, has_image=bool(image_path))
    result = agent.run(prompt, has_image=bool(image_path), image_path=image_path)

    result["task_type"] = task_type
    result["routing_reason"] = routing_reason

    add_chat_memory(prompt, str(result["result"]), persona=persona, db_path=dynamic_db_path)
    try:
        check_and_consolidate(project_id=project_id)
    except Exception as e:
        print(f"[MemoryManager Warning] Consolidation check error: {e}")

    _write_audit_log(prompt, result)

    result["sources"] = _last_sources

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

