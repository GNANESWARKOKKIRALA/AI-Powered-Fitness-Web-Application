"""
diet.py - AI Diet Planner Streamlit page.
Calls the Groq LLaMA model to produce a 7-day Indian diet plan.
"""
import streamlit as st
from ai_engine import generate_diet_plan


def show_diet_page(user: dict):
    st.title("🥗 AI Diet Planner")
    st.markdown("Get a personalised **7-day Indian meal plan** tailored to your goal.")

    # Pre-fill from workout page if available
    stats = st.session_state.get("user_stats", {})

    with st.form("diet_form"):
        col1, col2 = st.columns(2)
        with col1:
            weight   = st.number_input("Weight (kg)", 40, 200,
                                       int(stats.get("weight", 70)))
            calories = st.number_input("Daily Calorie Target (kcal)", 1200, 5000,
                                       int(stats.get("calories", 2200)))
        with col2:
            protein  = st.number_input("Daily Protein Target (g)", 50, 300,
                                       int(stats.get("protein_lo", 120)))
            goal     = st.selectbox("Fitness Goal",
                                    ["Bulking", "Cutting", "Maintenance"],
                                    index=["Bulking", "Cutting", "Maintenance"].index(
                                        stats.get("goal", "Maintenance")))

        veg = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Eggetarian"],
                       horizontal=True)
        submitted = st.form_submit_button("🍽️ Generate My Diet Plan", use_container_width=True)

    if submitted:
        with st.spinner("AI Chef is preparing your meal plan…"):
            profile = {
                "goal":     goal,
                "calories": calories,
                "protein":  protein,
                "weight":   weight,
                "age":      user["age"],
                "gender":   user["gender"],
                "veg_pref": veg,
            }
            plan = generate_diet_plan(profile)

        st.markdown("---")
        st.subheader("🗓️ Your 7-Day Indian Diet Plan")
        st.markdown(plan)

        st.info("💡 Tip: Drink at least 3–4 litres of water daily for optimal results.")
