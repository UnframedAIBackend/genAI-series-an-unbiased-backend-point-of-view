from typing import Any, List, Optional, Type, Union

from src.core.database.i_repository import IRepository, T


class FileManagementRepository(IRepository[T]):
    __IDENTIFIER: str = "file_management"

    def __init__(self, repository_class: Type[IRepository]):
        self.__repository = repository_class(self.__IDENTIFIER)

    async def find_by_id(self, id: Union[int, str]) -> Optional[T]:
        return await self.__repository.find_by_id(id)

    async def find_all(self) -> List[T]:
        return await self.__repository.find_all()

    async def create(self, data: Any) -> T:
        return await self.__repository.create(data)

    async def create_many(self, data: List[Any]) -> List[T]:
        return await self.__repository.create_many(data)

    async def update(self, id: Union[int, str], data: Any) -> Optional[T]:
        return await self.__repository.update(id, data)

    async def delete(self, id: Union[int, str]) -> bool:
        return await self.__repository.delete(id)
