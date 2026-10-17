# Research methodology and evaluation protocol

## Formal problem

Given documents `D`, query `q` and chunk set `C`, the objective is to rank chunks by relevance while preserving a source-backed explanation. The graph is `G=(V,E,P)`: `V` is normalized content-word tokens, `E` joins tokens co-occurring in the same sentence, and provenance `P(u,v)` contains the IDs of chunks in which the edge appears. A path `v_0 → ... → v_h` is accompanied by `h` sets of supporting chunk IDs, not a proof of an underlying factual relation.

## Ranking

`BM25(q,c)= Σ_{t∈q} log(1+(N-df_t+0.5)/(df_t+0.5)) * (tf_{t,c}(k1+1))/(tf_{t,c}+k1(1-b+b |c|/avgdl))` with `k1=1.5`, `b=0.75`. Graph support assigns weight 1 to query tokens and 0.5 to their immediate neighbors, then averages supported weights over the tokens in each chunk. Final score is a weighted mixture with λ=0.35 by default. This is heuristic, and longer chunks may be penalized by graph averaging.

## Evaluation best practices

Report (1) Recall@1,5,10, (2) MRR@k, (3) precision@k, (4) median and p95 latency, (5) memory and indexing time, (6) citation accuracy assessed by human annotators or validated entailment, (7) abstention calibration on unanswerable questions, (8) significance across query groups or bootstrap over questions. Avoid evaluating a selected hyperparameter on the test set. Compare BM25, graph-only, graph+BM25, dense-only, dense+graph, and full GraphRAG baselines where reproducible. Use fixed seeds where appropriate and dataset licensing records. For genuine research novelty, preregister an explicit distinct technique and test its incremental value.

## Limitations

The prototype does not identify semantic relations or distinguish names from common words; sentence splitting is English-biased. Term co-occurrence can make spurious bridges. Unverified extractive evidence can still be irrelevant. Threshold scores are query-dependent and are not calibrated probabilities. Entity paths do not establish causal reasoning. There is no claim of superior performance against GraphRAG or HippoRAG.
