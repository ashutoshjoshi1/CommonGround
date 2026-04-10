from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import Job, JobStatus, Source, SourceChunk, SourceVersion, User
from app.schemas.source import ReindexRequest, SourceDetailResponse, SourceResponse
from app.services.audit import log_audit_event
from app.services.ingestion import IngestionError, create_source_record, process_source
from app.services.storage import get_storage

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/upload", response_model=SourceResponse)
async def upload_source(
    workspace_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Source:
    ensure_workspace_access(db, current_user.id, workspace_id)
    payload = await file.read()

    try:
        source = create_source_record(
            db,
            workspace_id=workspace_id,
            uploaded_by_id=current_user.id,
            file_name=file.filename,
            payload=payload,
        )

        # local v1: process immediately for predictable developer UX
        process_source(db=db, source=source, payload=payload)
        job = (
            db.query(Job).filter(Job.source_id == source.id).order_by(Job.created_at.desc()).first()
        )
        if job:
            job.status = JobStatus.COMPLETED
            job.result_json = {"source_id": source.id, "status": "READY"}
            db.commit()
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        job = (
            db.query(Job).filter(Job.source_id == source.id).order_by(Job.created_at.desc()).first()
            if "source" in locals()
            else None
        )
        if job:
            job.status = JobStatus.FAILED
            job.last_error = str(exc)
            db.commit()
        raise HTTPException(status_code=500, detail="Source processing failed") from exc

    log_audit_event(
        db,
        action="source.upload",
        entity_type="source",
        entity_id=source.id,
        workspace_id=workspace_id,
        user_id=current_user.id,
        details={"file_name": source.file_name, "file_type": source.file_type},
    )
    return source


@router.get("", response_model=list[SourceResponse])
def list_sources(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Source]:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return (
        db.query(Source)
        .filter(Source.workspace_id == workspace_id)
        .order_by(Source.created_at.desc())
        .all()
    )


@router.get("/{source_id}", response_model=SourceDetailResponse)
def get_source_detail(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SourceDetailResponse:
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    ensure_workspace_access(db, current_user.id, source.workspace_id)

    chunks = (
        db.query(SourceChunk)
        .filter(SourceChunk.source_id == source.id)
        .order_by(SourceChunk.chunk_index.asc())
        .limit(12)
        .all()
    )
    preview_text = "\n\n".join(chunk.content for chunk in chunks)[:3000]

    return SourceDetailResponse(
        id=source.id,
        workspace_id=source.workspace_id,
        file_name=source.file_name,
        file_type=source.file_type,
        file_size=source.file_size,
        file_hash=source.file_hash,
        status=source.status.value if hasattr(source.status, "value") else str(source.status),
        metadata_json=source.metadata_json,
        dedupe_hint=source.dedupe_hint,
        created_at=source.created_at,
        updated_at=source.updated_at,
        preview_text=preview_text,
        chunks=chunks,
    )


@router.post("/{source_id}/reindex", response_model=SourceResponse)
def reindex_source(
    source_id: str,
    payload: ReindexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Source:
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    ensure_workspace_access(db, current_user.id, source.workspace_id)

    content = get_storage().read_bytes(source.storage_key)

    if payload.force:
        latest_version = (
            db.query(SourceVersion)
            .filter(SourceVersion.source_id == source.id)
            .order_by(SourceVersion.version_number.desc())
            .first()
        )
        if latest_version:
            db.query(SourceChunk).filter(
                SourceChunk.source_version_id == latest_version.id
            ).delete()
            db.commit()

    process_source(db=db, source=source, payload=content)

    log_audit_event(
        db,
        action="source.reindex",
        entity_type="source",
        entity_id=source.id,
        workspace_id=source.workspace_id,
        user_id=current_user.id,
        details={"force": payload.force},
    )

    return source
