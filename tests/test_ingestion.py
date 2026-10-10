from scripts import ingest_knowledge


def test_section_splitting():
    sections = ingest_knowledge.split_markdown_sections("# A\nText A\n## B\nText B", "x.md")
    assert [section["title"] for section in sections] == ["A", "B"]


def test_small_section_chunking():
    chunks = ingest_knowledge.split_large_section({"source": "x.md", "title": "A", "content": "short"})
    assert len(chunks) == 1 and chunks[0]["chunk_index"] == 0


def test_real_knowledge_dry_run():
    result = ingest_knowledge.build_index(dry_run=True)
    assert result["chunk_count"] >= 10
    assert {item["source"] for item in result["chunks"]} == {"profile.md", "experience.md", "projects.md"}
