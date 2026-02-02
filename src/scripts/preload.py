import logging
import os
import sys

from sentence_transformers import SentenceTransformer, models

from src.core.features.embedding.embedding_models import EMBEDDING_MODEL_MAP

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level))
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(getattr(logging, log_level))


def preload():
    token = os.getenv("HF_TOKEN")

    if not token:
        print("Warning: HF_TOKEN not set. Model downloads may fail for private models.")
        token = None

    for key, model_id in EMBEDDING_MODEL_MAP.items():
        print(f"Downloading {key}: {model_id}...")
        try:
            if "colbert" in model_id.lower():
                print("  - Initializing as explicit Transformer module...")
                word_embedding_model = models.Transformer(model_id, model_args={"token": token})
                pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(), pooling_mode="mean")
                SentenceTransformer(modules=[word_embedding_model, pooling_model])
            else:
                SentenceTransformer(model_id, token=token, trust_remote_code=True)

            print(f"{model_id} cached successfully.")
        except (OSError, ValueError) as e:
            print(f"Failed to load {model_id}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error loading {model_id}: {e}")
            sys.exit(1)

    print("All models preloaded!")


if __name__ == "__main__":
    preload()
