from database import get_connection
from passlib.context import CryptContext
from jose import jwt
import os
import secrets
from datetime import datetime, timedelta, timezone
from services.email_service import send_reset_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# -------------------------
# Verify password
# -------------------------
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# -------------------------
# Get user by email
# -------------------------
def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, email, password_hash FROM users WHERE email=%s",
        (email,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "email": row[1],
        "password_hash": row[2]
    }


# -------------------------
# Create JWT token
# -------------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -------------------------
# Authenticate user
# -------------------------
RESET_TOKEN_EXPIRE_MINUTES = 30


# -------------------------
# Ensure reset tokens table exists
# -------------------------
def ensure_reset_tokens_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token VARCHAR(100) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# -------------------------
# Forgot password
# -------------------------
def request_password_reset(email: str):
    user = get_user_by_email(email)
    if not user:
        return  # Silent — don't reveal whether email exists

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (user["id"],))
    cursor.execute(
        "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
        (user["id"], token, expires_at)
    )
    conn.commit()
    cursor.close()
    conn.close()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    if os.getenv("ENV") == "development":
        print(f"\n[DEV] Password reset link for {email}:\n{reset_link}\n")
    else:
        send_reset_email(email, reset_link)


# -------------------------
# Reset password
# -------------------------
def reset_user_password(token: str, new_password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, expires_at FROM password_reset_tokens WHERE token = %s",
        (token,)
    )
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return False

    user_id, expires_at = row
    expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        cursor.close()
        conn.close()
        return False

    new_hash = pwd_context.hash(new_password)
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
    cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
    conn.commit()
    cursor.close()
    conn.close()
    return True


# -------------------------
def authenticate_user(email: str, password: str):
    print("LOGIN ATTEMPT:", email)
    user = get_user_by_email(email)

    if not user:
        print("USER NOT FOUND")
        return None

    print("USER FOUND")

    if not verify_password(password, user["password_hash"]):
        print("PASSWORD NOT MATCH")
        return None

    print("AUTH SUCCESS")

    token = create_access_token({
        "sub": user["email"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }