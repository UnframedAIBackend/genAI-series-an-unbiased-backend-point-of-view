from typing import BinaryIO, Optional
from .file_management_service import FileManagementService


class FileManagementController:

    def __init__(self, file_management_service: FileManagementService):
        self.file_management_service = file_management_service

    def upload_file(self, file: BinaryIO, filename: str) -> FileMetadata:
        file_metadata = self.file_management_service.upload(file, filename)
        # call celery task to process file
        return file_metadata

    def get_file_info(self, file_id: str) -> Optional[FileMetadata]:
        return self.file_management_service.get_info(file_id)
