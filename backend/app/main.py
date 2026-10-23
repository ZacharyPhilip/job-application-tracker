"""Job Application Tracker REST API (FastAPI + SQLite)."""
import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .db import connect, init_db
from .schemas import ApplicationCreate, ApplicationOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create the table on startup if it doesn't exist
    yield


app = FastAPI(title="Job Application Tracker", version="0.1.0", lifespan=lifespan)


def get_db():
    """Provide one database connection per request and always close it."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/applications", response_model=ApplicationOut, status_code=201)
def create_application(item: ApplicationCreate, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute(
        "INSERT INTO applications (company, role, status, applied_date, url, notes) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (item.company, item.role, item.status,
         item.applied_date.isoformat() if item.applied_date else None,
         item.url, item.notes),
    )
    db.commit()
    row = db.execute("SELECT * FROM applications WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


@app.get("/applications", response_model=list[ApplicationOut])
def list_applications(db: sqlite3.Connection = Depends(get_db)):
    """Return all applications, newest first."""
    rows = db.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]