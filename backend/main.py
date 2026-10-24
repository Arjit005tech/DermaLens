import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database import Base, engine
from routers import auth, analyze, history

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DermaLens API",
    description="AI-assisted skin condition screening API",
    version="0.1.0",
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "DermaLens API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
