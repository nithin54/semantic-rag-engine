import json
from app.retriever import ContextAwareRAGEngine


QUERIES = [
    "How does the system handle peak load?",
    "How is performance improved?",
    "How is system reliability maintained?"
]


def benchmark(output_path: str = None):
    engine = ContextAwareRAGEngine()
    results = [engine.compare(query) for query in QUERIES]
    json_results = json.dumps(results, indent=4)
    print(json_results)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_results)

    return results


if __name__ == "__main__":
    benchmark("retrieval_benchmark.json")
