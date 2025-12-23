from typing import BinaryIO, Optional, Type

from src.core.configuration.configuration import config
from src.core.features.file_management.file_management_vendors import i_management_vendor
from src.core.features.file_management.file_management_vendors.local_management_vendor import LocalManagementVendor

from src.core.features.file_management.file_management_repository import FileManagementRepository

class FileManagementService:
    _vendors: dict[str, Type[i_management_vendor.IManagementVendor]] = {
        "local": LocalManagementVendor,
    }

    def __init__(self, repository: FileManagementRepository):
        vendor_type = config.get("FILE_STORAGE_VENDOR")
        uploads_path = config.get("UPLOADS_PATH")
        
        self.repository = repository

        vendor_class = self._vendors.get(vendor_type)
        if not vendor_class:
            raise ValueError(f"Unsupported file storage vendor: {vendor_type}")

        self.vendor: i_management_vendor.IManagementVendor = vendor_class(base_path=uploads_path)

    def upload(self, file: BinaryIO, filename: str) -> i_management_vendor.FileMetadata:
        return self.vendor.upload(file, filename)

    def get_info(self, file_id: str) -> Optional[i_management_vendor.FileMetadata]:
        return self.vendor.get_info(file_id)

    def get_file(self, file_id: str) -> Optional[bytes]:
        return self.vendor.get_file(file_id)

