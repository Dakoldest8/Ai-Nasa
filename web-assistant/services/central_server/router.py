def route(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["sad", "anxious", "depressed", "stress"]):
        return "mental"
    if any(w in t for w in ["run", "exercise", "workout"]):
        return "fitness"
    if any(w in t for w in ["diet", "food", "nutrition"]):
        return "nutrition"
    return "general"
