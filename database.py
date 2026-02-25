import sqlite3
import os

DB_PATH = "data.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Profiles table
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            goal TEXT,
            experience TEXT,
            bmi REAL,
            bmr REAL,
            daily_calories REAL,
            protein_req REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Progress table
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weight REAL,
            calories_eaten REAL,
            workout_done TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Chat history table
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------- USER OPERATIONS ----------

def create_user(name, email, hashed_password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Email already registered. Please login."
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user


# ---------- PROFILE OPERATIONS ----------

def save_profile(user_id, age, gender, height, weight, goal, experience,
                 bmi, bmr, daily_calories, protein_req):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO profiles (user_id, age, gender, height, weight, goal, experience,
                              bmi, bmr, daily_calories, protein_req)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            age=excluded.age, gender=excluded.gender,
            height=excluded.height, weight=excluded.weight,
            goal=excluded.goal, experience=excluded.experience,
            bmi=excluded.bmi, bmr=excluded.bmr,
            daily_calories=excluded.daily_calories,
            protein_req=excluded.protein_req
    """, (user_id, age, gender, height, weight, goal, experience,
          bmi, bmr, daily_calories, protein_req))
    conn.commit()
    conn.close()


def get_profile(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    profile = c.fetchone()
    conn.close()
    return profile


# ---------- PROGRESS OPERATIONS ----------

def log_progress(user_id, date, weight, calories_eaten, workout_done, notes):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO progress (user_id, date, weight, calories_eaten, workout_done, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, date, weight, calories_eaten, workout_done, notes))
    conn.commit()
    conn.close()


def get_progress(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM progress WHERE user_id = ?
        ORDER BY date ASC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


# ---------- CHAT OPERATIONS ----------

def save_chat(user_id, role, message):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message)
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id, limit=20):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT role, message FROM chat_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))


def clear_chat_history(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
