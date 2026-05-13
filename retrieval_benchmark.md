# Retrieval Benchmark Report

## Strategy A vs Strategy B

### Query 1
How does the system handle peak load?

#### Strategy A
Top 3 raw vector search results:
1. The system handles peak load using horizontal scaling and load balancers. (score 0.8083)
2. Auto-scaling increases server instances automatically during traffic spikes. (score 0.4334)
3. Rate limiting prevents abuse and protects backend services from overload. (score 0.3323)

#### Strategy B
Top 3 enhanced search results:
1. Auto-scaling increases server instances automatically during traffic spikes. (score 0.7869)
2. The system handles peak load using horizontal scaling and load balancers. (score 0.6387)
3. Distributed systems use replication and failover mechanisms for reliability. (score 0.3818)

### Query 2
How is performance improved?

#### Strategy A
Top 3 raw vector search results:
1. Caching improves application performance by reducing repeated database queries. (score 0.4302)
2. Message queues help process asynchronous workloads efficiently. (score 0.4079)
3. Monitoring tools track CPU, memory, and application latency. (score 0.3614)

#### Strategy B
Top 3 enhanced search results:
1. Caching improves application performance by reducing repeated database queries. (score 0.7680)
2. Message queues help process asynchronous workloads efficiently. (score 0.4346)
3. Monitoring tools track CPU, memory, and application latency. (score 0.4093)

### Query 3
How is system reliability maintained?

#### Strategy A
Top 3 raw vector search results:
1. Distributed systems use replication and failover mechanisms for reliability. (score 0.6450)
2. Monitoring tools track CPU, memory, and application latency. (score 0.3499)
3. Message queues help process asynchronous workloads efficiently. (score 0.3174)

#### Strategy B
Top 3 enhanced search results:
1. Distributed systems use replication and failover mechanisms for reliability. (score 0.8185)
2. Message queues help process asynchronous workloads efficiently. (score 0.2523)
3. The system handles peak load using horizontal scaling and load balancers. (score 0.2456)

### Observation
Query expansion improved semantic retrieval confidence for complex phrasing by rewriting user questions into broader, embedding-friendly terms. Strategy B increased the top result score for the first and third queries and aligned results more strongly with the user intent.

---

## Similarity Metric Choice

We selected Cosine Similarity because sentence-transformer embeddings represent semantic direction rather than magnitude.

Cosine similarity performs better than Euclidean distance for sentence embeddings because it focuses on contextual closeness and is invariant to vector length.

---

## Production Migration to Vertex AI Vector Search

Production migration steps:

1. Replace sentence-transformers with Vertex AI textembedding-gecko.
2. Replace FAISS with Vertex AI Matching Engine.
3. Store vectors inside a GCP Vector Index.
4. Use Gemini or Vertex AI GenerativeModel for query rewriting and reranking.
5. Deploy retrieval API using Cloud Run or GKE.
6. Add monitoring and evaluation using Cloud Logging and Vertex AI Evaluation.
