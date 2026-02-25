"""
fitness_calc.py
All fitness calculation logic using scientifically validated formulas.
"""


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Body Mass Index"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight 🟡"
    elif bmi < 25.0:
        return "Normal Weight 🟢"
    elif bmi < 30.0:
        return "Overweight 🟠"
    else:
        return "Obese 🔴"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor Equation (most accurate for general population)
    Male:   BMR = 10*W + 6.25*H - 5*A + 5
    Female: BMR = 10*W + 6.25*H - 5*A - 161
    """
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "Male":
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 0)


def calculate_tdee(bmr: float, activity_level: str = "Moderate") -> float:
    """
    Total Daily Energy Expenditure using activity multipliers.
    """
    multipliers = {
        "Sedentary (little/no exercise)": 1.2,
        "Light (1-3 days/week)": 1.375,
        "Moderate (3-5 days/week)": 1.55,
        "Active (6-7 days/week)": 1.725,
        "Very Active (2x/day)": 1.9,
    }
    multiplier = multipliers.get(activity_level, 1.55)
    return round(bmr * multiplier, 0)


def calculate_goal_calories(tdee: float, goal: str) -> float:
    """Adjust TDEE based on fitness goal."""
    if goal == "Bulking":
        return round(tdee + 400, 0)
    elif goal == "Cutting":
        return round(tdee - 400, 0)
    else:  # Maintain
        return round(tdee, 0)


def calculate_protein(weight_kg: float, goal: str, experience: str) -> float:
    """
    Protein requirements:
    - Cutting / Advanced: 2.2g per kg
    - Bulking / Intermediate: 2.0g per kg
    - Maintain / Beginner: 1.6g per kg
    """
    if goal == "Cutting" or experience == "Advanced":
        multiplier = 2.2
    elif goal == "Bulking" or experience == "Intermediate":
        multiplier = 2.0
    else:
        multiplier = 1.6
    return round(weight_kg * multiplier, 0)


def full_calculation(weight: float, height: float, age: int,
                     gender: str, goal: str, experience: str,
                     activity_level: str = "Moderate (3-5 days/week)") -> dict:
    """Run all calculations and return as a dictionary."""
    bmi = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    daily_calories = calculate_goal_calories(tdee, goal)
    protein = calculate_protein(weight, goal, experience)

    return {
        "bmi": bmi,
        "bmi_category": bmi_category(bmi),
        "bmr": bmr,
        "tdee": tdee,
        "daily_calories": daily_calories,
        "protein_req": protein,
    }
