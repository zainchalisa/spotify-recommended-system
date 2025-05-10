from app.models.schema import SongRequest, SentimentResponse
from fastapi import APIRouter
from transformers import pipeline, AutoTokenizer
import lyricsgenius
import os

nlp_router = APIRouter(tags = ["NLP Service"])


def get_lyrics_sentiment(song: SongRequest) -> SentimentResponse:
    genius = lyricsgenius.Genius(os.getenv("genius_client_token"))
    song_data = genius.search_song(song.song_name, song.artist_name)
    
    if not song_data:
        raise ValueError("Song not found")
    
    lyrics = song_data.lyrics

    # Load the sentiment classifier pipeline
    classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment", truncation=True, max_length=512)
    sentiment = classifier(lyrics)[0]  # Get the first result

    # Map sentiment labels
    label_map = {
        "LABEL_2": "positive",
        "LABEL_1": "neutral",
        "LABEL_0": "negative"
    }
    label = label_map.get(sentiment["label"], "unknown")

    # Return a SentimentResponse object
    return SentimentResponse(
        song=f"{song.song_name} - {song.artist_name}",
        label=label,
        score=sentiment["score"]
    )

@nlp_router.post("/lyrics-sentiment")
def lyrics_sentiment(song : SongRequest):
    sentiment = get_lyrics_sentiment(song)
    return {"sentiment": sentiment}


