import spotipy
from spotipy import SpotifyOAuth
import os
from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import requests

load_dotenv()

user_tokens= {}
playlist_router = APIRouter(tags=["Spotify"])

spotify_auth = SpotifyOAuth(
    client_id= os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    redirect_uri=os.getenv("redirect_uri"),
    scope='user-read-private user-read-email user-top-read')

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


@playlist_router.get("/playlists")
def get_playlists():

    sp, _ = get_client()
    
    playlists = sp.current_user_playlists()
    response = {}
    for items in playlists['items']:
        playlist_id = items['id']
        playlist_name = items['name']
        playlist_security = items['public']

        response[playlist_id] = {
            'name': playlist_name,
            'privacy': 'public' if playlist_security else 'private'
        }

    return {'playlists': response}

@playlist_router.get("/playlist/{playlist_id}")
def get_playlist_info(playlist_id: str):
    
    sp, _ = get_client()
    
    playlist_songs = sp.playlist_tracks(playlist_id)
    response = {}
    for items in playlist_songs['items']:
       track = items['track']
       
       track_id = track['id']
       track_name = track['name']
       track_artist = track['artists'][0]['name'] 

       response[track_id] = {
           'name': track_name,
           'artist_name': track_artist
       }


    return {'response': response}

@playlist_router.get("/user-top-tracks")
def get_users_top_tracks(time_range = 'short_term'):
    sp, _ = get_client()
    results = sp.current_user_top_tracks(time_range=time_range, limit=10)
    
    return {'top tracks': results}