"""
Dependencies for FastAPI dependency injection.
Similar to @Bean providers in Spring Boot.

PYTHON LEARNING NOTES:
- FastAPI has built-in dependency injection (like Spring's @Autowired)
- We define functions that FastAPI will call automatically
- These are used in route parameters with Depends()
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Generator

from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService


# OAuth2 scheme for JWT token
# This tells FastAPI where to look for the token
# PYTHON NOTES:
# OAuth2PasswordBearer(tokenUrl="...") creates a dependency
# tokenUrl is the login endpoint that returns the token
# This adds "Authorize" button in Swagger UI automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Spring Boot equivalent:
    @Bean
    public EntityManager entityManager() {
        return entityManagerFactory.createEntityManager();
    }
    
    PYTHON NOTES:
    - Generator is like an iterator in Java
    - yield is like return, but function can continue after
    - finally block always runs (like try-finally in Java)
    - This ensures database connection is closed after request
    
    Usage in route:
    @router.get("/users")
    def get_users(db: Session = Depends(get_db)):
        # db is automatically provided by FastAPI
        users = db.query(User).all()
        return users
    """
    db = SessionLocal()
    try:
        yield db  # Provide the database session
    finally:
        db.close()  # Always close the connection


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get current authenticated user.
    
    Spring Boot equivalent:
    @GetMapping("/protected")
    public ResponseEntity<?> protectedRoute(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(user);
    }
    
    PYTHON NOTES:
    - This is a dependency that depends on other dependencies
    - get_db provides database session
    - oauth2_scheme extracts token from Authorization header
    - FastAPI calls this automatically for protected routes
    
    Args:
        db: Database session (injected by FastAPI)
        token: JWT token from Authorization header (injected by FastAPI)
    
    Returns:
        Current authenticated User
    
    Raises:
        HTTPException 401: If token is invalid or user not found
    
    Usage in route:
    @router.get("/me")
    def get_profile(current_user: User = Depends(get_current_user)):
        # current_user is automatically provided
        return current_user
    """
    auth_service = AuthService()
    
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
    """
    Dependency to get current active user only.
    
    Spring Boot equivalent:
    @PreAuthorize("hasAuthority('ACTIVE')")
    
    PYTHON NOTES:
    - This dependency depends on get_current_user
    - Adds extra check to ensure user is active
    - Dependency chain: oauth2_scheme -> get_db -> get_current_user -> get_current_active_user
    
    Args:
        current_user: Current user (injected by get_current_user dependency)
    
    Returns:
        Current active User
    
    Raises:
        HTTPException 400: If user is inactive
    
    Usage in route:
    @router.get("/profile")
    def get_profile(user: User = Depends(get_current_active_user)):
        # Only active users can access this
        return user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current superuser (admin) only.
    
    Spring Boot equivalent:
    @PreAuthorize("hasRole('ADMIN')")
    
    PYTHON NOTES:
    - Only allows superusers (admins) to access route
    - Useful for admin-only endpoints
    
    Args:
        current_user: Current user (injected)
    
    Returns:
        Current superuser
    
    Raises:
        HTTPException 403: If user is not superuser
    
    Usage in route:
    @router.delete("/users/{id}")
    def delete_user(
        user_id: int,
        admin: User = Depends(get_current_superuser)
    ):
        # Only admins can delete users
        pass
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# PYTHON NOTES - How FastAPI Dependency Injection Works:
"""
Example route with dependencies:

@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # FastAPI automatically:
    # 1. Calls get_db() -> provides db session
    # 2. Calls oauth2_scheme -> extracts token from header
    # 3. Calls get_current_user(db, token) -> provides user
    # 4. Calls your function with db and current_user
    # 5. Closes db session after function completes
    
    return {"user": current_user.email}

Spring Boot equivalent:
@GetMapping("/profile")
public Map<String, String> getProfile(@AuthenticationPrincipal User currentUser) {
    return Map.of("user", currentUser.getEmail());
}

KEY DIFFERENCES:
- Spring: Uses annotations and reflection (@Autowired)
- FastAPI: Uses function parameters and type hints (Depends())
- Both achieve the same result: automatic dependency injection!
"""