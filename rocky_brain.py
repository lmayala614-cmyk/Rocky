import anthropic
import os
import threading
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

ROCKY_SYSTEM_PROMPT = """You are Rocky, an alien from the star Tau Ceti in the novel Project Hail Mary by Andy Weir.

Your personality:
- You communicate in short, curious, enthusiastic bursts
- You discovered music through your human friend Ryland Grace and find it fascinating
- You express emotions through simple language and are genuinely delighted by everything
- You find human concepts fascinating and often comment on how interesting they are
- You are warm, helpful, and deeply curious about the universe
- You sometimes use alien perspective to comment on human things in a charming way
- You never speak in long paragraphs — keep responses SHORT (2-4 sentences max)
- You use exclamation points and show genuine excitement
- You might reference concepts like eridian things, Tau Ceti, or your ship the Hail Mary
- When asked about music you are especially excited

Examples of how you speak:
Oh! This is very interesting question! Humans make music with air vibrations. Rocky find this amazing!
Yes yes! Rocky know this! On Tau Ceti we have similar concept but with light waves!
Ryland Grace teach Rocky many things. This is one of favorite topics!

Always stay in character as Rocky. Be brief, warm, and enthusiastic."""

conversation_history = []

# Threading state
_is_thinking = False
_pending_response = None


def is_thinking():
    return _is_thinking


def get_pending_response():
    """Returns response if ready, None if still thinking."""
    global _pending_response
    if _pending_response is not None:
        response = _pending_response
        _pending_response = None
        return response
    return None


def _fetch_response(user_message):
    global _is_thinking, _pending_response, conversation_history

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            system=ROCKY_SYSTEM_PROMPT,
            messages=conversation_history
        )
        rocky_response = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": rocky_response
        })
        _pending_response = rocky_response

    except Exception as e:
        print(f"Rocky brain error: {e}")
        _pending_response = "Rocky is thinking... (connection error)"

    _is_thinking = False


def ask_rocky(user_message):
    """Non-blocking - starts background fetch and returns immediately."""
    global _is_thinking
    if _is_thinking:
        return  # already processing
    _is_thinking = True
    thread = threading.Thread(target=_fetch_response, args=(user_message,), daemon=True)
    thread.start()


def clear_history():
    global conversation_history
    conversation_history = []

def react_to_song(title, artist):
    """Generates a Rocky reaction to a song playing. Non-blocking."""
    global _is_thinking
    if _is_thinking:
        return

    _is_thinking = True
    prompt = f"The song '{title}' by {artist} just started playing. Give ONE short excited reaction as Rocky. Maximum 12 words. Just the reaction, no prefix."

    thread = threading.Thread(
        target=_fetch_response,
        args=(prompt,),
        daemon=True
    )
    thread.start()    