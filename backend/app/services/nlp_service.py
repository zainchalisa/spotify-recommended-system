from app.models.schema import SongRequest
from fastapi import APIRouter
from transformers import pipeline, AutoTokenizer
import lyricsgenius
import os

nlp_router = APIRouter(tags = ["NLP Service"])


def get_lyrics_sentiment(song_name: str, artist_name: str):
    genius = lyricsgenius.Genius(os.getenv("genius_client_token"))
    song = genius.search_song(song_name, artist_name)
    
    if not song:
        return "song not found"
    

    lyrics = song.lyrics

    # Loading the sentiment classifier pipeline
    classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment", truncation=True, max_length=512)
    sentiment = classifier(lyrics)


    response = {}
    for vals in sentiment:
        if vals['label'] == 'LABEL_2':
            label = 'positive'
        elif vals['label'] == 'LABEL_1':
            label = 'neutral'
        elif vals['label'] == 'LABEL_0':
            label = 'negative'

        response[f'{song_name} - {artist_name}'] = {
            'label': label,
            'score': vals['score']
        }


    return response

@nlp_router.post("/lyrics-sentiment")
def lyrics_sentiment(song : SongRequest):
    sentiment = get_lyrics_sentiment(song.song_name, song.artist_name)
    return {"sentiment": sentiment}


