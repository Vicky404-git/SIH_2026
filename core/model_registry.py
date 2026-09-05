import ollama

CAPABILITY_HINTS = {
    "coding": ["coder", "code", "starcoder", "codellama"],
    "vision": ["llava", "vision", "moondream", "bakllava"],
    "reasoning": ["llama", "qwen", "mistral", "phi"],
}

EXCLUDE_FROM_GENERATION = ["embed"]

def discover_models():
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
