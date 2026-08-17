from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.possessions import router as possessions_router

app = FastAPI()
app.include_router(
    possessions_router
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "courtvision-api",
    }