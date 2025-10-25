from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.database import Base


class DocumentType(str, Enum):
    """
    Document type enum.

    """
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    OTHER = "other"


class Document(Base):

    __tablename__ = "documents"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to JobApplication
    job_application_id = Column(
        Integer,
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # File information
    filename = Column(String(255), nullable=False)  # Original filename
    filepath = Column(String(500), nullable=False)  # Path where file is stored
    file_size = Column(Integer, nullable=False)     # Size in bytes
    content_type = Column(String(100), nullable=False)  # MIME type (e.g., application/pdf)
    
    # Document type
    document_type = Column(
        SQLEnum(DocumentType),
        default=DocumentType.OTHER,
        nullable=False
    )
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to JobApplication
    # PYTHON NOTES:
    # back_populates creates bidirectional relationship
    # When JobApplication is deleted, documents are deleted too (CASCADE)
    job_application = relationship("JobApplication", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, type={self.document_type})>"
