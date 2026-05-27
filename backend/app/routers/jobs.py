from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models import Job, Sheet, Song
from app.schemas import JobRead
from app.services.job_runner import run_transcription_job

router = APIRouter(prefix="", tags=["transcription"])


class TranscriptionRequest(BaseModel):
    target: Literal["standard", "tab", "both"] = "both"


@router.post("/songs/{song_id}/transcribe", response_model=JobRead)
def transcribe_song(
    song_id: int,
    payload: TranscriptionRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Job:
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    sheet = Sheet(song_id=song_id, target=payload.target)
    session.add(sheet)
    session.commit()
    session.refresh(sheet)

    job = Job(
        song_id=song_id,
        sheet_id=sheet.id,
        target=payload.target,
        status="pending",
        result_message="Transcription queued.",
    )
    session.add(job)
    session.commit()
    session.refresh(job)

    background_tasks.add_task(
        run_transcription_job,
        job.id,
        song_id,
        sheet.id,
        payload.target,
    )
    return job


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, session: Session = Depends(get_session)) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
