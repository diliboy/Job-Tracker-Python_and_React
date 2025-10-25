from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.database import Base


# PYTHON NOTES:
# Enum defines a set of named constants (like enum in Java)
# class Status(Enum) is like: public enum Status { APPLIED, INTERVIEW, ... }
class ApplicationStatus(str, Enum):
    """
    Job application status enum.
    
    """
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobApplication(Base):

    __tablename__ = "job_applications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to User
    # PYTHON NOTES:
    # ForeignKey("users.id") creates foreign key relationship
    # Like @JoinColumn(name = "user_id") in JPA
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Job details
    company_name = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    job_url = Column(String(500), nullable=True)
    location = Column(String(200), nullable=True)
    salary_range = Column(String(100), nullable=True)
    
    # Application details
    status = Column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.APPLIED,
        nullable=False,
        index=True
    )
    
    # Dates
    applied_date = Column(DateTime(timezone=True), nullable=True)
    interview_date = Column(DateTime(timezone=True), nullable=True)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    
    # Notes and description
    job_description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Contact information
    contact_person = Column(String(200), nullable=True)
    contact_email = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to User
    # PYTHON NOTES:
    # relationship() creates ORM relationship (like @ManyToOne)
    # back_populates="job_applications" creates bidirectional relationship
    # In Java: @ManyToOne private User user;
    user = relationship("User", back_populates="job_applications")
    
    # Relationship to Documents
    # PYTHON NOTES:
    # cascade="all, delete-orphan" means:
    # - When job is deleted, delete its documents
    # - Like @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    documents = relationship("Document", back_populates="job_application", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation"""
        return f"<JobApplication(id={self.id}, company={self.company_name}, title={self.job_title}, status={self.status})>"