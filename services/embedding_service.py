from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

EMBEDDING_DIMENSION = 384
EMBEDDING_BATCH_SIZE = 16


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the model once and reuse it.
    """

    model = SentenceTransformer(
        EMBEDDING_MODEL_NAME,
        device="cpu"
    )

    model.eval()

    return model


def create_embeddings(
    texts: list[str],
) -> np.ndarray:
    """
    Convert multiple text passages into embeddings.
    """

    if not texts:
        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32,
        )

    cleaned_texts = [
        text.strip()
        for text in texts
    ]

    if any(not text for text in cleaned_texts):
        raise ValueError(
            "Cannot create an embedding for empty text."
        )

    model = get_embedding_model()

    embeddings = model.encode(
        cleaned_texts,
        batch_size=EMBEDDING_BATCH_SIZE,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings = embeddings.astype(np.float32)

    if embeddings.shape != (
        len(cleaned_texts),
        EMBEDDING_DIMENSION,
    ):
        raise RuntimeError(
            "Unexpected embedding shape: "
            f"{embeddings.shape}"
        )

    if not np.isfinite(embeddings).all():
        raise RuntimeError(
            "The embeddings contain invalid numbers."
        )

    return embeddings


def add_embeddings_to_chunks(
    chunks: list[dict],
) -> dict:
    """
    Generate and attach one embedding to every chunk.
    """

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = create_embeddings(chunk_texts)

    embedded_chunks = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
        strict=True,
    ):
        embedded_chunks.append({
            **chunk,

            # Convert NumPy array to a normal Python list
            # so FastAPI and MongoDB can process it.
            "embedding": embedding.tolist(),

            # Because normalization is enabled,
            # this should be approximately 1.0.
            "embedding_norm": round(
                float(np.linalg.norm(embedding)),
                6,
            ),
        })

    return {
        "embedding_model": EMBEDDING_MODEL_NAME,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "chunks": embedded_chunks,
    }