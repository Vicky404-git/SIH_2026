try:
    import ollama
except ImportError:
    ollama = None

CAPABILITY_HINTS = {
    "coding": ["coder", "code", "starcoder", "codellama"],
    "vision": ["llava", "vision", "moondream", "bakllava"],
    "reasoning": ["llama", "qwen", "mistral", "phi"],
}

EXCLUDE_FROM_GENERATION = ["embed"]

def discover_models():
    """Auto-discover locally installed Ollama models at runtime.
    Returns a list of dicts with name, size, and guessed_capability.
    """
    if ollama is None:
        return []
    try:
        response = ollama.list()
        models = response.get("models", [])
    except Exception:
        return []

    tagged = []
    for m in models:
        name = m.get("model") or m.get("name", "")
        name_lower = name.lower()

        if any(ex in name_lower for ex in EXCLUDE_FROM_GENERATION):
            continue  # skip embedding-only models

        guessed = "general"
        for capability, hints in CAPABILITY_HINTS.items():
            if any(h in name_lower for h in hints):
                guessed = capability
                break
        tagged.append({"name": name, "size": m.get("size", 0), "guessed_capability": guessed})
    return tagged


def get_best_model(capability: str, model_map: dict = None):
    """Return the best locally available model name for a given capability.

    Fallback chain:
      1. User-configured override in model_map (if provided)
      2. Auto-discovered model matching the capability
      3. Any model tagged as "general"
      4. None (caller must handle — no silent misrouting)

    Returns (model_name: str | None, warning: str | None)
    """
    if model_map and model_map.get(capability):
        return model_map[capability], None

    discovered = discover_models()

    if not discovered:
        return None, "No local Ollama models found. Run `ollama pull <model>` to install one."

    # Try exact capability match
    match = next((m["name"] for m in discovered if m["guessed_capability"] == capability), None)
    if match:
        return match, None

    # Fallback to general
    general = next((m["name"] for m in discovered if m["guessed_capability"] == "general"), None)
    if general:
        return general, f"No '{capability}' model found locally. Falling back to general model: {general}"

    # Last resort: pick the first available model
    fallback = discovered[0]["name"]
    return fallback, f"No '{capability}' or 'general' model found. Using first available: {fallback}"

