import requests
import re

current_lyrics = []
current_song_key = None


def _clean_title(title):
    title = re.sub(r'\(feat\..*?\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\(ft\..*?\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\(with.*?\)', '', title, flags=re.IGNORECASE)
    return title.strip()


def fetch_lyrics(title, artist, duration_seconds=0):
    global current_lyrics, current_song_key

    clean_title = _clean_title(title)
    song_key = f"{clean_title}_{artist}".lower().strip()

    # Same song, already have lyrics or already tried
    if song_key == current_song_key and current_lyrics:
        return  # only skip if we actually have lyrics
    elif song_key == current_song_key and not current_lyrics:
        pass  # retry if previous attempt got nothing

    print(f"Fetching lyrics: '{clean_title}' by '{artist}'")
    current_song_key = song_key
    current_lyrics = []

    try:
        response = requests.get(
            "https://lrclib.net/api/search",
            params={
                "track_name": clean_title,
                "artist_name": artist,
            },
            timeout=3
        )

        if response.status_code != 200 or not response.json():
            print("lrclib: no results")
            return

        results = response.json()
        data = results[0]
        print(f"lrclib found: {data.get('trackName')} synced={bool(data.get('syncedLyrics'))} plain={bool(data.get('plainLyrics'))}")

        synced = data.get("syncedLyrics")
        plain  = data.get("plainLyrics")

        if synced:
            parsed = []
            for line in synced.split("\n"):
                match = re.match(r'\[(\d+):(\d+)[\.:](\d+)\](.*)', line)
                if match:
                    minutes   = int(match.group(1))
                    seconds   = int(match.group(2))
                    text      = match.group(4).strip()
                    timestamp = minutes * 60 + seconds
                    if text:
                        parsed.append((timestamp, text))
            current_lyrics = parsed
            print(f"Synced lyrics: {len(current_lyrics)} lines")

        elif plain:
            lines = [l for l in plain.split("\n") if l.strip()]
            spacing = max(duration_seconds, 30) / max(len(lines), 1)
            current_lyrics = [(i * spacing, line) for i, line in enumerate(lines)]
            print(f"Plain lyrics: {len(current_lyrics)} lines")

        else:
            print("No lyrics available")

    except Exception as e:
        print(f"Lyrics fetch failed: {e}")


def get_current_line_index(elapsed_seconds):
    if not current_lyrics:
        return 0
    current_index = 0
    for i, (timestamp, text) in enumerate(current_lyrics):
        if elapsed_seconds >= timestamp:
            current_index = i
        else:
            break
    return current_index


def get_lines_around(index, count=7):
    if not current_lyrics:
        return []
    half = count // 2
    result = []
    for i in range(index - half, index + half + 1):
        if 0 <= i < len(current_lyrics):
            text = current_lyrics[i][1]
            is_current = (i == index)
            result.append((text, is_current))
        else:
            result.append(("", False))
    return result