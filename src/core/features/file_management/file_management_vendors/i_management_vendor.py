from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import BinaryIO, Optional


class FileStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class FileMetadata:
    id: str
    original_filename: str
    stored_filename: str
    path: str
    size: int
    uploaded_at: datetime
    status: FileStatus


class IManagementVendor(ABC):
    @abstractmethod
    def upload(self, file: BinaryIO, filename: str) -> FileMetadata:
        pass

    @abstractmethod
    def get_info(self, file_id: str) -> Optional[FileMetadata]:
        pass

    @abstractmethod
    def get_file_by_path(self, path: str) -> Optional[bytes]:
        pass
