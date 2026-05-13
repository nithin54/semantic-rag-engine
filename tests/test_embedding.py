from app.embedding import EmbeddingModel


def test_embedding_generation():
    model = EmbeddingModel()
    embedding = model.embed_text("hello world")

    assert embedding is not None
    assert len(embedding) > 0
