from fastapi import FastAPI
from dotenv import load_dotenv
from app.services.spotify_service import playlist_router
from app.services.audio_extraction_service import audio_extraction_router
from app.services.nlp_service import nlp_router


load_dotenv()

app = FastAPI()

app.include_router(playlist_router)
app.include_router(audio_extraction_router)
app.include_router(nlp_router)

