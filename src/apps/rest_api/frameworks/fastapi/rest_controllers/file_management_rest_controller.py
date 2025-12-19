from fastapi import APIRouter, UploadFile, File, HTTPException
from io import BytesIO
from src.core.features.file_management.file_management_controller import FileManagementController
from src.core.container.container import container


class FileManagementRestController:
    def __init__(self) -> None:
        self.file_management_controller: FileManagementController = container.file_management_controller()

        self.router = APIRouter(prefix="/files", tags=["file-management"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.add_api_route(
            "/upload",
            self.upload_file,
            methods=["POST"],
            summary="Upload a file",
        )
        self.router.add_api_route(
            "/{file_id}",
            self.get_file_info,
            methods=["GET"],
            summary="Get file information",
        )

    async def upload_file(self, file: UploadFile = File(...)) -> dict:
        """Upload a file to the configured storage vendor."""
        try:
            content = await file.read()
            file_obj = BytesIO(content)

            metadata = await self.file_management_controller.upload_file(
                file_obj,
                file.filename or "unknown"
            )

            return {
                "message": "File uploaded successfully",
                "file_id": metadata["id"],
                "filename": metadata["original_filename"],
                "size": metadata["size"],
                "uploaded_at": metadata["uploaded_at"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    async def get_file_info(self, file_id: str) -> dict:
        """Get file metadata by ID."""
        info = self.file_management_controller.get_file_info(file_id)

        if not info:
            raise HTTPException(status_code=404, detail="File not found")

        return info


file_management_controller = FileManagementRestController()
router = file_management_controller.router
