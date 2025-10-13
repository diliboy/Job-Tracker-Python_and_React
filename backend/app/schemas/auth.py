"""
Authentication schemas - DTOs for login, tokens, etc.
Similar to LoginRequest, TokenResponse in Spring Security.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LoginRequest(BaseModel):
    """
    Login request schema.
    Similar to LoginRequest in Spring Boot.
    
    In Spring Security, this would be:
    @PostMapping("/login")
    public ResponseEntity<Token> login(@RequestBody LoginRequest request)
    """
    email: EmailStr
    password: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "strongpassword123"
            }
        }
    )


class Token(BaseModel):
    """
    JWT Token response.
    Similar to JwtResponse in Spring Security.
    """
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    """
    Data stored in JWT token.
    Similar to JWT Claims in Spring Security.
    """
    email: str | None = None
    user_id: int | None = None