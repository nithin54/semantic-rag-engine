class MockTextEmbeddingModel:
    def get_embeddings(self, text):
        return f"Mock embedding generated for: {text}"


class MockGenerativeModel:
    def expand_query(self, query):
        expansions = {
            "How does the system handle peak load?":
                "Explain auto scaling load balancing traffic spikes and high availability.",
            "How is performance improved?":
                "Explain caching optimization latency reduction and database efficiency.",
            "How is system reliability maintained?":
                "Explain failover replication distributed systems redundancy."
        }
        return expansions.get(query, query)
