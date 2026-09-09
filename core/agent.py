import json
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class ToolResult:
    ok: bool
    output: str

@dataclass
class Trace:
    steps: list = field(default_factory=list)
    def log(self, **kwargs):
        self.steps.append(kwargs)

class Tool:
    def __init__(self, name, fn, description):
        self.name, self.fn, self.description = name, fn, description

class Agent:
    def __init__(self, llm_call, tools, max_steps=6):
        self.llm_call = llm_call
        self.tools = {t.name: t for t in tools}
        self.max_steps = max_steps

    def run(self, task: str, has_image: bool = False, image_path: str = None) -> dict:

        trace = Trace()
        history = []
        tried_calls = set()
        
        for step in range(self.max_steps):
            prompt = self._build_prompt(task, history)
            raw = self.llm_call(prompt, has_image = has_image, image_path = image_path)
            
            print(f"\n[DEBUG] Step {step} Raw LLM Output:\n{raw}\n{'-'*40}")

            cleaned_raw = raw.strip()
            if cleaned_raw.startswith("```json"):
                cleaned_raw = cleaned_raw[7:]
            elif cleaned_raw.startswith("```"):
                cleaned_raw = cleaned_raw[3:]
            if cleaned_raw.endswith("```"):
                cleaned_raw = cleaned_raw[:-3]
            cleaned_raw = cleaned_raw.strip()

            try:
                decision = json.loads(cleaned_raw)
            except json.JSONDecodeError as e:
                trace.log(step=step, error=f"JSON Parse Error: {e}")
                history.append("System Error: Your last response was not valid JSON. You MUST output raw JSON without markdown formatting or conversational text.")
                continue

            trace.log(step=step, decision=decision)

            if decision["action"] == "finish":
                return {"result": decision["result"], "trace": trace.steps, "status": "completed"}

            elif decision["action"] == "call_tool":
                tool = self.tools.get(decision["tool"])
                if not tool:
                    history.append(f"ERROR: unknown tool {decision['tool']}")
                    continue
                if not isinstance(decision.get("arg"), str):
                    history.append(f"System Error: 'arg' must be a plain string, not {type(decision.get('arg')).__name__}. Retry with a string.")
                    continue
                call_key = (decision["tool"], decision["arg"])
                if call_key in tried_calls:
                    history.append(f"System Error: You already tried {decision['tool']}({decision['arg']}) with no useful result. Try a different query or finish.")
                    continue
                tried_calls.add(call_key)
                result = tool.fn(decision["arg"])
                history.append(f"Step {step}: {tool.name}({decision['arg']}) -> {'OK' if result.ok else 'FAIL'}: {result.output[:400]}")
                trace.log(step=step, tool=tool.name, arg=decision["arg"], result_ok=result.ok)

            else:
                history.append(
                    f"System Error: 'action' must be exactly \"call_tool\" or \"finish\" — you sent "
                    f"\"{decision.get('action')}\". To call a tool, use: "
                    f'{{"action": "call_tool", "tool": "search_knowledge_base", "arg": "your query"}}'
                    )
                continue

        # graceful partial-progress output, not a bare failure
        summary = self._summarize_partial(history)
        return {"result": summary, "trace": trace.steps, "status": "incomplete"}

    def _build_prompt(self, task, history):
        tool_menu = "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())
        hist = "\n".join(history) if history else "(nothing yet)"
        return f"""Task: {task}
            
            Available tools:
            {tool_menu}
            
            History of actions taken:
            {hist}

            CRITICAL RULES:
                1. You are a sovereign agent. Think step-by-step. You must respond ONLY in valid JSON.
                2. If no relevant manuals are found, you MUST explicitly say so — but you must
                STILL provide a complete, substantive answer from general knowledge. Admitting
                the gap is not a substitute for answering the question.
                3. Example of a correct tool call for generating a document:
                {{"action": "call_tool", "tool": "generate_docx", "arg": "# Title\\n\\nParagraph text here."}}
                The "arg" must always be a single plain markdown STRING, never a JSON object or array.            

            Choose one of these two formats:
                
                Option 1 (Use a tool):
                    {{"action": "call_tool", "tool": "<name>", "arg": "<arg>"}}

                Option 2 (Task is complete):
                    {{
                        "action": "finish",
                        "result": "<the final text, file path, or deliverable>",
                        "reasoning": "<step-by-step justification>",
                        "confidence": "high | medium | low"
                        }}"""

    def _summarize_partial(self, history):
        return "Stopped before finishing. Progress so far:\n" + "\n".join(history)
