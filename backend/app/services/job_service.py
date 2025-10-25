from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from math import ceil

from app.models.job_application import JobApplication, ApplicationStatus
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationListResponse,
    JobApplicationStats
)
from app.repositories.job_repository import JobApplicationRepository
from app.core.exceptions import NotFoundException, ForbiddenException


class JobApplicationService:
    
    def __init__(self):
        """Initialize repository"""
        self.job_repo = JobApplicationRepository()
    
    def create_application(
        self,
        db: Session,
        job_create: JobApplicationCreate,
        user_id: int
    ) -> JobApplicationResponse:
        
        job = self.job_repo.create(db, job_create, user_id)
        return JobApplicationResponse.model_validate(job)
    
    def get_application(
        self,
        db: Session,
        job_id: int,
        user_id: int
    ) -> JobApplicationResponse:
        
        job = self.job_repo.get_by_id(db, job_id, user_id)
        
        if not job:
            raise NotFoundException(f"Job application with id {job_id} not found")
        
        return JobApplicationResponse.model_validate(job)
    
    def get_all_applications(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 10,
        status: Optional[ApplicationStatus] = None,
        company: Optional[str] = None
    ) -> JobApplicationListResponse:
    
        # Calculate skip (offset)
        # PYTHON NOTES:
        # If page=1, size=10: skip=0
        # If page=2, size=10: skip=10
        # If page=3, size=10: skip=20
        skip = (page - 1) * size
        
        # Get jobs and total count
        jobs = self.job_repo.get_all_by_user(
            db,
            user_id,
            skip=skip,
            limit=size,
            status=status,
            company=company
        )
        
        total = self.job_repo.count_by_user(db, user_id, status=status, company=company)
        
        # Calculate total pages
        # PYTHON NOTES:
        # ceil() rounds up: ceil(25/10) = 3 pages
        # math.ceil is like Math.ceil() in Java
        pages = ceil(total / size) if size > 0 else 0
        
        # Convert to response models
        # PYTHON NOTES:
        # List comprehension: [expression for item in list]
        # Like: jobs.stream().map(JobApplicationResponse::from).collect(Collectors.toList())
        items = [JobApplicationResponse.model_validate(job) for job in jobs]
        
        return JobApplicationListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    def update_application(
        self,
        db: Session,
        job_id: int,
        job_update: JobApplicationUpdate,
        user_id: int
    ) -> JobApplicationResponse:
        
        job = self.job_repo.update(db, job_id, user_id, job_update)
        
        if not job:
            raise NotFoundException(f"Job application with id {job_id} not found")
        
        return JobApplicationResponse.model_validate(job)
    
    def delete_application(
        self,
        db: Session,
        job_id: int,
        user_id: int
    ) -> Dict[str, str]:
        
        deleted = self.job_repo.delete(db, job_id, user_id)
        
        if not deleted:
            raise NotFoundException(f"Job application with id {job_id} not found")
        
        # PYTHON NOTES:
        # Return dictionary (converted to JSON automatically)
        # Like: return Map.of("message", "...") in Java
        return {"message": "Job application deleted successfully"}
    
    def get_statistics(
        self,
        db: Session,
        user_id: int
    ) -> JobApplicationStats:
        
        stats = self.job_repo.get_statistics(db, user_id)
        
        return JobApplicationStats(
            total_applications=stats.get('total_applications', 0),
            applied=stats.get('applied', 0),
            interview=stats.get('interview', 0),
            offer=stats.get('offer', 0),
            rejected=stats.get('rejected', 0),
            withdrawn=stats.get('withdrawn', 0)
        )
    
    def get_recent_applications(
        self,
        db: Session,
        user_id: int,
        limit: int = 5
    ) -> List[JobApplicationResponse]:
        
        jobs = self.job_repo.get_recent(db, user_id, limit)
        return [JobApplicationResponse.model_validate(job) for job in jobs]
