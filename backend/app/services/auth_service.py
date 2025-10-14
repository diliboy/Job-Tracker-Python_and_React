"""
Authentication Service - Business Logic Layer.
Similar to @Service class in Spring Boot.

PYTHON LEARNING NOTES:
- This is where business logic lives (between Controller and Repository)
- We separate concerns: Controller -> Service -> Repository
- Services can call multiple repositories and add business rules
"""
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
    """
    Authentication service handling user registration and login.
    
    Spring Boot equivalent:
    @Service
    public class AuthService {
        @Autowired
        private UserRepository userRepository;
        @Autowired
        private PasswordEncoder passwordEncoder;
    }
    
    PYTHON NOTES:
    - __init__ is the constructor (runs when creating new instance)
    - self.user_repo stores the repository for use in other methods
    - We don't use @Autowired, we manually pass dependencies
    """
    
    def __init__(self):
        """
        Constructor - initialize dependencies.
        
        PYTHON NOTES:
        - self.user_repo = UserRepository() creates a new instance
        - In Java: this.userRepository = new UserRepository()
        - We could also pass it as parameter for better testing (Dependency Injection)
        """
        self.user_repo = UserRepository()
    
    def register(self, db: Session, user_create: UserCreate) -> User:
        """
        Register a new user.
        
        Spring Boot equivalent:
        public User register(UserCreateDTO userDto) {
            if (userRepository.existsByEmail(userDto.getEmail())) {
                throw new ConflictException("Email already registered");
            }
            // ... create user
        }
        
        PYTHON NOTES:
        - We check if email/username exists before creating
        - raise Exception() is like throw new Exception() in Java
        - ConflictException returns HTTP 409 automatically
        
        Args:
            db: Database session (like EntityManager in JPA)
            user_create: User registration data (DTO)
        
        Returns:
            Created User object
        
        Raises:
            ConflictException: If email or username already exists
        """
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
        """
        Authenticate user with email and password.
        
        Spring Boot equivalent:
        public User authenticate(String email, String password) {
            User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UnauthorizedException());
            
            if (!passwordEncoder.matches(password, user.getPassword())) {
                throw new UnauthorizedException();
            }
            return user;
        }
        
        PYTHON NOTES:
        - Returns User if credentials are valid, None otherwise
        - We don't throw exception here, we return None (more Pythonic)
        - The controller will decide how to handle None
        
        Args:
            db: Database session
            email: User's email
            password: Plain text password
        
        Returns:
            User object if authenticated, None otherwise
        """
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
        """
        Login user and generate JWT token.
        
        Spring Boot equivalent:
        public TokenResponse login(String email, String password) {
            User user = authenticate(email, password);
            String token = jwtTokenProvider.generateToken(user);
            return new TokenResponse(token, "bearer");
        }
        
        PYTHON NOTES:
        - This method combines authenticate + token generation
        - Returns Token object (contains access_token and token_type)
        - raise is like throw in Java
        
        Args:
            db: Database session
            email: User's email
            password: Plain text password
        
        Returns:
            Token object with JWT access token
        
        Raises:
            UnauthorizedException: If credentials are invalid
        """
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
        """
        Get current user from JWT token.
        
        Spring Boot equivalent:
        public User getCurrentUser(String token) {
            Claims claims = jwtTokenProvider.validateToken(token);
            String email = claims.getSubject();
            return userRepository.findByEmail(email)
                .orElseThrow(() -> new UnauthorizedException());
        }
        
        PYTHON NOTES:
        - This decodes JWT and fetches user from database
        - Used for protected routes that require authentication
        
        Args:
            db: Database session
            token: JWT access token
        
        Returns:
            User object
        
        Raises:
            UnauthorizedException: If token is invalid or user not found
        """
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


# PYTHON NOTES - How to use this service:
"""
# In controller/route:
auth_service = AuthService()

# Register user
new_user = auth_service.register(db, user_create_dto)

# Login user
token = auth_service.login(db, "email@example.com", "password")

# Get current user from token
current_user = auth_service.get_current_user(db, "jwt_token_here")
"""