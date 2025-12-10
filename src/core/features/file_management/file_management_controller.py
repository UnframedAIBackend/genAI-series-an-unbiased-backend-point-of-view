from typing import BinaryIO, Optional
from .file_management_service import FileManagementService


class FileManagementController:

    def __init__(self, file_management_service: FileManagementService):
        self.file_management_service = file_management_service

    def upload_file(self, file: BinaryIO, filename: str) -> dict:
        return self.file_management_service.upload(file, filename)

    def get_file_info(self, file_id: str) -> Optional[dict]:
        return self.file_management_service.get_info(file_id)
