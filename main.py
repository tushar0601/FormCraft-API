import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.routes.api import router as api_router

app = FastAPI(title="Form Service")


DEFAULT_ORIGINS = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

ENV_ORIGIN = os.getenv("FRONTEND_ORIGIN", "").strip()  # e.g. https://forms.yourdomain.com
origins = [o for o in (list(DEFAULT_ORIGINS) + ([ENV_ORIGIN] if ENV_ORIGIN else [])) if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # in prod: keep this explicit, avoid "*"
    allow_credentials=True,           # needed if you use cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],              # or list explicitly: ["Authorization","Content-Type",...]
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    row = db.execute(text("SELECT version();")).fetchone()
    return {"version": row[0]}