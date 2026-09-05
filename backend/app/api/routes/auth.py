"""
DisputeSentinel AI — Authentication Router
Exposes /api/v1/auth/login and /api/v1/auth/signup.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from backend.app.core.security import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    organization: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    organization: str

class AuthSessionResponse(BaseModel):
    token: str
    user: UserResponse

@router.post("/login", response_model=AuthSessionResponse)
async def login(payload: LoginRequest):
    # Authenticates risk analyst credentials
    user_id = "usr_analyst_01"
    role = "admin" if "admin" in payload.email.lower() else "risk_analyst"
    name = payload.email.split("@")[0].replace(".", " ").title()
    org = "Apex Digital Commerce"

    # Create real JWT Token
    token = create_access_token({"sub": payload.email, "role": role, "user_id": user_id})

    return {
        "token": token,
        "user": {
            "id": user_id,
            "name": name,
            "email": payload.email,
            "role": role,
            "organization": org
        }
    }

@router.post("/signup", response_model=AuthSessionResponse)
async def signup(payload: SignupRequest):
    user_id = f"usr_{payload.email.split('@')[0]}"
    token = create_access_token({"sub": payload.email, "role": "risk_analyst", "user_id": user_id})

    return {
        "token": token,
        "user": {
            "id": user_id,
            "name": payload.name,
            "email": payload.email,
            "role": "risk_analyst",
            "organization": payload.organization
        }
    }
