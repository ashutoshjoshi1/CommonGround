from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    EmbeddingMetadata,
    Job,
    JobStatus,
    Source,
    SourceChunk,
    SourceStatus,
    SourceVersion,
)
from app.services.chunking import chunk_text
from app.services.embeddings import get_embedding_service
from app.services.parsing import SUPPORTED_EXTENSIONS, parse_content
from app.services.storage import get_storage


class IngestionError(Exception):
    pass


def validate_upload(file_name: str, payload: bytes) -> None:
    suffix = file_name.lower().rsplit(".", 1)
    extension = f".{suffix[-1]}" if len(suffix) > 1 else ""
    if extension not in SUPPORTED_EXTENSIONS:
        raise IngestionError(f"Unsupported file type: {extension}")

    size_mb = len(payload) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise IngestionError(
            f"File exceeds max size {settings.max_upload_size_mb}MB. Received {size_mb:.2f}MB"
        )


def _detect_dedupe_hint(db: Session, workspace_id: str, file_hash: str) -> str | None:
    existing = (
        db.query(Source)
        .filter(Source.workspace_id == workspace_id, Source.file_hash == file_hash)
        .order_by(Source.created_at.desc())
        .first()
    )
    if existing:
        return f"Potential duplicate of source {existing.id} ({existing.file_name})"
    return None


def process_source(db: Session, source: Source, payload: bytes) -> Source:
    version: SourceVersion | None = None
    try:
        source.status = SourceStatus.PARSING
        source.updated_at = datetime.now(UTC)
        db.commit()

        text, metadata = parse_content(source.file_name, payload)
        if not text.strip():
            raise IngestionError("No extractable content found in source")

        source.status = SourceStatus.INDEXING
        source.metadata_json = metadata
        db.commit()

        latest_version = (
            db.query(SourceVersion)
            .filter(SourceVersion.source_id == source.id)
            .order_by(SourceVersion.version_number.desc())
            .first()
        )
        version_number = 1 if latest_version is None else latest_version.version_number + 1

        version = SourceVersion(
            source_id=source.id,
            version_number=version_number,
            status=SourceStatus.INDEXING,
            parser_version="v1",
            content_summary=text[:1200],
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        chunks = chunk_text(text)
        embedder = get_embedding_service()
        vectors = embedder.embed_texts([chunk.content for chunk in chunks]) if chunks else []

        for idx, chunk in enumerate(chunks):
            vector = vectors[idx] if idx < len(vectors) else [0.0] * settings.embedding_dim
            record = SourceChunk(
                source_id=source.id,
                source_version_id=version.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                token_count=max(1, len(chunk.content.split())),
                metadata_json={"length": len(chunk.content)},
                embedding=vector,
            )
            db.add(record)
            db.flush()

            db.add(
                EmbeddingMetadata(
                    source_chunk_id=record.id,
                    model_name=settings.embedding_model,
                    provider=settings.model_provider,
                    dimension=settings.embedding_dim,
                )
            )

        source.status = SourceStatus.READY
        version.status = SourceStatus.READY
        db.commit()
        db.refresh(source)
        return source
    except Exception as exc:
        source.status = SourceStatus.FAILED
        source.error_message = str(exc)
        if version:
            version.status = SourceStatus.FAILED
        db.commit()
        raise


def create_source_record(
    db: Session,
    *,
    workspace_id: str,
    uploaded_by_id: str,
    file_name: str,
    payload: bytes,
) -> Source:
    validate_upload(file_name=file_name, payload=payload)

    file_hash = hashlib.sha256(payload).hexdigest()
    storage_key = f"{workspace_id}/{file_hash}/{file_name}"

    storage = get_storage()
    storage.save_bytes(storage_key, payload)

    source = Source(
        workspace_id=workspace_id,
        uploaded_by_id=uploaded_by_id,
        file_name=file_name,
        file_type=file_name.split(".")[-1].lower(),
        file_size=len(payload),
        file_hash=file_hash,
        storage_key=storage_key,
        status=SourceStatus.UPLOADED,
        dedupe_hint=_detect_dedupe_hint(db, workspace_id, file_hash),
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    job = Job(
        workspace_id=workspace_id,
        source_id=source.id,
        job_type="source_ingestion",
        status=JobStatus.QUEUED,
        payload_json={"source_id": source.id},
    )
    db.add(job)
    db.commit()

    return source
