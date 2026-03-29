"""
auth.py - User registration and login logic
Passwords are hashed with bcrypt before storage.
All queries are parameterised to prevent SQL injection.
"""
import bcrypt
from database import get_connection


# ── Helpers ────────────────────────────────────────────────────────────────────
def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── Public API ─────────────────────────────────────────────────────────────────
def register_user(name: str, email: str, password: str, age: int, gender: str):
    """
    Insert a new user record.
    Returns (True, "success message") or (False, "error message").
    """
    try:
        conn = get_connection()
        cur  = conn.cursor()

        # Guard: duplicate email
        cur.execute("SELECT id FROM Users WHERE email = ?", (email,))
        if cur.fetchone():
            conn.close()
            return False, "Email already registered. Please log in."

        hashed = _hash_password(password)
        cur.execute(
            "INSERT INTO Users (name, email, password_hash, age, gender) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, email, hashed, age, gender)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful! Please log in."

    except Exception as exc:
        return False, f"Database error: {exc}"


def login_user(email: str, password: str):
    """
    Validate credentials.
    Returns (user_dict, None) on success, or (None, "error message") on failure.
    """
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute(
            "SELECT id, name, email, password_hash, age, gender "
            "FROM Users WHERE email = ?",
            (email,)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return None, "No account found with that email."

        if not _verify_password(password, row[3]):
            return None, "Incorrect password."

        user = {
            "id":     row[0],
            "name":   row[1],
            "email":  row[2],
            "age":    row[4],
            "gender": row[5],
        }
        return user, None

    except Exception as exc:
        return None, f"Database error: {exc}"
