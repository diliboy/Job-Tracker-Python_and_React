"""
Custom exceptions for the application.
Similar to custom exceptions in Spring Boot.

In Spring Boot:
@ResponseStatus(HttpStatus.NOT_FOUND)
public class NotFoundException extends RuntimeException { }
"""
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Exception for resource not found (404).
    """
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(HTTPException):
    """
    Exception for bad requests (400).
    """
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    """
    Exception for unauthorized access (401).
    """
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    """
    Exception for forbidden access (403).
    """
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(HTTPException):
    """
    Exception for conflicts (409) - e.g., duplicate email.
    """
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)