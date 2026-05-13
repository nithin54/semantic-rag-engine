from app.mock_vertex_ai import MockGenerativeModel


def test_query_expansion():
    model = MockGenerativeModel()
    result = model.expand_query("How does the system handle peak load?")

    assert "auto scaling" in result.lower()
