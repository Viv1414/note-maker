from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db import create_db_and_tables, engine
from app.main import app

db_path = Path(settings.database_url.replace("sqlite:///", ""))
if db_path.exists():
    db_path.unlink()
engine.dispose()
create_db_and_tables()

with TestClient(app) as client:
    assert client.get("/health").json() == {"status": "ok"}

    files = {"audio_file": ("test.wav", BytesIO(b"RIFF"), "audio/wav")}
    data = {"title": "Test Song", "artist": "Test Artist"}
    song = client.post("/songs", data=data, files=files).json()
    assert song["title"] == "Test Song"

    job = client.post(f"/songs/{song['id']}/transcribe", json={"target": "both"}).json()
    finished = client.get(f"/jobs/{job['id']}").json()
    assert finished["status"] == "completed"
    assert finished["sheet_id"] is not None

    sheet = client.get(f"/sheets/{finished['sheet_id']}").json()
    assert "musicxml" in sheet

    share = client.post(f"/sheets/{finished['sheet_id']}/share").json()
    shared = client.get(f"/shared/{share['share_token']}").json()
    assert shared["id"] == finished["sheet_id"]

    print("API smoke test passed", song["id"], finished["sheet_id"])
