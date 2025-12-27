import os
import shutil
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger
from config import config

class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def upload_file(self, file_path: str, user_id: int, filename: str) -> str:
        """Upload file and return storage URL"""
        pass
    
    @abstractmethod
    def download_file(self, storage_url: str, local_path: str) -> bool:
        """Download file from storage"""
        pass
    
    @abstractmethod
    def delete_file(self, storage_url: str) -> bool:
        """Delete file from storage"""
        pass
    
    @abstractmethod
    def list_user_files(self, user_id: int) -> list:
        """List all files for a user"""
        pass

class LocalStorage(StorageBackend):
    """Local file system storage"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or config.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorage initialized: {self.base_path}")
    
    def upload_file(self, file_path: str, user_id: int, filename: str) -> str:
        """Store file locally"""
        try:
            user_dir = self.base_path / f"user_{user_id}" / "documents"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            destination = user_dir / filename
            shutil.copy2(file_path, destination)
            
            storage_url = f"local://{destination}"
            logger.info(f"File uploaded: {storage_url}")
            return storage_url
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise e
    
    def download_file(self, storage_url: str, local_path: str) -> bool:
        """Copy file from storage"""
        try:
            file_path = storage_url.replace("local://", "")
            shutil.copy2(file_path, local_path)
            return True
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False
    
    def delete_file(self, storage_url: str) -> bool:
        """Delete file from storage"""
        try:
            file_path = storage_url.replace("local://", "")
            Path(file_path).unlink(missing_ok=True)
            logger.info(f"File deleted: {storage_url}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def list_user_files(self, user_id: int) -> list:
        """List all files for a user"""
        user_dir = self.base_path / f"user_{user_id}" / "documents"
        if not user_dir.exists():
            return []
        return [str(f) for f in user_dir.glob("*") if f.is_file()]
    
    def get_file_path(self, storage_url: str) -> str:
        """Get local file path from storage URL"""
        return storage_url.replace("local://", "")

class S3Storage(StorageBackend):
    """AWS S3 storage"""
    
    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_REGION
            )
            self.bucket_name = config.S3_BUCKET_NAME
            logger.info(f"S3Storage initialized: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Error initializing S3: {e}")
            raise e
    
    def upload_file(self, file_path: str, user_id: int, filename: str) -> str:
        """Upload file to S3"""
        try:
            s3_key = f"users/user_{user_id}/documents/{filename}"
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            storage_url = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"File uploaded to S3: {storage_url}")
            return storage_url
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            raise e
    
    def download_file(self, storage_url: str, local_path: str) -> bool:
        """Download file from S3"""
        try:
            # Parse S3 URL
            s3_key = storage_url.replace(f"s3://{self.bucket_name}/", "")
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return True
        except Exception as e:
            logger.error(f"Error downloading from S3: {e}")
            return False
    
    def delete_file(self, storage_url: str) -> bool:
        """Delete file from S3"""
        try:
            s3_key = storage_url.replace(f"s3://{self.bucket_name}/", "")
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"File deleted from S3: {storage_url}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from S3: {e}")
            return False
    
    def list_user_files(self, user_id: int) -> list:
        """List all files for a user in S3"""
        try:
            prefix = f"users/user_{user_id}/documents/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [f"s3://{self.bucket_name}/{obj['Key']}" for obj in response.get('Contents', [])]
        except Exception as e:
            logger.error(f"Error listing S3 files: {e}")
            return []

class CloudflareR2Storage(StorageBackend):
    """Cloudflare R2 storage (S3-compatible)"""
    
    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                endpoint_url=config.R2_ENDPOINT,
                aws_access_key_id=config.R2_ACCESS_KEY_ID,
                aws_secret_access_key=config.R2_SECRET_ACCESS_KEY
            )
            self.bucket_name = config.R2_BUCKET_NAME
            logger.info(f"R2Storage initialized: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Error initializing R2: {e}")
            raise e
    
    def upload_file(self, file_path: str, user_id: int, filename: str) -> str:
        """Upload file to R2"""
        try:
            r2_key = f"users/user_{user_id}/documents/{filename}"
            self.s3_client.upload_file(file_path, self.bucket_name, r2_key)
            storage_url = f"r2://{self.bucket_name}/{r2_key}"
            logger.info(f"File uploaded to R2: {storage_url}")
            return storage_url
        except Exception as e:
            logger.error(f"Error uploading to R2: {e}")
            raise e
    
    def download_file(self, storage_url: str, local_path: str) -> bool:
        """Download file from R2"""
        try:
            r2_key = storage_url.replace(f"r2://{self.bucket_name}/", "")
            self.s3_client.download_file(self.bucket_name, r2_key, local_path)
            return True
        except Exception as e:
            logger.error(f"Error downloading from R2: {e}")
            return False
    
    def delete_file(self, storage_url: str) -> bool:
        """Delete file from R2"""
        try:
            r2_key = storage_url.replace(f"r2://{self.bucket_name}/", "")
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=r2_key)
            logger.info(f"File deleted from R2: {storage_url}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from R2: {e}")
            return False
    
    def list_user_files(self, user_id: int) -> list:
        """List all files for a user in R2"""
        try:
            prefix = f"users/user_{user_id}/documents/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [f"r2://{self.bucket_name}/{obj['Key']}" for obj in response.get('Contents', [])]
        except Exception as e:
            logger.error(f"Error listing R2 files: {e}")
            return []

class StorageFactory:
    """Factory to get appropriate storage backend"""
    
    @staticmethod
    def get_storage() -> StorageBackend:
        """Get storage backend based on configuration"""
        storage_type = config.STORAGE_TYPE.lower()
        
        if storage_type == "local":
            return LocalStorage()
        elif storage_type == "s3":
            return S3Storage()
        elif storage_type == "r2":
            return CloudflareR2Storage()
        else:
            logger.warning(f"Unknown storage type: {storage_type}, defaulting to local")
            return LocalStorage()

# Initialize global storage instance
storage = StorageFactory.get_storage()
