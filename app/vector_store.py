import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension):
        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []
        self.metadata = []

    def add_documents(self, embeddings, docs, metadata=None):
        embeddings = np.array(embeddings).astype("float32")
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.documents.extend(docs)
        if metadata is None:
            metadata = [{} for _ in docs]
        self.metadata.extend(metadata)

    def search(self, query_embedding, top_k=3):
        query_embedding = np.array([query_embedding]).astype("float32")
        faiss.normalize_L2(query_embedding)
        scores, indices = self.index.search(query_embedding, top_k)
        results = []

        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            results.append({
                "document": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(score)
            })

        return results
