"""
Job Application Repository - Data Access Layer.
Similar to @Repository in Spring Boot.

PYTHON LEARNING NOTES:
- Query building with filters
- Pagination with offset and limit
- Aggregation queries for statistics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Dict
from app.models.job_application import JobApplication, ApplicationStatus
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate


class JobApplicationRepository:
    """
    Repository for Job Application database operations.
    
    Spring Boot equivalent:
    @Repository
    public interface JobApplicationRepository extends JpaRepository<JobApplication, Long> {
        List<JobApplication> findByUserId(Long userId);
        // ... custom queries
    }
    """
    
    def create(self, db: Session, job_create: JobApplicationCreate, user_id: int) -> JobApplication:
        """
        Create new job application.
        
        Spring Boot equivalent:
        public JobApplication save(JobApplicationCreateDTO dto, Long userId)
        
        PYTHON NOTES:
        - **job_create.model_dump() unpacks Pydantic model to dict
        - user_id=user_id adds the user relationship
        """
        db_job = JobApplication(
            **job_create.model_dump(),
            user_id=user_id
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        return db_job
    
    def get_by_id(self, db: Session, job_id: int, user_id: int) -> Optional[JobApplication]:
        """
        Get job application by ID for specific user.
        
        Spring Boot equivalent:
        Optional<JobApplication> findByIdAndUserId(Long id, Long userId);
        
        PYTHON NOTES:
        - .filter() adds multiple WHERE conditions
        - Chaining filters is like AND in SQL
        """
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
        """
        Get all job applications for user with filters and pagination.
        
        Spring Boot equivalent:
        @Query("SELECT j FROM JobApplication j WHERE j.userId = :userId ...")
        Page<JobApplication> findByUserIdWithFilters(
            Long userId, 
            ApplicationStatus status,
            String company,
            Pageable pageable
        );
        
        PYTHON NOTES:
        - Build query dynamically based on provided filters
        - .order_by(desc(...)) sorts descending (newest first)
        - .offset() and .limit() for pagination
        """
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
        """
        Count total applications for user with filters.
        
        Spring Boot equivalent:
        @Query("SELECT COUNT(j) FROM JobApplication j WHERE j.userId = :userId ...")
        long countByUserIdWithFilters(Long userId, ...);
        
        PYTHON NOTES:
        - .count() returns total count
        - Used for pagination (total pages calculation)
        """
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
        """
        Update job application.
        
        Spring Boot equivalent:
        public JobApplication update(Long id, Long userId, JobApplicationUpdateDTO dto)
        
        PYTHON NOTES:
        - exclude_unset=True only includes fields that were set in request
        - If field not provided, it's not in the dict and won't be updated
        """
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
        """
        Delete job application.
        
        Spring Boot equivalent:
        public boolean deleteByIdAndUserId(Long id, Long userId)
        """
        db_job = self.get_by_id(db, job_id, user_id)
        if not db_job:
            return False
        
        db.delete(db_job)
        db.commit()
        
        return True
    
    def get_statistics(self, db: Session, user_id: int) -> Dict[str, int]:
        """
        Get application statistics by status.
        
        Spring Boot equivalent:
        @Query("SELECT j.status, COUNT(j) FROM JobApplication j WHERE j.userId = :userId GROUP BY j.status")
        List<Object[]> getStatisticsByUserId(Long userId);
        
        PYTHON NOTES:
        - func.count() is SQL COUNT() function
        - .group_by() groups results
        - Returns list of tuples: [(status, count), ...]
        - We convert to dict for easier use
        """
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
        """
        Get recent job applications.
        
        Spring Boot equivalent:
        @Query("SELECT j FROM JobApplication j WHERE j.userId = :userId ORDER BY j.createdAt DESC")
        List<JobApplication> findRecentByUserId(Long userId, Pageable pageable);
        
        PYTHON NOTES:
        - Order by created_at descending (newest first)
        - Limit to specified number
        """
        return db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).order_by(
            desc(JobApplication.created_at)
        ).limit(limit).all()


# PYTHON NOTES - Query Examples:
"""
# Simple query:
jobs = db.query(JobApplication).filter(JobApplication.user_id == 1).all()
# SQL: SELECT * FROM job_applications WHERE user_id = 1

# Multiple filters (AND):
jobs = db.query(JobApplication).filter(
    JobApplication.user_id == 1,
    JobApplication.status == 'applied'
).all()
# SQL: SELECT * FROM job_applications WHERE user_id = 1 AND status = 'applied'

# LIKE query:
jobs = db.query(JobApplication).filter(
    JobApplication.company_name.ilike('%google%')
).all()
# SQL: SELECT * FROM job_applications WHERE company_name ILIKE '%google%'

# Ordering:
jobs = db.query(JobApplication).order_by(desc(JobApplication.created_at)).all()
# SQL: SELECT * FROM job_applications ORDER BY created_at DESC

# Pagination:
jobs = db.query(JobApplication).offset(10).limit(10).all()
# SQL: SELECT * FROM job_applications OFFSET 10 LIMIT 10

# Count:
count = db.query(JobApplication).filter(JobApplication.user_id == 1).count()
# SQL: SELECT COUNT(*) FROM job_applications WHERE user_id = 1

# Aggregation:
result = db.query(
    JobApplication.status,
    func.count(JobApplication.id)
).group_by(JobApplication.status).all()
# SQL: SELECT status, COUNT(id) FROM job_applications GROUP BY status
"""