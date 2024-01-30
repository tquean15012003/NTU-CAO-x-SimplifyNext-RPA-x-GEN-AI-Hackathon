import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.entry.handler import router as entry_router

logging.basicConfig(level=logging.INFO, force=True)

app = FastAPI()


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emails = []

ROUTE_BASE = "/api/v1"
app.include_router(entry_router, prefix=f"{ROUTE_BASE}/entry")