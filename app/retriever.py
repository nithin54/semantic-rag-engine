from app.embedding import EmbeddingModel
from app.vector_store import VectorStore
from app.mock_vertex_ai import MockGenerativeModel
from app.data_loader import DocumentLoader


class ContextAwareRAGEngine:
    def __init__(self, documents=None):
        self.loader = DocumentLoader(documents)
        self.documents = self.loader.load()
        self.embedding_model = EmbeddingModel()
        self.query_expander = MockGenerativeModel()
        self.vector_store = self._build_vector_store()

    def _build_vector_store(self):
        texts = self.loader.texts()
        embeddings = self.embedding_model.embed_documents(texts)
        dimension = len(embeddings[0])
        store = VectorStore(dimension)
        metadata = [
            {
                "id": document["id"],
                "source": document["source"],
                "tags": document["tags"],
            }
            for document in self.documents
        ]
        store.add_documents(embeddings, texts, metadata)
        return store

    def raw_search(self, query, top_k=3):
        query_embedding = self.embedding_model.embed_text(query)
        return self.vector_store.search(query_embedding, top_k)

    def enhanced_search(self, query, top_k=3):
        expanded_query = self.query_expander.expand_query(query)
        query_embedding = self.embedding_model.embed_text(expanded_query)
        return self.vector_store.search(query_embedding, top_k)

    def search(self, query, strategy="a", top_k=3):
        if strategy.lower() == "b":
            return {
                "query": query,
                "strategy": "AI-Enhanced Retrieval",
                "expanded_query": self.query_expander.expand_query(query),
                "results": self.enhanced_search(query, top_k),
            }

        return {
            "query": query,
            "strategy": "Raw Vector Search",
            "results": self.raw_search(query, top_k),
        }

    def compare(self, query, top_k=3):
        expanded_query = self.query_expander.expand_query(query)
        return {
            "query": query,
            "expanded_query": expanded_query,
            "strategy_a_raw_search": self.raw_search(query, top_k),
            "strategy_b_enhanced_search": self.enhanced_search(query, top_k),
        }
