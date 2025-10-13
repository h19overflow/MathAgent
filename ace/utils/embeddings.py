from typing import List
import asyncio


async def get_embedding(text: str, model: str = "gemini") -> List[float]:
    try:
        from google import genai
        from google.genai import types
        import os

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        result = client.models.embed_content(
            model="models/text-embedding-004",
            contents=text
        )

        return result.embeddings[0].values
    except Exception:
        return simple_embedding_fallback(text)


def simple_embedding_fallback(text: str) -> List[float]:
    words = text.lower().split()
    vocab_size = 1000
    embedding = [0.0] * 384

    for i, word in enumerate(words[:100]):
        hash_val = hash(word) % vocab_size
        idx = hash_val % 384
        embedding[idx] += 1.0 / (i + 1)

    return embedding


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot_product / (mag1 * mag2)
