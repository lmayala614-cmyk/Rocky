import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Load credentials from .env file
load_dotenv()

# Connect to Spotify
# The "scope" tells Spotify what permissions Rocky needs
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
))

# Get what's currently playing
current = sp.current_playback()

if current and current["is_playing"]:
    track = current["item"]
    print(f"Now playing: {track['name']}")
    print(f"Artist: {track['artists'][0]['name']}")
    print(f"Album: {track['album']['name']}")
    print(f"Progress: {current['progress_ms'] // 1000}s")
else:
    print("Nothing playing right now.")
    print("Start a song in Spotify on any device, then run this again.")