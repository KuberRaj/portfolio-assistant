import pytest
from portfolio_agent import rag_service


def test_cosine_similarity():
    assert rag_service.cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert rag_service.cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_dimension_mismatch():
    with pytest.raises(ValueError):
        rag_service.cosine_similarity([1.0], [1.0, 2.0])


def test_normalizers():
    assert rag_service.normalize_top_k(0) == 1
    assert rag_service.normalize_top_k(100) == rag_service.MAX_TOP_K
    assert rag_service.normalize_similarity_threshold(-1) == 0.0
    assert rag_service.normalize_similarity_threshold(2) == 1.0


def test_validate_index_rejects_bad_dimension():
    with pytest.raises(ValueError):
        rag_service.validate_index({"embedding_model": "m", "embedding_dimension": 2, "chunks": [{"source": "x", "title": "y", "content": "z", "embedding": [1.0]}]})


def test_search_ranks_without_network(monkeypatch):
    fake = {"embedding_model": "m", "embedding_dimension": 2, "chunks": [
        {"source": "experience.md", "title": "ADK", "content": "Google ADK experience", "chunk_index": 0, "embedding": [1.0, 0.0]},
        {"source": "projects.md", "title": "BQ", "content": "BigQuery work", "chunk_index": 0, "embedding": [0.0, 1.0]},
    ]}
    monkeypatch.setattr(rag_service, "load_index", lambda: fake)
    monkeypatch.setattr(rag_service, "generate_query_embedding", lambda *args, **kwargs: [1.0, 0.0])
    result = rag_service.search_portfolio("ADK", top_k=1)
    assert result["status"] == "success"
    assert result["results"][0]["source"] == "experience.md"


def test_search_not_found_without_network(monkeypatch):
    fake = {"embedding_model": "m", "embedding_dimension": 2, "chunks": [{"source": "x.md", "title": "X", "content": "X", "embedding": [0.0, 1.0]}]}
    monkeypatch.setattr(rag_service, "load_index", lambda: fake)
    monkeypatch.setattr(rag_service, "generate_query_embedding", lambda *args,**kwargs: [1.0, 0.0])
    assert rag_service.search_portfolio("none", minimum_similarity=0.5)["status"] == "not_found"
