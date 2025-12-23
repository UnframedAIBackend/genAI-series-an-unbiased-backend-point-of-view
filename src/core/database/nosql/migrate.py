import asyncio
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from pymongo import AsyncMongoClient
from src.core.configuration.configuration import config


class NoSQLMigrate:
    def __init__(self):
        self.migrations_dir = Path("src/core/database/nosql/migrations")
        self.database_url = config.get("DATABASE_URL")
        print(self.database_url)
    
    async def run(self) -> None:
        db_engine = config.get("DATABASE_ENGINE")
        if db_engine not in ["mongodb", "nosql"]:
            print(f"Skipping NoSQL migrations. Current engine: {db_engine}")
            return

        print("Running NoSQL migrations...")
        
        if not self.migrations_dir.exists():
            print(f"Migrations directory not found: {self.migrations_dir}")
            return
        
        client = AsyncMongoClient(self.database_url)
        try:
            db = client.get_database()
            for file in sorted(self.migrations_dir.glob("0*.py")):
                print(f"Running migration: {file.name}")
                module = self.__load_migration(file)
                await module.up(db)
            print("✓ NoSQL Migrations completed successfully")
        except Exception as e:
            print(f"✗ NoSQL Migration failed: {e}")
            raise
        finally:
            await client.close()

    def __load_migration(self, file: Path):
        spec = spec_from_file_location(file.stem, file)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


if __name__ == "__main__":
    asyncio.run(NoSQLMigrate().run())
