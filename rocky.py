import pygame
import sys
from datetime import datetime

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

BLACK      = (10,  13,  20)
SURFACE    = (17,  21,  32)
RAISED     = (24,  30,  46)
BORDER     = (31,  42,  64)
ACCENT     = (0,   212, 255)
PURPLE     = (124, 58,  237)
GREEN      = (0,   230, 118)
TEXT_WHITE = (232, 237, 245)
TEXT_DIM   = (136, 150, 170)
MUTED      = (74,  85,  104)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rocky")

font_large  = pygame.font.SysFont("monospace", 28, bold=True)
font_medium = pygame.font.SysFont("monospace", 18)
font_small  = pygame.font.SysFont("monospace", 12)
font_tiny   = pygame.font.SysFont("monospace", 10)

current_screen = "home"

home_buttons = [
    {"rect": pygame.Rect(40, 120, 720, 50), "label": "Music Player",  "goto": "music"},
    {"rect": pygame.Rect(40, 185, 720, 50), "label": "Speakers",      "goto": "speakers"},
    {"rect": pygame.Rect(40, 250, 720, 50), "label": "Talk to Rocky", "goto": "chat"},
]

back_button = pygame.Rect(20, 420, 100, 40)

current_song = {
    "title": "Mr. Brightside",
    "artist": "The Killers",
    "album": "Hot Fuss",
    "duration_seconds": 222,
}

elapsed_seconds = 0.0
is_playing = True

play_button = pygame.Rect(370, 350, 60, 60)
prev_button = pygame.Rect(290, 365, 50, 50)
next_button = pygame.Rect(460, 365, 50, 50)

# ---- FAKE SPEAKER DATA ----
# A list of dictionaries - one dictionary per speaker.
# "connected" means Rocky can actually reach it. "on" means it's playing right now.
speakers = [
    {"name": "Living Room", "model": "JBL Charge 5",  "connected": True,  "on": True},
    {"name": "Garage",      "model": "JBL Charge 5",  "connected": True,  "on": True},
    {"name": "Backyard",    "model": "Acoon Pair",    "connected": True,  "on": False},
    {"name": "Kitchen",     "model": "Echo Dot",      "connected": False, "on": False},
]

# We'll calculate each speaker card's rectangle on the fly when drawing,
# but we also need a matching list of rects to check clicks against.
# This list gets filled in every time we draw the speaker screen.
speaker_card_rects = []
broadcast_button = pygame.Rect(40, 90, 720, 50)


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def draw_home():
    title = font_large.render("ROCKY", True, ACCENT)
    screen.blit(title, (20, 20))
    status = font_small.render("online . ready", True, TEXT_DIM)
    screen.blit(status, (22, 56))
    pygame.draw.line(screen, BORDER, (0, 75), (SCREEN_WIDTH, 75), 1)

    for button in home_buttons:
        pygame.draw.rect(screen, RAISED, button["rect"], border_radius=10)
        pygame.draw.rect(screen, BORDER, button["rect"], width=1, border_radius=10)
        label = font_medium.render(button["label"], True, TEXT_WHITE)
        text_y = button["rect"].y + (button["rect"].height - label.get_height()) // 2
        screen.blit(label, (button["rect"].x + 20, text_y))


def draw_music_screen():
    title = font_large.render("NOW PLAYING", True, ACCENT)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, BORDER, (0, 60), (SCREEN_WIDTH, 60), 1)

    art_rect = pygame.Rect(300, 80, 200, 200)
    pygame.draw.rect(screen, SURFACE, art_rect, border_radius=12)
    pygame.draw.rect(screen, BORDER, art_rect, width=1, border_radius=12)
    note_icon = font_large.render("note", True, TEXT_DIM)
    icon_x = art_rect.centerx - note_icon.get_width() // 2
    icon_y = art_rect.centery - note_icon.get_height() // 2
    screen.blit(note_icon, (icon_x, icon_y))

    title_text = font_medium.render(current_song["title"], True, TEXT_WHITE)
    screen.blit(title_text, (400 - title_text.get_width() // 2, 295))

    artist_text = font_small.render(current_song["artist"], True, TEXT_DIM)
    screen.blit(artist_text, (400 - artist_text.get_width() // 2, 320))

    bar_x, bar_y, bar_width, bar_height = 250, 250, 300, 4
    pygame.draw.rect(screen, BORDER, (bar_x, bar_y, bar_width, bar_height), border_radius=2)

    progress = elapsed_seconds / current_song["duration_seconds"]
    progress = min(progress, 1.0)
    filled_width = int(bar_width * progress)
    pygame.draw.rect(screen, ACCENT, (bar_x, bar_y, filled_width, bar_height), border_radius=2)

    elapsed_label = font_tiny.render(format_time(elapsed_seconds), True, TEXT_DIM)
    screen.blit(elapsed_label, (bar_x, bar_y + 10))

    total_label = font_tiny.render(format_time(current_song["duration_seconds"]), True, TEXT_DIM)
    screen.blit(total_label, (bar_x + bar_width - total_label.get_width(), bar_y + 10))

    pygame.draw.rect(screen, RAISED, prev_button, border_radius=25)
    prev_label = font_medium.render("|<", True, TEXT_DIM)
    screen.blit(prev_label, (prev_button.centerx - prev_label.get_width() // 2,
                              prev_button.centery - prev_label.get_height() // 2))

    pygame.draw.circle(screen, ACCENT, play_button.center, 30)
    play_symbol = "||" if is_playing else ">"
    play_label = font_medium.render(play_symbol, True, BLACK)
    screen.blit(play_label, (play_button.centerx - play_label.get_width() // 2,
                              play_button.centery - play_label.get_height() // 2))

    pygame.draw.rect(screen, RAISED, next_button, border_radius=25)
    next_label = font_medium.render(">|", True, TEXT_DIM)
    screen.blit(next_label, (next_button.centerx - next_label.get_width() // 2,
                              next_button.centery - next_label.get_height() // 2))

    draw_back_button()


def draw_speakers_screen():
    global speaker_card_rects

    title = font_large.render("SPEAKERS", True, ACCENT)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, BORDER, (0, 60), (SCREEN_WIDTH, 60), 1)

    # --- Broadcast to all bar ---
    any_on = any(s["on"] for s in speakers if s["connected"])
    bc_color = ACCENT if any_on else MUTED
    pygame.draw.rect(screen, RAISED, broadcast_button, border_radius=10)
    pygame.draw.rect(screen, bc_color, broadcast_button, width=1, border_radius=10)
    bc_label = font_medium.render("Broadcast to All", True, TEXT_WHITE)
    screen.blit(bc_label, (broadcast_button.x + 20, broadcast_button.y + 14))

    connected_count = sum(1 for s in speakers if s["connected"] and s["on"])
    bc_count = font_small.render(f"{connected_count} active", True, TEXT_DIM)
    screen.blit(bc_count, (broadcast_button.right - 100, broadcast_button.y + 17))

    # --- Reset the list of clickable rects since we're rebuilding it this frame ---
    speaker_card_rects = []

    # --- Draw one card per speaker ---
    start_y = 160
    card_height = 60
    gap = 12

    for index, speaker in enumerate(speakers):
        card_y = start_y + index * (card_height + gap)
        card_rect = pygame.Rect(40, card_y, 720, card_height)

        # Remember this rect along with which speaker it belongs to, for click detection later
        speaker_card_rects.append({"rect": card_rect, "speaker": speaker})

        # Card background changes based on state
        if not speaker["connected"]:
            border_color = BORDER
        elif speaker["on"]:
            border_color = ACCENT
        else:
            border_color = BORDER

        pygame.draw.rect(screen, SURFACE, card_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, card_rect, width=1, border_radius=10)

        # Status dot on the left
        dot_color = ACCENT if (speaker["connected"] and speaker["on"]) else MUTED
        pygame.draw.circle(screen, dot_color, (card_rect.x + 25, card_rect.centery), 6)

        # Name and model text
        name_label = font_medium.render(speaker["name"], True, TEXT_WHITE)
        screen.blit(name_label, (card_rect.x + 45, card_rect.y + 10))

        if speaker["connected"]:
            model_text = speaker["model"]
        else:
            model_text = speaker["model"] + " - not connected"
        model_label = font_small.render(model_text, True, TEXT_DIM)
        screen.blit(model_label, (card_rect.x + 45, card_rect.y + 33))

        # Toggle switch on the right
        toggle_rect = pygame.Rect(card_rect.right - 70, card_rect.centery - 12, 50, 24)
        toggle_color = ACCENT if speaker["on"] else MUTED
        pygame.draw.rect(screen, toggle_color, toggle_rect, border_radius=12)

        # The little circle inside the toggle - moves right when on, left when off
        if speaker["on"]:
            circle_x = toggle_rect.right - 12
        else:
            circle_x = toggle_rect.left + 12
        pygame.draw.circle(screen, BLACK, (circle_x, toggle_rect.centery), 9)

    draw_back_button()


def draw_chat_screen():
    title = font_large.render("TALK TO ROCKY", True, ACCENT)
    screen.blit(title, (20, 20))
    msg = font_medium.render("Rocky isn't listening yet.", True, TEXT_DIM)
    screen.blit(msg, (40, 120))
    draw_back_button()


def draw_back_button():
    pygame.draw.rect(screen, RAISED, back_button, border_radius=8)
    pygame.draw.rect(screen, BORDER, back_button, width=1, border_radius=8)
    label = font_small.render("< Back", True, TEXT_DIM)
    screen.blit(label, (back_button.x + 20, back_button.y + 12))

def draw_clock():
    now = datetime.now()  # grabs the current date and time
    time_string = now.strftime("%I:%M %p")  # formats it like "09:41 PM"
    
    # strip a leading zero if present, so "09:41 PM" becomes "9:41 PM"
    if time_string.startswith("0"):
        time_string = time_string[1:]

    clock_label = font_small.render(time_string, True, TEXT_DIM)
    # Position it in the top right corner, with a little padding from the edge
    screen.blit(clock_label, (SCREEN_WIDTH - clock_label.get_width() - 20, 24))


clock = pygame.time.Clock()

while True:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if current_screen == "home":
                for button in home_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        current_screen = button["goto"]

            elif current_screen == "music":
                if back_button.collidepoint(mouse_pos):
                    current_screen = "home"
                elif play_button.collidepoint(mouse_pos):
                    is_playing = not is_playing
                elif next_button.collidepoint(mouse_pos):
                    elapsed_seconds = 0
                elif prev_button.collidepoint(mouse_pos):
                    elapsed_seconds = 0

            elif current_screen == "speakers":
                if back_button.collidepoint(mouse_pos):
                    current_screen = "home"
                elif broadcast_button.collidepoint(mouse_pos):
                    # If any connected speaker is on, turn all off. Otherwise turn all on.
                    any_on = any(s["on"] for s in speakers if s["connected"])
                    for s in speakers:
                        if s["connected"]:
                            s["on"] = not any_on
                else:
                    # Check if a click landed on any individual speaker card
                    for entry in speaker_card_rects:
                        if entry["rect"].collidepoint(mouse_pos) and entry["speaker"]["connected"]:
                            entry["speaker"]["on"] = not entry["speaker"]["on"]

            else:
                if back_button.collidepoint(mouse_pos):
                    current_screen = "home"

    if current_screen == "music" and is_playing:
        elapsed_seconds += dt
        if elapsed_seconds >= current_song["duration_seconds"]:
            elapsed_seconds = 0

    screen.fill(BLACK)

    if current_screen == "home":
        draw_home()
    elif current_screen == "music":
        draw_music_screen()
    elif current_screen == "speakers":
        draw_speakers_screen()
    elif current_screen == "chat":
        draw_chat_screen()

    draw_clock()

    pygame.display.flip()