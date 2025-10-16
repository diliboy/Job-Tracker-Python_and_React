"""
Job Application schemas (DTOs).
Similar to Request/Response DTOs in Spring Boot.

PYTHON LEARNING NOTES:
- Pydantic models define structure and validation
- Optional[Type] means field can be None (like Optional<Type> in Java)
- Field() adds validation rules (like @NotNull, @Size in Java)
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.job_application import ApplicationStatus


class JobApplicationBase(BaseModel):
    """
    Base schema with common fields.
    
    PYTHON NOTES:
    - Optional[str] means field can be None or string
    - Field(...) with ... means field is required
    - Field(None) means field is optional with default None
    """
    company_name: str = Field(..., min_length=1, max_length=200, description="Company name")
    job_title: str = Field(..., min_length=1, max_length=200, description="Job title/position")
    job_url: Optional[str] = Field(None, max_length=500, description="URL to job posting")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    salary_range: Optional[str] = Field(None, max_length=100, description="Salary range (e.g., $80k-$100k)")
    
    status: ApplicationStatus = Field(
        default=ApplicationStatus.APPLIED,
        description="Application status"
    )
    
    applied_date: Optional[datetime] = Field(None, description="Date when applied")
    interview_date: Optional[datetime] = Field(None, description="Interview date/time")
    follow_up_date: Optional[datetime] = Field(None, description="Date to follow up")
    
    job_description: Optional[str] = Field(None, description="Job description")
    notes: Optional[str] = Field(None, description="Personal notes")
    
    contact_person: Optional[str] = Field(None, max_length=200, description="Contact person name")
    contact_email: Optional[str] = Field(None, max_length=200, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone")


class JobApplicationCreate(JobApplicationBase):
    """
    Schema for creating job application.
    
    Spring Boot equivalent:
    public class JobApplicationCreateRequest { ... }
    
    PYTHON NOTES:
    - Inherits all fields from JobApplicationBase
    - Used for POST requests
    - user_id is not included (comes from JWT token)
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_name": "Google",
                "job_title": "Senior Software Engineer",
                "job_url": "https://careers.google.com/jobs/123",
                "location": "Auckland, New Zealand",
                "salary_range": "$120k-$150k",
                "status": "applied",
                "applied_date": "2024-10-16T10:00:00Z",
                "notes": "Applied through referral"
            }
        }
    )


class JobApplicationUpdate(BaseModel):
    """
    Schema for updating job application.
    All fields are optional.
    
    Spring Boot equivalent:
    public class JobApplicationUpdateRequest { ... }
    
    PYTHON NOTES:
    - All fields Optional - only update what's provided
    - Like PATCH request (partial update)
    """
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    job_title: Optional[str] = Field(None, min_length=1, max_length=200)
    job_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    salary_range: Optional[str] = Field(None, max_length=100)
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    job_description: Optional[str] = None
    notes: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)


class JobApplicationResponse(JobApplicationBase):
    """
    Schema for job application response.
    
    Spring Boot equivalent:
    public class JobApplicationResponse extends JobApplicationBase {
        private Long id;
        private Long userId;
        // ... timestamps
    }
    
    PYTHON NOTES:
    - This is what API returns to client
    - Includes id, user_id, timestamps
    - from_attributes=True allows SQLAlchemy model conversion
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class JobApplicationListResponse(BaseModel):
    """
    Schema for paginated list response.
    
    Spring Boot equivalent:
    public class PageResponse<T> {
        private List<T> items;
        private int total;
        private int page;
        private int size;
    }
    
    PYTHON NOTES:
    - Generic list response with pagination info
    - List[JobApplicationResponse] is like List<JobApplicationResponse> in Java
    """
    items: list[JobApplicationResponse]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "size": 10,
                "pages": 5
            }
        }
    )


class JobApplicationStats(BaseModel):
    """
    Schema for dashboard statistics.
    
    PYTHON NOTES:
    - Simple DTO for statistics
    - Used in dashboard endpoint
    """
    total_applications: int
    applied: int
    interview: int
    offer: int
    rejected: int
    withdrawn: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_applications": 25,
                "applied": 10,
                "interview": 8,
                "offer": 2,
                "rejected": 4,
                "withdrawn": 1
            }
        }
    )


# PYTHON NOTES - Pydantic Features:
"""
Automatic Validation:
- Pydantic validates data types automatically
- No need for @Valid annotation like Spring Boot
- Raises 422 error if validation fails

Example:
job = JobApplicationCreate(
    company_name="Google",
    job_title="Engineer"
)
# Pydantic automatically validates:
# - company_name is string and not empty
# - job_title is string and not empty
# - All optional fields default to None

Type Conversion:
- Pydantic converts types automatically
- "2024-10-16" string -> datetime object
- "applied" string -> ApplicationStatus.APPLIED enum

Java Spring Boot equivalent:
@Valid @RequestBody JobApplicationCreate job
// Spring validates using Bean Validation annotations
"""