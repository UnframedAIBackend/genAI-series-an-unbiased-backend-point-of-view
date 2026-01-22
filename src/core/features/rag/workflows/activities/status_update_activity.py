from typing import Optional

from temporalio import activity

from src.core.container.container import container


@activity.defn
class FileStatusActivity:
    def __init__(self):
        self.file_management_repository = container.file_management_repository()

    @activity.defn
    async def update_file_status(self, file_id: str, status: str, error_message: Optional[str] = None) -> None:
        """
        Activity to update the processing status of a file.
        """
        file_record = await self.file_management_repository.find_by_id(file_id)
        if file_record:
            file_record["status"] = status
            if error_message:
                file_record["error_message"] = error_message
            await self.file_management_repository.update(file_id, file_record)
            activity.logger.info(f"Updated file {file_id} status to {status}")
        else:
            activity.logger.warning(f"File record with id {file_id} not found. Status update to {status} failed.")
