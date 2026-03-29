# 💪 Gnaneswar Fitness AI

A production-level AI Fitness Web Application built with Python + Streamlit.

## Features
- 🔐 Secure user authentication (bcrypt hashing)
- 🏋️ AI Workout Generator (6 splits: PPL, Bro, Arnold, Upper/Lower, Full Body, Strength)
- 🥗 7-Day Indian Diet Planner (AI-powered via Groq LLaMA 3.3)
- 🤖 AI Chat Trainer (multi-turn conversation)
- 📊 Progress Tracker with charts
- 🧮 BMI, BMR, TDEE, Protein calculations

## Setup

### 1. Prerequisites
- Python 3.10+
- SQL Server Express (SQLEXPRESS) with Windows Authentication
- ODBC Driver 17 for SQL Server
- Groq API key (free at console.groq.com)

### 2. Install dependencies
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure environment
Edit `.env` with your actual values:
```
DB_HOST=localhost\SQLEXPRESS
DB_NAME=fitness_app
DB_TRUSTED_CONNECTION=yes
GROQ_API_KEY=your_actual_key_here
```

### 4. Run the app
```bash
streamlit run app.py
```

## Project Structure
```
Fitness_AI/
├── app.py          # Main Streamlit app & page routing
├── auth.py         # Login / Register logic
├── database.py     # SQL Server connection & schema setup
├── ai_engine.py    # Groq LLaMA 3.3 AI calls
├── config.py       # Environment variable loader
├── diet.py         # Diet planner UI page
├── workout.py      # Workout generator UI page + calculations
├── progress.py     # Progress tracker UI page
├── requirements.txt
├── .env            # ← Add your secrets here (not committed)
└── .gitignore
```

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| AI/LLM | Groq API (LLaMA 3.3 70B) |
| Database | SQL Server Express (pyodbc) |
| Auth | bcrypt password hashing |
| Config | python-dotenv |
| Charts | Streamlit native (line_chart) |
| Data | pandas |
