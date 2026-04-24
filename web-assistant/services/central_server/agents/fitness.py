try:
    from ..memory import save_memory
except ImportError:
    from memory import save_memory

def handle(user_id: str, text: str, memory: dict, llm) -> dict:
    """
    Provide exercise recommendations and update memory.
    `text` is expected as a dictionary-like string:
    '{"goal": "strength", "level": "beginner"}'
    """
    try:
        user_data = eval(text)
    except Exception:
        return {"response": "Invalid input format. Send as a dictionary.", "memory": memory}

    goal = user_data.get("goal", "general")
    level = user_data.get("level", "beginner")

    if goal == "strength":
        exercises = ["Bodyweight squats", "Push-ups", "Resistance band rows"] if level == "beginner" else ["Weighted squats", "Bench press", "Deadlifts"]
    elif goal == "cardio":
        exercises = ["Running 20 min", "Cycling 30 min", "Jump rope 15 min"]
    else:
        exercises = ["Walking 30 min", "Stretching 15 min", "Bodyweight exercises"]

    response = "Recommended exercises: " + ", ".join(exercises)

    if memory is None:
        memory = {}
    memory["fitness"] = {
        "goal": goal,
        "level": level,
        "recommendations": exercises
    }

    save_memory("users", user_id, memory)

    return {"response": response, "memory": memory}
