from typing import List
import logging

from src.core.features.vector_store.vector_store_repository import VectorStoreRepository
from src.core.features.vector_store.vector_store_entity import VectorEntity

class VectorStoreService:
    def __init__(self, repository: VectorStoreRepository):
        self.repository = repository

    async def save(self, vectors: List[VectorEntity]) -> None:
        result = await self.repository.create_many(vectors)
        logging.info(f"Saved {len(result)} vectors to the vector store")