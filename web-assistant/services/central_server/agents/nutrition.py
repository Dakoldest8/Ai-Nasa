try:
    from ..memory import save_memory
except ImportError:
    from memory import save_memory
from . import nutrition_calc

def handle(user_id: str, text: str, memory: dict, llm) -> dict:
    """
    Handle nutrition requests and update memory.
    `text` expected as a dictionary-like string:
    '{"sex": "male", "age": 30, "weight": 70, "height": 175, "activity": "active", "env": "earth", "radiation": "low", "eva": "none"}'
    """
    try:
        user_data = eval(text)
    except Exception:
        return {"response": "Invalid input format. Send as a dictionary.", "memory": memory}

    bmi = nutrition_calc.calculate_bmi(user_data["weight"], user_data["height"])
    eer = nutrition_calc.calculate_eer(user_data["sex"], user_data["age"], user_data["weight"], user_data["height"], user_data["activity"])
    calories = nutrition_calc.adjust_calories_for_eva(eer, user_data["eva"])
    protein = nutrition_calc.protein_dri(user_data["weight"], user_data["env"])
    calcium = nutrition_calc.calcium_dri(user_data["env"])
    vitamin_d = nutrition_calc.vitamin_d_dri(user_data["env"])
    sodium = nutrition_calc.sodium_target(user_data["env"])
    sodium_max_val = nutrition_calc.sodium_max()
    vitamin_c = nutrition_calc.vitamin_c_dri(user_data["sex"], user_data["radiation"])
    water = nutrition_calc.water_dri(user_data["sex"], user_data["env"], user_data["eva"])

    report = (
        f"--- NUTRITION REPORT ---\n"
        f"BMI: {bmi}\n"
        f"Calories: {calories} kcal\n"
        f"Protein: {protein} g\n"
        f"Calcium: {calcium} mg\n"
        f"Vitamin D: {vitamin_d} mcg\n"
        f"Vitamin C: {vitamin_c} mg\n"
        f"Water: {water} ml\n"
        f"Sodium target: {sodium} mg\n"
        f"Sodium max: {sodium_max_val} mg"
    )

    if memory is None:
        memory = {}
    memory["nutrition"] = user_data
    memory["nutrition"]["report"] = report

    save_memory("users", user_id, memory)

    return {"response": report, "memory": memory}
