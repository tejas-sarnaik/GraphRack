"""Retrieval evaluation using explicit chunk-level relevant IDs."""
import json
from pathlib import Path


def evaluate(engine, jsonl_path, k=5):
    n, hits, reciprocal, recall = 0, 0.0, 0.0, 0.0
    details = []
    for line in Path(jsonl_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        q = json.loads(line)
        truth = set(q["relevant_chunk_ids"])
        if not truth:
            raise ValueError("Every evaluation question requires at least one relevant chunk")
        ids = [r.chunk_id for r in engine.search(q["query"], top_k=k)]
        rr = next((1 / (i + 1) for i, cid in enumerate(ids) if cid in truth), 0.0)
        precision = len(set(ids) & truth) / k
        rec = len(set(ids) & truth) / len(truth)
        n += 1; hits += precision; reciprocal += rr; recall += rec
        details.append({"query": q["query"], "retrieved": ids, "precision_at_k": precision,
                        "recall_at_k": rec, "reciprocal_rank": rr})
    if not n:
        raise ValueError("Evaluation dataset is empty")
    return {"queries": n, "k": k, "precision_at_k": hits / n,
            "recall_at_k": recall / n, "mrr_at_k": reciprocal / n, "details": details}
