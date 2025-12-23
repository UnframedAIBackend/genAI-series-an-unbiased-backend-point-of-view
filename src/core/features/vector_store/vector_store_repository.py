from typing import Optional, List, Any

from src.core.database.repository import IRepository
from src.core.features.vector_store.vector_store_entity import VectorEntity

class VectorStoreRepository(IRepository):
    __IDENTIFIER: str = "vector_store"
    __repository: IRepository

    def __init__(self):
        self.__repository = self._get_engine(self.__IDENTIFIER)

    async def find_by_id(self, id: int | str) -> Optional[VectorEntity]:
        return await self.__repository.find_by_id(id)
    
    async def find_all(self) -> List[VectorEntity]:
        return await self.__repository.find_all()
    
    async def create(self, data: VectorEntity) -> VectorEntity:
        return await self.__repository.create(data)
    
    async def update(self, id: int | str, data: VectorEntity) -> Optional[VectorEntity]:
        return await self.__repository.update(id, data)
    
    async def delete(self, id: int | str) -> bool:
        return await self.__repository.delete(id)