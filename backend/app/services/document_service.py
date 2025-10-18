"""
Document Service - Business logic for document operations.
Similar to @Service class in Spring Boot.

PYTHON LEARNING NOTES:
- Coordinates between file storage and database
- Handles both file operations and database records
"""
from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List
from pathlib import Path

from app.models.documents import Document, DocumentType
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.file_service import FileService
from app.repositories.job_repository import JobApplicationRepository
from app.core.exceptions import NotFoundException, ForbiddenException


class DocumentService:
    """
    Document service handling file uploads and management.
    
    Spring Boot equivalent:
    @Service
    public class DocumentService {
        @Autowired
        private DocumentRepository documentRepository;
        
        @Autowired
        private FileStorageService fileStorageService;
    }
    
    PYTHON NOTES:
    - Combines file operations with database operations
    - Ensures job exists and belongs to user before upload
    """
    
    def __init__(self):
        """Initialize dependencies"""
        self.file_service = FileService()
        self.job_repo = JobApplicationRepository()
    
    async def upload_document(
        self,
        db: Session,
        job_id: int,
        user_id: int,
        file: UploadFile,
        document_type: DocumentType
    ) -> DocumentUploadResponse:
        """
        Upload document for job application.
        
        Spring Boot equivalent:
        public DocumentUploadResponse uploadDocument(
            Long jobId,
            Long userId,
            MultipartFile file,
            DocumentType documentType
        ) throws IOException {
            // verify job exists and belongs to user
            // save file to disk
            // save metadata to database
            // return response
        }
        
        PYTHON NOTES:
        - async function because file I/O is async
        - await keyword waits for async operations
        - Similar to CompletableFuture in Java
        
        Args:
            db: Database session
            job_id: Job application ID
            user_id: Current user ID
            file: Uploaded file
            document_type: Type of document (resume, cover_letter, etc.)
        
        Returns:
            DocumentUploadResponse with success message and document info
        
        Raises:
            NotFoundException: If job not found
            ForbiddenException: If job doesn't belong to user
        """
        # Verify job exists and belongs to user
        job = self.job_repo.get_by_id(db, job_id, user_id)
        if not job:
            raise NotFoundException(f"Job application with id {job_id} not found")
        
        # Save file to disk
        # PYTHON NOTES:
        # await pauses execution until file is saved
        # Like: CompletableFuture.get() in Java
        filepath, original_filename, file_size = await self.file_service.save_file(
            file,
            user_id,
            job_id
        )
        
        # Create document record in database
        document = Document(
            job_application_id=job_id,
            filename=original_filename,
            filepath=filepath,
            file_size=file_size,
            content_type=file.content_type,
            document_type=document_type
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Return response
        return DocumentUploadResponse(
            message="File uploaded successfully",
            document=DocumentResponse.model_validate(document)
        )
    
    def get_documents(
        self,
        db: Session,
        job_id: int,
        user_id: int
    ) -> List[DocumentResponse]:
        """
        Get all documents for a job application.
        
        Spring Boot equivalent:
        public List<DocumentResponse> getDocuments(Long jobId, Long userId) {
            JobApplication job = jobRepository.findByIdAndUserId(jobId, userId)
                .orElseThrow(() -> new NotFoundException());
            
            return documentRepository.findByJobApplicationId(jobId)
                .stream()
                .map(DocumentResponse::from)
                .collect(Collectors.toList());
        }
        
        PYTHON NOTES:
        - Returns list of document metadata (not actual files)
        - Client can use document IDs to download files
        
        Args:
            db: Database session
            job_id: Job application ID
            user_id: Current user ID
        
        Returns:
            List of DocumentResponse
        
        Raises:
            NotFoundException: If job not found
        """
        # Verify job exists and belongs to user
        job = self.job_repo.get_by_id(db, job_id, user_id)
        if not job:
            raise NotFoundException(f"Job application with id {job_id} not found")
        
        # Get documents
        # PYTHON NOTES:
        # db.query(Document).filter(...).all() gets all matching documents
        # List comprehension converts to response DTOs
        documents = db.query(Document).filter(
            Document.job_application_id == job_id
        ).all()
        
        return [DocumentResponse.model_validate(doc) for doc in documents]
    
    def get_document(
        self,
        db: Session,
        document_id: int,
        user_id: int
    ) -> tuple[Document, Path]:
        """
        Get document by ID and verify ownership.
        
        Spring Boot equivalent:
        public Pair<Document, Path> getDocument(Long documentId, Long userId) {
            Document doc = documentRepository.findById(documentId)
                .orElseThrow(() -> new NotFoundException());
            
            // verify user owns the job
            if (!doc.getJobApplication().getUserId().equals(userId)) {
                throw new ForbiddenException();
            }
            
            Path filePath = fileStorageService.getFilePath(doc.getFilepath());
            return Pair.of(doc, filePath);
        }
        
        PYTHON NOTES:
        - Returns tuple (Document, Path) - like Pair in Java
        - Used for file downloads
        - Verifies user owns the job before allowing download
        
        Args:
            db: Database session
            document_id: Document ID
            user_id: Current user ID
        
        Returns:
            Tuple of (Document, Path to file)
        
        Raises:
            NotFoundException: If document not found
            ForbiddenException: If user doesn't own the job
        """
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise NotFoundException(f"Document with id {document_id} not found")
        
        # Verify user owns the job application
        job = self.job_repo.get_by_id(db, document.job_application_id, user_id)
        if not job:
            raise ForbiddenException("You don't have permission to access this document")
        
        # Get file path
        file_path = self.file_service.get_file_path(document.filepath)
        
        return document, file_path
    
    def delete_document(
        self,
        db: Session,
        document_id: int,
        user_id: int
    ) -> dict:
        """
        Delete document (both file and database record).
        
        Spring Boot equivalent:
        public Map<String, String> deleteDocument(Long documentId, Long userId) {
            Document doc = documentRepository.findById(documentId)
                .orElseThrow(() -> new NotFoundException());
            
            // verify ownership
            if (!doc.getJobApplication().getUserId().equals(userId)) {
                throw new ForbiddenException();
            }
            
            // delete file from disk
            fileStorageService.deleteFile(doc.getFilepath());
            
            // delete from database
            documentRepository.delete(doc);
            
            return Map.of("message", "Document deleted successfully");
        }
        
        PYTHON NOTES:
        - Deletes both file from disk AND database record
        - Transaction ensures both succeed or both fail
        
        Args:
            db: Database session
            document_id: Document ID
            user_id: Current user ID
        
        Returns:
            Success message
        
        Raises:
            NotFoundException: If document not found
            ForbiddenException: If user doesn't own the job
        """
        # Get document and verify ownership
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise NotFoundException(f"Document with id {document_id} not found")
        
        # Verify user owns the job application
        job = self.job_repo.get_by_id(db, document.job_application_id, user_id)
        if not job:
            raise ForbiddenException("You don't have permission to delete this document")
        
        # Delete file from disk
        self.file_service.delete_file(document.filepath)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}


# PYTHON NOTES - Async/Await:
"""
Async functions in Python:

async def function():
    result = await some_async_operation()
    return result

- 'async def' defines an async function
- 'await' pauses execution until operation completes
- Non-blocking: other code can run while waiting

Spring Boot equivalent (with CompletableFuture):
public CompletableFuture<Result> function() {
    return someAsyncOperation()
        .thenApply(result -> {
            return result;
        });
}

Or with Spring @Async:
@Async
public Future<Result> function() {
    Result result = someOperation();
    return new AsyncResult<>(result);
}

FastAPI automatically handles async:
- If function is async, it runs in async context
- If function is sync, it runs in thread pool
- Mix both in same application!

File I/O is typically async for better performance:
await file.read()  # Non-blocking
vs
file.read()        # Blocking

Same concept as NIO in Java!
"""