from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator

from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService


# HTTPBearer scheme for JWT token
# This tells FastAPI to look for "Authorization: Bearer <token>" header
# PYTHON NOTES:
# HTTPBearer() creates a simple bearer token scheme
# User just pastes token in Swagger UI, no username/password needed
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()
    try:
        yield db  # Provide the database session
    finally:
        db.close()  # Always close the connection


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:

    auth_service = AuthService()
    
    # Extract token from credentials
    token = credentials.credentials
    
    try:
        user = auth_service.get_current_user(db, token)
        return user
    except Exception as e:
        # PYTHON NOTES:
        # 'raise' is like 'throw' in Java
        # HTTPException is FastAPI's way to return HTTP errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
 
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
