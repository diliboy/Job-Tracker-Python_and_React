from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationListResponse,
    JobApplicationStats
)
from app.models.job_application import ApplicationStatus
from app.services.job_service import JobApplicationService
from app.dependencies import get_db, get_current_active_user
from app.models.user import User


# Create router
router = APIRouter()

# Initialize service
job_service = JobApplicationService()


@router.post(
    "",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job application",
    description="Create a new job application"
)
def create_job_application(
    job_create: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    return job_service.create_application(db, job_create, current_user.id)


@router.get(
    "",
    response_model=JobApplicationListResponse,
    summary="Get all job applications",
    description="Get all job applications with pagination and filters"
)
def get_all_job_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[ApplicationStatus] = Query(None, description="Filter by status"),
    company: Optional[str] = Query(None, description="Filter by company name")
):
   
    return job_service.get_all_applications(
        db,
        current_user.id,
        page=page,
        size=size,
        status=status,
        company=company
    )


@router.get(
    "/stats",
    response_model=JobApplicationStats,
    summary="Get statistics",
    description="Get job application statistics grouped by status"
)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    return job_service.get_statistics(db, current_user.id)


@router.get(
    "/{job_id}",
    response_model=JobApplicationResponse,
    summary="Get job application by ID",
    description="Get a specific job application by its ID"
)
def get_job_application(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    return job_service.get_application(db, job_id, current_user.id)


@router.put(
    "/{job_id}",
    response_model=JobApplicationResponse,
    summary="Update job application",
    description="Update an existing job application"
)
def update_job_application(
    job_id: int,
    job_update: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    return job_service.update_application(db, job_id, job_update, current_user.id)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete job application",
    description="Delete a job application"
)
def delete_job_application(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    return job_service.delete_application(db, job_id, current_user.id)