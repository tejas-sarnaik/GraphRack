"""Dependency-free, deterministic text processing."""
import math
import re
import unicodedata
from collections import Counter

TOKEN_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(unicodedata.normalize("NFKC", text).casefold())


def split_sentences(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", text) if x.strip()]


def chunks(text: str, size: int = 120, overlap: int = 25) -> list[str]:
    if not 0 <= overlap < size:
        raise ValueError("Require 0 <= overlap < size")
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size - overlap) if words[i:i + size]]


def bm25(query: list[str], corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Okapi BM25, with corpus-length and document-frequency normalization."""
    if not corpus:
        return []
    n = len(corpus)
    avgdl = sum(map(len, corpus)) / n or 1.0
    dfs = Counter(term for doc in corpus for term in set(doc))
    scores = []
    for doc in corpus:
        tf = Counter(doc)
        norm = k1 * (1 - b + b * len(doc) / avgdl)
        score = sum(math.log1p((n - dfs[t] + 0.5) / (dfs[t] + 0.5)) *
                    tf[t] * (k1 + 1) / (tf[t] + norm)
                    for t in set(query) if tf[t])
        scores.append(score)
    return scores
