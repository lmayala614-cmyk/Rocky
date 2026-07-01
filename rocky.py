import pygame
import sys
from datetime import datetime

pygame.init()
pygame.mixer.init()

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

back_button = {"rect": pygame.Rect(20, 420, 100, 40)}

broadcast_button = pygame.Rect(40, 75, 720, 45)

play_button = pygame.Rect(370, 290, 60, 60)
prev_button = pygame.Rect(290, 305, 50, 50)
next_button = pygame.Rect(460, 305, 50, 50)
vol_down_button = pygame.Rect(160, 305, 50, 50)
vol_up_button   = pygame.Rect(590, 305, 50, 50)

songs = [
    {
        "title": "Test Song",
        "artist": "Your Artist",
        "album": "Your Album",
        "duration_seconds": 180,
        "file": "test.mp3",
    },
]

state = {
    "current_song_index": 0,
    "current_song": songs[0],
    "elapsed_seconds": 0.0,
    "is_playing": False,
    "volume": 0.8,
}

speakers = [
    {"name": "Living Room", "model": "JBL Charge 5", "connected": True,  "on": True},
    {"name": "Garage",      "model": "JBL Charge 5", "connected": True,  "on": True},
    {"name": "Backyard",    "model": "Acoon Pair",   "connected": True,  "on": False},
    {"name": "Desktop",     "model": "1 OontZ Angle 3",  "connected": True,  "on": True},
    {"name": "Kitchen",     "model": "Echo Dot",     "connected": False, "on": False},
]

speaker_card_rects = []


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def draw_back_button(y_position=420):
    btn = pygame.Rect(20, y_position, 100, 40)
    back_button["rect"] = btn
    pygame.draw.rect(screen, RAISED, btn, border_radius=8)
    pygame.draw.rect(screen, BORDER, btn, width=1, border_radius=8)
    label = font_small.render("< Back", True, TEXT_DIM)
    screen.blit(label, (btn.x + 20, btn.y + 12))


def draw_clock():
    now = datetime.now()
    time_string = now.strftime("%I:%M %p")
    if time_string.startswith("0"):
        time_string = time_string[1:]
    clock_label = font_small.render(time_string, True, TEXT_DIM)
    screen.blit(clock_label, (SCREEN_WIDTH - clock_label.get_width() - 20, 24))


def draw_rocky_says(emoji_text, comment, y_position=350):
    box_rect = pygame.Rect(40, y_position, 720, 60)
    pygame.draw.rect(screen, RAISED, box_rect, border_radius=10)
    pygame.draw.rect(screen, BORDER, box_rect, width=1, border_radius=10)
    header = font_tiny.render("ROCKY SAYS", True, ACCENT)
    screen.blit(header, (box_rect.x + 16, box_rect.y + 10))
    emoji_label = font_medium.render(emoji_text, True, TEXT_WHITE)
    screen.blit(emoji_label, (box_rect.x + 16, box_rect.y + 28))
    comment_label = font_small.render(comment, True, TEXT_DIM)
    screen.blit(comment_label, (box_rect.x + 140, box_rect.y + 33))


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

    draw_rocky_says("[ * w * ]", "  Hello! I am ready to help.", 350)
    draw_back_button(420)


def draw_music_screen():
    title = font_large.render("NOW PLAYING", True, ACCENT)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, BORDER, (0, 60), (SCREEN_WIDTH, 60), 1)

    art_rect = pygame.Rect(300, 70, 180, 140)
    pygame.draw.rect(screen, SURFACE, art_rect, border_radius=12)
    pygame.draw.rect(screen, BORDER, art_rect, width=1, border_radius=12)
    note_icon = font_large.render("note", True, TEXT_DIM)
    screen.blit(note_icon, (art_rect.centerx - note_icon.get_width() // 2,
                             art_rect.centery - note_icon.get_height() // 2))

    title_text = font_medium.render(state["current_song"]["title"], True, TEXT_WHITE)
    screen.blit(title_text, (400 - title_text.get_width() // 2, 220))

    artist_text = font_small.render(state["current_song"]["artist"], True, TEXT_DIM)
    screen.blit(artist_text, (400 - artist_text.get_width() // 2, 248))

    bar_x, bar_y, bar_width, bar_height = 250, 268, 300, 4
    pygame.draw.rect(screen, BORDER, (bar_x, bar_y, bar_width, bar_height), border_radius=2)
    progress = min(state["elapsed_seconds"] / state["current_song"]["duration_seconds"], 1.0)
    pygame.draw.rect(screen, ACCENT, (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=2)

    elapsed_label = font_tiny.render(format_time(state["elapsed_seconds"]), True, TEXT_DIM)
    screen.blit(elapsed_label, (bar_x, bar_y + 10))
    total_label = font_tiny.render(format_time(state["current_song"]["duration_seconds"]), True, TEXT_DIM)
    screen.blit(total_label, (bar_x + bar_width - total_label.get_width(), bar_y + 10))

    pygame.draw.rect(screen, RAISED, prev_button, border_radius=25)
    prev_label = font_medium.render("|<", True, TEXT_DIM)
    screen.blit(prev_label, (prev_button.centerx - prev_label.get_width() // 2,
                              prev_button.centery - prev_label.get_height() // 2))

    pygame.draw.circle(screen, ACCENT, play_button.center, 30)
    play_symbol = "||" if state["is_playing"] else ">"
    play_label = font_medium.render(play_symbol, True, BLACK)
    screen.blit(play_label, (play_button.centerx - play_label.get_width() // 2,
                              play_button.centery - play_label.get_height() // 2))

    pygame.draw.rect(screen, RAISED, next_button, border_radius=25)
    next_label = font_medium.render(">|", True, TEXT_DIM)
    screen.blit(next_label, (next_button.centerx - next_label.get_width() // 2,
                              next_button.centery - next_label.get_height() // 2))
    
    # Volume down button
    pygame.draw.rect(screen, RAISED, vol_down_button, border_radius=25)
    vd_label = font_medium.render("v-", True, TEXT_DIM)
    screen.blit(vd_label, (vol_down_button.centerx - vd_label.get_width() // 2,
                            vol_down_button.centery - vd_label.get_height() // 2))

    # Volume up button
    pygame.draw.rect(screen, RAISED, vol_up_button, border_radius=25)
    vu_label = font_medium.render("v+", True, TEXT_DIM)
    screen.blit(vu_label, (vol_up_button.centerx - vu_label.get_width() // 2,
                            vol_up_button.centery - vu_label.get_height() // 2))

    # Volume bar
    vol_bar_x, vol_bar_y, vol_bar_width, vol_bar_height = 150, 365, 500, 4
    pygame.draw.rect(screen, BORDER, (vol_bar_x, vol_bar_y, vol_bar_width, vol_bar_height), border_radius=2)
    filled = int(vol_bar_width * state["volume"])
    pygame.draw.rect(screen, ACCENT, (vol_bar_x, vol_bar_y, filled, vol_bar_height), border_radius=2)

    # Volume percentage label
    vol_pct = font_tiny.render(f"VOL  {int(state['volume'] * 100)}%", True, TEXT_DIM)
    screen.blit(vol_pct, (vol_bar_x + vol_bar_width // 2 - vol_pct.get_width() // 2, vol_bar_y + 10))

    if state["is_playing"]:
        draw_rocky_says("[ ~ ~ ~ ]", "  This song has good energy!", 350)
    else:
        draw_rocky_says("[ . _ . ]", "  Paused. Take your time, human.", 350)

    draw_back_button(425)


def draw_speakers_screen():
    global speaker_card_rects

    title = font_large.render("SPEAKERS", True, ACCENT)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, BORDER, (0, 60), (SCREEN_WIDTH, 60), 1)

    any_on = any(s["on"] for s in speakers if s["connected"])
    bc_color = ACCENT if any_on else MUTED
    pygame.draw.rect(screen, RAISED, broadcast_button, border_radius=10)
    pygame.draw.rect(screen, bc_color, broadcast_button, width=1, border_radius=10)
    bc_label = font_medium.render("Broadcast to All", True, TEXT_WHITE)
    screen.blit(bc_label, (broadcast_button.x + 20, broadcast_button.y + 12))
    connected_count = sum(1 for s in speakers if s["connected"] and s["on"])
    bc_count = font_small.render(f"{connected_count} active", True, TEXT_DIM)
    screen.blit(bc_count, (broadcast_button.right - 100, broadcast_button.y + 15))

    speaker_card_rects = []
    start_y = 140
    card_height = 48
    gap = 8

    for index, speaker in enumerate(speakers):
        card_y = start_y + index * (card_height + gap)
        card_rect = pygame.Rect(40, card_y, 720, card_height)
        speaker_card_rects.append({"rect": card_rect, "speaker": speaker})

        border_color = ACCENT if (speaker["connected"] and speaker["on"]) else BORDER
        pygame.draw.rect(screen, SURFACE, card_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, card_rect, width=1, border_radius=10)

        dot_color = ACCENT if (speaker["connected"] and speaker["on"]) else MUTED
        pygame.draw.circle(screen, dot_color, (card_rect.x + 25, card_rect.centery), 6)

        name_label = font_medium.render(speaker["name"], True, TEXT_WHITE)
        screen.blit(name_label, (card_rect.x + 45, card_rect.y + 8))

        model_text = speaker["model"] if speaker["connected"] else speaker["model"] + " - not connected"
        model_label = font_small.render(model_text, True, TEXT_DIM)
        screen.blit(model_label, (card_rect.x + 45, card_rect.y + 28))

        toggle_rect = pygame.Rect(card_rect.right - 70, card_rect.centery - 12, 50, 24)
        toggle_color = ACCENT if speaker["on"] else MUTED
        pygame.draw.rect(screen, toggle_color, toggle_rect, border_radius=12)
        circle_x = toggle_rect.right - 12 if speaker["on"] else toggle_rect.left + 12
        pygame.draw.circle(screen, BLACK, (circle_x, toggle_rect.centery), 9)

    rocky_box_y = start_y + len(speakers) * (card_height + gap) + 10

    if connected_count == 0:
        draw_rocky_says("[ - . - ]", "  No speakers active right now.", rocky_box_y)
    elif connected_count == 1:
        draw_rocky_says("[ o w o ]", "  One speaker playing. Cozy.", rocky_box_y)
    else:
        draw_rocky_says("[ ^ o ^ ]", f"  {connected_count} speakers active. Sound everywhere!", rocky_box_y)

    draw_back_button(rocky_box_y + 65)


def draw_chat_screen():
    title = font_large.render("TALK TO ROCKY", True, ACCENT)
    screen.blit(title, (20, 20))
    msg = font_medium.render("Rocky isn't listening yet.", True, TEXT_DIM)
    screen.blit(msg, (40, 120))
    draw_rocky_says("[ ? . ? ]", "  Say something! (coming soon)", 300)
    draw_back_button(380)


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
                        if button["goto"] == "music":
                            pygame.mixer.music.load(state["current_song"]["file"])
                            pygame.mixer.music.set_volume(state["volume"])
                            pygame.mixer.music.play()
                            state["is_playing"] = True
                            

            elif current_screen == "music":
                if back_button["rect"].collidepoint(mouse_pos):
                    pygame.mixer.music.stop()
                    state["is_playing"] = False
                    state["elapsed_seconds"] = 0
                    current_screen = "home"

                elif play_button.collidepoint(mouse_pos):
                    if state["is_playing"]:
                        pygame.mixer.music.pause()
                        state["is_playing"] = False
                    else:
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play()
                        else:
                            pygame.mixer.music.unpause()
                        state["is_playing"] = True

                elif next_button.collidepoint(mouse_pos):
                    state["current_song_index"] = (state["current_song_index"] + 1) % len(songs)
                    state["current_song"] = songs[state["current_song_index"]]
                    state["elapsed_seconds"] = 0
                    pygame.mixer.music.load(state["current_song"]["file"])
                    if state["is_playing"]:
                        pygame.mixer.music.play()

                elif prev_button.collidepoint(mouse_pos):
                    state["current_song_index"] = (state["current_song_index"] - 1) % len(songs)
                    state["current_song"] = songs[state["current_song_index"]]
                    state["elapsed_seconds"] = 0
                    pygame.mixer.music.load(state["current_song"]["file"])
                    if state["is_playing"]:
                        pygame.mixer.music.play()

                elif vol_down_button.collidepoint(mouse_pos):
                    state["volume"] = max(0.0, state["volume"] - 0.1)
                    pygame.mixer.music.set_volume(state["volume"])

                elif vol_up_button.collidepoint(mouse_pos):
                    state["volume"] = min(1.0, state["volume"] + 0.1)
                    pygame.mixer.music.set_volume(state["volume"])        

            elif current_screen == "speakers":
                if back_button["rect"].collidepoint(mouse_pos):
                    current_screen = "home"
                elif broadcast_button.collidepoint(mouse_pos):
                    any_on = any(s["on"] for s in speakers if s["connected"])
                    for s in speakers:
                        if s["connected"]:
                            s["on"] = not any_on
                else:
                    for entry in speaker_card_rects:
                        if entry["rect"].collidepoint(mouse_pos) and entry["speaker"]["connected"]:
                            entry["speaker"]["on"] = not entry["speaker"]["on"]

            else:
                if back_button["rect"].collidepoint(mouse_pos):
                    current_screen = "home"

    if current_screen == "music" and state["is_playing"]:
        state["elapsed_seconds"] += dt
        if state["elapsed_seconds"] >= state["current_song"]["duration_seconds"]:
            state["elapsed_seconds"] = 0
            state["current_song_index"] = (state["current_song_index"] + 1) % len(songs)
            state["current_song"] = songs[state["current_song_index"]]
            pygame.mixer.music.load(state["current_song"]["file"])
            pygame.mixer.music.play()

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