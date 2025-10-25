from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Dict
from app.models.job_application import JobApplication, ApplicationStatus
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate


class JobApplicationRepository:
    
    def create(self, db: Session, job_create: JobApplicationCreate, user_id: int) -> JobApplication:
        
        db_job = JobApplication(
            **job_create.model_dump(),
            user_id=user_id
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        return db_job
    
    def get_by_id(self, db: Session, job_id: int, user_id: int) -> Optional[JobApplication]:
        
        return db.query(JobApplication).filter(
            JobApplication.id == job_id,
            JobApplication.user_id == user_id
        ).first()
    
    def get_all_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[ApplicationStatus] = None,
        company: Optional[str] = None
    ) -> List[JobApplication]:
    
        query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
        
        # Add optional filters
        # PYTHON NOTES:
        # if status: checks if status is not None
        # Dynamically adds WHERE clauses based on parameters
        if status:
            query = query.filter(JobApplication.status == status)
        
        if company:
            # PYTHON NOTES:
            # .ilike() is case-insensitive LIKE (similar to ILIKE in PostgreSQL)
            # f"%{company}%" is string interpolation (like $"%{company}%" in C#)
            query = query.filter(JobApplication.company_name.ilike(f"%{company}%"))
        
        # Order by created date (newest first)
        query = query.order_by(desc(JobApplication.created_at))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all()
    
    def count_by_user(
        self,
        db: Session,
        user_id: int,
        status: Optional[ApplicationStatus] = None,
        company: Optional[str] = None
    ) -> int:
       
        query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
        
        if status:
            query = query.filter(JobApplication.status == status)
        
        if company:
            query = query.filter(JobApplication.company_name.ilike(f"%{company}%"))
        
        return query.count()
    
    def update(
        self,
        db: Session,
        job_id: int,
        user_id: int,
        job_update: JobApplicationUpdate
    ) -> Optional[JobApplication]:
        
        db_job = self.get_by_id(db, job_id, user_id)
        if not db_job:
            return None
        
        # Get update data (only fields that were set)
        update_data = job_update.model_dump(exclude_unset=True)
        
        # Update fields
        for key, value in update_data.items():
            setattr(db_job, key, value)
        
        db.commit()
        db.refresh(db_job)
        
        return db_job
    
    def delete(self, db: Session, job_id: int, user_id: int) -> bool:
        
        db_job = self.get_by_id(db, job_id, user_id)
        if not db_job:
            return False
        
        db.delete(db_job)
        db.commit()
        
        return True
    
    def get_statistics(self, db: Session, user_id: int) -> Dict[str, int]:
        
        # Query to count applications by status
        # SQL: SELECT status, COUNT(*) FROM job_applications WHERE user_id = ? GROUP BY status
        results = db.query(
            JobApplication.status,
            func.count(JobApplication.id)
        ).filter(
            JobApplication.user_id == user_id
        ).group_by(
            JobApplication.status
        ).all()
        
        # PYTHON NOTES:
        # Convert list of tuples to dictionary
        # results = [('applied', 5), ('interview', 3), ...]
        # stats = {'applied': 5, 'interview': 3, ...}
        stats = {status.value: count for status, count in results}
        
        # Ensure all statuses are present (even if count is 0)
        for status in ApplicationStatus:
            if status.value not in stats:
                stats[status.value] = 0
        
        # Add total count
        stats['total_applications'] = sum(stats.values())
        
        return stats
    
    def get_recent(self, db: Session, user_id: int, limit: int = 5) -> List[JobApplication]:
        
        return db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).order_by(
            desc(JobApplication.created_at)
        ).limit(limit).all()