from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, tickets
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TaskDesk API", version="1.0.0", lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
