# semantic-rag-engine

## Senior Gen AI Assessment: Semantic RAG & Vector Search

## Overview
This repository implements a local Retrieval-Augmented Generation (RAG) pipeline with two retrieval strategies:

- **Strategy A: Raw Vector Search** — direct embedding similarity search using the user query.
- **Strategy B: AI-Enhanced Retrieval** — a mocked query expansion model rewrites the input before similarity search.

The system ingests technical text, generates embeddings with `sentence-transformers`, and stores vectors in a lightweight FAISS index.

## Repository Structure

- `app/embedding.py` — local embedding model wrapper using `sentence-transformers`.
- `app/vector_store.py` — FAISS vector store with cosine similarity search.
- `app/mock_vertex_ai.py` — mocked query expansion logic simulating GenerativeModel behavior.
- `app/data_loader.py` — document ingestion and metadata management.
- `app/retriever.py` — orchestrates raw and enhanced retrieval strategies.
- `app/benchmark.py` — produces structured strategy comparison output.
- `app/web_server.py` — Flask dashboard and API for live retrieval and benchmark reports.
- `retrieval_benchmark.md` — evaluation report comparing raw and enhanced retrieval strategies.
- `tests/` — pytest suite validating embeddings, query expansion, and retrieval.

## Setup

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

### Start the dashboard

```bash
python -m app.main server
```

Open the UI at `http://127.0.0.1:5000`.

### Run benchmark

```bash
python -m app.main benchmark
```

The benchmark outputs a structured comparison for at least 3 complex queries and the results are documented in `retrieval_benchmark.md`.

### Run tests

```bash
pytest
```

## Assessment Requirements Covered

- **Embedding Model**: Local `sentence-transformers` embeddings simulate Vertex AI text embedding behavior.
- **Vector Database**: FAISS is used for local semantic storage and search.
- **Mocking**: `MockGenerativeModel` rewrites queries for Strategy B.
- **Orchestration**: `ContextAwareRAGEngine` manages ingestion, embedding, and retrieval.
- **Benchmark Report**: `retrieval_benchmark.md` shows structured comparisons between Strategy A and B.

## Design Notes

### Similarity Metric
This implementation uses **Cosine Similarity** because sentence-transformer embeddings encode semantic direction more effectively than magnitude. Cosine similarity is invariant to vector length and better suited for sentence-level similarity than Euclidean distance.

### Production Migration to Vertex AI
To migrate this design to Vertex AI and Matching Engine:

1. Replace `sentence-transformers` with Vertex AI `textembedding-gecko`.
2. Replace FAISS with Vertex AI Matching Engine or a managed Vertex AI vector index.
3. Replace `MockGenerativeModel` with Vertex AI `GenerativeModel` for query rewriting.
4. Deploy the API with Cloud Run, GKE, or a Vertex AI Endpoint.
5. Add logging, monitoring, and evaluation via Cloud Logging and Vertex AI Evaluation.

## Notes

- The dashboard now includes strategy definitions and a clear benchmark comparison flow.
- The codebase supports live query comparison and benchmark visualization.
