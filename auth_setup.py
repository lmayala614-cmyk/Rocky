from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# This forces spotipy to do the full auth flow
# and save the token to .cache
os.environ["SPOTIPY_CLIENT_ID"] = os.getenv("SPOTIFY_CLIENT_ID")
os.environ["SPOTIPY_CLIENT_SECRET"] = os.getenv("SPOTIFY_CLIENT_SECRET")
os.environ["SPOTIPY_REDIRECT_URI"] = os.getenv("SPOTIFY_REDIRECT_URI")

scope = " ".join([
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "playlist-read-private",
    "playlist-read-collaborative",
])

auth_manager = SpotifyOAuth(scope=scope)
sp = spotipy.Spotify(auth_manager=auth_manager)

# This triggers the auth flow
me = sp.me()
print(f"Logged in as: {me['display_name']}")
print("Auth successful! You can now run rocky.py")