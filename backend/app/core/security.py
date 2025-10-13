"""
Security utilities - Password hashing and JWT tokens.
Similar to PasswordEncoder and JwtTokenProvider in Spring Security.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing context
# Similar to BCryptPasswordEncoder in Spring Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Similar to:
    passwordEncoder.matches(rawPassword, encodedPassword) in Spring
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Similar to:
    passwordEncoder.encode(rawPassword) in Spring
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Similar to JwtTokenProvider.generateToken() in Spring Security.
    
    Args:
        data: Dictionary containing user data (email, user_id, etc.)
        expires_delta: Optional expiration time delta
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Add expiration to token payload
    to_encode.update({"exp": expire})
    
    # Encode JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token.
    
    Similar to JwtTokenProvider.validateToken() in Spring Security.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None