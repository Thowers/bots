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

def get_playlist_by_genre(genre):
    results = sp.search(q=f"{genre} playlist", type="playlist", limit=1)
    if results["playlists"]["items"]:
        return results["playlists"]["items"][0]["external_urls"]["spotify"]
    return None

def get_tracks_by_artist(artist):
    results = sp.search(q=f"{artist}", type="track", limit=5)
    tracks = [track["external_urls"]["spotify"] for track in results["tracks"]["items"]]
    return tracks