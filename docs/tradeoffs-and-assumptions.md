# Tradeoffs and Assumptions

## Assumptions

- Local-first developer workflow is the initial target
- Deterministic fallback embedding and synthesis are acceptable for non-GPU dev environments
- Immediate synchronous ingestion in the upload endpoint improves local predictability

## Tradeoffs

- Retrieval scoring currently runs in Python over candidate rows (simple and portable) rather than pure SQL vector search optimization
- OCR baseline relies on local tesseract availability; advanced scanned-PDF OCR is deferred
- Prompt and evaluation UX is practical and usable but intentionally lightweight in first release

## Known Constraints

- Large-model runtime behavior is intentionally abstracted and not hard-bound to a single provider
- Production hardening for strict RBAC and tenancy isolation needs additional policy layer work
