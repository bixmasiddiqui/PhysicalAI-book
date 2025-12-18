"""
Authentication Routes: Signup, Login, Profile
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import timedelta

from .database import get_db, User
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()
security = HTTPBearer()

# Request/Response Models
class OnboardingData(BaseModel):
    role: str = Field(..., description="Student|Professional|Researcher|Instructor")
    programming_experience: str = Field(..., description="Beginner|Intermediate|Advanced")
    robotics_experience: str = Field(..., description="None|Simulation-only|Hardware")
    preferred_language: str = Field(..., description="English|Urdu|Other")
    hardware_availability: str = Field(..., description="RTX Workstation|Cloud|Jetson Kit|None")

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    onboarding: OnboardingData

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str

class UserProfile(BaseModel):
    id: int
    email: str
    onboarding: Dict[str, Any]
    created_at: str

# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT and return current user"""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user with onboarding questions

    **Onboarding Questions:**
    1. Primary role: Student, Professional, Researcher, or Instructor
    2. Programming experience: Beginner, Intermediate, or Advanced
    3. Robotics experience: None, Simulation-only, or Hardware
    4. Preferred language: English, Urdu, or Other
    5. Hardware availability: RTX Workstation, Cloud, Jetson Kit, or None
    """

    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(request.password)
    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        onboarding=request.onboarding.dict()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )

    return TokenResponse(
        access_token=access_token,
        user_id=new_user.id,
        email=new_user.email
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password

    Returns JWT token for authenticated requests
    """

    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email
    )

@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile

    Requires: Authorization header with Bearer token
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        onboarding=current_user.onboarding or {},
        created_at=current_user.created_at.isoformat()
    )

@router.put("/me")
async def update_profile(
    onboarding: OnboardingData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user onboarding preferences

    Requires: Authorization header with Bearer token
    """
    current_user.onboarding = onboarding.dict()
    db.commit()

    return {
        "success": True,
        "message": "Profile updated successfully",
        "onboarding": current_user.onboarding
    }

@router.get("/health")
async def auth_health():
    """Auth module health check"""
    return {
        "status": "ok",
        "module": "authentication",
        "endpoints": {
            "signup": "POST /auth/signup",
            "login": "POST /auth/login",
            "profile": "GET /auth/me",
            "update": "PUT /auth/me"
        }
    }
