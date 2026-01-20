from dependency_injector import containers, providers

from src.core.configuration.configuration import config
from src.core.database.nosql.nosql_repository import NoSQLRepository
from src.core.database.nosql.nosql_vector_repository import NoSQLVectorRepository
from src.core.database.sql.sql_repository import SQLRepository
from src.core.database.sql.sql_vector_repository import SQLVectorRepository
from src.core.features.chunk.chunk_strategy_controller import ChunkStrategyController
from src.core.features.chunk.chunk_strategy_service import ChunkStrategyService
from src.core.features.embedding.embedding_controller import EmbeddingController
from src.core.features.embedding.embedding_service import EmbeddingService
from src.core.features.file_management.file_management_controller import FileManagementController
from src.core.features.file_management.file_management_repository import FileManagementRepository
from src.core.features.file_management.file_management_service import FileManagementService
from src.core.features.llm.llm_service import LlmService
from src.core.features.rag.rag_controller import RagController
from src.core.features.rag.rag_service import RagService
from src.core.features.vector_store.vector_store_repository import VectorStoreRepository
from src.core.features.vector_store.vector_store_service import VectorStoreService


class Container(containers.DeclarativeContainer):
    db_engine = providers.Object(config.get("DATABASE_ENGINE"))

    base_repository_class = providers.Selector(
        db_engine,
        mongodb=providers.Object(NoSQLRepository),
        postgres=providers.Object(SQLRepository),
    )

    vector_repository_class = providers.Selector(
        db_engine,
        mongodb=providers.Object(NoSQLVectorRepository),
        postgres=providers.Object(SQLVectorRepository),
    )

    file_management_repository = providers.Singleton(
        FileManagementRepository,
        repository_class=base_repository_class,
    )

    vector_store_repository = providers.Singleton(
        VectorStoreRepository,
        repository_class=vector_repository_class,
    )

    file_management_service = providers.Factory(FileManagementService, repository=file_management_repository)

    vector_store_service = providers.Factory(VectorStoreService, repository=vector_store_repository)

    llm_service = providers.Singleton(LlmService)

    embedding_service = providers.Singleton(EmbeddingService)

    rag_service = providers.Singleton(
        RagService,
        vector_store_service=vector_store_service,
        embedding_service=embedding_service,
        llm_service=llm_service,
    )

    file_management_controller = providers.Factory(
        FileManagementController,
        file_management_service=file_management_service,
        rag_service=rag_service,
        repository=file_management_repository,
    )

    chunk_strategy_service = providers.Singleton(ChunkStrategyService)

    chunk_strategy_controller = providers.Factory(
        ChunkStrategyController,
        chunk_strategy_service=chunk_strategy_service,
        file_management_service=file_management_service,
    )

    embedding_controller = providers.Factory(EmbeddingController, embedding_service=embedding_service)

    rag_controller = providers.Factory(RagController, rag_service=rag_service)


container = Container()
