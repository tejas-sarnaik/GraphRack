# GitHub publication checklist

## Repository name

**GraphRack** (recommended). Alternative: `GraphRack-Explainable-RAG`.

If you rename an existing repository, update README badges, all issue links, and `CITATION.cff` URLs accordingly. Do not delete existing code without reviewing it.

## About / description (copy and paste)

**Explainable, local-first GraphRAG toolkit with source-backed evidence paths, hybrid retrieval, citations, and reproducible evaluation.**

## Website

Leave blank until you publish a real demo or documentation site.

## Topics

`graphrag`, `rag`, `knowledge-graph`, `nlp`, `retrieval-augmented-generation`, `explainable-ai`, `information-retrieval`, `python`, `open-source`, `llm`

## Settings

- Public repository; enable Issues and Discussions.
- Add the MIT License and release `v0.1.0` after CI is green.
- Pin to your profile, add a real screenshot/demo when available.
- Update the homepage and links after changing a repository's name.
- Publish a reproducible benchmark before making any superiority or novelty claims.

## Upload without overwriting history

Clone the actual repository, copy these files into it and review `git diff` before committing. For a brand-new empty repository, `git init`, add files, and push. The GitHub connector did not have write permissions for the named `PolicyRAG` repository, so this package is intentionally not pushed.

## Suggested release title

`GraphRack v0.1.0 — Local-first evidence-graph retrieval with traceable sources`

## Suggested short launch post

> Introducing GraphRack: a tiny, local-first evidence-graph retrieval toolkit. Inspect BM25 + graph ranking, follow provenance-backed paths, and evaluate retrieval with reproducible labels—no API key required. Early research prototype; contributions welcome.
