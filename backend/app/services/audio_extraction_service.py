import os
import librosa
import yt_dlp
import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from app.services.spotify_service import users_playlist
from app.models.schema import SongRequest
import subprocess


# i need to grab the stored tracks and artist details
# pass them to yt-dlp and get the audio file
# pass the audio file to librosa
# get the audio features
# save the audio features to dictionary

audio_extraction_router = APIRouter(tags = ["Audio Extraction"])

# 'audio_snippets' folder exists
def download_audio_snippet(song_name: str, artist_name: str):
    query = f"{song_name} {artist_name}"
    
    audio_snippets_folder = "./app/audio_snippets"
    if not os.path.exists(audio_snippets_folder):
        os.makedirs(audio_snippets_folder) 
    
    ydl_opts = {
        'format': 'bestaudio/best', 
        'outtmpl': os.path.join(audio_snippets_folder, '%(id)s.%(ext)s'), 
        'noplaylist': True,  
        'extractaudio': True, 
        'audio-quality': '192K', 
        'verbose': True, 
        'quiet': False, 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{query}", download=True)
            
            if 'entries' in info_dict:
                video_info = info_dict['entries'][0]
            else:
                video_info = info_dict
                
            audio_file_path = ydl.prepare_filename(video_info)
            print(f"Downloaded audio snippet: {audio_file_path}")
            
            if not os.path.exists(audio_file_path):
                video_id = video_info['id']
                for file in os.listdir(audio_snippets_folder):
                    if file.startswith(video_id):
                        audio_file_path = os.path.join(audio_snippets_folder, file)
                        break
            
            converted_file_path = os.path.join(audio_snippets_folder, f"{artist_name} - {song_name}.mp3")
            
            subprocess.run(['ffmpeg', '-i', audio_file_path, '-vn', '-ar', '44100', '-ac', '2', '-ab', '192k', converted_file_path])
            print(f"Converted audio to MP3: {converted_file_path}")
            
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
            
            return converted_file_path
    
    except Exception as e:
        print(f"Error downloading or converting the song: {str(e)}")
        return None

def extract_audio_features(file_path: str):
    
    y, sr = librosa.load(file_path, sr=None, duration=30) 
    
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key = np.argmax(np.mean(chroma, axis=1))  
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

    
    # need to convert elements before returning
    return {
        "key": int(key), 
        "tempo": float(tempo),
        "chroma": chroma.tolist(),
        "mfcc": mfcc.tolist(),
        "spectral_centroid": spectral_centroid.tolist(),
        "spectral_bandwidth": spectral_bandwidth.tolist(),
        "spectral_contrast": spectral_contrast.tolist()  
    }

@audio_extraction_router.post("/extract_features")
def extract_features(song_request: SongRequest):
    try:
        audio_file_path = download_audio_snippet(song_request.song_name, song_request.artist_name)
        
        features = extract_audio_features(audio_file_path)
        
        return {'features': features}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
