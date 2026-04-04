from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import contact  # noqa: F401 — register model metadata
from app.routers import contacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Contacts API",
    description="REST API for storing and managing contacts (PostgreSQL + SQLAlchemy).",
    lifespan=lifespan,
)

app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])


@app.get("/")
def root():
    return {"message": "Contacts API", "docs": "/docs"}
