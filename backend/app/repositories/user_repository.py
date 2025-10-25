from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserRepository:
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
    

    def create(self, db: Session, user_create: UserCreate) -> User:
        
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
        
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        
        return True
    

    def exists_by_email(self, db: Session, email: str) -> bool:
        
        return db.query(User).filter(User.email == email).first() is not None
    

    def exists_by_username(self, db: Session, username: str) -> bool:
        
        return db.query(User).filter(User.username == username).first() is not None
