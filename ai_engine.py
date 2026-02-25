import requests

# ---------------------------------------------------------------------------
# Configuration — Groq API (Free, No Rate Limits)
# ---------------------------------------------------------------------------
GROQ_API_KEY = "YOUR API KEY"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.1-8b-instant"


def _call_groq(prompt: str) -> str:
    """
    Sends a prompt to Groq and returns the text response.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful fitness and nutrition expert."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
        "stream": False
    }

    try:
        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "⚠️ Network error. Check your internet connection."
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        msg = ""
        try:
            msg = e.response.json().get("error", {}).get("message", "")
        except Exception:
            pass
        if status == 401:
            return "⚠️ Invalid Groq API key. Please check your key at console.groq.com."
        elif status == 429:
            return "⚠️ Too many requests. Please wait 1 minute and try again."
        elif status == 400:
            return f"⚠️ Bad request: {msg}. Please try again."
        else:
            return f"⚠️ HTTP Error {status}: {msg or str(e)}"
    except (KeyError, IndexError):
        return "⚠️ Unexpected response from Groq API. Please try again."
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# ---------------------------------------------------------------------------
# Diet Plan Generator
# ---------------------------------------------------------------------------

def generate_diet_plan(profile: dict) -> str:
    goal = profile.get("goal", "Maintain")
    if goal == "Bulking":
        calorie_note = f"calorie SURPLUS (+400 kcal) — target ~{int(profile['daily_calories']) + 400} kcal/day"
    elif goal == "Cutting":
        calorie_note = f"calorie DEFICIT (-400 kcal) — target ~{int(profile['daily_calories']) - 400} kcal/day"
    else:
        calorie_note = f"maintenance calories — target ~{int(profile['daily_calories'])} kcal/day"

    prompt = f"""
You are an expert Indian sports nutritionist and gym dietician.

Create a detailed, practical 7-day Indian diet plan for:
- Name: {profile.get('name', 'User')}
- Age: {profile.get('age')} years | Gender: {profile.get('gender')}
- Weight: {profile.get('weight')} kg | Height: {profile.get('height')} cm
- Fitness Goal: {goal}
- Daily Calorie Target: {calorie_note}
- Daily Protein Requirement: {profile.get('protein_req', 150):.0f}g

Rules:
1. Use ONLY common Indian foods (dal, roti, sabzi, paneer, eggs, chicken, rice, etc.)
2. Include: Breakfast, Mid-Morning Snack, Lunch, Evening Snack, Dinner
3. Mention approximate calories and protein for each meal
4. Show total daily calories and protein at end of each day
5. Format each day clearly with headings like Day 1 - Monday
6. Keep meals realistic, affordable, and gym-friendly
7. Be specific with quantities (e.g., 2 whole eggs + 3 egg whites, 200g cooked chicken breast)
"""
    return _call_groq(prompt)


# ---------------------------------------------------------------------------
# Workout Generator
# ---------------------------------------------------------------------------

def generate_workout_plan(profile: dict) -> str:
    prompt = f"""
You are an elite certified personal trainer and bodybuilding coach.

Create a complete weekly gym workout plan for:
- Fitness Goal: {profile.get('goal', 'Maintain')}
- Experience Level: {profile.get('experience', 'Beginner')}
- Gender: {profile.get('gender', 'Male')}

Requirements:
1. Use Push-Pull-Legs (PPL) split across 6 days, Day 7 is Rest
2. For each exercise include: Sets x Reps, Rest time, and a short tip
3. Structure:
   Day 1: Push - Chest, Shoulders, Triceps
   Day 2: Pull - Back, Biceps
   Day 3: Legs - Quads, Hamstrings, Calves, Glutes
   Day 4: Push Variation
   Day 5: Pull Variation
   Day 6: Legs Variation
   Day 7: Rest and Recovery
4. Adjust intensity for experience level:
   Beginner: 3 sets, compound movements, lower volume
   Intermediate: 4 sets, mix of compound and isolation
   Advanced: 4-5 sets, high volume, drop sets and supersets
5. Format each day with heading Day X - Muscle Groups
6. Include warm-up and cool-down recommendations
"""
    return _call_groq(prompt)


# ---------------------------------------------------------------------------
# AI Chatbot (Trainer Mode)
# ---------------------------------------------------------------------------

def chat_with_trainer(user_message: str, chat_history: list, profile: dict) -> str:
    history_text = ""
    for msg in chat_history[-8:]:
        role_label = "User" if msg["role"] == "user" else "Trainer"
        history_text += f"{role_label}: {msg['message']}\n"

    profile_context = ""
    if profile:
        profile_context = f"""
User Profile:
- Goal: {profile.get('goal', 'Not set')}
- Experience: {profile.get('experience', 'Not set')}
- Weight: {profile.get('weight', 'N/A')} kg
- Daily Calories: {profile.get('daily_calories', 'N/A')} kcal
"""

    prompt = f"""
You are Gnaneswar's personal AI gym trainer — an expert in bodybuilding,
strength training, sports nutrition, and fitness. You speak confidently,
motivationally, and give SPECIFIC, ACTIONABLE advice.

{profile_context}

Conversation so far:
{history_text}

User: {user_message}
Trainer:"""

    return _call_groq(prompt)