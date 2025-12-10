import asyncio
from pathlib import Path
import asyncpg
from src.core.configuration.configuration import config


class SQLSeeder:
    def __init__(self):
        self.seeders_dir = Path("src/core/database/sql/seeders")
        self.database_url = config.get("DATABASE_URL").replace("+asyncpg", "")
    
    async def run(self) -> None:
        print("Running seeders...")
        
        if not self.seeders_dir.exists():
            print(f"Seeders directory not found: {self.seeders_dir}")
            return
        
        conn = await asyncpg.connect(self.database_url)
        try:
            for file in sorted(self.seeders_dir.glob("*.sql")):
                print(f"Running seeder: {file.name}")
                sql = file.read_text()
                await conn.execute(sql)
            print("✓ Seeders completed successfully")
        except Exception as e:
            print(f"✗ Seeder failed: {e}")
            raise
        finally:
            await conn.close()


if __name__ == "__main__":
    seeder = SQLSeeder()
    asyncio.run(seeder.run())
