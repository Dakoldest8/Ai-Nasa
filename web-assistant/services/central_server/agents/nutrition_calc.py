# nutrition_calc.py
from typing import Literal

# ---------------------------
# Input validation helpers
# ---------------------------
def validate_positive_number(value: float, name: str, min_val: float = 0, max_val: float = 1e6) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not (min_val <= value <= max_val):
        raise ValueError(f"{name} must be between {min_val} and {max_val}")
    return value

# ---------------------------
# BMI
# ---------------------------
def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    weight_kg = validate_positive_number(weight_kg, "Weight", 10, 200)
    height_cm = validate_positive_number(height_cm, "Height", 50, 250)
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

# ---------------------------
# EER (Estimated Energy Requirement)
# ---------------------------
def calculate_eer(
    sex: Literal["male", "female"],
    age: int,
    weight_kg: float,
    height_cm: float,
    activity_level: Literal["sedentary", "low", "active", "very active"]
) -> int:
    weight_kg = validate_positive_number(weight_kg, "Weight", 10, 200)
    height_cm = validate_positive_number(height_cm, "Height", 50, 250)
    age = int(age)

    pa_map = {"sedentary": 1.0, "low": 1.11, "active": 1.25, "very active": 1.48}
    pa = pa_map.get(activity_level, 1.0)
    height_m = height_cm / 100

    if sex == "male":
        eer = 662 - 9.53 * age + pa * (15.91 * weight_kg + 539.6 * height_m)
    else:
        eer = 354 - 6.91 * age + pa * (9.36 * weight_kg + 726 * height_m)

    return round(eer)

# ---------------------------
# Adjust calories for EVA
# ---------------------------
def adjust_calories_for_eva(calories: int, eva: Literal["none", "occasional", "frequent"]) -> int:
    if eva == "frequent":
        return calories + 300
    elif eva == "occasional":
        return calories + 150
    return calories

# ---------------------------
# Protein
# ---------------------------
def protein_dri(weight_kg: float, env: Literal["earth", "space"]) -> int:
    weight_kg = validate_positive_number(weight_kg, "Weight")
    factor = 1.0 if env == "space" else 0.8
    return round(weight_kg * factor)

# ---------------------------
# Calcium
# ---------------------------
def calcium_dri(env: Literal["earth", "space"]) -> int:
    return 1200 if env == "space" else 1000

# ---------------------------
# Vitamin D
# ---------------------------
def vitamin_d_dri(env: Literal["earth", "space"]) -> int:
    return 20 if env == "space" else 15

# ---------------------------
# Sodium
# ---------------------------
def sodium_target(env: Literal["earth", "space"]) -> int:
    return 1800 if env == "space" else 2300

def sodium_max() -> int:
    return 2300

# ---------------------------
# Vitamin C
# ---------------------------
def vitamin_c_dri(sex: Literal["male", "female"], radiation: Literal["low", "moderate", "high"]) -> int:
    base = 90 if sex == "male" else 75
    if radiation == "high":
        base += 20
    return base

# ---------------------------
# Water
# ---------------------------
def water_dri(sex: Literal["male", "female"], env: Literal["earth", "space"], eva: Literal["none", "occasional", "frequent"]) -> int:
    base = 3700 if sex == "male" else 2700
    if env == "space":
        base -= 200
    if eva == "frequent":
        base += 500
    return base
