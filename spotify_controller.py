import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import time
import requests
from PIL import Image
import io
import pygame

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope=" ".join([
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "playlist-read-private",
        "playlist-read-collaborative",
    ]),
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

# Cache so we don't re-download the same album art every frame
_last_art_url = None
_cached_art_surface = None

last_update_time = 0
UPDATE_INTERVAL = 2.0
_last_elapsed_at_refresh = 0
_last_refresh_wall_time = None


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
            _last_elapsed_at_refresh = current_track["elapsed_seconds"]
            _last_refresh_wall_time = time.time()
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

def get_album_art(size=(180, 180)):
    """
    Downloads album art and returns a pygame Surface.
    Caches it so we only download when the song changes.
    Returns None if no art is available.
    """
    global _last_art_url, _cached_art_surface

    url = current_track["album_art_url"]

    if not url:
        return None

    # If the URL hasn't changed, return the cached version
    if url == _last_art_url and _cached_art_surface is not None:
        return _cached_art_surface

    try:
        # Download the image bytes from Spotify's CDN
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        # Convert bytes → PIL Image → resize → pygame Surface
        image = Image.open(io.BytesIO(response.content))
        image = image.resize(size, Image.LANCZOS)
        image = image.convert("RGB")

        # PIL uses (R,G,B) strings, pygame needs a specific format
        raw = image.tobytes()
        surface = pygame.image.fromstring(raw, size, "RGB")

        # Cache it
        _last_art_url = url
        _cached_art_surface = surface

        return surface

    except Exception as e:
        print(f"Album art fetch failed: {e}")
        return None    


def get_playlists():
    """Returns list of user's playlists as simple dicts."""
    try:
        results = sp.current_user_playlists(limit=20)
        playlists = []
        for item in results["items"]:
            if item:
                playlists.append({
                    "name": item["name"],
                    "id": item["id"],
                })
        return playlists
    except Exception as e:
        print(f"Get playlists failed: {e}")
        return []


def get_playlist_tracks(playlist_id):
    """Returns list of tracks in a playlist as simple dicts."""
    try:
        results = sp.playlist_items(
            playlist_id,
            limit=50,
            additional_types=["track"]
        )
        tracks = []
        for item in results["items"]:
            if not item:
                continue
            # Spotify API now uses "item" key instead of "track"
            track = item.get("track") or item.get("item")
            if not track:
                continue
            if track.get("type") != "track":
                continue
            artists = track.get("artists", [])
            tracks.append({
                "name": track.get("name", "Unknown"),
                "artist": artists[0]["name"] if artists else "Unknown",
                "uri": track.get("uri", ""),
                "duration_seconds": track.get("duration_ms", 0) // 1000,
            })
        return tracks
    except Exception as e:
        print(f"Get playlist tracks failed: {e}")
        return [{"name": "Cannot read this playlist", "artist": "Create your own playlist in Spotify", "uri": "", "duration_seconds": 0}]


def play_track(track_uri):
    """Plays a specific track by URI."""
    try:
        sp.start_playback(uris=[track_uri])
    except Exception as e:
        print(f"Play track failed: {e}")


def play_playlist(playlist_id):
    """Plays an entire playlist."""
    try:
        sp.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
    except Exception as e:
        print(f"Play playlist failed: {e}")    

def get_interpolated_elapsed():
    if not current_track["is_playing"]:
        return current_track["elapsed_seconds"]
    if _last_refresh_wall_time is None:
        return current_track["elapsed_seconds"]
    seconds_since_refresh = time.time() - _last_refresh_wall_time
    # Cap at 2.5 seconds so we never drift too far from Spotify's truth
    seconds_since_refresh = min(seconds_since_refresh, 2.5)
    return _last_elapsed_at_refresh + seconds_since_refresh     

def get_dominant_color():
    """
    Extract the dominant color from the current album art.
    Returns an (r, g, b) tuple or None if no art available.
    """
    if _cached_art_surface is None:
        return None

    try:
        # Sample a grid of pixels from the art surface
        surf = _cached_art_surface
        w, h = surf.get_size()
        samples = []

        for x in range(0, w, 8):
            for y in range(0, h, 8):
                color = surf.get_at((x, y))[:3]
                # Skip very dark or very bright pixels
                brightness = sum(color) / 3
                if 30 < brightness < 220:
                    samples.append(color)

        if not samples:
            return None

        # Average the samples
        r = int(sum(c[0] for c in samples) / len(samples))
        g = int(sum(c[1] for c in samples) / len(samples))
        b = int(sum(c[2] for c in samples) / len(samples))

        # Boost saturation so it looks vivid not muddy
        import colorsys
        h_val, s_val, v_val = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        s_val = min(1.0, s_val * 1.8)
        v_val = min(1.0, v_val * 1.3)
        r, g, b = colorsys.hsv_to_rgb(h_val, s_val, v_val)
        return (int(r*255), int(g*255), int(b*255))

    except Exception as e:
        print(f"Color extract failed: {e}")
        return None