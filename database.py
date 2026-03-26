import mysql.connector
from mysql.connector import Error

# ─────────────────────────────────────────────────────────────────
# MySQL Configuration
# ─────────────────────────────────────────────────────────────────
HOST     = 'localhost'
USER     = 'User name'
PASSWORD = 'user_password'
DATABASE = 'your database'
# ─────────────────────────────────────────────────────────────────


def get_connection():
    return mysql.connector.connect(
        host=HOST, user=USER,
        password=PASSWORD, database=DATABASE
    )


def init_db():
    try:
        conn = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        conn.commit()
        conn.close()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INT AUTO_INCREMENT PRIMARY KEY,
                name       VARCHAR(100) NOT NULL,
                email      VARCHAR(255) NOT NULL UNIQUE,
                password   VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id        INT PRIMARY KEY,
                age            INT,
                gender         VARCHAR(10),
                height         FLOAT,
                weight         FLOAT,
                goal           VARCHAR(50),
                experience     VARCHAR(50),
                activity_level VARCHAR(50),
                bmi            FLOAT,
                bmr            FLOAT,
                daily_calories FLOAT,
                protein_req    FLOAT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id             INT AUTO_INCREMENT PRIMARY KEY,
                user_id        INT,
                date           DATE,
                weight         FLOAT,
                calories_eaten FLOAT,
                workout_done   TINYINT(1) DEFAULT 0,
                notes          VARCHAR(500),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id         INT AUTO_INCREMENT PRIMARY KEY,
                user_id    INT,
                role       VARCHAR(20),
                message    TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")

    except Error as e:
        print(f"❌ Database error: {e}")


def create_user(name, email, hashed_password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_user_by_email(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'name': row[1], 'email': row[2], 'password': row[3]}
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_user_by_id(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'name': row[1], 'email': row[2]}
        return None
    except Exception as e:
        return None


def save_profile(user_id, age, gender, height, weight, goal,
                 experience, activity_level, bmi, bmr,
                 daily_calories, protein_req):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM profiles WHERE user_id = %s", (user_id,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("""
                UPDATE profiles SET age=%s, gender=%s, height=%s, weight=%s,
                goal=%s, experience=%s, activity_level=%s, bmi=%s, bmr=%s,
                daily_calories=%s, protein_req=%s WHERE user_id=%s
            """, (age, gender, height, weight, goal, experience,
                  activity_level, bmi, bmr, daily_calories, protein_req, user_id))
        else:
            cursor.execute("""
                INSERT INTO profiles (user_id, age, gender, height, weight, goal,
                experience, activity_level, bmi, bmr, daily_calories, protein_req)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (user_id, age, gender, height, weight, goal,
                  experience, activity_level, bmi, bmr, daily_calories, protein_req))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def get_profile(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'user_id': row[0], 'age': row[1], 'gender': row[2],
                'height': row[3], 'weight': row[4], 'goal': row[5],
                'experience': row[6], 'activity_level': row[7],
                'bmi': row[8], 'bmr': row[9],
                'daily_calories': row[10], 'protein_req': row[11]
            }
        return None
    except Exception as e:
        return None


def save_progress(user_id, date, weight, calories_eaten, workout_done, notes):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO progress (user_id, date, weight, calories_eaten, workout_done, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, date, weight, calories_eaten, 1 if workout_done else 0, notes))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def get_progress(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, weight, calories_eaten, workout_done, notes
            FROM progress WHERE user_id = %s ORDER BY date ASC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'date': r[0], 'weight': r[1], 'calories_eaten': r[2],
                 'workout_done': bool(r[3]), 'notes': r[4]} for r in rows]
    except Exception as e:
        return []


def save_chat_message(user_id, role, message):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)",
            (user_id, role, message)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def get_chat_history(user_id, limit=50):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, message, created_at FROM chat_history
            WHERE user_id = %s ORDER BY created_at ASC LIMIT %s
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [{'role': r[0], 'message': r[1], 'created_at': r[2]} for r in rows]
    except Exception as e:
        return []


def clear_chat_history(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
