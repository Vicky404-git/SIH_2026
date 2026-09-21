"""Pre-execution AST inspector for agent-generated code.

Defence-in-depth: scans Python source for dangerous imports BEFORE
the sandbox subprocess is spawned.  Uses only stdlib (ast module).
"""

import ast
from typing import Dict, Any, List

# Modules that agent-generated code must NEVER import.
# Strict by default — blocks filesystem, network, and system access.
BLOCKED_MODULES = frozenset({
    "os", "subprocess", "shutil", "socket", "http", "urllib",
    "requests", "pathlib", "sqlite3", "ctypes", "sys",
    "importlib", "code", "codeop", "compileall",
    "signal", "multiprocessing", "threading",
})


def inspect_code(source: str) -> Dict[str, Any]:
    """Parse *source* and check every import against the blocklist.

    Returns
    -------
    dict  {"safe": bool, "blocked_imports": list[str]}
        - safe=True  → no blocked imports found, OK to execute
        - safe=False → at least one blocked import; list them
    """
    blocked: List[str] = []

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        # Unparseable code is rejected outright — never execute what we
        # cannot statically verify.
        return {"safe": False, "blocked_imports": [f"<SyntaxError: {e}>"]}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_module = alias.name.split(".")[0]
                if top_module in BLOCKED_MODULES:
                    blocked.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top_module = node.module.split(".")[0]
                if top_module in BLOCKED_MODULES:
                    blocked.append(node.module)

    return {"safe": len(blocked) == 0, "blocked_imports": blocked}
