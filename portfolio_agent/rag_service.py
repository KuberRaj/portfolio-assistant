from __future__ import annotations

import json
import math
import os
from pathlib import Path
from threading import Lock
from typing import Any

from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AGENT_DIRECTORY = Path(__file__).resolve().parent

INDEX_FILE = (
    AGENT_DIRECTORY
    / "vector_store"
    / "portfolio_index.json"
)

DEFAULT_TOP_K = 5
MAX_TOP_K = 8

# Start with a relatively permissive threshold.
# After testing retrieval results, this can be adjusted.
DEFAULT_MINIMUM_SIMILARITY = 0.30


# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_index_lock = Lock()

_cached_index: dict[str, Any] | None = None
_cached_modified_time: float | None = None

_genai_client: genai.Client | None = None


# ---------------------------------------------------------------------------
# Google Gen AI client
# ---------------------------------------------------------------------------

def get_genai_client() -> genai.Client:
    """
    Create and cache the Google Gen AI client.

    Returns:
        A configured Google Gen AI client.

    Raises:
        RuntimeError:
            If GOOGLE_API_KEY is not configured.
    """
    global _genai_client

    if _genai_client is not None:
        return _genai_client

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. "
            "Add it to the backend .env file."
        )

    _genai_client = genai.Client(
        api_key=api_key
    )

    return _genai_client


# ---------------------------------------------------------------------------
# Index loading and validation
# ---------------------------------------------------------------------------

def load_index() -> dict[str, Any]:
    """
    Load the local portfolio vector index.

    The index is cached in memory after the first load. If the index
    file is regenerated, the modified timestamp changes and the cache
    is refreshed automatically.

    Returns:
        The validated vector-index payload.

    Raises:
        FileNotFoundError:
            If the vector index has not been generated.
        ValueError:
            If the vector index has an invalid structure.
    """
    global _cached_index
    global _cached_modified_time

    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            "The portfolio vector index does not exist. "
            "Run 'python scripts/ingest_knowledge.py' first."
        )

    current_modified_time = INDEX_FILE.stat().st_mtime

    with _index_lock:
        if (
            _cached_index is not None
            and _cached_modified_time == current_modified_time
        ):
            return _cached_index

        try:
            raw_content = INDEX_FILE.read_text(
                encoding="utf-8",
            )

            index_payload = json.loads(raw_content)

        except json.JSONDecodeError as error:
            raise ValueError(
                "The portfolio vector index contains invalid JSON."
            ) from error

        except OSError as error:
            raise ValueError(
                "The portfolio vector index could not be read."
            ) from error

        validate_index(index_payload)

        _cached_index = index_payload
        _cached_modified_time = current_modified_time

        return index_payload


def validate_index(index_payload: Any) -> None:
    """
    Validate the vector-index structure.

    Args:
        index_payload:
            Parsed JSON content from the vector-index file.

    Raises:
        ValueError:
            If any required field is missing or invalid.
    """
    if not isinstance(index_payload, dict):
        raise ValueError(
            "The portfolio vector index must be a JSON object."
        )

    embedding_model = index_payload.get(
        "embedding_model"
    )

    embedding_dimension = index_payload.get(
        "embedding_dimension"
    )

    chunks = index_payload.get("chunks")

    if (
        not isinstance(embedding_model, str)
        or not embedding_model.strip()
    ):
        raise ValueError(
            "The index does not contain a valid embedding_model."
        )

    if (
        not isinstance(embedding_dimension, int)
        or embedding_dimension <= 0
    ):
        raise ValueError(
            "The index does not contain a valid "
            "embedding_dimension."
        )

    if not isinstance(chunks, list):
        raise ValueError(
            "The index does not contain a valid chunks list."
        )

    if not chunks:
        raise ValueError(
            "The portfolio vector index contains no chunks."
        )

    required_fields = {
        "source",
        "title",
        "content",
        "embedding",
    }

    for position, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            raise ValueError(
                f"Index chunk {position} is not a JSON object."
            )

        missing_fields = required_fields.difference(
            chunk.keys()
        )

        if missing_fields:
            missing_fields_text = ", ".join(
                sorted(missing_fields)
            )

            raise ValueError(
                f"Index chunk {position} is missing required "
                f"fields: {missing_fields_text}."
            )

        if not isinstance(chunk["source"], str):
            raise ValueError(
                f"Index chunk {position} has an invalid source."
            )

        if not isinstance(chunk["title"], str):
            raise ValueError(
                f"Index chunk {position} has an invalid title."
            )

        if not isinstance(chunk["content"], str):
            raise ValueError(
                f"Index chunk {position} has invalid content."
            )

        embedding = chunk["embedding"]

        if not isinstance(embedding, list):
            raise ValueError(
                f"Index chunk {position} has an invalid "
                "embedding value."
            )

        if len(embedding) != embedding_dimension:
            raise ValueError(
                f"Index chunk {position} has embedding dimension "
                f"{len(embedding)}, but the index expects "
                f"{embedding_dimension}."
            )

        for value_position, value in enumerate(embedding):
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Index chunk {position} contains a "
                    f"non-numeric embedding value at position "
                    f"{value_position}."
                )


# ---------------------------------------------------------------------------
# Vector operations
# ---------------------------------------------------------------------------

def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vector_a:
            First embedding vector.
        vector_b:
            Second embedding vector.

    Returns:
        A cosine-similarity score between -1 and 1.

    Raises:
        ValueError:
            If the vectors have different dimensions.
    """
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding dimensions do not match. "
            f"Received {len(vector_a)} and {len(vector_b)}."
        )

    if not vector_a:
        return 0.0

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(
            vector_a,
            vector_b,
        )
    )

    magnitude_a = math.sqrt(
        sum(
            value * value
            for value in vector_a
        )
    )

    magnitude_b = math.sqrt(
        sum(
            value * value
            for value in vector_b
        )
    )

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


# ---------------------------------------------------------------------------
# Query embedding
# ---------------------------------------------------------------------------

def generate_query_embedding(
    query: str,
    embedding_model: str,
    embedding_dimension: int,
) -> list:
    """
    Generate an embedding for a portfolio-search query.

    The same embedding model and output dimension used during document
    ingestion must also be used for queries.

    Args:
        query:
            Search query from the portfolio agent.
        embedding_model:
            Embedding model stored in the generated index.
        embedding_dimension:
            Embedding dimension stored in the generated index.

    Returns:
        Query embedding as a list of floating-point numbers.

    Raises:
        RuntimeError:
            If the embedding API returns no valid vector.
    """
    cleaned_query = " ".join(
        query.strip().split()
    )

    if not cleaned_query:
        raise ValueError(
            "The query cannot be empty."
        )

    client = get_genai_client()

    response = client.models.embed_content(
        model=embedding_model,
        contents=cleaned_query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=embedding_dimension,
        ),
    )

    if not response.embeddings:
        raise RuntimeError(
            "The embedding API returned no query embeddings."
        )

    first_embedding = response.embeddings[0]

    if not first_embedding.values:
        raise RuntimeError(
            "The embedding API returned an empty query vector."
        )

    query_embedding = [
        float(value)
        for value in first_embedding.values
    ]

    if len(query_embedding) != embedding_dimension:
        raise RuntimeError(
            "The query embedding has an unexpected dimension. "
            f"Expected {embedding_dimension}, received "
            f"{len(query_embedding)}."
        )

    return query_embedding


# ---------------------------------------------------------------------------
# Input normalization
# ---------------------------------------------------------------------------

def normalize_top_k(top_k: Any) -> int:
    """
    Normalize the requested retrieval-result count.
    """
    try:
        normalized_top_k = int(top_k)
    except (TypeError, ValueError):
        normalized_top_k = DEFAULT_TOP_K

    return max(
        1,
        min(
            normalized_top_k,
            MAX_TOP_K,
        ),
    )


def normalize_similarity_threshold(
    minimum_similarity: Any,
) -> float:
    """
    Normalize the requested similarity threshold.
    """
    try:
        normalized_threshold = float(
            minimum_similarity
        )
    except (TypeError, ValueError):
        normalized_threshold = (
            DEFAULT_MINIMUM_SIMILARITY
        )

    return max(
        0.0,
        min(
            normalized_threshold,
            1.0,
        ),
    )


# ---------------------------------------------------------------------------
# Semantic portfolio search tool
# ---------------------------------------------------------------------------

def search_portfolio(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    minimum_similarity: float = DEFAULT_MINIMUM_SIMILARITY,
) -> dict[str, Any]:
    """
    Search Kunal's published portfolio using semantic similarity.

    Use this tool whenever a visitor asks about Kunal's professional
    profile, skills, technologies, experience, responsibilities,
    projects, education, achievements, or career background.

    Args:
        query:
            A concise semantic search query describing the information
            required to answer the visitor's question.

        top_k:
            Maximum number of relevant knowledge chunks to return.
            The accepted range is 1 through MAX_TOP_K.

        minimum_similarity:
            Minimum cosine-similarity score required for a result.
            The accepted range is 0 through 1.

    Returns:
        A dictionary with one of these statuses:

        success:
            Relevant portfolio sections were found.

        not_found:
            The search completed, but no result satisfied the
            configured similarity threshold.

        error:
            Retrieval could not be completed.
    """
    if not isinstance(query, str):
        return {
            "status": "error",
            "message": (
                "The portfolio search query must be a string."
            ),
            "query": "",
            "result_count": 0,
            "results": [],
        }

    cleaned_query = " ".join(
        query.strip().split()
    )

    if not cleaned_query:
        return {
            "status": "error",
            "message": (
                "A non-empty portfolio search query is required."
            ),
            "query": "",
            "result_count": 0,
            "results": [],
        }

    selected_top_k = normalize_top_k(top_k)

    selected_threshold = (
        normalize_similarity_threshold(
            minimum_similarity
        )
    )

    try:
        index_payload = load_index()

        embedding_model = index_payload[
            "embedding_model"
        ]

        embedding_dimension = index_payload[
            "embedding_dimension"
        ]

        chunks = index_payload["chunks"]

        query_embedding = generate_query_embedding(
            query=cleaned_query,
            embedding_model=embedding_model,
            embedding_dimension=embedding_dimension,
        )

        ranked_results: list[dict[str, Any]] = []

        for chunk in chunks:
            raw_embedding = chunk.get("embedding")

            if not isinstance(raw_embedding, list):
                continue

            document_embedding = [
                float(value)
                for value in raw_embedding
            ]

            if (
                len(document_embedding)
                != embedding_dimension
            ):
                continue

            similarity = cosine_similarity(
                vector_a=query_embedding,
                vector_b=document_embedding,
            )

            if similarity < selected_threshold:
                continue

            content = str(
                chunk.get(
                    "content",
                    "",
                )
            ).strip()

            if not content:
                continue

            ranked_results.append(
                {
                    "source": str(
                        chunk.get(
                            "source",
                            "unknown",
                        )
                    ),
                    "section": str(
                        chunk.get(
                            "title",
                            "Untitled section",
                        )
                    ),
                    "chunk_index": int(
                        chunk.get(
                            "chunk_index",
                            0,
                        )
                    ),
                    "content": content,
                    "similarity": round(
                        similarity,
                        4,
                    ),
                }
            )

        ranked_results.sort(
            key=lambda result: result["similarity"],
            reverse=True,
        )

        selected_results = ranked_results[
            :selected_top_k
        ]

        if not selected_results:
            return {
                "status": "not_found",
                "message": (
                    "No sufficiently relevant information was "
                    "found in Kunal's published portfolio."
                ),
                "query": cleaned_query,
                "minimum_similarity": selected_threshold,
                "result_count": 0,
                "results": [],
            }

        return {
            "status": "success",
            "message": (
                f"Retrieved {len(selected_results)} relevant "
                "portfolio sections."
            ),
            "query": cleaned_query,
            "minimum_similarity": selected_threshold,
            "result_count": len(selected_results),
            "results": selected_results,
        }

    except FileNotFoundError as error:
        return {
            "status": "error",
            "message": str(error),
            "query": cleaned_query,
            "result_count": 0,
            "results": [],
        }

    except ValueError as error:
        return {
            "status": "error",
            "message": (
                "The portfolio vector index or search input is "
                f"invalid: {error}"
            ),
            "query": cleaned_query,
            "result_count": 0,
            "results": [],
        }

    except Exception as error:
        return {
            "status": "error",
            "message": (
                "Portfolio retrieval could not be completed. "
                f"{type(error).__name__}: {error}"
            ),
            "query": cleaned_query,
            "result_count": 0,
            "results": [],
        }


# ---------------------------------------------------------------------------
# Optional local test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        "What experience does Kunal have with Google ADK?",
        "Tell me about Kunal's cloud migration work.",
        "What data pipeline projects has Kunal worked on?",
        "Does Kunal have an AWS certification?",
    ]

    for test_query in test_queries:
        print()
        print("=" * 80)
        print(f"Query: {test_query}")
        print("=" * 80)

        result = search_portfolio(
            query=test_query,
            top_k=3,
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )