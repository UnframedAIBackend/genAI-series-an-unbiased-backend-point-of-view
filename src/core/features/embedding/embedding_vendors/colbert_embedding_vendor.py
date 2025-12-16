from typing import Any
from src.core.features.embedding.embedding_vendors.i_embedding_vendor import IEmbeddingVendor
from src.core.features.embedding.embedding_models import Embedding, EMBEDDING_MODEL_MAP


class ColbertEmbeddingVendor(IEmbeddingVendor):
    
    def __init__(self):
        self.model = None

    def generate(self, chunks: list[str]) -> list[Any]:
        if not self.model:
            from sentence_transformers import SentenceTransformer, models
            from src.core.configuration.configuration import config
            
            model_id = EMBEDDING_MODEL_MAP[Embedding.COLBERT]
            token = config.get("HF_TOKEN")
            
            # Initialize explicitly as a Transformer to avoid "No sentence-transformers model found" warning
            word_embedding_model = models.Transformer(model_id, model_args={"token": token})
            self.model = SentenceTransformer(modules=[word_embedding_model])

        features = self.model.tokenize(chunks)
        features = {key: value.to(self.model.device) for key, value in features.items()}
        
        out = self.model.forward(features)
        token_embeddings = out['token_embeddings']
        
        return token_embeddings.tolist()
