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
