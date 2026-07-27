import requests
import threading

BOARD_URL = "https://pi-notes-board.lovable.app"

ROCKY_CONFIRMATIONS = [
    "Got it! Rocky add to board. Very organized!",
    "Done! Rocky file this information. Humans love lists!",
    "Added! Rocky think calendars are fascinating human invention!",
    "Got it! Rocky put on board. Ryland Grace also make lists!",
    "Done! Rocky add. Organization is interesting human behavior!",
    "Added to board! Rocky find human scheduling very complex but interesting!",
    "Got it! Rocky note this. Time management — very human concept!",
]

def _post_item(content, item_type="note"):
    try:
        response = requests.post(
            f"{BOARD_URL}/api/pin",
            json={
                "content": content,
                "type": item_type,
                "source": "Rocky"
            },
            timeout=8
        )
        print(f"Board response: {response.status_code}")
        return response.status_code < 300
    except Exception as e:
        print(f"Board post failed: {e}")
        return False


def add_item(content, item_type="note"):
    """Non-blocking board post."""
    thread = threading.Thread(
        target=_post_item,
        args=(content, item_type),
        daemon=True
    )
    thread.start()


def get_confirmation():
    import random
    return random.choice(ROCKY_CONFIRMATIONS)