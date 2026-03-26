def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "⚠️"
    elif bmi < 25:
        return "Normal Weight", "✅"
    elif bmi < 30:
        return "Overweight", "⚠️"
    else:
        return "Obese", "❌"


def calculate_bmr(weight, height_cm, age, gender):
    if gender == "Male":
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) - 161
    return round(bmr, 1)


def calculate_tdee(bmr, activity_level):
    multipliers = {
        "Sedentary (No exercise)": 1.2,
        "Lightly Active (1-3 days/week)": 1.375,
        "Moderately Active (3-5 days/week)": 1.55,
        "Very Active (6-7 days/week)": 1.725,
        "Extra Active (Physical job)": 1.9
    }
    multiplier = multipliers.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)


def calculate_goal_calories(tdee, goal):
    if goal == "Bulking (Gain Muscle)":
        return round(tdee + 400, 1)
    elif goal == "Cutting (Lose Fat)":
        return round(tdee - 400, 1)
    else:
        return tdee


def calculate_protein(weight, goal, experience):
    if goal == "Cutting (Lose Fat)" or experience == "Advanced":
        return round(weight * 2.2, 1)
    elif goal == "Bulking (Gain Muscle)":
        return round(weight * 2.0, 1)
    else:
        return round(weight * 1.6, 1)


def get_all_calculations(weight, height_cm, age, gender, activity_level, goal, experience):
    bmi = calculate_bmi(weight, height_cm)
    bmi_cat, bmi_icon = get_bmi_category(bmi)
    bmr = calculate_bmr(weight, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    daily_calories = calculate_goal_calories(tdee, goal)
    protein = calculate_protein(weight, goal, experience)
    return {
        'bmi': bmi, 'bmi_category': bmi_cat, 'bmi_icon': bmi_icon,
        'bmr': bmr, 'tdee': tdee,
        'daily_calories': daily_calories, 'protein_req': protein
    }
