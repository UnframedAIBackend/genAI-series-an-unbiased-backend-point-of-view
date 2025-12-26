import hashlib
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Optional

from .i_management_vendor import FileMetadata, FileStatus, IManagementVendor


class LocalManagementVendor(IManagementVendor):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_store: dict[str, dict] = {}

    def upload(self, file: BinaryIO, filename: str) -> FileMetadata:
        """Upload a file to local storage with hash-based naming."""
        content = file.read()
        file_hash = hashlib.md5(content).hexdigest()[:16]

        file_extension = Path(filename).suffix
        hashed_filename = f"{file_hash}{file_extension}"
        destination_path = self.base_path / hashed_filename

        with open(destination_path, "wb") as dest_file:
            dest_file.write(content)

        metadata = {
            "id": file_hash,
            "original_filename": filename,
            "stored_filename": hashed_filename,
            "path": hashed_filename,
            "size": len(content),
            "uploaded_at": datetime.now().isoformat(),
            "status": FileStatus.PENDING,
        }

        self.metadata_store[file_hash] = metadata

        return metadata

    def get_info(self, file_id: str) -> Optional[FileMetadata]:
        """Retrieve file metadata by ID (hash)."""
        return self.metadata_store.get(file_id)

    def get_file(self, file_id: str) -> Optional[bytes]:
        """Retrieve file content by ID (hash)."""
        metadata = self.get_info(file_id)
        if metadata:
            return self.get_file_by_path(metadata["path"])
        return None

    def get_file_by_path(self, path: str) -> Optional[bytes]:
        """Retrieve file content by absolute path."""
        try:
            with open(path, "rb") as file:
                return file.read()
        except Exception:
            return None
