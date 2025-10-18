"""
Document schemas (DTOs).
Similar to file upload DTOs in Spring Boot.

PYTHON LEARNING NOTES:
- Pydantic models for file metadata
- Actual file handled separately (as bytes)
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models.documents import DocumentType


class DocumentResponse(BaseModel):
    """
    Schema for document response.
    
    Spring Boot equivalent:
    public class DocumentResponse {
        private Long id;
        private String filename;
        private String contentType;
        private Integer fileSize;
        private DocumentType documentType;
        private LocalDateTime createdAt;
    }
    
    PYTHON NOTES:
    - Returns file metadata (not the actual file)
    - Client can use id to download file later
    """
    id: int
    job_application_id: int
    filename: str
    file_size: int
    content_type: str
    document_type: DocumentType
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    """
    Schema for file upload response.
    
    PYTHON NOTES:
    - Returned immediately after upload
    - Contains message and document info
    """
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


# PYTHON NOTES - File Upload in FastAPI:
"""
Unlike Pydantic models, files are handled differently:

from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):
    # file.filename - original filename
    # file.content_type - MIME type
    # file.file - file object (can read bytes)
    # await file.read() - read file content

Spring Boot equivalent:
@PostMapping("/upload")
public ResponseEntity<?> uploadFile(
    @RequestParam("file") MultipartFile file
) {
    String filename = file.getOriginalFilename();
    String contentType = file.getContentType();
    byte[] bytes = file.getBytes();
    // ... save file
}

Both handle multipart/form-data uploads!
"""