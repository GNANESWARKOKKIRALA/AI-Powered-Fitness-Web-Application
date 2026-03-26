import bcrypt
import re
from database import create_user, get_user_by_email


def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None


def register_user(name, email, password):
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters!"
    if not validate_email(email):
        return False, "Please enter a valid email address!"
    if len(password) < 6:
        return False, "Password must be at least 6 characters!"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_str = hashed.decode('utf-8')
    success = create_user(name.strip(), email.lower().strip(), hashed_str)
    if success:
        return True, "Account created successfully!"
    return False, "Email already exists! Please use a different email."


def login_user(email, password):
    if not email or not password:
        return False, None, "Please enter email and password!"
    user = get_user_by_email(email.lower().strip())
    if not user:
        return False, None, "Email not found! Please register first."
    stored = user['password']
    if isinstance(stored, str):
        stored = stored.encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), stored):
        return True, user, "Login successful!"
    return False, None, "Wrong password! Please try again."
