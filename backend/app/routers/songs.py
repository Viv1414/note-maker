from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.db import get_session
from app.models import Sheet, Song
from app.schemas import SheetRead, SongRead
from app.services.storage import save_audio_file

router = APIRouter(prefix="/songs", tags=["songs"])


@router.post("", response_model=SongRead)
def create_song(
    title: Annotated[str, Form(...)],
    artist: Annotated[Optional[str], Form()] = None,
    audio_file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> Song:
    audio_path = save_audio_file(audio_file)
    song = Song(title=title, artist=artist, audio_file_path=audio_path)

    session.add(song)
    session.commit()
    session.refresh(song)
    return song


@router.get("", response_model=list[SongRead])
def list_songs(session: Session = Depends(get_session)) -> list[Song]:
    statement = select(Song).order_by(Song.created_at.desc())
    return session.exec(statement).all()


@router.get("/{song_id}", response_model=SongRead)
def get_song(song_id: int, session: Session = Depends(get_session)) -> Song:
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.get("/{song_id}/sheets", response_model=list[SheetRead])
def list_sheets_for_song(song_id: int, session: Session = Depends(get_session)) -> list[Sheet]:
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    statement = select(Sheet).where(Sheet.song_id == song_id).order_by(Sheet.created_at.desc())
    return session.exec(statement).all()
