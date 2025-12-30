from typing import Optional

from temporalio.client import Client


class TemporalClientSingleton:
    """Singleton for Temporal client to reuse connections"""

    _instance: Optional[Client] = None

    @classmethod
    async def get_client(cls, host: str, namespace: str) -> Client:
        """Get or create Temporal client instance"""
        if cls._instance is None:
            cls._instance = await Client.connect(host, namespace=namespace)
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """Close the client connection"""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
