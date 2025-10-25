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
   
    document, file_path = document_service.get_document(db, document_id, current_user.id)
 
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
    
    return document_service.delete_document(db, document_id, current_user.id)