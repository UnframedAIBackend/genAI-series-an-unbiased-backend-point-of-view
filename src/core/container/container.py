from dependency_injector import containers, providers
from src.core.features.file_management.file_management_service import FileManagementService
from src.core.features.file_management.file_management_controller import FileManagementController
from src.core.features.chunk.chunk_strategy_service import ChunkStrategyService
from src.core.features.chunk.chunk_strategy_controller import ChunkStrategyController
from src.core.features.embedding.embedding_service import EmbeddingService
from src.core.features.embedding.embedding_controller import EmbeddingController
from src.core.features.rag.rag_service import RagService
from src.core.features.rag.rag_controller import RagController
from src.core.features.file_management.file_management_repository import FileManagementRepository
from src.core.features.vector_store.vector_store_service import VectorStoreService

class Container(containers.DeclarativeContainer):

    file_management_repository = providers.Singleton(FileManagementRepository)
    vector_store_repository = providers.Singleton(VectorStoreRepository)

    file_management_service = providers.Factory(
        FileManagementService,
        repository=file_management_repository
    )

    vector_store_service = providers.Factory(
        VectorStoreService,
        repository=vector_store_repository
    )

    rag_service = providers.Singleton(RagService)

    file_management_controller = providers.Factory(
        FileManagementController,
        file_management_service=file_management_service,
        rag_service=rag_service,
        file_management_repository=file_management_repository
    )

    chunk_strategy_service = providers.Singleton(ChunkStrategyService)

    chunk_strategy_controller = providers.Factory(
        ChunkStrategyController,
        chunk_strategy_service=chunk_strategy_service,
        file_management_service=file_management_service
    )

    embedding_service = providers.Singleton(EmbeddingService)

    embedding_controller = providers.Factory(
        EmbeddingController,
        embedding_service=embedding_service
    )


    rag_controller = providers.Factory(
        RagController,
        rag_service=rag_service
    )

container = Container()
