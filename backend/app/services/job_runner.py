from __future__ import annotations

from sqlmodel import Session

from app.db import engine
from app.models import Job, SheetVersion
from app.services.transcription import transcribe_audio


def run_transcription_job(job_id: int, song_id: int, sheet_id: int, target: str) -> None:
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            return

        job.status = "processing"
        session.add(job)
        session.commit()

        from app.models import Song

        song = session.get(Song, song_id)
        if not song:
            job.status = "failed"
            job.result_message = "Song not found."
            session.add(job)
            session.commit()
            return

        result = transcribe_audio(song.audio_file_path, song.title, song.artist, target)
        version = SheetVersion(
            sheet_id=sheet_id,
            version_number=1,
            musicxml=result.musicxml,
            editor_json=result.editor_json,
        )
        session.add(version)

        job.status = "completed"
        job.sheet_id = sheet_id
        job.result_message = result.message
        session.add(job)
        session.commit()
