from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import Sheet
from app.schemas import ShareLinkRead, SheetDetailRead, SheetVersionCreate
from app.services.sheets import get_latest_version, sheet_to_detail

router = APIRouter(prefix="/sheets", tags=["sheets"])


@router.get("/{sheet_id}", response_model=SheetDetailRead)
def get_sheet_latest(sheet_id: int, session: Session = Depends(get_session)) -> SheetDetailRead:
    sheet = session.get(Sheet, sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return sheet_to_detail(sheet, get_latest_version(session, sheet_id))


@router.post("/{sheet_id}/versions", response_model=SheetDetailRead)
def create_sheet_version(
    sheet_id: int,
    payload: SheetVersionCreate,
    session: Session = Depends(get_session),
) -> SheetDetailRead:
    sheet = session.get(Sheet, sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")

    latest = get_latest_version(session, sheet_id)
    if not payload.musicxml and not payload.editor_json:
        raise HTTPException(status_code=400, detail="Provide musicxml and/or editor_json")

    from app.models import SheetVersion

    version = SheetVersion(
        sheet_id=sheet_id,
        version_number=latest.version_number + 1,
        musicxml=payload.musicxml or latest.musicxml,
        editor_json=payload.editor_json or latest.editor_json,
    )
    session.add(version)
    session.commit()
    session.refresh(version)
    return sheet_to_detail(sheet, version)


@router.post("/{sheet_id}/share", response_model=ShareLinkRead)
def create_share_link(sheet_id: int, session: Session = Depends(get_session)) -> ShareLinkRead:
    sheet = session.get(Sheet, sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Sheet not found")

    if not sheet.share_token:
        sheet.share_token = uuid4().hex
        session.add(sheet)
        session.commit()
        session.refresh(sheet)

    return ShareLinkRead(
        share_token=sheet.share_token,
        share_path=f"/shared/{sheet.share_token}",
    )
