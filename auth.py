import bcrypt
import re
from database import create_user, get_user_by_email


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(pattern, email) is not None


def register_user(name: str, email: str, password: str, confirm_password: str):
    """
    Validates input and registers a new user.
    Returns (success: bool, message: str)
    """
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "All fields are required."

    if len(name) < 2:
        return False, "Name must be at least 2 characters."

    if not is_valid_email(email):
        return False, "Invalid email format."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    hashed = hash_password(password)
    success, message = create_user(name, email, hashed)
    return success, message


def login_user(email: str, password: str):
    """
    Authenticates user.
    Returns (user_row or None, message: str)
    """
    email = email.strip().lower()

    if not email or not password:
        return None, "Please enter email and password."

    if not is_valid_email(email):
        return None, "Invalid email format."

    user = get_user_by_email(email)
    if not user:
        return None, "No account found with this email."

    if not verify_password(password, user["password"]):
        return None, "Incorrect password."

    return user, f"Welcome back, {user['name']}! 💪"
