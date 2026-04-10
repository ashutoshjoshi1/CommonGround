# Prompt Lab and Evaluation

## Prompt Lab

Features:

- prompt template CRUD
- version creation
- active/default flags
- side-by-side output comparison against the same query

Data model:

- `prompts`
- `prompt_versions`

## Evaluation

Evaluation objects include:

- dataset items (queries + optional expected answers)
- run configuration (`top_k`, pass threshold)
- execution summary

Scoring dimensions:

- groundedness heuristic
- citation coverage
- retrieval relevance
- hallucination risk heuristic
- latency

Outputs:

- per-item scores and pass/fail
- aggregate pass rate and average risk/latency
- prompt-version comparison helper endpoint
