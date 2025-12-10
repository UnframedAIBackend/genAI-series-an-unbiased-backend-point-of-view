from dependency_injector import containers, providers
from src.core.features.file_management.file_management_service import FileManagementService
from src.core.features.file_management.file_management_controller import FileManagementController
from src.core.features.chunk.chunk_strategy_service import ChunkStrategyService
from src.core.features.chunk.chunk_strategy_controller import ChunkStrategyController

class Container(containers.DeclarativeContainer):
    
    file_management_service = providers.Singleton(FileManagementService)
    
    file_management_controller = providers.Factory(
        FileManagementController,
        file_management_service=file_management_service
    )
    
    chunk_strategy_service = providers.Singleton(ChunkStrategyService)
    
    chunk_strategy_controller = providers.Factory(
        ChunkStrategyController,
        chunk_strategy_service=chunk_strategy_service,
        file_management_service=file_management_service
    )

container = Container()
