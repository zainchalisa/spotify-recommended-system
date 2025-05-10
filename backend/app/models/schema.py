
from pydantic import BaseModel


class SongRequest(BaseModel):
    song_name: str
    artist_name: str

class Playlist(BaseModel):
    id: str
    name: str
    privacy: str

class Track(BaseModel):
    id: str
    name: str
    artist_name: str

class SentimentResponse(BaseModel):
    song: str
    label: str
    score: float

class AudioFeaturesResponse(BaseModel):
    key: int
    tempo: float
    chroma: list
    mfcc: list
    spectral_centroid: list
    spectral_bandwidth: list
    spectral_contrast: list