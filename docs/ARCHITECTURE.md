# Architecture

`io.py` streams local text inputs; `text.py` chunks/normalizes/tokens/scores; `graph.py` builds per-sentence lexical co-occurrence edges with provenance; `engine.py` couples BM25 ranking, one-hop graph expansion, abstention and persistence; `eval.py` computes labeled retrieval scores; `cli.py` provides command-line UX. Index format v1 stores source text chunks; the graph is deterministically rebuilt on load. This prioritizes transparency over scale. Large corpora are currently held in memory and the graph is quadratic in sentence unique-token count.
