"""Deterministic entity co-occurrence evidence graph.

Edges mean co-occurrence in a source chunk, NOT a verified semantic relation.
"""
from collections import defaultdict, deque
from dataclasses import dataclass, field
from .text import split_sentences, tokenize

STOP = set("the a an and or is are was were this that with from into at by for on in to of as it its they them he she we have has had can will not which where when how what why between also their".split())


def candidates(text: str, *, min_len: int = 4) -> set[str]:
    """Transparent keyword-entity heuristic; no NER or factual typing implied."""
    counts = defaultdict(int)
    for tok in tokenize(text):
        if len(tok) >= min_len and tok not in STOP and not tok.isnumeric():
            counts[tok] += 1
    return {t for t, count in counts.items() if count > 0}


@dataclass
class EvidenceGraph:
    chunk_entities: dict[str, set[str]] = field(default_factory=dict)
    entity_chunks: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    edges: dict[tuple[str, str], set[str]] = field(default_factory=lambda: defaultdict(set))

    def add(self, chunk_id: str, text: str) -> None:
        entities = candidates(text)
        self.chunk_entities[chunk_id] = entities
        for entity in entities:
            self.entity_chunks[entity].add(chunk_id)
        # Edges only within sentences; provenance attached to every edge.
        for sentence in split_sentences(text):
            sent_entities = sorted(candidates(sentence))
            for i, src in enumerate(sent_entities):
                for dst in sent_entities[i + 1:]:
                    self.edges[(src, dst)].add(chunk_id)

    def neighbors(self, entity: str) -> dict[str, set[str]]:
        result = {}
        for (a, b), refs in self.edges.items():
            if a == entity:
                result[b] = refs
            elif b == entity:
                result[a] = refs
        return result

    def paths(self, start: str, end: str, max_hops: int = 3, limit: int = 5) -> list[dict]:
        """Bounded BFS returns shortest paths with evidence attached to each hop."""
        if max_hops < 1 or limit < 1:
            return []
        if start == end:
            return [{"entities": [start], "evidence": []}] if start in self.entity_chunks else []
        q = deque([(start, [start], [])])
        found = []
        while q and len(found) < limit:
            cur, nodes, evidence = q.popleft()
            if len(nodes) - 1 >= max_hops:
                continue
            for nxt, refs in sorted(self.neighbors(cur).items()):
                if nxt in nodes:
                    continue
                path, ev = nodes + [nxt], evidence + [sorted(refs)]
                if nxt == end:
                    found.append({"entities": path, "evidence": ev})
                    if len(found) >= limit:
                        break
                else:
                    q.append((nxt, path, ev))
        return found

    def to_dict(self) -> dict:
        return {"nodes": [{"id": e, "chunks": sorted(ids)} for e, ids in sorted(self.entity_chunks.items())],
                "edges": [{"source": a, "target": b, "chunks": sorted(refs)}
                          for (a, b), refs in sorted(self.edges.items())]}
