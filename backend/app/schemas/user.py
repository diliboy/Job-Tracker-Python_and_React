"""
User schemas (DTOs) - Data Transfer Objects.
Similar to DTOs or Request/Response classes in Spring Boot.

Pydantic models provide:
- Automatic validation (like @Valid in Spring)
- Serialization/Deserialization (like Jackson)
- Documentation (like Swagger annotations)
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    Similar to a base DTO class in Java.
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for user registration.
    Similar to UserRegistrationRequest in Spring Boot.
    
    Usage in controller:
    @PostMapping("/register")
    public ResponseEntity<User> register(@Valid @RequestBody UserCreate user)
    """
    password: str = Field(..., min_length=6, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "strongpassword123"
            }
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    All fields are optional.
    Similar to UserUpdateRequest in Spring Boot.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponse(UserBase):
    """
    Schema for user response (without password).
    Similar to UserDTO or UserResponse in Spring Boot.
    
    This is what gets returned to the client.
    NEVER include password in response!
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # This tells Pydantic to work with SQLAlchemy models
    # Similar to @JsonIgnoreProperties in Spring
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    """
    Schema for user in database (internal use).
    Includes hashed password.
    Similar to User entity but as a Pydantic model.
    """
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)