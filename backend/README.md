# Note Maker Backend (FastAPI)

This is a starter backend for your Note Maker app.

## What is included

- FastAPI app bootstrap with CORS for the frontend
- SQLite + SQLModel persistence
- Song upload endpoint
- Stub or ML transcription that creates `Sheet` + `SheetVersion` records
- Async job processing with status polling
- Sheet fetch, edit (new version), and public share links
- Job status endpoint

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example`:

```bash
copy .env.example .env
```

4. Run the API from the `backend` directory:

```bash
python -m uvicorn app.main:app --reload
```

Or from repo root: `.\scripts\run-backend.ps1`

Open docs at `http://127.0.0.1:8000/docs`.

## Main endpoints

- `GET /health`
- `POST /songs` (form-data: `title`, optional `artist`, file `audio_file`)
- `GET /songs`
- `GET /songs/{song_id}`
- `GET /songs/{song_id}/sheets`
- `POST /songs/{song_id}/transcribe` with JSON body:
  - `{"target":"standard"}` or `{"target":"tab"}` or `{"target":"both"}`
- `GET /jobs/{job_id}`
- `GET /sheets/{sheet_id}` (latest version with MusicXML + editor JSON)
- `POST /sheets/{sheet_id}/versions` (save edits)
- `POST /sheets/{sheet_id}/share`
- `GET /shared/{share_token}` (public read-only sheet)
