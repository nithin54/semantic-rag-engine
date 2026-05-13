from app.retriever import ContextAwareRAGEngine


def test_retrieval_results():
    engine = ContextAwareRAGEngine()
    results = engine.raw_search("How does the system handle peak load?")

    assert len(results) == 3
    assert isinstance(results[0], dict)
    assert "score" in results[0]
