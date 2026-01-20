import json
import logging
from typing import BinaryIO, Optional

from src.core.features.file_management.file_management_repository import FileManagementRepository
from src.core.features.rag.rag_service import RagService

from .file_management_service import FileManagementService
from .file_management_vendors.i_management_vendor import FileMetadata


class FileManagementController:
    def __init__(
        self,
        file_management_service: FileManagementService,
        rag_service: RagService,
        repository: FileManagementRepository,
    ):
        self.file_management_service = file_management_service
        self.rag_service = rag_service
        self.repository = repository

    async def upload_file(self, file: BinaryIO, filename: str) -> FileMetadata:
        file_metadata = self.file_management_service.upload(file, filename)
        file_metadata_dict = {**file_metadata, "status": file_metadata["status"].value}
        workflow_info = await self.rag_service.start_file_processing(file_metadata_dict)

        logging.info(f"RAG workflow started for file {json.dumps(workflow_info)}")

        try:
            await self.repository.create(file_metadata_dict)
        except Exception as db_error:
            print("Failed to save file metadata to database: ", db_error)

        return file_metadata

    def get_file_info(self, file_id: str) -> Optional[FileMetadata]:
        return self.file_management_service.get_info(file_id)
