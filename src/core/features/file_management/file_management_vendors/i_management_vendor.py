from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class IManagementVendor(ABC):
    @abstractmethod
    def upload(self, file: BinaryIO, filename: str) -> dict:
        pass

    @abstractmethod
    def get_info(self, file_id: str) -> Optional[dict]:
        pass
    
    @abstractmethod
    def get_file(self, file_id: str) -> Optional[bytes]:
        pass
