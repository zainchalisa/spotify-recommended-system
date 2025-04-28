
from pydantic import BaseModel


class SongRequest(BaseModel):
    song_name: str
    artist_name: str