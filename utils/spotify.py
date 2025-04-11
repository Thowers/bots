import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"), 
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_tracks_by_artist(artist):
    results = sp.search(q=f"{artist}", type="track", limit=5)
    tracks = []
    for item in results["tracks"]["items"]:
        track_name = item["name"]
        artist_name = item["artists"][0]["name"]
        tracks.append({"name": track_name, "artist": artist_name})
    return tracks