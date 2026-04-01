from database import get_connection
from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime, timedelta

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
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -------------------------
# Authenticate user
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