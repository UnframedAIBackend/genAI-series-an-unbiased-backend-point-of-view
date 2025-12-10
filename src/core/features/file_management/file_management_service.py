from typing import BinaryIO, Optional, Type
from src.core.configuration.configuration import config
from .file_management_vendors.i_management_vendor import IManagementVendor
from .file_management_vendors.local_management_vendor import LocalManagementVendor

class FileManagementService:
    _vendors: dict[str, Type[IManagementVendor]] = {
        "local": LocalManagementVendor,
    }

    def __init__(self):
        vendor_type = config.get("FILE_STORAGE_VENDOR")
        uploads_path = config.get("UPLOADS_PATH")
        
        vendor_class = self._vendors.get(vendor_type)
        if not vendor_class:
            raise ValueError(f"Unsupported file storage vendor: {vendor_type}")
        
        self.vendor: IManagementVendor = vendor_class(base_path=uploads_path)

    def upload(self, file: BinaryIO, filename: str) -> dict:
        return self.vendor.upload(file, filename)
    
    def get_info(self, file_id: str) -> Optional[dict]:
        return self.vendor.get_info(file_id)
    
    def get_file(self, file_id: str) -> Optional[bytes]:
        return self.vendor.get_file(file_id)
