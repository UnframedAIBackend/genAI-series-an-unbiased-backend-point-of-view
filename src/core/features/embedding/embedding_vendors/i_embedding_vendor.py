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
        if token:
            print(f"Initializing model {model_id} with token: {token[:4]}...{token[-4:]}")
        else:
            print(f" {model_id} WITHOUT token")

        try:
            return SentenceTransformer(model_id, token=token, **kwargs)
        except Exception as e:
            print(f"Error initializing model {model_id}: {e}")
            raise e
