"""
User model - Database entity.
Similar to @Entity class in JPA/Hibernate.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User entity for authentication.
    
    In Spring Boot, this would be:
    @Entity
    @Table(name="users")
    public class User {
        @Id
        @GeneratedValue(strategy = GenerationType.IDENTITY)
        private Long id;
        ...
    }
    """
    __tablename__ = "users"
    
    # Primary key - similar to @Id @GeneratedValue in JPA
    id = Column(Integer, primary_key=True, index=True)
    
    # User fields
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    # Timestamps - similar to @CreatedDate and @LastModifiedDate in Spring
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - similar to @OneToMany in JPA
    # We'll add this later when we create JobApplication model
    # job_applications = relationship("JobApplication", back_populates="user")
    
    def __repr__(self):
        """String representation - similar to toString() in Java"""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"