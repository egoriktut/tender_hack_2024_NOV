import multiprocessing

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import endpoints

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
multiprocessing.set_start_method('spawn')

app.include_router(endpoints.router)
