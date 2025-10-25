import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.config import settings
from app.core.exceptions import BadRequestException


class FileService:
    
    # Allowed file types and extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    }
    
    def __init__(self):
        
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        """
        # Check if file is empty
        if not file.filename:
            raise BadRequestException("No file provided")
        
        # Check file extension
        # PYTHON NOTES:
        # Path(filename).suffix gets file extension (e.g., ".pdf")
        # .lower() converts to lowercase
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise BadRequestException(
                f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check content type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise BadRequestException(
                f"Content type not allowed: {file.content_type}"
            )
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename to prevent overwrites.
        
        """
        file_path = Path(original_filename)
        file_ext = file_path.suffix
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
        
        # Create filename: originalname_uuid.ext
        # Example: resume_a1b2c3d4.pdf
        return f"{file_path.stem}_{unique_id}{file_ext}"
    
    async def save_file(
        self,
        file: UploadFile,
        user_id: int,
        job_id: int
    ) -> Tuple[str, str, int]:
        """
        Save uploaded file to disk.
        
        """
        # Validate file
        self._validate_file(file)
        
        # Create directory structure: uploads/user_{id}/job_{id}/
        # PYTHON NOTES:
        # / operator joins paths (like Paths.get() in Java)
        user_dir = self.upload_dir / f"user_{user_id}" / f"job_{job_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)
        file_path = user_dir / unique_filename
        
        # Save file to disk
        # PYTHON NOTES:
        # await file.read() reads file content as bytes (async)
        # with open() is a context manager (auto-closes file)
        # "wb" means write binary mode
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Get file size
        file_size = len(contents)
        
        # Check file size limit
        if file_size > settings.max_upload_size:
            # Delete file if too large
            file_path.unlink()  # Delete file
            raise BadRequestException(
                f"File too large. Maximum size: {settings.max_upload_size} bytes"
            )
        
        # Return relative path (from upload_dir), filename, and size
        # PYTHON NOTES:
        # str(path) converts Path object to string
        # relative_to() gets relative path
        relative_path = str(file_path.relative_to(self.upload_dir))
        
        return relative_path, file.filename, file_size
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete file from disk.
        
        """
        try:
            file_path = self.upload_dir / filepath
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_path(self, filepath: str) -> Path:
        """
        Get absolute file path.
        
        """
        file_path = self.upload_dir / filepath
        
        if not file_path.exists():
            raise BadRequestException("File not found")
        
        return file_path