import json
import pytest
from graphrack import GraphRack
from graphrack.graph import EvidenceGraph
from graphrack.text import chunks, bm25
from graphrack.eval import evaluate


def demo():
    return (GraphRack().add_document("a", "Aurora connects to Atlas. Atlas tests retrieval.")
            .add_document("b", "Cedar publishes evaluations for Atlas."))


def test_add_search():
    e = demo()
    hits = e.search("Aurora Atlas")
    assert hits and hits[0].doc_id == "a"
    assert hits[0].matched_entities


def test_save_load(tmp_path):
    e = demo(); target = tmp_path / "idx.json"; e.save(target)
    assert GraphRack.load(target).search("Aurora")[0].chunk_id == e.search("Aurora")[0].chunk_id


def test_evidence_response():
    answer = demo().ask("Aurora Atlas")
    assert answer["status"] == "extractive_evidence"
    assert answer["citations"]


def test_abstain():
    assert demo().ask("%%%%")["status"] == "insufficient_evidence"


def test_path_provenance():
    paths = demo().bridge("aurora", "atlas")
    assert paths and paths[0]["evidence"][0] == ["a::c0"]


def test_chunk_validation():
    with pytest.raises(ValueError): chunks("text", size=3, overlap=3)


def test_duplicate_document():
    with pytest.raises(ValueError): demo().add_document("a", "duplicate")


def test_bm25_empty():
    assert bm25(["hello"], []) == []


def test_evaluation(tmp_path):
    file = tmp_path / "q.jsonl"
    file.write_text(json.dumps({"query": "Aurora", "relevant_chunk_ids": ["a::c0"]}) + "\n")
    m = evaluate(demo(), file, k=1)
    assert m["mrr_at_k"] == 1.0


def test_malformed_index(tmp_path):
    path = tmp_path / "bad.json"; path.write_text('{"version": 99, "records": []}')
    with pytest.raises(ValueError): GraphRack.load(path)


def test_no_phantom_relation():
    g = EvidenceGraph(); g.add("x", "Aurora is helpful. Atlas is useful.")
    assert not g.paths("aurora", "atlas")
