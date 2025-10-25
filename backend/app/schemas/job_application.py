from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.job_application import ApplicationStatus


class JobApplicationBase(BaseModel):

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

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class JobApplicationListResponse(BaseModel):

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

