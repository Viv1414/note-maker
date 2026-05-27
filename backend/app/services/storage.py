from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def save_audio_file(upload_file: UploadFile) -> str:
    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(upload_file.filename or "").suffix or ".bin"
    unique_name = f"{uuid4()}{suffix}"
    output_path = media_dir / unique_name

    with output_path.open("wb") as f:
        f.write(upload_file.file.read())

    return str(output_path)
