import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.possessions import router as possessions_router

from app.routes.videos import (
    router as videos_router,
)


app = FastAPI()


frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000",
)


allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    frontend_url,
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    possessions_router
)

app.include_router(
    videos_router
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "courtvision-api",
    }