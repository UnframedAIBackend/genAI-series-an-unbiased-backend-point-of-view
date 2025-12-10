from typing import TypeVar, List, Optional, Any
from pymongo import AsyncMongoClient
from bson import ObjectId
from datetime import datetime
from src.core.configuration.configuration import config
from src.core.database.i_repository import IRepository

T = TypeVar("T")

class NoSQLRepository(IRepository[T]):

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = AsyncMongoClient(config.get("DATABASE_URL"))
        self.db = self.client.get_database()
        self.collection = self.db[self.collection_name]

    async def create(self, data: dict) -> dict:
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        result = await self.collection.insert_one(data)
        data["id"] = str(result.inserted_id)
        return data

    async def find_all(self) -> List[dict]:
        results = []
        async for document in self.collection.find({}):
            document["id"] = str(document.pop("_id"))
            results.append(document)
        return results

    async def find_by_id(self, id: str) -> Optional[dict]:
        try:
            document = await self.collection.find_one({"_id": ObjectId(id)})
        except Exception:
            return None
            
        if document:
            document["id"] = str(document.pop("_id"))
            return document
        return None

    async def update(self, id: str, data: dict) -> Optional[dict]:
        try:
            object_id = ObjectId(id)
        except Exception:
            return None

        data["updated_at"] = datetime.now()
        result = await self.collection.find_one_and_update(
            {"_id": object_id},
            {"$set": data},
            return_document=True
        )
        if result:
            result["id"] = str(result.pop("_id"))
            return result
        return None

    async def delete(self, id: str) -> bool:
        try:
            object_id = ObjectId(id)
        except Exception:
            return False

        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0
