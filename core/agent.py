# core/agent.py
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

    def run(self, task: str) -> dict:
        trace = Trace()
        history = []

        for step in range(self.max_steps):
            prompt = self._build_prompt(task, history)
            raw = self.llm_call(prompt)
            try:
                decision = json.loads(raw)
            except json.JSONDecodeError:
                trace.log(step=step, error="model returned non-JSON, retrying")
                continue

            trace.log(step=step, decision=decision)

            if decision["action"] == "finish":
                return {"result": decision["result"], "trace": trace.steps, "status": "completed"}

            if decision["action"] == "call_tool":
                tool = self.tools.get(decision["tool"])
                if not tool:
                    history.append(f"ERROR: unknown tool {decision['tool']}")
                    continue
                result = tool.fn(decision["arg"])
                history.append(f"Step {step}: {tool.name}({decision['arg']}) -> {'OK' if result.ok else 'FAIL'}: {result.output[:400]}")
                trace.log(step=step, tool=tool.name, arg=decision["arg"], result_ok=result.ok)

        # graceful partial-progress output, not a bare failure
        summary = self._summarize_partial(history)
        return {"result": summary, "trace": trace.steps, "status": "incomplete"}

    def _build_prompt(self, task, history):
        tool_menu = "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())
        hist = "\n".join(history) if history else "(nothing yet)"
        return f"""Task: {task}

Available tools:
{tool_menu}

History:
{hist}

Respond ONLY as JSON:
{{"action": "call_tool", "tool": "<name>", "arg": "<arg>"}}
or
{{"action": "finish", "result": "<final deliverable text/path>"}}
"""

    def _summarize_partial(self, history):
        return "Stopped before finishing. Progress so far:\n" + "\n".join(history)
