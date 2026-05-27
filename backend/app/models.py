from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Song(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    artist: Optional[str] = None
    audio_file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Sheet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    song_id: int = Field(foreign_key="song.id", index=True)
    target: str = Field(default="both")
    share_token: Optional[str] = Field(default=None, index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SheetVersion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sheet_id: int = Field(foreign_key="sheet.id", index=True)
    version_number: int = Field(default=1)
    musicxml: str = Field(default="")
    editor_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    song_id: int = Field(index=True)
    sheet_id: Optional[int] = Field(default=None, foreign_key="sheet.id", index=True)
    target: str = Field(default="both")
    status: str = Field(default="pending")
    result_message: str = Field(default="Transcription queued.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
