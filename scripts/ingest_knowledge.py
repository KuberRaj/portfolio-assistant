from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from google.genai import types
import argparse
from dotenv import load_dotenv
from google import genai

BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]

AGENT_DIRECTORY = BACKEND_DIRECTORY
KNOWLEDGE_DIRECTORY = AGENT_DIRECTORY / "knowledge"
VECTOR_STORE_DIRECTORY = AGENT_DIRECTORY / "vector_store"
INDEX_FILE = VECTOR_STORE_DIRECTORY / "portfolio_index.json"

ALLOWED_EXTENSIONS = {
    ".md",
    ".txt",
}

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768

MAX_CHUNK_CHARACTERS = 1400
CHUNK_OVERLAP_CHARACTERS = 200


def load_environment() -> None:
    load_dotenv(BACKEND_DIRECTORY / ".env")

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY was not found in the backend .env file.")


def normalize_text(text: str) -> str:
    """
    Normalize whitespace without removing meaningful Markdown content.
    """
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_markdown_sections(
    content: str,
    source_filename: str,
) -> list[dict[str, str]]:
    """
    Split a Markdown document around headings.

    Each resulting section retains its heading and source filename.
    """
    sections: list[dict[str, str]] = []

    current_heading = Path(source_filename).stem.replace("_", " ").title()
    current_lines: list[str] = []

    def save_current_section() -> None:
        nonlocal current_lines

        section_content = normalize_text("\n".join(current_lines))

        if not section_content:
            current_lines = []
            return

        sections.append(
            {
                "source": source_filename,
                "title": current_heading,
                "content": section_content,
            }
        )

        current_lines = []

    for line in content.splitlines():
        heading_match = re.match(
            r"^(#{1,6})\s+(.+?)\s*$",
            line.strip(),
        )

        if heading_match:
            save_current_section()
            current_heading = heading_match.group(2).strip()
            continue

        current_lines.append(line)

    save_current_section()

    return sections


def split_large_section(
    section: dict[str, str],
) -> list[dict[str, Any]]:
    """
    Split large sections into overlapping chunks.

    Paragraph boundaries are preferred. Character-based splitting is
    used only when a single paragraph is too large.
    """
    content = section["content"]

    if len(content) <= MAX_CHUNK_CHARACTERS:
        return [
            {
                **section,
                "chunk_index": 0,
            }
        ]

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", content)
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = (
            f"{current_chunk}\n\n{paragraph}".strip() if current_chunk else paragraph
        )

        if len(candidate) <= MAX_CHUNK_CHARACTERS:
            current_chunk = candidate
            continue

        if current_chunk:
            chunks.append(current_chunk)

            overlap = current_chunk[-CHUNK_OVERLAP_CHARACTERS:]
            current_chunk = f"{overlap}\n\n{paragraph}".strip()
        else:
            start = 0

            while start < len(paragraph):
                end = start + MAX_CHUNK_CHARACTERS
                chunks.append(paragraph[start:end].strip())

                start = max(
                    end - CHUNK_OVERLAP_CHARACTERS,
                    start + 1,
                )

            current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk)

    return [
        {
            **section,
            "content": chunk,
            "chunk_index": chunk_index,
        }
        for chunk_index, chunk in enumerate(chunks)
        if chunk
    ]


def load_document_chunks() -> list[dict[str, Any]]:
    """
    Load and chunk all approved knowledge files.
    """
    if not KNOWLEDGE_DIRECTORY.exists():
        raise FileNotFoundError(
            f"Knowledge directory does not exist: " f"{KNOWLEDGE_DIRECTORY}"
        )

    document_chunks: list[dict[str, Any]] = []

    knowledge_files = sorted(
        path
        for path in KNOWLEDGE_DIRECTORY.rglob("*")
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
    )

    if not knowledge_files:
        raise RuntimeError("No Markdown or text knowledge files were found.")

    for file_path in knowledge_files:
        relative_filename = str(file_path.relative_to(KNOWLEDGE_DIRECTORY))

        content = file_path.read_text(encoding="utf-8")
        sections = split_markdown_sections(
            content=content,
            source_filename=relative_filename,
        )

        for section in sections:
            document_chunks.extend(split_large_section(section))

    return document_chunks


def create_embedding_text(chunk: dict[str, Any]) -> str:
    """
    Add meaningful metadata to the text passed to the embedding model.
    """
    return f"title: {chunk['title']} | " f"text: {chunk['content']}"


def generate_embedding(
    client: genai.Client,
    text: str,
    title: str,
) -> list:
    """
    Generate a document embedding for one portfolio chunk.
    """
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            title=title,
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    if not response.embeddings:
        raise RuntimeError("The embedding API returned no embeddings.")

    first_embedding = response.embeddings[0]

    if not first_embedding.values:
        raise RuntimeError("The embedding API returned an empty vector.")

    embedding = [float(value) for value in first_embedding.values]

    if len(embedding) != EMBEDDING_DIMENSION:
        raise RuntimeError(
            "The generated document embedding has an "
            f"unexpected dimension. Expected "
            f"{EMBEDDING_DIMENSION}, received "
            f"{len(embedding)}."
        )

    return embedding


def build_index(
    dry_run: bool = False,
) -> dict[str, Any\]:
    # load_environment()

    chunks = load_document_chunks()

    if dry_run:
        return {
            "status": "dry_run",
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "source": chunk["source"],
                    "title": chunk["title"],
                    "chunk_index": chunk["chunk_index"],
                    "characters": len(chunk["content"]),
                }
                for chunk in chunks
            ],
        }

    client = genai.Client(
        api_key=os.environ["GOOGLE_API_KEY"],
    )

    VECTOR_STORE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    indexed_chunks: list[dict[str, Any]] = []

    print(f"Found {len(chunks)} knowledge chunks.")

    for position, chunk in enumerate(chunks, start=1):
        embedding_text = create_embedding_text(chunk)

        print(
            f"[{position}/{len(chunks)}] "
            f"Embedding {chunk['source']} -> {chunk['title']}"
        )

        embedding = generate_embedding(
            client=client,
            text=chunk["content"],
            title=chunk["title"],
        )

        indexed_chunks.append(
            {
                "id": (
                    f"{chunk['source']}::"
                    f"{chunk['title']}::"
                    f"{chunk['chunk_index']}"
                ),
                "source": chunk["source"],
                "title": chunk["title"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "embedding": embedding,
            }
        )

        time.sleep(0.15)

    index_payload = {
        "schema_version": 1,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "chunk_count": len(indexed_chunks),
        "chunks": indexed_chunks,
    }

    temporary_index_file = INDEX_FILE.with_suffix(".tmp")

    temporary_index_file.write_text(
        json.dumps(
            index_payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_index_file.replace(INDEX_FILE)

    print()
    print(f"Successfully indexed {len(indexed_chunks)} chunks.")
    print(f"Index written to: {INDEX_FILE}")
    return index_payload


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the portfolio RAG vector index.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate knowledge files and chunking without "
            "calling the embedding API."
        ),
    )

    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    try:
        result = build_index(
            dry_run=arguments.dry_run,
        )

        if arguments.dry_run:
            print(
                json.dumps(
                    result,
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print()
            print(
                f"Successfully generated "
                f"{result['chunk_count']} knowledge chunks."
            )
            print(
                f"Index written to: {INDEX_FILE}"
            )

        return 0

    except Exception as error:
        print(
            f"Knowledge ingestion failed: {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
