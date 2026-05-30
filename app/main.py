from fastapi import FastAPI
from app.api import methods

app = FastAPI()
app.include_router(methods.router)