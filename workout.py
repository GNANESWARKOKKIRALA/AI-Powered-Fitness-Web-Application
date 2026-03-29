"""
workout.py - Fitness calculation helpers & Streamlit workout UI page.
"""
import streamlit as st
from ai_engine import generate_workout


# ── Calculation helpers ────────────────────────────────────────────────────────
def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:  return "Underweight"
    if bmi < 25.0:  return "Normal weight"
    if bmi < 30.0:  return "Overweight"
    return "Obese"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor formula."""
    if gender.lower() == "male":
        return round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5, 0)
    return round(10 * weight_kg + 6.25 * height_cm - 5 * age - 161, 0)


ACTIVITY_MULTIPLIERS = {
    "Sedentary (no exercise)":          1.2,
    "Lightly active (1-3 days/week)":   1.375,
    "Moderately active (3-5 days/week)":1.55,
    "Very active (6-7 days/week)":      1.725,
    "Super active (athlete)":           1.9,
}


def calculate_tdee(bmr: float, activity: str) -> float:
    return round(bmr * ACTIVITY_MULTIPLIERS.get(activity, 1.55), 0)


def calorie_target(tdee: float, goal: str) -> float:
    if goal == "Bulking":       return tdee + 400
    if goal == "Cutting":       return tdee - 400
    return tdee


def protein_target(weight_kg: float, goal: str) -> tuple[float, float]:
    """Returns (min_g, max_g)."""
    lo = round(weight_kg * 1.6, 0)
    hi = round(weight_kg * 2.2, 0)
    return lo, hi


# ── Streamlit page ─────────────────────────────────────────────────────────────
def show_workout_page(user: dict):
    st.title("🏋️ AI Workout Generator")
    st.markdown("Fill in your profile below and let the AI build your perfect training plan.")

    with st.form("workout_form"):
        col1, col2 = st.columns(2)
        with col1:
            height  = st.number_input("Height (cm)", 140, 220, 170)
            weight  = st.number_input("Weight (kg)", 40,  200, 70)
            goal    = st.selectbox("Fitness Goal", ["Bulking", "Cutting", "Maintenance"])
        with col2:
            experience = st.selectbox("Experience Level",
                                      ["Beginner", "Intermediate", "Advanced"])
            days       = st.slider("Days Available per Week", 3, 6, 4)
            activity   = st.selectbox("Activity Level", list(ACTIVITY_MULTIPLIERS.keys()))

        submitted = st.form_submit_button("⚡ Generate My Workout Plan", use_container_width=True)

    if submitted:
        bmi  = calculate_bmi(weight, height)
        bmr  = calculate_bmr(weight, height, user["age"], user["gender"])
        tdee = calculate_tdee(bmr, activity)
        cals = calorie_target(tdee, goal)
        p_lo, p_hi = protein_target(weight, goal)

        st.markdown("---")
        st.subheader("📊 Your Body Stats")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("BMI",          f"{bmi}",           bmi_category(bmi))
        m2.metric("BMR",          f"{int(bmr)} kcal")
        m3.metric("Daily Calories", f"{int(cals)} kcal")
        m4.metric("Protein Target", f"{int(p_lo)}–{int(p_hi)} g")

        st.markdown("---")
        st.subheader("🤖 AI-Recommended Workout Plan")
        with st.spinner("AI is building your personalised plan…"):
            profile = {
                "goal":        goal,
                "experience":  experience,
                "days_per_week": days,
                "weight":      weight,
                "age":         user["age"],
                "gender":      user["gender"],
            }
            plan = generate_workout(profile)
        st.markdown(plan)

        # Save stats to session
        st.session_state["user_stats"] = {
            "bmi": bmi, "bmr": bmr, "tdee": tdee,
            "calories": cals, "protein_lo": p_lo, "protein_hi": p_hi,
            "weight": weight, "goal": goal,
        }
