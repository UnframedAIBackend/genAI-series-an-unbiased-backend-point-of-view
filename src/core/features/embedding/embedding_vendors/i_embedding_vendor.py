from abc import ABC, abstractmethod
from typing import Any
from sentence_transformers import SentenceTransformer
from src.core.configuration.configuration import config

class IEmbeddingVendor(ABC):
    
    @abstractmethod
    def generate(self, chunks: list[str]) -> list[Any]:
        pass

    def create_model(self, model_id: str, **kwargs) -> SentenceTransformer:
        token = config.get("HF_TOKEN")
        return SentenceTransformer(model_id, token=token, **kwargs)