import spotipy
from spotipy import SpotifyOAuth
import os
from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from app.models.schema import Playlist, Track
from typing import List

load_dotenv()

user_tokens= {}
users_playlist = {}

playlist_router = APIRouter(tags=["Spotify"])

spotify_auth = SpotifyOAuth(
    client_id= os.getenv("spotify_client_id"),
    client_secret=os.getenv("spotify_client_secret"),
    redirect_uri=os.getenv("redirect_uri"),
    scope='user-read-private user-read-email user-top-read user-library-read user-follow-read user-read-recently-played')

@playlist_router.get("/login")
def login():
    auth_url = spotify_auth.get_authorize_url()
    return RedirectResponse(auth_url)

@playlist_router.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    token_info = spotify_auth.get_access_token(code, as_dict=True)

    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")

    # Save access token in a simple way for now
    user_tokens["access_token"] = access_token
    user_tokens["refresh_token"] = refresh_token

    sp = spotipy.Spotify(auth=access_token)

    user = sp.current_user()
    return {"message": "Login successful!", "username": user["display_name"]}

def get_client():
    access_token = user_tokens.get("access_token")
    refresh_token = user_tokens.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="User not authenticated.")

    sp = spotipy.Spotify(auth=access_token)
    return sp, access_token


@playlist_router.get("/playlists", response_model=List[Playlist])
def get_playlists():
    sp, _ = get_client()
    playlists = sp.current_user_playlists()
    
    # Build a list of Playlist objects
    response = [
        Playlist(
            id=items['id'],
            name=items['name'],
            privacy='public' if items['public'] else 'private'
        )
        for items in playlists['items']
    ]

    return response

@playlist_router.get("/playlist/{playlist_id}", response_model=List[Track])
def get_playlist_info(playlist_id: str):
    sp, _ = get_client()
    playlist_songs = sp.playlist_tracks(playlist_id)
    
    # Build a list of Track objects
    response = [
        Track(
            id=track['id'],
            name=track['name'],
            artist_name=track['artists'][0]['name']
        )
        for track in [item['track'] for item in playlist_songs['items']]
    ]

    return response

@playlist_router.get("/user-top-tracks")
def get_users_top_tracks(time_range: str = 'short_term'):
    sp, _ = get_client()
    results = sp.current_user_top_tracks(time_range=time_range, limit=10)

    # Extract only the required fields
    top_tracks = [
        {
            "id": track["id"],
            "track_name": track["name"],
            "artist_name": track["artists"][0]["name"],
            "popularity": track["popularity"],
            "duration_ms": track["duration_ms"],
            "explicit": track["explicit"],
            "preview_url": track["preview_url"]
            }
        for track in results["items"]
    ]


    return {"top_tracks": top_tracks}

@playlist_router.get("/user-top-artists")
def get_users_top_artists(time_range: str = 'short_term'):
    sp, _ = get_client()
    results = sp.current_user_top_artists(time_range=time_range, limit=10)

    # Extract only the required fields
    top_artists = [
        {
            "id": artist["id"],
            "artist_name": artist["name"],
            "genres": artist["genres"],
            "popularity": artist["popularity"]
        }
        for artist in results["items"]
    ]

    return {"top_artists": top_artists}

@playlist_router.get("/user-saved-tracks")
def get_users_saved_tracks():
    sp, _ = get_client()
    results = sp.current_user_saved_tracks(limit=10)

    saved_tracks = [
        {
            "track_name": track["track"]["name"],
            "artist_name": track["track"]["artists"][0]["name"]
        }
        for track in results["items"]
    ]
    
    return {'saved tracks': saved_tracks}
@playlist_router.get("/user-following")
def get_users_following():
    sp, _ = get_client()
    results = sp.current_user_followed_artists(limit=10)

    # Extract only the required fields
    following_artists = [
        {
            "artist_name": artist["name"],
            "genres": artist["genres"],
            "popularity": artist["popularity"]
        }
        for artist in results["artists"]["items"]
    ]

    return {'following': following_artists}

@playlist_router.get("/user-recently-played")
def get_users_recently_played():
    sp, _ = get_client()
    results = sp.current_user_recently_played(limit=15)

    user_recently_played = [
        {
            "track_name": item["track"]["name"],
            "artist_name": item["track"]["artists"][0]["name"],
            "played_at": item["played_at"]
        }
        for item in results["items"]
    ]
    
    return {'recently played': user_recently_played}

@playlist_router.get("/track-info/{track_id}")
def get_track_info(track_id: str):
    sp, _ = get_client()
    results = sp.track(track_id)

    track_info = [
        {
            "track_name": results["name"],
            "artist_name": results["artists"][0]["name"],
            "album_name": results["album"]["name"],
            "release_date": results["album"]["release_date"],
            "popularity": results["popularity"],
            "duration_ms": results["duration_ms"],
            "explicit": results["explicit"]
        }
    ]
    
    return {'track info': track_info}

@playlist_router.get('/artists-info/{artist_id}')
def get_artists_genre(artist_id: str):
    sp, _ = get_client()
    results = sp.artist(artist_id)

    artist_genre = [
        {
            "artist_name": results["name"],
            "genres": results["genres"],
            "popularity": results["popularity"]
        }
    ]
    
    return {'artist genre': artist_genre}