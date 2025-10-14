"""
User Repository - Data Access Layer.
Similar to @Repository or Spring Data JPA Repository in Spring Boot.

PYTHON LEARNING NOTES:
- We use classes to group related functions (like Java)
- __init__ is the constructor (like public UserRepository() in Java)
- self is like 'this' in Java - refers to the current instance
- Type hints like 'Optional[User]' mean "User object or None" (like Java's Optional<User>)
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserRepository:
    """
    Repository for User database operations.
    
    In Spring Boot this would be:
    @Repository
    public class UserRepository {
        @Autowired
        private EntityManager em;
    }
    
    PYTHON NOTES:
    - We pass 'db: Session' to methods instead of autowiring
    - Session is like EntityManager in JPA
    """
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        Find user by ID.
        
        Spring Boot equivalent:
        public Optional<User> findById(Long id)
        
        PYTHON NOTES:
        - db.query(User) creates a SELECT query for User table
        - .filter(User.id == user_id) adds WHERE clause
        - .first() executes query and returns first result or None
        - No need for try-catch, SQLAlchemy handles it
        """
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Find user by email.
        
        Spring Boot equivalent:
        Optional<User> findByEmail(String email);
        
        PYTHON NOTES:
        - Same pattern as get_by_id but filter by email
        - Returns None if not found (like Optional.empty() in Java)
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Find user by username.
        
        Spring Boot equivalent:
        Optional<User> findByUsername(String username);
        """
        return db.query(User).filter(User.username == username).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        
        Spring Boot equivalent:
        Page<User> findAll(Pageable pageable);
        
        PYTHON NOTES:
        - skip is like OFFSET in SQL
        - limit is like LIMIT in SQL
        - .all() returns a list (like List<User> in Java)
        - Default parameters: skip=0, limit=100 (like overloaded methods in Java)
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user_create: UserCreate) -> User:
        """
        Create a new user.
        
        Spring Boot equivalent:
        public User save(UserCreateDTO dto) {
            User user = new User();
            user.setEmail(dto.getEmail());
            // ... etc
            return userRepository.save(user);
        }
        
        PYTHON NOTES:
        - **user_create.model_dump(exclude={'password'}) unpacks dictionary into named arguments
        - Like spreading an object: new User(...dto) in JavaScript
        - model_dump() converts Pydantic model to dict (like toMap() in Java)
        - exclude={'password'} removes password field from dict
        """
        # Hash the password
        hashed_password = get_password_hash(user_create.password)
        
        # Create user instance
        # This converts: {"email": "x", "username": "y"} 
        # Into: User(email="x", username="y")
        db_user = User(
            **user_create.model_dump(exclude={'password'}),
            hashed_password=hashed_password
        )
        
        # PYTHON NOTES:
        # db.add() stages the object (like persist() in JPA)
        # db.commit() saves to database (like transaction commit)
        # db.refresh() reloads from database to get generated ID (like em.refresh())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def update(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update user by ID.
        
        Spring Boot equivalent:
        public User update(Long id, UserUpdateDTO dto)
        
        PYTHON NOTES:
        - exclude_unset=True only includes fields that were actually set
        - If user didn't provide email, it won't be in the dict
        - setattr(obj, 'field', value) is like obj.setField(value) in Java
        """
        # Find the user
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        # Get update data (only fields that were set)
        update_data = user_update.model_dump(exclude_unset=True)
        
        # If password is being updated, hash it
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data['password'])
            del update_data['password']  # Remove plain password
        
        # Update fields
        # PYTHON NOTES:
        # for key, value in dict.items() loops through dictionary
        # Like: for(Map.Entry<String, Object> entry : map.entrySet())
        for key, value in update_data.items():
            setattr(db_user, key, value)  # db_user.key = value
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def delete(self, db: Session, user_id: int) -> bool:
        """
        Delete user by ID.
        
        Spring Boot equivalent:
        public boolean deleteById(Long id)
        
        PYTHON NOTES:
        - Returns True if deleted, False if not found
        - In Python, we often return bool instead of throwing exceptions
        """
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        
        return True
    
    def exists_by_email(self, db: Session, email: str) -> bool:
        """
        Check if email exists.
        
        Spring Boot equivalent:
        boolean existsByEmail(String email);
        
        PYTHON NOTES:
        - .first() returns object or None
        - 'is not None' checks if object exists
        - In Python: None is like null in Java
        """
        return db.query(User).filter(User.email == email).first() is not None
    
    def exists_by_username(self, db: Session, username: str) -> bool:
        """
        Check if username exists.
        
        Spring Boot equivalent:
        boolean existsByUsername(String username);
        """
        return db.query(User).filter(User.username == username).first() is not None


# PYTHON NOTES - Creating instance:
# In other files, we'll use this like:
# user_repo = UserRepository()
# user = user_repo.get_by_id(db, 1)
# 
# Unlike Spring's @Autowired, we manually create instances
# FastAPI has dependency injection which we'll see later!