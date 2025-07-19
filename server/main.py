from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from server.db.index import lifespan
from contextlib import asynccontextmanager

load_dotenv()

app = FastAPI(
    lifespan=lifespan,
    title="Modaic API",
    description="A FastAPI application for Modaic",
    version="1.0.0",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
