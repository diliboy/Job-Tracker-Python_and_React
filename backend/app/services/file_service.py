"""
File Service - Handles file upload/download/deletion.
Similar to file storage services in Spring Boot.

PYTHON LEARNING NOTES:
- File I/O operations
- UUID for unique filenames
- Path manipulation with pathlib
"""
import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.config import settings
from app.core.exceptions import BadRequestException


class FileService:
    """
    Service for file operations.
    
    Spring Boot equivalent:
    @Service
    public class FileStorageService {
        private final Path fileStorageLocation;
        // ... file operations
    }
    
    PYTHON NOTES:
    - pathlib.Path is better than string paths
    - Like java.nio.file.Path in Java
    """
    
    # Allowed file types and extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    }
    
    def __init__(self):
        """
        Initialize file service.
        
        PYTHON NOTES:
        - Create upload directory if it doesn't exist
        - Path(settings.upload_dir) converts string to Path object
        """
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Spring Boot equivalent:
        private void validateFile(MultipartFile file) {
            if (file.isEmpty()) {
                throw new BadRequestException("File is empty");
            }
            // ... validate extension and size
        }
        
        PYTHON NOTES:
        - Checks file type, extension, and size
        - Raises exception if validation fails
        
        Args:
            file: Uploaded file
        
        Raises:
            BadRequestException: If file is invalid
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
        
        Spring Boot equivalent:
        private String generateUniqueFilename(String originalFilename) {
            String extension = FilenameUtils.getExtension(originalFilename);
            return UUID.randomUUID().toString() + "." + extension;
        }
        
        PYTHON NOTES:
        - uuid.uuid4() generates random UUID (like UUID.randomUUID() in Java)
        - str(uuid) converts UUID to string
        - Path().stem gets filename without extension
        - Path().suffix gets extension with dot
        
        Args:
            original_filename: Original uploaded filename
        
        Returns:
            Unique filename with UUID prefix
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
        
        Spring Boot equivalent:
        public FileInfo saveFile(MultipartFile file, Long userId, Long jobId) 
            throws IOException {
            // validate file
            // create directory structure
            // save file
            // return file info
        }
        
        PYTHON NOTES:
        - async/await for non-blocking I/O
        - Tuple[str, str, int] return type means returns 3 values
        - Like returning an object with 3 fields
        
        Args:
            file: Uploaded file
            user_id: User ID
            job_id: Job application ID
        
        Returns:
            Tuple of (filepath, filename, file_size)
        
        Raises:
            BadRequestException: If file is invalid
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
        
        Spring Boot equivalent:
        public boolean deleteFile(String filepath) {
            Path file = Paths.get(uploadDir, filepath);
            return Files.deleteIfExists(file);
        }
        
        PYTHON NOTES:
        - Path.unlink() deletes file (like Files.delete() in Java)
        - Returns True if deleted, False if not found
        
        Args:
            filepath: Relative path to file
        
        Returns:
            True if deleted, False if file not found
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
        
        PYTHON NOTES:
        - Converts relative path to absolute path
        - Used when serving file downloads
        
        Args:
            filepath: Relative path to file
        
        Returns:
            Absolute Path object
        
        Raises:
            BadRequestException: If file doesn't exist
        """
        file_path = self.upload_dir / filepath
        
        if not file_path.exists():
            raise BadRequestException("File not found")
        
        return file_path


# PYTHON NOTES - File Operations:
"""
File I/O in Python:

1. Read file:
with open(filepath, "rb") as f:
    contents = f.read()

2. Write file:
with open(filepath, "wb") as f:
    f.write(contents)

3. Delete file:
Path(filepath).unlink()

4. Check if exists:
Path(filepath).exists()

5. Create directory:
Path(dirpath).mkdir(parents=True, exist_ok=True)

Spring Boot equivalent:
1. Read: Files.readAllBytes(Paths.get(filepath))
2. Write: Files.write(Paths.get(filepath), contents)
3. Delete: Files.deleteIfExists(Paths.get(filepath))
4. Exists: Files.exists(Paths.get(filepath))
5. Create dir: Files.createDirectories(Paths.get(dirpath))

Very similar patterns!

Context Manager (with statement):
with open(file) as f:
    # use file

Automatically closes file when done.
Like try-with-resources in Java:
try (FileInputStream fis = new FileInputStream(file)) {
    // use file
}
"""