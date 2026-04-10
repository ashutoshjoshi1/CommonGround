# Ingestion Pipeline

## Supported Formats

- PDF
- DOCX
- TXT
- CSV
- PNG/JPG/JPEG

## Processing Stages

1. Validation

- extension whitelist
- size limit enforcement

2. Storage

- object persisted via storage backend abstraction
- `storage_key` linked to source record

3. Parsing

- PDF text extraction (`pypdf`)
- DOCX extraction (`python-docx`)
- CSV row flattening
- image OCR (`pytesseract`) fallback path

4. Chunking

- fixed-size overlapping windows (`chunk_size`, `chunk_overlap`)

5. Embeddings

- `sentence-transformers` primary path
- deterministic local fallback embedding path

6. Persistence

- `source_versions`
- `source_chunks`
- `embedding_metadata`

7. Status Lifecycle

- `uploaded` -> `parsing` -> `indexing` -> `ready`
- failures recorded with error reason

## Re-index Behavior

- endpoint supports standard or force re-index
- force mode removes prior chunk rows for latest version
