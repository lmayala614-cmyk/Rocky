import requests
import threading
import os
from dotenv import load_dotenv
import random

load_dotenv()

BOARD_URL = "https://pi-notes-board.lovable.app"
API_KEY = os.getenv("BOARD_API_KEY")

ROCKY_CONFIRMATIONS = [
    "Got it! Rocky add to board. Very organized!",
    "Done! Rocky file this information. Humans love lists!",
    "Added! Rocky think calendars are fascinating human invention!",
    "Got it! Rocky put on board. Ryland Grace also make lists!",
    "Done! Rocky add. Organization is interesting human behavior!",
    "Added to board! Rocky find human scheduling very complex but interesting!",
    "Got it! Rocky note this. Time management — very human concept!",
]

def _post_item(content):
    try:
        response = requests.post(
            f"{BOARD_URL}/api/public/notes",
            headers={
                "content-type": "application/json",
                "x-api-key": API_KEY
            },
            json={"body": content},
            timeout=8
        )
        print(f"Board response: {response.status_code} {response.text[:100]}")
        return response.status_code < 300
    except Exception as e:
        print(f"Board post failed: {e}")
        return False

def add_item(content):
    thread = threading.Thread(target=_post_item, args=(content,), daemon=True)
    thread.start()

def get_confirmation():
    return random.choice(ROCKY_CONFIRMATIONS)