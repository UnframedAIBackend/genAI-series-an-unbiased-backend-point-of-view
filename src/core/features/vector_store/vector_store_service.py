import logging
from typing import List

from src.core.features.vector_store.vector_store_entity import VectorEntity
from src.core.features.vector_store.vector_store_repository import VectorStoreRepository


class VectorStoreService:
    def __init__(self, repository: VectorStoreRepository):
        self.repository = repository

    async def save(self, vectors: List[VectorEntity]) -> None:
        result = await self.repository.create_many(vectors)
        logging.info(f"Saved {len(result)} vectors to the vector store")
