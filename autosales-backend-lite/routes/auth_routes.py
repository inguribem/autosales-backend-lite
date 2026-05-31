from fastapi import APIRouter, HTTPException
from schemas.auth_schema import LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from services.auth_service import authenticate_user, request_password_reset, reset_user_password

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    result = authenticate_user(data.email, data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    found = request_password_reset(data.email)
    if not found:
        raise HTTPException(status_code=404, detail="No account found with that email address.")
    return {"message": "A reset link has been sent to your email."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    success = reset_user_password(data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password updated successfully"}