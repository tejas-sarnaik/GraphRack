"""GraphRack command-line interface."""
import argparse
import json
from .engine import GraphRack
from .eval import evaluate
from .io import read_documents


def main(argv=None):
    parser = argparse.ArgumentParser(prog="graphrack", description="Explainable local GraphRAG retrieval")
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index", help="Index local .txt/.md/.jsonl documents")
    index.add_argument("input")
    index.add_argument("--out", default="graphrack-index.json")
    index.add_argument("--chunk-size", type=int, default=120)
    index.add_argument("--overlap", type=int, default=25)
    ask = sub.add_parser("ask", help="Retrieve cited source evidence")
    ask.add_argument("question")
    ask.add_argument("--index", default="graphrack-index.json")
    ask.add_argument("--top-k", type=int, default=5)
    search = sub.add_parser("search", help="Inspect retrieval scores")
    search.add_argument("query")
    search.add_argument("--index", default="graphrack-index.json")
    search.add_argument("--top-k", type=int, default=5)
    bridge = sub.add_parser("bridge", help="Find provenance-backed entity paths")
    bridge.add_argument("source")
    bridge.add_argument("target")
    bridge.add_argument("--index", default="graphrack-index.json")
    bridge.add_argument("--hops", type=int, default=3)
    graph = sub.add_parser("graph", help="Export graph nodes/edges as JSON")
    graph.add_argument("--index", default="graphrack-index.json")
    graph.add_argument("--out", default="graph.json")
    ev = sub.add_parser("eval", help="Evaluate retrieval on labeled questions")
    ev.add_argument("questions")
    ev.add_argument("--index", default="graphrack-index.json")
    ev.add_argument("--top-k", type=int, default=5)
    a = parser.parse_args(argv)
    if a.command == "index":
        eng = GraphRack()
        for doc_id, text in read_documents(a.input):
            eng.add_document(doc_id, text, chunk_size=a.chunk_size, overlap=a.overlap)
        eng.save(a.out)
        result = {"saved": a.out, "chunks": len(eng.records), "nodes": len(eng.graph.entity_chunks),
                  "edges": len(eng.graph.edges)}
    else:
        eng = GraphRack.load(a.index)
        if a.command == "ask": result = eng.ask(a.question, a.top_k)
        elif a.command == "search": result = [r.to_dict() for r in eng.search(a.query, a.top_k)]
        elif a.command == "bridge": result = eng.bridge(a.source, a.target, a.hops)
        elif a.command == "graph":
            result = eng.graph.to_dict()
            with open(a.out, "w", encoding="utf-8") as f: json.dump(result, f, indent=2)
            result = {"saved": a.out, "nodes": len(result["nodes"]), "edges": len(result["edges"])}
        else: result = evaluate(eng, a.questions, a.top_k)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
