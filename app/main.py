import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routers import auth, users, articles, model
from app.db import session
from app.core import config
from app import models

app = FastAPI(title="Wambaza Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in config.settings.FRONTEND_URL.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def on_startup():
    # create tables if not exists (for development)
    models.Base.metadata.create_all(bind=session.engine)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(model.router)
