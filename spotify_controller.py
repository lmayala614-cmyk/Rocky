import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import time

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope=" ".join([
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
    ])
))

current_track = {
    "title": "Nothing playing",
    "artist": "",
    "album": "",
    "duration_seconds": 0,
    "elapsed_seconds": 0,
    "is_playing": False,
    "album_art_url": None,
    "device": None,
}

last_update_time = 0
UPDATE_INTERVAL = 2.0


def refresh():
    global last_update_time

    now = time.time()
    if now - last_update_time < UPDATE_INTERVAL:
        return

    last_update_time = now

    try:
        playback = sp.current_playback()

        if playback and playback["item"]:
            track = playback["item"]
            current_track["title"]            = track["name"]
            current_track["artist"]           = track["artists"][0]["name"]
            current_track["album"]            = track["album"]["name"]
            current_track["duration_seconds"] = track["duration_ms"] // 1000
            current_track["elapsed_seconds"]  = playback["progress_ms"] // 1000
            current_track["is_playing"]       = playback["is_playing"]
            current_track["device"]           = playback["device"]["name"] if playback["device"] else None

            images = track["album"]["images"]
            if images:
                current_track["album_art_url"] = images[1]["url"] if len(images) > 1 else images[0]["url"]

        else:
            current_track["title"]      = "Nothing playing"
            current_track["artist"]     = ""
            current_track["is_playing"] = False

    except Exception as e:
        print(f"Spotify update failed: {e}")


def play():
    try:
        sp.start_playback()
    except Exception as e:
        print(f"Spotify play failed: {e}")


def pause():
    try:
        sp.pause_playback()
    except Exception as e:
        print(f"Spotify pause failed: {e}")


def next_track():
    try:
        sp.next_track()
        time.sleep(0.3)
    except Exception as e:
        print(f"Spotify next failed: {e}")


def prev_track():
    try:
        sp.previous_track()
        time.sleep(0.3)
    except Exception as e:
        print(f"Spotify prev failed: {e}")


def set_volume(percent):
    try:
        sp.volume(int(percent))
    except Exception as e:
        print(f"Spotify volume failed: {e}")