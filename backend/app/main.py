from fastapi import FastAPI
from dotenv import load_dotenv
from app.services.spotify import playlist_router


load_dotenv()

app = FastAPI()

app.include_router(playlist_router)

