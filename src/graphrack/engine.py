"""Core index, graph expansion, provenance and extractive responses."""
from dataclasses import dataclass
import json
from pathlib import Path
from .graph import EvidenceGraph, candidates
from .text import bm25, chunks, split_sentences, tokenize


@dataclass
class SearchResult:
    chunk_id: str
    doc_id: str
    score: float
    text: str
    matched_entities: list[str]

    def to_dict(self) -> dict:
        return {"chunk_id": self.chunk_id, "doc_id": self.doc_id, "score": round(self.score, 6),
                "text": self.text, "matched_entities": self.matched_entities}


class GraphRack:
    """No LLM calls, API keys, network, or opaque hallucinated graph relations."""
    def __init__(self):
        self.records: list[dict] = []
        self.graph = EvidenceGraph()

    def add_document(self, doc_id: str, text: str, chunk_size: int = 120, overlap: int = 25):
        if not doc_id or not isinstance(text, str):
            raise ValueError("Nonempty doc_id and string text required")
        if any(r["doc_id"] == doc_id for r in self.records):
            raise ValueError(f"Duplicate document ID: {doc_id}")
        for i, chunk in enumerate(chunks(text, chunk_size, overlap)):
            cid = f"{doc_id}::c{i}"
            self.records.append({"chunk_id": cid, "doc_id": doc_id, "text": chunk})
            self.graph.add(cid, chunk)
        return self

    def search(self, query: str, top_k: int = 5, expansion: float = 0.35) -> list[SearchResult]:
        if top_k < 1 or not 0 <= expansion <= 1:
            raise ValueError("top_k >= 1 and expansion in [0, 1] required")
        if not self.records or not tokenize(query):
            return []
        docs = [tokenize(r["text"]) for r in self.records]
        lexical = bm25(tokenize(query), docs)
        qentities = candidates(query)
        reachable: dict[str, float] = {}
        for entity in qentities:
            for near in self.graph.neighbors(entity):
                reachable[near] = max(reachable.get(near, 0), 0.5)
            reachable[entity] = 1.0
        scale = max(lexical) or 1.0
        ranked = []
        for record, score in zip(self.records, lexical):
            entities = self.graph.chunk_entities[record["chunk_id"]]
            graph_score = sum(reachable[e] for e in entities if e in reachable) / max(len(entities), 1)
            total = (1 - expansion) * score / scale + expansion * graph_score
            if total > 0:
                ranked.append(SearchResult(record["chunk_id"], record["doc_id"], total,
                                           record["text"], sorted(entities & qentities)))
        return sorted(ranked, key=lambda r: (-r.score, r.chunk_id))[:top_k]

    def ask(self, query: str, top_k: int = 5, threshold: float = 0.1) -> dict:
        """Extractive evidence preview, not a generative answer or verified entailment."""
        hits = self.search(query, top_k)
        if not hits or hits[0].score < threshold:
            return {"question": query, "status": "insufficient_evidence", "answer": None,
                    "citations": [], "retrieval": [h.to_dict() for h in hits]}
        terms = set(tokenize(query))
        sentences = [(len(set(tokenize(s)) & terms), h.score, s, h.chunk_id)
                     for h in hits for s in split_sentences(h.text)]
        _, _, best, cid = max(sentences, key=lambda x: (x[0], x[1], -len(x[2])))
        return {"question": query, "status": "extractive_evidence", "answer": best,
                "citations": [cid], "retrieval": [h.to_dict() for h in hits],
                "warning": "Extracted text is source evidence, not a verified answer."}

    def bridge(self, start: str, end: str, max_hops: int = 3) -> list[dict]:
        return self.graph.paths(start.casefold(), end.casefold(), max_hops)

    def save(self, path: str | Path):
        Path(path).write_text(json.dumps({"version": 1, "records": self.records}, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("version") != 1 or not isinstance(data.get("records"), list):
            raise ValueError("Unsupported or invalid index format")
        obj = cls()
        seen = set()
        for r in data["records"]:
            cid, doc, chunk = r["chunk_id"], r["doc_id"], r["text"]
            if cid in seen or not all(isinstance(v, str) for v in (cid, doc, chunk)):
                raise ValueError("Invalid or duplicate chunk record")
            seen.add(cid)
            obj.records.append({"chunk_id": cid, "doc_id": doc, "text": chunk})
            obj.graph.add(cid, chunk)
        return obj
