from typing import TypeVar, List, Optional, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from src.core.configuration.configuration import config
from src.core.database.i_repository import IRepository

T = TypeVar("T")

class SQLRepository(IRepository[T]):
    def __init__(self, table_name: str, schema: Optional[str] = None):
        self.table_name = table_name
        self.schema = schema
        self.engine = create_async_engine(config.get("DATABASE_URL"))

    @property
    def full_table_name(self) -> str:
        return f"{self.schema}.{self.table_name}" if self.schema else self.table_name

    async def find_all(self) -> List[T]:
        async with AsyncSession(self.engine) as session:
            result = await session.execute(text(f"SELECT * FROM {self.full_table_name}"))
            return result.mappings().all()

    async def create(self, data: dict) -> T:
        columns = ", ".join(data.keys())
        values = ", ".join([f":{k}" for k in data.keys()])
        sql = text(f"INSERT INTO {self.full_table_name} ({columns}) VALUES ({values}) RETURNING *")
        
        async with AsyncSession(self.engine) as session:
            result = await session.execute(sql, data)
            await session.commit()
            return result.mappings().first()
    
    async def create_many(self, data: [dict]) -> List[T]:
        columns = ", ".join(data[0].keys())
        values = ", ".join([f":{k}" for k in data[0].keys()])
        sql = text(f"INSERT INTO {self.full_table_name} ({columns}) VALUES ({values}) RETURNING *")
        
        async with AsyncSession(self.engine) as session:
            result = await session.execute(sql, data)
            await session.commit()
            return result.mappings().all()  

    async def find_by_id(self, id: int) -> Optional[T]:
        async with AsyncSession(self.engine) as session:
            result = await session.execute(text(f"SELECT * FROM {self.full_table_name} WHERE id = :id"), {"id": id})
            return result.mappings().first()

    async def update(self, id: int, data: dict) -> Optional[T]:
        set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
        sql = text(f"UPDATE {self.full_table_name} SET {set_clause} WHERE id = :id RETURNING *")
        data["id"] = id
        
        async with AsyncSession(self.engine) as session:
            result = await session.execute(sql, data)
            await session.commit()
            return result.mappings().first()

    async def delete(self, id: int) -> bool:
        async with AsyncSession(self.engine) as session:
            result = await session.execute(text(f"DELETE FROM {self.full_table_name} WHERE id = :id"), {"id": id})
            await session.commit()
            return result.rowcount > 0
