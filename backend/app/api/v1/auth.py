"""
Authentication Controller - API endpoints.
Similar to @RestController in Spring Boot.

PYTHON LEARNING NOTES:
- APIRouter is like @RestController
- @router.post() is like @PostMapping
- Response models define what gets returned (like @ResponseBody)
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.dependencies import get_db, get_current_active_user
from app.models.user import User


# Create router
# PYTHON NOTES:
# APIRouter groups related endpoints together
# prefix="/auth" means all routes start with /auth
# tags=["Authentication"] groups them in Swagger UI
router = APIRouter()

# Initialize service
# PYTHON NOTES:
# We create one instance to use in all routes
# In Spring, this would be @Autowired
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
    """
    Register a new user.
    
    Spring Boot equivalent:
    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public UserResponse register(@Valid @RequestBody UserCreate userCreate) {
        return authService.register(userCreate);
    }
    
    PYTHON NOTES:
    - @router.post() defines a POST endpoint
    - response_model=UserResponse tells FastAPI what to return
    - status_code=201 sets HTTP status code
    - user_create: UserCreate - FastAPI automatically validates request body
    - db: Session = Depends(get_db) - FastAPI injects database session
    - No need for @Valid - Pydantic validates automatically!
    
    Args:
        user_create: User registration data (from request body)
        db: Database session (injected by FastAPI)
    
    Returns:
        UserResponse: Created user data (without password)
    
    Raises:
        409 Conflict: If email or username already exists
    """
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
    """
    Login and get JWT token.
    
    Spring Boot equivalent:
    @PostMapping("/login")
    public TokenResponse login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request.getEmail(), request.getPassword());
    }
    
    PYTHON NOTES:
    - FastAPI automatically parses JSON body to LoginRequest object
    - Validates email format and required fields
    - Returns Token object with JWT
    
    Args:
        login_request: Login credentials (email and password)
        db: Database session (injected)
    
    Returns:
        Token: JWT access token and token type
    
    Raises:
        401 Unauthorized: If credentials are invalid
    """
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
    """
    Get current authenticated user's profile.
    
    Spring Boot equivalent:
    @GetMapping("/me")
    public UserResponse getCurrentUser(@AuthenticationPrincipal User user) {
        return UserResponse.from(user);
    }
    
    PYTHON NOTES:
    - current_user: User = Depends(get_current_active_user)
    - FastAPI automatically:
      1. Extracts JWT token from Authorization header
      2. Validates the token
      3. Fetches user from database
      4. Injects user into this function
    - If token is invalid, returns 401 automatically
    - No manual token parsing needed!
    
    Args:
        current_user: Current authenticated user (injected by FastAPI)
    
    Returns:
        UserResponse: Current user's profile
    
    Requires:
        Authorization: Bearer <token> header
    """
    return current_user


# PYTHON NOTES - How to test these endpoints:
"""
1. Register a user:
   POST /api/v1/auth/register
   {
       "email": "test@example.com",
       "username": "testuser",
       "password": "password123",
       "full_name": "Test User"
   }

2. Login:
   POST /api/v1/auth/login
   {
       "email": "test@example.com",
       "password": "password123"
   }
   
   Response:
   {
       "access_token": "eyJhbGc...",
       "token_type": "bearer"
   }

3. Get profile (protected route):
   GET /api/v1/auth/me
   Headers:
   Authorization: Bearer eyJhbGc...

Spring Boot Comparison:
- FastAPI: Functions with decorators (@router.post)
- Spring Boot: Methods with annotations (@PostMapping)
- FastAPI: Type hints for validation (user_create: UserCreate)
- Spring Boot: @Valid annotation for validation
- FastAPI: Depends() for dependency injection
- Spring Boot: @Autowired for dependency injection

Both achieve the same result with different syntax!
"""