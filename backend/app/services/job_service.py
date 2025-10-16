"""
Job Application Service - Business Logic Layer.
Similar to @Service class in Spring Boot.

PYTHON LEARNING NOTES:
- Service layer handles business logic
- Coordinates between controller and repository
- Can call multiple repositories if needed
"""
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
    """
    Job Application service handling business logic.
    
    Spring Boot equivalent:
    @Service
    public class JobApplicationService {
        @Autowired
        private JobApplicationRepository jobRepository;
    }
    
    PYTHON NOTES:
    - __init__ initializes dependencies
    - Methods contain business logic and validation
    """
    
    def __init__(self):
        """Initialize repository"""
        self.job_repo = JobApplicationRepository()
    
    def create_application(
        self,
        db: Session,
        job_create: JobApplicationCreate,
        user_id: int
    ) -> JobApplicationResponse:
        """
        Create new job application.
        
        Spring Boot equivalent:
        public JobApplicationResponse createApplication(
            JobApplicationCreateDTO dto,
            Long userId
        ) {
            JobApplication job = jobRepository.save(dto, userId);
            return JobApplicationResponse.from(job);
        }
        
        PYTHON NOTES:
        - Takes user_id from JWT token (provided by controller)
        - Returns Pydantic model (automatically converted to JSON)
        
        Args:
            db: Database session
            job_create: Job application data
            user_id: Current user's ID (from JWT)
        
        Returns:
            JobApplicationResponse with created job data
        """
        job = self.job_repo.create(db, job_create, user_id)
        return JobApplicationResponse.model_validate(job)
    
    def get_application(
        self,
        db: Session,
        job_id: int,
        user_id: int
    ) -> JobApplicationResponse:
        """
        Get job application by ID.
        
        Spring Boot equivalent:
        public JobApplicationResponse getApplication(Long jobId, Long userId) {
            return jobRepository.findByIdAndUserId(jobId, userId)
                .map(JobApplicationResponse::from)
                .orElseThrow(() -> new NotFoundException());
        }
        
        PYTHON NOTES:
        - Raises NotFoundException if not found (returns 404 automatically)
        - Ensures user can only access their own applications
        
        Args:
            db: Database session
            job_id: Job application ID
            user_id: Current user's ID
        
        Returns:
            JobApplicationResponse
        
        Raises:
            NotFoundException: If job not found or doesn't belong to user
        """
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
        """
        Get all job applications with pagination and filters.
        
        Spring Boot equivalent:
        public Page<JobApplicationResponse> getAllApplications(
            Long userId,
            Pageable pageable,
            ApplicationStatus status,
            String company
        ) {
            Page<JobApplication> jobs = jobRepository.findByUserIdWithFilters(...);
            return jobs.map(JobApplicationResponse::from);
        }
        
        PYTHON NOTES:
        - page starts at 1 (not 0 like Spring Boot)
        - skip = (page - 1) * size calculates offset
        - Returns custom pagination response
        
        Args:
            db: Database session
            user_id: Current user's ID
            page: Page number (starts at 1)
            size: Items per page
            status: Optional status filter
            company: Optional company name filter
        
        Returns:
            JobApplicationListResponse with items and pagination info
        """
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
        """
        Update job application.
        
        Spring Boot equivalent:
        public JobApplicationResponse updateApplication(
            Long jobId,
            JobApplicationUpdateDTO dto,
            Long userId
        ) {
            JobApplication job = jobRepository.findByIdAndUserId(jobId, userId)
                .orElseThrow(() -> new NotFoundException());
            // update fields...
            return JobApplicationResponse.from(jobRepository.save(job));
        }
        
        Args:
            db: Database session
            job_id: Job application ID
            job_update: Update data
            user_id: Current user's ID
        
        Returns:
            JobApplicationResponse with updated data
        
        Raises:
            NotFoundException: If job not found
        """
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
        """
        Delete job application.
        
        Spring Boot equivalent:
        public Map<String, String> deleteApplication(Long jobId, Long userId) {
            if (!jobRepository.deleteByIdAndUserId(jobId, userId)) {
                throw new NotFoundException();
            }
            return Map.of("message", "Job application deleted successfully");
        }
        
        Args:
            db: Database session
            job_id: Job application ID
            user_id: Current user's ID
        
        Returns:
            Success message
        
        Raises:
            NotFoundException: If job not found
        """
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
        """
        Get dashboard statistics.
        
        Spring Boot equivalent:
        public JobApplicationStats getStatistics(Long userId) {
            Map<String, Integer> stats = jobRepository.getStatisticsByUserId(userId);
            return JobApplicationStats.from(stats);
        }
        
        PYTHON NOTES:
        - Returns statistics grouped by status
        - Used for dashboard charts/metrics
        
        Args:
            db: Database session
            user_id: Current user's ID
        
        Returns:
            JobApplicationStats with counts by status
        """
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
        """
        Get recent job applications.
        
        Spring Boot equivalent:
        public List<JobApplicationResponse> getRecentApplications(Long userId, int limit) {
            return jobRepository.findRecentByUserId(userId, PageRequest.of(0, limit))
                .stream()
                .map(JobApplicationResponse::from)
                .collect(Collectors.toList());
        }
        
        Args:
            db: Database session
            user_id: Current user's ID
            limit: Number of recent jobs to return
        
        Returns:
            List of recent JobApplicationResponse
        """
        jobs = self.job_repo.get_recent(db, user_id, limit)
        return [JobApplicationResponse.model_validate(job) for job in jobs]


# PYTHON NOTES - Service Layer Pattern:
"""
Controller -> Service -> Repository -> Database

Controller:
- Handles HTTP requests/responses
- Validates authentication
- Calls service methods

Service (this file):
- Business logic and validation
- Coordinates multiple repositories
- Handles exceptions

Repository:
- Direct database operations
- Simple CRUD operations
- Query building

This is the same pattern as Spring Boot!

Example flow:
1. User sends: POST /api/v1/jobs with job data
2. Controller extracts user_id from JWT token
3. Controller calls: job_service.create_application(db, job_data, user_id)
4. Service validates and calls: job_repo.create(db, job_data, user_id)
5. Repository saves to database and returns entity
6. Service converts entity to DTO
7. Controller returns JSON response

Same as Spring Boot MVC pattern!
"""