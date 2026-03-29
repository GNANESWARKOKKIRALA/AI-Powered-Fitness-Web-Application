"""
ai_engine.py - Groq LLaMA integration (robust + future-proof)
"""

from groq import Groq
from config import GROQ_API_KEY

# Initialise client once
_client = Groq(api_key=GROQ_API_KEY)

# ✅ Updated models
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"


def _safe_completion(messages, max_tokens=1500):
    """Handles Groq calls with fallback + error protection."""
    try:
        response = _client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[Groq ERROR - primary] {e}")

        # 🔁 fallback model
        try:
            response = _client.chat.completions.create(
                model=FALLBACK_MODEL,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        except Exception as e2:
            print(f"[Groq ERROR - fallback] {e2}")
            return "⚠️ AI service is temporarily unavailable. Please try again later."


def _call_groq(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return _safe_completion(messages, max_tokens)


# ── Workout Generator ──────────────────────────────────────────────────────────
def generate_workout(profile: dict) -> str:
    system = (
        "You are an elite certified personal trainer and bodybuilding coach. "
        "You provide structured, science-based workout plans. "
        "Always explain your split choice, then give a full weekly schedule "
        "with exercises, sets, reps, rest times, warm-up, and optional cardio. "
        "Format output clearly using headings and bullet points."
    )

    user = f"""
Create a complete workout plan for:
- Goal: {profile['goal']}
- Experience: {profile['experience']}
- Days available per week: {profile['days_per_week']}
- Weight: {profile['weight']} kg
- Age: {profile['age']}
- Gender: {profile['gender']}
"""

    return _call_groq(system, user, max_tokens=1800)


# ── Diet Planner ───────────────────────────────────────────────────────────────
def generate_diet_plan(profile: dict) -> str:
    system = (
        "You are a certified sports nutritionist specialising in Indian cuisine. "
        "Create detailed, realistic and practical meal plans using common Indian foods. "
        "Keep it structured and easy to follow."
    )

    user = f"""
Create a 7-day Indian diet plan for:
- Goal: {profile['goal']}
- Daily calorie target: {profile['calories']} kcal
- Daily protein target: {profile['protein']} g
- Weight: {profile['weight']} kg
- Age: {profile['age']}
- Gender: {profile['gender']}
"""

    return _call_groq(system, user, max_tokens=2000)


# ── Chat Trainer ───────────────────────────────────────────────────────────────
def chat_with_trainer(conversation_history: list, user_message: str) -> str:
    system = (
        "You are Gnaneswar AI Fitness Coach – a professional gym trainer, "
        "nutritionist, and bodybuilding expert. "
        "Respond in a motivating, knowledgeable, and friendly tone. "
        "Give practical, actionable advice. Keep answers concise but complete."
    )

    messages = [{"role": "system", "content": system}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    return _safe_completion(messages, max_tokens=1000)