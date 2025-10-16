"""
Job Application Controller - API endpoints.
Similar to @RestController in Spring Boot.

PYTHON LEARNING NOTES:
- APIRouter groups related endpoints
- Path parameters: {job_id}
- Query parameters: ?page=1&size=10
- Automatic request/response validation
"""
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
    """
    Create a new job application.
    
    Spring Boot equivalent:
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public JobApplicationResponse createJobApplication(
        @Valid @RequestBody JobApplicationCreate jobCreate,
        @AuthenticationPrincipal User currentUser
    ) {
        return jobService.createApplication(jobCreate, currentUser.getId());
    }
    
    PYTHON NOTES:
    - job_create: JobApplicationCreate - request body, automatically validated
    - current_user: User = Depends(...) - extracted from JWT token
    - No need to manually parse JSON or extract user ID
    
    Request body example:
    {
        "company_name": "Google",
        "job_title": "Software Engineer",
        "status": "applied",
        "applied_date": "2024-10-16T10:00:00Z"
    }
    
    Returns:
        201 Created with JobApplicationResponse
    
    Requires:
        Authorization: Bearer <token>
    """
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
    """
    Get all job applications with pagination and filters.
    
    Spring Boot equivalent:
    @GetMapping
    public Page<JobApplicationResponse> getAllJobApplications(
        @AuthenticationPrincipal User currentUser,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(required = false) ApplicationStatus status,
        @RequestParam(required = false) String company
    ) {
        Pageable pageable = PageRequest.of(page, size);
        return jobService.getAllApplications(currentUser.getId(), pageable, status, company);
    }
    
    PYTHON NOTES:
    - Query() defines query parameters with validation
    - ge=1 means "greater than or equal to 1"
    - le=100 means "less than or equal to 100"
    - Optional means parameter is not required
    - Default values provided
    
    Example requests:
    - GET /api/v1/jobs
    - GET /api/v1/jobs?page=2&size=20
    - GET /api/v1/jobs?status=interview
    - GET /api/v1/jobs?company=google&status=applied
    
    Returns:
        {
            "items": [...],
            "total": 50,
            "page": 1,
            "size": 10,
            "pages": 5
        }
    """
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
    """
    Get job application statistics.
    
    Spring Boot equivalent:
    @GetMapping("/stats")
    public JobApplicationStats getStatistics(@AuthenticationPrincipal User currentUser) {
        return jobService.getStatistics(currentUser.getId());
    }
    
    PYTHON NOTES:
    - Simple GET endpoint, no parameters
    - Returns aggregated statistics
    
    Returns:
        {
            "total_applications": 25,
            "applied": 10,
            "interview": 8,
            "offer": 2,
            "rejected": 4,
            "withdrawn": 1
        }
    """
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
    """
    Get job application by ID.
    
    Spring Boot equivalent:
    @GetMapping("/{jobId}")
    public JobApplicationResponse getJobApplication(
        @PathVariable Long jobId,
        @AuthenticationPrincipal User currentUser
    ) {
        return jobService.getApplication(jobId, currentUser.getId());
    }
    
    PYTHON NOTES:
    - job_id: int - path parameter from URL
    - FastAPI automatically converts string to int
    - Validates that job_id is actually an integer
    
    Example: GET /api/v1/jobs/123
    
    Returns:
        JobApplicationResponse
    
    Raises:
        404 Not Found: If job doesn't exist or doesn't belong to user
    """
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
    """
    Update job application.
    
    Spring Boot equivalent:
    @PutMapping("/{jobId}")
    public JobApplicationResponse updateJobApplication(
        @PathVariable Long jobId,
        @Valid @RequestBody JobApplicationUpdate jobUpdate,
        @AuthenticationPrincipal User currentUser
    ) {
        return jobService.updateApplication(jobId, jobUpdate, currentUser.getId());
    }
    
    PYTHON NOTES:
    - PUT for full/partial updates
    - Only provided fields are updated (partial update)
    - job_update validated automatically
    
    Example: PUT /api/v1/jobs/123
    Body:
    {
        "status": "interview",
        "interview_date": "2024-10-20T14:00:00Z",
        "notes": "Second round interview"
    }
    
    Returns:
        Updated JobApplicationResponse
    """
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
    """
    Delete job application.
    
    Spring Boot equivalent:
    @DeleteMapping("/{jobId}")
    public Map<String, String> deleteJobApplication(
        @PathVariable Long jobId,
        @AuthenticationPrincipal User currentUser
    ) {
        jobService.deleteApplication(jobId, currentUser.getId());
        return Map.of("message", "Job application deleted successfully");
    }
    
    PYTHON NOTES:
    - DELETE method
    - Returns 200 OK with message
    - Some APIs return 204 No Content instead
    
    Example: DELETE /api/v1/jobs/123
    
    Returns:
        {"message": "Job application deleted successfully"}
    """
    return job_service.delete_application(db, job_id, current_user.id)


# PYTHON NOTES - FastAPI Routing:
"""
URL Path Parameters:
- /{job_id} - captured as function parameter
- Example: @router.get("/{job_id}") -> def func(job_id: int)
- Like @PathVariable in Spring Boot

Query Parameters:
- ?page=1&size=10 - defined with Query()
- Example: page: int = Query(1, ge=1)
- Like @RequestParam in Spring Boot

Request Body:
- JSON in request body
- Example: job_create: JobApplicationCreate
- Like @RequestBody in Spring Boot

Response Models:
- response_model=JobApplicationResponse
- Automatically converts and validates response
- Like @ResponseBody in Spring Boot

Dependencies:
- Depends(get_db) - inject database session
- Depends(get_current_active_user) - inject authenticated user
- Like @Autowired in Spring Boot

HTTP Methods:
- @router.get() - GET request
- @router.post() - POST request
- @router.put() - PUT request
- @router.delete() - DELETE request
- @router.patch() - PATCH request

Same concepts as Spring Boot, different syntax!
"""