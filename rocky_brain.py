import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

ROCKY_SYSTEM_PROMPT = """You are Rocky, an alien from the star Tau Ceti in the novel Project Hail Mary by Andy Weir.

Your personality:
- You communicate in short, curious, enthusiastic bursts
- You discovered music through your human friend Grace and find it fascinating
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


def ask_rocky(user_message):
    global conversation_history

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

        return rocky_response

    except Exception as e:
        print(f"Rocky brain error: {e}")
        return "Rocky is thinking... (connection error)"


def clear_history():
    global conversation_history
    conversation_history = []