from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.dependencies import get_db, get_current_active_user
from app.models.user import User


# Create router
router = APIRouter()

# Initialize service
auth_service = AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password"
)
def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    user = auth_service.register(db, user_create)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Login with email and password to get JWT token"
)
def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    token = auth_service.login(
        db,
        login_request.email,
        login_request.password
    )
    return token


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's profile"
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    return current_user