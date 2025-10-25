from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models.documents import DocumentType


class DocumentResponse(BaseModel):
    
    id: int
    job_application_id: int
    filename: str
    file_size: int
    content_type: str
    document_type: DocumentType
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    
    message: str
    document: DocumentResponse
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "File uploaded successfully",
                "document": {
                    "id": 1,
                    "job_application_id": 1,
                    "filename": "resume.pdf",
                    "file_size": 1048576,
                    "content_type": "application/pdf",
                    "document_type": "resume",
                    "created_at": "2024-10-16T10:00:00Z"
                }
            }
        }
    )
