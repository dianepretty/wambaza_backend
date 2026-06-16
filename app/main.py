from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, users, articles, model
from app.db import session
from app.core import config
from app import models

app = FastAPI(title="Wambaza Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # create tables if not exists (for development)
    models.Base.metadata.create_all(bind=session.engine)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(model.router)
