from fastapi import APIRouter, HTTPException
from schemas.auth_schema import LoginRequest, TokenResponse
from services.auth_service import authenticate_user

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    result = authenticate_user(data.email, data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result