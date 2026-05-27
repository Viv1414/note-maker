from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SongRead(BaseModel):
    id: int
    title: str
    artist: Optional[str]
    audio_file_path: Optional[str]
    created_at: datetime


class JobRead(BaseModel):
    id: int
    song_id: int
    sheet_id: Optional[int]
    target: str
    status: str
    result_message: str
    created_at: datetime


class SheetRead(BaseModel):
    id: int
    song_id: int
    target: str
    share_token: Optional[str]
    created_at: datetime


class SheetDetailRead(BaseModel):
    id: int
    song_id: int
    target: str
    share_token: Optional[str]
    created_at: datetime
    musicxml: str
    editor_json: Optional[str]
    version_number: int


class SheetVersionCreate(BaseModel):
    musicxml: Optional[str] = None
    editor_json: Optional[str] = None


class ShareLinkRead(BaseModel):
    share_token: str
    share_path: str
