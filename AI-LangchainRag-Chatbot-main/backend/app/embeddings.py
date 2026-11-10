
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import EMBEDDING_MODEL_NAME


_embedding_model = None


def get_embedding_model():

    global _embedding_model

    # Load the embedding model only once
    if _embedding_model is None:

        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": 64
            }
        )

    return _embedding_model
