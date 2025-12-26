from typing import Any

from .embedding_models import Embedding
from .embedding_vendors.colbert_embedding_vendor import ColbertEmbeddingVendor
from .embedding_vendors.gemma_embedding_vendor import GemmaEmbeddingVendor
from .embedding_vendors.i_embedding_vendor import IEmbeddingVendor
from .embedding_vendors.vanilla_embedding_vendor import VanillaEmbeddingVendor


class EmbeddingService:
    __vendors: dict[Embedding, IEmbeddingVendor] = {
        Embedding.VANILLA: VanillaEmbeddingVendor(),
        Embedding.GEMMA: GemmaEmbeddingVendor(),
        Embedding.COLBERT: ColbertEmbeddingVendor(),
    }

    def generate(self, model_id: Embedding, chunks: list[str]) -> list[Any]:
        vendor = self.__get_vendor(model_id)
        return vendor.generate(chunks)

    def __get_vendor(self, model_id: Embedding) -> IEmbeddingVendor:
        vendor = self.__vendors.get(model_id)
        if not vendor:
            valid_models = ", ".join([e.value for e in Embedding])
            raise ValueError(
                f"Unsupported embedding model: {model_id}. "
                f"Valid options: {valid_models}"
            )
        return vendor
