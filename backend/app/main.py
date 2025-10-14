"""
Main application file - Entry point.
Similar to @SpringBootApplication class in Spring Boot.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

# Create FastAPI application instance
# Similar to SpringApplication.run() in Spring Boot
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/api/docs",  # Swagger UI (like Springdoc)
    redoc_url="/api/redoc",  # Alternative API docs
)

# Configure CORS
# Similar to @CrossOrigin or WebMvcConfigurer in Spring
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Runs when application starts.
    Similar to @PostConstruct or CommandLineRunner in Spring Boot.
    """
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📝 Environment: {settings.environment}")
    print(f"🔧 Debug mode: {settings.debug}")
    
    # Initialize database (create tables)
    # In production, use Alembic migrations instead
    init_db()
    print("✅ Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when application shuts down.
    Similar to @PreDestroy in Spring Boot.
    """
    print("👋 Shutting down application...")


# Health check endpoint
# Similar to Spring Actuator's /health endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    Returns 200 OK if the application is running.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/")
async def root():
    """
    Root endpoint - welcome message.
    """
    return {
        "message": f"Welcome to {settings.app_name}!",
        "version": settings.app_version,
        "docs": "/api/docs"
    }


# Import and include routers here (we'll add these later)
# Similar to @ComponentScan in Spring Boot
# from app.api.v1 import auth, jobs, users
from app.api.v1 import auth

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])