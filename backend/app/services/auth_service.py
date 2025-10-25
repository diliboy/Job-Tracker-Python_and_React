from datetime import timedelta
from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import Token
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException
from app.config import settings


class AuthService:

    
    def __init__(self):
   
        self.user_repo = UserRepository()
    
    def register(self, db: Session, user_create: UserCreate) -> User:

        # Check if email already exists
        if self.user_repo.exists_by_email(db, user_create.email):
            raise ConflictException("Email already registered")
        
        # Check if username already exists
        if self.user_repo.exists_by_username(db, user_create.username):
            raise ConflictException("Username already taken")
        
        # Create the user (password will be hashed in repository)
        user = self.user_repo.create(db, user_create)
        
        return user
    
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
  
        # Find user by email
        user = self.user_repo.get_by_email(db, email)
        
        # PYTHON NOTES:
        # 'if not user' checks if user is None (like if(user == null) in Java)
        # 'or not' is logical OR (like || in Java)
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def login(self, db: Session, email: str, password: str) -> Token:

        # Authenticate user
        user = self.authenticate(db, email, password)
        
        if not user:
            raise UnauthorizedException("Incorrect email or password")
        
        # Create access token
        # PYTHON NOTES:
        # {} creates a dictionary (like Map<String, Object> in Java)
        # f"string {variable}" is string interpolation (like $"{variable}" in C#)
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": user.email,  # "sub" is JWT standard for subject
                "user_id": user.id,
                "email": user.email
            },
            expires_delta=access_token_expires
        )
        
        # Return Token object
        # PYTHON NOTES:
        # Token(access_token=...) creates a new Token instance
        # Like: new Token(accessToken, "bearer") in Java
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
    
    def get_current_user(self, db: Session, token: str) -> User:

        from app.core.security import decode_access_token
        
        # Decode token
        payload = decode_access_token(token)
        
        if not payload:
            raise UnauthorizedException("Could not validate credentials")
        
        # Get email from token payload
        # PYTHON NOTES:
        # dict.get("key") returns value or None if key doesn't exist
        # Like: map.get("key") in Java, but returns null instead of throwing exception
        email: str = payload.get("sub")
        
        if not email:
            raise UnauthorizedException("Could not validate credentials")
        
        # Get user from database
        user = self.user_repo.get_by_email(db, email)
        
        if not user:
            raise UnauthorizedException("User not found")
        
        if not user.is_active:
            raise UnauthorizedException("User is inactive")
        
        return user


