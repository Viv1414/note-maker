from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Sheet, SheetVersion
from app.schemas import SheetDetailRead


def get_latest_version(session: Session, sheet_id: int) -> SheetVersion:
    statement = (
        select(SheetVersion)
        .where(SheetVersion.sheet_id == sheet_id)
        .order_by(SheetVersion.version_number.desc())
    )
    version = session.exec(statement).first()
    if not version:
        raise HTTPException(status_code=404, detail="No versions for this sheet")
    return version


def sheet_to_detail(sheet: Sheet, version: SheetVersion) -> SheetDetailRead:
    return SheetDetailRead(
        id=sheet.id,
        song_id=sheet.song_id,
        target=sheet.target,
        share_token=sheet.share_token,
        created_at=sheet.created_at,
        musicxml=version.musicxml,
        editor_json=version.editor_json,
        version_number=version.version_number,
    )
