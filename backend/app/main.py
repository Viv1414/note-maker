from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import create_db_and_tables
from app.routers import health, jobs, shared, sheets, songs

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(health.router)
app.include_router(songs.router)
app.include_router(sheets.router)
app.include_router(shared.router)
app.include_router(jobs.router)
