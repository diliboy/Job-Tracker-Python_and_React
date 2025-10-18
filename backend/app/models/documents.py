"""
Document model - for storing uploaded files (resumes, cover letters).
Similar to @Entity class in JPA.

PYTHON LEARNING NOTES:
- File metadata stored in database
- Actual file stored on disk (in uploads folder)
- Similar to file upload systems in Spring Boot
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.database import Base


class DocumentType(str, Enum):
    """
    Document type enum.
    
    PYTHON NOTES:
    - Defines allowed document types
    - Stored as string in database
    """
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    OTHER = "other"


class Document(Base):
    """
    Document entity for file uploads.
    
    Spring Boot equivalent:
    @Entity
    @Table(name="documents")
    public class Document {
        @Id
        @GeneratedValue(strategy = GenerationType.IDENTITY)
        private Long id;
        
        @ManyToOne
        @JoinColumn(name = "job_application_id")
        private JobApplication jobApplication;
        
        private String filename;
        private String filepath;
        // ... other fields
    }
    
    PYTHON NOTES:
    - Stores file metadata (not the actual file content)
    - Actual files stored in filesystem (uploads/ folder)
    - filepath points to file location
    """
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


# PYTHON NOTES - File Upload Pattern:
"""
File Upload Flow:
1. Client uploads file via multipart/form-data
2. Server receives file in memory
3. Save file to disk (uploads/ folder)
4. Create Document record in database with metadata
5. Return document info to client

File Storage Structure:
uploads/
├── user_1/
│   ├── job_1/
│   │   ├── resume_abc123.pdf
│   │   └── cover_letter_def456.pdf
│   └── job_2/
│       └── resume_ghi789.pdf

This is the same pattern used in Spring Boot file uploads!

Security Considerations:
- Validate file types (only allow PDF, DOCX, etc.)
- Validate file size (prevent huge uploads)
- Generate unique filenames (prevent overwrites)
- Store files outside web root (prevent direct access)
- Virus scanning (optional, for production)
"""