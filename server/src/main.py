import os
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from src.db.index import lifespan
from src.db.pg import Base, engine
from src.api.index import (
    user_router,
    auth_router,
    contributor_router,
    webhook_router,
    agent_router,
)
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    lifespan=lifespan,
    title="Modaic API",
    description="A FastAPI application for Modaic",
    version="1.0.0",
)

Base.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://modaic.dev",
    "https://www.modaic.dev",
    "https://api.modaic.dev",
    "https://git.modaic.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/v1/user")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(contributor_router, prefix="/api/v1/contributor")
app.include_router(webhook_router, prefix="/api/v1/webhooks")
app.include_router(agent_router, prefix="/api/v1/agents")


@app.get("/")
async def root():
    return {"message": "Welcome to Modaic API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
