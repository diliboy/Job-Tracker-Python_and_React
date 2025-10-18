"""
Document Controller - File upload/download endpoints.
Similar to @RestController in Spring Boot.

PYTHON LEARNING NOTES:
- UploadFile for file uploads
- FileResponse for file downloads
- Form data instead of JSON for file uploads
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.models.documents import DocumentType
from app.services.document_service import DocumentService
from app.dependencies import get_db, get_current_active_user
from app.models.user import User


# Create router
router = APIRouter()

# Initialize service
document_service = DocumentService()


@router.post(
    "/jobs/{job_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
    description="Upload a document (resume, cover letter) for a job application"
)
async def upload_document(
    job_id: int,
    file: UploadFile = File(..., description="File to upload (PDF, DOC, DOCX, TXT)"),
    document_type: DocumentType = Form(..., description="Type of document"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload document for job application.
    
    Spring Boot equivalent:
    @PostMapping("/jobs/{jobId}/documents")
    @ResponseStatus(HttpStatus.CREATED)
    public DocumentUploadResponse uploadDocument(
        @PathVariable Long jobId,
        @RequestParam("file") MultipartFile file,
        @RequestParam("documentType") DocumentType documentType,
        @AuthenticationPrincipal User currentUser
    ) throws IOException {
        return documentService.uploadDocument(jobId, currentUser.getId(), file, documentType);
    }
    
    PYTHON LEARNING NOTES:
    - UploadFile = File(...) receives uploaded file
    - Form(...) receives form data (not JSON)
    - Content-Type: multipart/form-data required
    - async def because file I/O is async
    
    Request (multipart/form-data):
    - file: [binary file data]
    - document_type: "resume" | "cover_letter" | "other"
    
    Example with curl:
    curl -X POST "http://localhost:8000/api/v1/jobs/1/documents" \
      -H "Authorization: Bearer <token>" \
      -F "file=@resume.pdf" \
      -F "document_type=resume"
    
    Returns:
        201 Created with document info
    
    Raises:
        400: Invalid file type or size
        404: Job not found
    """
    return await document_service.upload_document(
        db,
        job_id,
        current_user.id,
        file,
        document_type
    )


@router.get(
    "/jobs/{job_id}/documents",
    response_model=List[DocumentResponse],
    summary="Get all documents",
    description="Get all documents for a job application"
)
def get_documents(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all documents for a job application.
    
    Spring Boot equivalent:
    @GetMapping("/jobs/{jobId}/documents")
    public List<DocumentResponse> getDocuments(
        @PathVariable Long jobId,
        @AuthenticationPrincipal User currentUser
    ) {
        return documentService.getDocuments(jobId, currentUser.getId());
    }
    
    PYTHON NOTES:
    - Returns list of document metadata
    - Does NOT return actual files
    - Client uses document IDs to download files
    
    Example: GET /api/v1/jobs/1/documents
    
    Returns:
        List of DocumentResponse with metadata
    """
    return document_service.get_documents(db, job_id, current_user.id)


@router.get(
    "/documents/{document_id}",
    summary="Download document",
    description="Download a document file"
)
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download document file.
    
    Spring Boot equivalent:
    @GetMapping("/documents/{documentId}")
    public ResponseEntity<Resource> downloadDocument(
        @PathVariable Long documentId,
        @AuthenticationPrincipal User currentUser
    ) throws IOException {
        Pair<Document, Path> result = documentService.getDocument(documentId, currentUser.getId());
        Document doc = result.getLeft();
        Path filePath = result.getRight();
        
        Resource resource = new FileSystemResource(filePath);
        
        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(doc.getContentType()))
            .header(HttpHeaders.CONTENT_DISPOSITION, 
                "attachment; filename=\"" + doc.getFilename() + "\"")
            .body(resource);
    }
    
    PYTHON NOTES:
    - FileResponse streams file to client
    - Sets Content-Disposition header for download
    - Automatically sets Content-Type
    - Efficient for large files (streams, doesn't load into memory)
    
    Example: GET /api/v1/documents/1
    
    Returns:
        File download (binary content)
    
    Headers:
        Content-Type: application/pdf
        Content-Disposition: attachment; filename="resume.pdf"
    """
    document, file_path = document_service.get_document(db, document_id, current_user.id)
    
    # PYTHON NOTES:
    # FileResponse automatically:
    # - Streams file content
    # - Sets appropriate headers
    # - Handles large files efficiently
    return FileResponse(
        path=file_path,
        filename=document.filename,
        media_type=document.content_type
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete document",
    description="Delete a document file and its metadata"
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete document.
    
    Spring Boot equivalent:
    @DeleteMapping("/documents/{documentId}")
    public Map<String, String> deleteDocument(
        @PathVariable Long documentId,
        @AuthenticationPrincipal User currentUser
    ) {
        return documentService.deleteDocument(documentId, currentUser.getId());
    }
    
    PYTHON NOTES:
    - Deletes both file from disk and database record
    - Ensures user owns the job before deletion
    
    Example: DELETE /api/v1/documents/1
    
    Returns:
        {"message": "Document deleted successfully"}
    """
    return document_service.delete_document(db, document_id, current_user.id)


# PYTHON NOTES - File Upload/Download Patterns:
"""
1. FILE UPLOAD (multipart/form-data):

FastAPI:
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    # save file

Spring Boot:
@PostMapping("/upload")
public ResponseEntity<?> upload(@RequestParam("file") MultipartFile file) {
    byte[] contents = file.getBytes();
    // save file
}

2. FILE DOWNLOAD:

FastAPI:
@router.get("/download/{id}")
def download(id: int):
    return FileResponse(path=filepath, filename="file.pdf")

Spring Boot:
@GetMapping("/download/{id}")
public ResponseEntity<Resource> download(@PathVariable Long id) {
    Resource resource = new FileSystemResource(filepath);
    return ResponseEntity.ok()
        .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"file.pdf\"")
        .body(resource);
}

3. FORM DATA vs JSON:

File uploads use multipart/form-data:
- file: binary file
- document_type: text field

Regular API requests use application/json:
- JSON body

FastAPI automatically handles both!

4. ASYNC FILE I/O:

FastAPI:
async def upload(file: UploadFile):
    contents = await file.read()  # Non-blocking

Faster than blocking I/O:
def upload(file: UploadFile):
    contents = file.file.read()   # Blocking

Same as NIO vs traditional I/O in Java!
"""