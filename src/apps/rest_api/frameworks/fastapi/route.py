from fastapi import APIRouter
from .rest_controllers.file_management_rest_controller import router as file_management_router
from .rest_controllers.chunk_strategy_rest_controller import router as chunk_router
from .rest_controllers.embedding_rest_controller import router as embedding_router

router = APIRouter()

router.include_router(file_management_router)
router.include_router(chunk_router)
router.include_router(embedding_router)
