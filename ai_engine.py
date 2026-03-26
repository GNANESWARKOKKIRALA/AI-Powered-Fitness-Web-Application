import requests
import os

GROQ_API_KEY = "YOUR_API"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"


def call_groq(system_prompt, user_prompt, max_tokens=2048):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": False
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def generate_diet_plan(profile, user_name):
    goal_map = {
        "Bulking (Gain Muscle)": f"Bulking — eat {int(profile['daily_calories'])} kcal (TDEE + 400)",
        "Cutting (Lose Fat)":    f"Cutting — eat {int(profile['daily_calories'])} kcal (TDEE - 400)",
        "Maintain Weight":       f"Maintain — eat {int(profile['daily_calories'])} kcal"
    }
    goal_str = goal_map.get(profile['goal'], profile['goal'])
    system = "You are an expert Indian sports nutritionist and gym dietician."
    user = f"""Create a detailed 7-day Indian diet plan for:
- Name: {user_name}, Age: {profile['age']}, Gender: {profile['gender']}
- Weight: {profile['weight']}kg, Height: {profile['height']}cm
- Goal: {goal_str}
- Daily Protein Target: {profile['protein_req']}g/day

Rules:
1. Use ONLY Indian foods (dal, roti, rice, paneer, eggs, chicken, curd, fruits)
2. Show calories and protein for every meal
3. Include 5 meals: Breakfast, Mid-Morning Snack, Lunch, Evening Snack, Dinner
4. Format: Day 1, Day 2... Day 7 with all meals listed
5. Add weekly total calories at end"""
    return call_groq(system, user, 2048)


def generate_workout_plan(profile, user_name):
    system = "You are an expert gym trainer and strength coach."
    user = f"""Create a complete 6-day Push Pull Legs workout program for:
- Name: {user_name}, Age: {profile['age']}, Gender: {profile['gender']}
- Weight: {profile['weight']}kg, Goal: {profile['goal']}
- Experience: {profile['experience']}

Format:
- Day 1: Push (Chest, Shoulders, Triceps)
- Day 2: Pull (Back, Biceps)
- Day 3: Legs (Quads, Hamstrings, Glutes, Calves)
- Day 4: Push+, Day 5: Pull+, Day 6: Legs+, Day 7: Rest

For each exercise show: Sets x Reps, Rest time, coaching tip"""
    return call_groq(system, user, 2048)


def chat_with_trainer(user_message, profile, user_name, chat_history):
    system = f"""You are an expert personal fitness trainer and nutritionist.
You are talking to {user_name}.
Their profile: Age {profile['age']}, Gender {profile['gender']},
Weight {profile['weight']}kg, Goal {profile['goal']},
Experience {profile['experience']},
Daily calories {profile['daily_calories']} kcal,
Protein target {profile['protein_req']}g/day.
Give personalized, motivating, practical fitness advice."""

    messages = [{"role": "system", "content": system}]
    for msg in chat_history[-8:]:
        messages.append({"role": msg['role'], "content": msg['message']})
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
        "stream": False
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {str(e)}"
