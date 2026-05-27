from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Sheet
from app.schemas import SheetDetailRead
from app.services.sheets import get_latest_version, sheet_to_detail

router = APIRouter(prefix="/shared", tags=["sharing"])


@router.get("/{share_token}", response_model=SheetDetailRead)
def get_shared_sheet(share_token: str, session: Session = Depends(get_session)) -> SheetDetailRead:
    statement = select(Sheet).where(Sheet.share_token == share_token)
    sheet = session.exec(statement).first()
    if not sheet:
        raise HTTPException(status_code=404, detail="Shared sheet not found")
    return sheet_to_detail(sheet, get_latest_version(session, sheet.id))
