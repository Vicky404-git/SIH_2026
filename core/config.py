"""
CLANKA CONFIG / RESOURCE CONTROL
=================================
Pure logic - no CLI printing. `mem_percent` is the one user-facing knob;
everything else (num_ctx, top_k, chunk size) derives from it so the rest
of the codebase doesn't have to know about raw byte budgets.
"""

import json
import os
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

CONFIG_DIR = Path(os.path.expanduser("~/.clanka"))
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULTS = {
    "mem_percent": 50,      # % of system RAM Clanka is allowed to target
    "persona": "default",
    "last_consolidated": 0,  # unix timestamp, used later by memory consolidation
}

# Rough context-window ladder. Bigger num_ctx = more RAM for the KV cache.
# These are deliberately conservative - better to under-promise than lag
# the user's machine, which was the original complaint.
_CTX_LADDER = [
    (20, 1024),
    (40, 2048),
    (60, 4096),
    (80, 8192),
    (100, 16384),
]


def load_config():
    """Loads config from disk, filling in any missing keys with defaults."""
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}

    merged = {**DEFAULTS, **data}
    return merged


def save_config(config):
    """Writes config to disk. Creates ~/.clanka if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def set_mem_percent(percent):
    """Validates and persists a new mem_percent. Returns the saved config."""
    percent = int(percent)
    if not (5 <= percent <= 100):
        raise ValueError("mem_percent must be between 5 and 100")

    config = load_config()
    config["mem_percent"] = percent
    save_config(config)
    return config


def get_total_ram_gb():
    """System RAM in GB, or None if psutil isn't available."""
    if psutil is None:
        return None
    return psutil.virtual_memory().total / (1024 ** 3)


def _num_ctx_for_percent(percent):
    for threshold, ctx in _CTX_LADDER:
        if percent <= threshold:
            return ctx
    return _CTX_LADDER[-1][1]


def get_ollama_options(mem_percent=None):
    """Maps mem_percent -> options dict to pass into ollama.generate(options=...).

    This is the main integration point: every call site should build its
    options through this function instead of hardcoding num_ctx.
    """
    if mem_percent is None:
        mem_percent = load_config()["mem_percent"]

    num_ctx = _num_ctx_for_percent(mem_percent)

    # num_thread: scale with percent, but never claim more than the machine has
    cpu_count = os.cpu_count() or 4
    num_thread = max(1, round(cpu_count * (mem_percent / 100)))

    return {
        "num_ctx": num_ctx,
        "num_thread": num_thread,
    }


def get_rag_params(mem_percent=None):
    """Maps mem_percent -> RAG retrieval budget (top_k, max chars injected)."""
    if mem_percent is None:
        mem_percent = load_config()["mem_percent"]

    if mem_percent <= 20:
        return {"top_k": 1, "max_file_chars": 1500}
    elif mem_percent <= 40:
        return {"top_k": 2, "max_file_chars": 2500}
    elif mem_percent <= 60:
        return {"top_k": 3, "max_file_chars": 4000}
    elif mem_percent <= 80:
        return {"top_k": 5, "max_file_chars": 6000}
    else:
        return {"top_k": 8, "max_file_chars": 10000}


def get_background_job_percent():
    """Throttle level for background jobs (e.g. weekly memory consolidation),
    always well below the interactive mem_percent so it doesn't compete with
    a live session. Fixed low default per the plan (~10%), floor of 5.
    """
    return max(5, min(10, load_config()["mem_percent"] // 2))
