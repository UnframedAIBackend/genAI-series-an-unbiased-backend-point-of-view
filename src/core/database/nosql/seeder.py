import asyncio
from pymongo import AsyncMongoClient
from src.core.configuration.configuration import config

class NoSQLSeeder:
    
    @staticmethod
    async def run():
        print("Running NoSQL seeders...")
        try:
            client = AsyncMongoClient(config.get("DATABASE_URL"))
            db = client.get_database()
            collection = db["notes"]
            
            await collection.delete_many({})
            
            notes = [
                {"content": "The only limit to our realization of tomorrow is our doubts of today.", "times_sent": 0},
                {"content": "Do what you can, with what you have, where you are.", "times_sent": 0},
                {"content": "The best way to predict the future is to invent it.", "times_sent": 0}
            ]
            
            await collection.insert_many(notes)
            print("Seeded MongoDB")
            await client.close()
        except Exception as e:
            print(f"✗ MongoDB Seeder failed: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(NoSQLSeeder.run())
