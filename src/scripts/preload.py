import sys
import logging

from sentence_transformers import SentenceTransformer, models
from src.core.features.embedding.embedding_models import EMBEDDING_MODEL_MAP
from src.core.configuration.configuration import config

log_level = config.get("LOG_LEVEL").upper()
logging.basicConfig(level=getattr(logging, log_level))
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(getattr(logging, log_level))

def preload():
    token = config.get("HF_TOKEN")

    for key, model_id in EMBEDDING_MODEL_MAP.items():
        print(f"Downloading {key}: {model_id}...")
        try:
            if "colbert" in model_id.lower():
                print(f"  - Initializing as explicit Transformer module...")
                word_embedding_model = models.Transformer(model_id, model_args={"token": token})
                SentenceTransformer(modules=[word_embedding_model])
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
