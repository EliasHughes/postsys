from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.logging import logger
from app.models import *  # noqa: F401,F403
from app.services.seed import seed_if_empty

app = FastAPI(title=settings.APP_NAME, version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3016", "http://127.0.0.1:3016", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        logger.info("ComercioPro listo — motor=%s", settings.DB_ENGINE)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
