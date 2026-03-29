"""
config.py - Environment variable loader
Reads all sensitive settings from the .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Database settings ──────────────────────────────────────────────────────────
DB_HOST = os.getenv("DB_HOST", r"localhost\SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME", "fitness_app")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")

# ── AI API settings ────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── App settings ───────────────────────────────────────────────────────────────
APP_TITLE = "Gnaneswar Fitness AI"
APP_ICON  = "💪"
