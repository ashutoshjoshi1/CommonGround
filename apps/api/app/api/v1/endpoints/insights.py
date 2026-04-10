from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import ensure_workspace_access, get_current_user
from app.db.session import get_db
from app.models import Finding, Source, User
from app.schemas.insights import FindingsCreate, FindingsResponse, InsightsResponse
from app.services.audit import log_audit_event
from app.services.insights import compute_workspace_insights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/{workspace_id}", response_model=InsightsResponse)
def get_workspace_insights(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return compute_workspace_insights(db=db, workspace_id=workspace_id)


@router.get("/{workspace_id}/findings", response_model=list[FindingsResponse])
def list_findings(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Finding]:
    ensure_workspace_access(db, current_user.id, workspace_id)
    return (
        db.query(Finding)
        .filter(Finding.workspace_id == workspace_id)
        .order_by(Finding.created_at.desc())
        .all()
    )


@router.post("/findings", response_model=FindingsResponse)
def create_finding(
    payload: FindingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Finding:
    ensure_workspace_access(db, current_user.id, payload.workspace_id)

    finding = Finding(
        workspace_id=payload.workspace_id,
        source_id=payload.source_id,
        run_id=payload.run_id,
        finding_type=payload.finding_type,
        title=payload.title,
        body=payload.body,
        confidence=payload.confidence,
        metadata_json=payload.metadata_json,
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)

    log_audit_event(
        db,
        action="finding.create",
        entity_type="finding",
        entity_id=finding.id,
        workspace_id=finding.workspace_id,
        user_id=current_user.id,
    )

    return finding


@router.post("/sources/{source_id}/image-findings", response_model=list[FindingsResponse])
def generate_image_findings(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Finding]:
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    ensure_workspace_access(db, current_user.id, source.workspace_id)

    text = str(source.metadata_json.get("ocr_text", "")) or ""
    if not text:
        text = " ".join(str(v) for v in source.metadata_json.values())

    findings = [
        Finding(
            workspace_id=source.workspace_id,
            source_id=source.id,
            finding_type="image-observation",
            title="Extracted visual notes",
            body=(text[:600] or "No clear OCR text extracted from image source."),
            confidence=0.52,
            metadata_json={"source_type": source.file_type},
        )
    ]

    for finding in findings:
        db.add(finding)
    db.commit()

    log_audit_event(
        db,
        action="source.image_findings",
        entity_type="source",
        entity_id=source.id,
        workspace_id=source.workspace_id,
        user_id=current_user.id,
    )

    return findings
