import pygame
import sys
from datetime import datetime
import spotify_controller as spotify
import lyrics_controller as lyrics
import rocky_brain
import home_controller as home

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

BLACK      = (12,  10,  18)
SURFACE    = (22,  18,  32)
RAISED     = (35,  28,  50)
BORDER     = (55,  42,  75)
ACCENT     = (180, 130, 255)   # soft purple instead of cold cyan
ACCENT2    = (255, 160, 100)   # warm orange accent
PURPLE     = (140, 80,  220)
GREEN      = (100, 220, 160)
TEXT_WHITE = (245, 240, 255)   # slightly warm white
TEXT_DIM   = (160, 145, 185)   # warm lavender dim
MUTED      = (90,  80,  110)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
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
    {"rect": pygame.Rect(40, 315, 720, 50), "label": "Playlists",     "goto": "playlists"},
]

back_button = {"rect": pygame.Rect(20, 420, 120, 40)}
broadcast_button = pygame.Rect(40, 75, 720, 45)
play_button     = pygame.Rect(375, 330, 55, 55)
prev_button     = pygame.Rect(295, 343, 50, 50)
next_button     = pygame.Rect(465, 343, 50, 50)
vol_down_button = pygame.Rect(170, 343, 50, 50)
vol_up_button   = pygame.Rect(590, 343, 50, 50)
lyrics_button = pygame.Rect(20, 68, 80, 26)
playlist_button = pygame.Rect(40, 310, 720, 50)

scroll_dragging = False
scroll_drag_start_y = 0
scroll_drag_start_offset = 0
ticker_x = SCREEN_WIDTH  # starts off right edge
ticker_speed = 1.5       # pixels per frame
button_pressed = None
button_press_timer = 0

state = {
    "current_song_index": 0,
    "elapsed_seconds": 0.0,
    "is_playing": False,
    "volume": 0.8,
    "speaker_scroll": 0,
    "show_lyrics": False,
    "playlists": [],
    "playlist_scroll": 0,
    "selected_playlist": None,
    "playlist_tracks": [],
    "playlists_loaded": False,
    "track_scroll": 0,
    "playlist_screen": "playlists",  # "playlists" or "tracks"
    "chat_messages": [],      # list of {"role": "user"/"rocky", "text": "..."}
    "chat_input": "",         # what the user is currently typing
    "chat_scroll": 0,         # scroll position for message history
    "last_reacted_song": "",
    "rocky_song_comment": "Hello! I am ready to help.",
    "rocky_song_face": "[ * w * ]",
    "home_page": 0,           # 0 = main menu, 1 = smart home
    "swipe_start_x": 0,       # where swipe started
    "swipe_active": False,
    "smarthome_devices": [
        {"name": "TV Lights", "device_key": "tv_lights", "on": False},
    ],        # currently swiping
}

speakers = [
    {"name": "Living Room", "model": "JBL Charge 5",  "connected": True,  "on": True},
    {"name": "Garage",      "model": "JBL Charge 5",  "connected": True,  "on": True},
    {"name": "Backyard",    "model": "Acoon Pair",     "connected": True,  "on": False},
    {"name": "Desktop",     "model": "OontZ Angle 3", "connected": True,  "on": True},
    {"name": "Kitchen",     "model": "Echo Dot",       "connected": False, "on": False},
]

speaker_card_rects = []


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def draw_clock():
    now = datetime.now()
    time_string = now.strftime("%I:%M %p")
    if time_string.startswith("0"):
        time_string = time_string[1:]
    clock_label = font_small.render(time_string, True, TEXT_DIM)
    screen.blit(clock_label, (SCREEN_WIDTH - clock_label.get_width() - 20, 24))


def draw_bottom_bar(face, comment):
    global ticker_x

    bottom_y = 425
    btn = pygame.Rect(20, bottom_y, 130, 40)
    back_button["rect"] = btn
    pygame.draw.rect(screen, RAISED, btn, border_radius=8)
    pygame.draw.rect(screen, BORDER, btn, width=1, border_radius=8)
    back_label = font_small.render("< Back", True, TEXT_DIM)
    screen.blit(back_label, (btn.x + 20, btn.y + 12))

    rocky_rect = pygame.Rect(170, bottom_y, 590, 40)
    pygame.draw.rect(screen, RAISED, rocky_rect, border_radius=8)
    pygame.draw.rect(screen, BORDER, rocky_rect, width=1, border_radius=8)
    header = font_tiny.render("ROCKY SAYS", True, ACCENT)
    screen.blit(header, (rocky_rect.x + 10, rocky_rect.y + 6))

    # Rocky face - fixed left
    face_label = font_small.render(face, True, TEXT_WHITE)
    screen.blit(face_label, (rocky_rect.x + 10, rocky_rect.y + 20))

    # Only scroll if text is too wide to fit, otherwise draw static
    comment_surface = font_small.render(comment, True, TEXT_DIM)
    comment_width = comment_surface.get_width()
    ticker_area = pygame.Rect(rocky_rect.x + 110, rocky_rect.y, rocky_rect.width - 115, 40)
    available_width = ticker_area.width

    if comment_width <= available_width:
        # Short text — just draw it static, no scrolling
        screen.blit(comment_surface, (ticker_area.x, rocky_rect.y + 20))
    else:
        # Long text — scroll it
        old_clip = screen.get_clip()
        screen.set_clip(ticker_area)
        screen.blit(comment_surface, (ticker_area.x + ticker_x, rocky_rect.y + 20))
        screen.set_clip(old_clip)
        ticker_x -= ticker_speed
        if ticker_x < -comment_width:
            ticker_x = available_width


def draw_home():
    # Header - same on all pages
    title = font_large.render("ROCKY", True, ACCENT)
    screen.blit(title, (20, 20))
    status = font_small.render("online . ready", True, TEXT_DIM)
    screen.blit(status, (title.get_width() + 28, 30))

    if spotify.current_track["title"] != "Nothing playing":
        now_label = font_tiny.render("NOW PLAYING", True, MUTED)
        screen.blit(now_label, (20, 68))
        song_text = f"{spotify.current_track['title']} - {spotify.current_track['artist']}"
        song_label = font_small.render(song_text, True, TEXT_DIM)
        if song_label.get_width() > SCREEN_WIDTH - 40:
            song_text = f"{spotify.current_track['title'][:20]}... - {spotify.current_track['artist']}"
            song_label = font_small.render(song_text, True, TEXT_DIM)
        screen.blit(song_label, (20, 82))

    pygame.draw.line(screen, BORDER, (0, 100), (SCREEN_WIDTH, 100), 1)

    if state["home_page"] == 0:
        draw_home_page_main()
    elif state["home_page"] == 1:
        draw_home_page_smarthome()

    # Page dots at bottom center
    total_pages = 2
    dot_y = 410
    dot_spacing = 20
    total_dot_width = (total_pages - 1) * dot_spacing
    dot_start_x = (SCREEN_WIDTH - total_dot_width) // 2

    for i in range(total_pages):
        dot_x = dot_start_x + i * dot_spacing
        color = ACCENT if i == state["home_page"] else MUTED
        radius = 5 if i == state["home_page"] else 3
        pygame.draw.circle(screen, color, (dot_x, dot_y), radius)

    draw_bottom_bar(
        state.get("rocky_song_face", "[ * w * ]"),
        state.get("rocky_song_comment", "Hello! I am ready to help.")
    )


def draw_home_page_main():
    buttons_y = [130, 195, 260, 325]
    btn_width = 500
    btn_x = (SCREEN_WIDTH - btn_width) // 2

    for i, button in enumerate(home_buttons):
        rect = pygame.Rect(btn_x, buttons_y[i], btn_width, 44)
        is_pressed = (button_pressed == i)
        bg_color = ACCENT if is_pressed else RAISED
        border_color = ACCENT if is_pressed else BORDER
        label_color = BLACK if is_pressed else TEXT_WHITE
        pygame.draw.rect(screen, bg_color, rect, border_radius=10)
        pygame.draw.rect(screen, border_color, rect, width=1, border_radius=10)
        label = font_medium.render(button["label"], True, label_color)
        text_x = rect.x + (rect.width - label.get_width()) // 2
        text_y = rect.y + (rect.height - label.get_height()) // 2
        screen.blit(label, (text_x, text_y))
        home_buttons[i]["rect"] = rect


def draw_home_page_smarthome():
    subtitle = font_small.render("SMART HOME", True, ACCENT)
    screen.blit(subtitle, (20, 110))

    card_height = 60
    gap = 10
    start_y = 135

    for index, device in enumerate(state["smarthome_devices"]):
        card_y = start_y + index * (card_height + gap)
        card_rect = pygame.Rect(40, card_y, 720, card_height)

        border_color = ACCENT if device["on"] else BORDER
        pygame.draw.rect(screen, SURFACE, card_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, card_rect, width=1, border_radius=10)

        dot_color = ACCENT if device["on"] else MUTED
        pygame.draw.circle(screen, dot_color, (card_rect.x + 28, card_rect.centery), 7)

        name_label = font_medium.render(device["name"], True, TEXT_WHITE)
        screen.blit(name_label, (card_rect.x + 50, card_rect.y + 10))

        status_label = font_small.render("ON" if device["on"] else "OFF",
                                          True, ACCENT if device["on"] else MUTED)
        screen.blit(status_label, (card_rect.x + 50, card_rect.y + 34))

        toggle_rect = pygame.Rect(card_rect.right - 75, card_rect.centery - 13, 55, 26)
        toggle_color = ACCENT if device["on"] else MUTED
        pygame.draw.rect(screen, toggle_color, toggle_rect, border_radius=13)
        circle_x = toggle_rect.right - 13 if device["on"] else toggle_rect.left + 13
        pygame.draw.circle(screen, BLACK, (circle_x, toggle_rect.centery), 10)


def draw_music_screen():
    title = font_large.render("NOW PLAYING", True, ACCENT)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, BORDER, (0, 60), (SCREEN_WIDTH, 60), 1)

    toggle_color = ACCENT if state["show_lyrics"] else RAISED
    pygame.draw.rect(screen, toggle_color, lyrics_button, border_radius=8)
    pygame.draw.rect(screen, BORDER, lyrics_button, width=1, border_radius=8)
    toggle_label = font_small.render("ART" if state["show_lyrics"] else "LYRICS", True, TEXT_WHITE)
    screen.blit(toggle_label, (lyrics_button.centerx - toggle_label.get_width() // 2,
                                lyrics_button.centery - toggle_label.get_height() // 2))

    if state["show_lyrics"]:
        elapsed = spotify.get_interpolated_elapsed()
        current_index = lyrics.get_current_line_index(elapsed)
        lines = lyrics.get_lines_around(current_index, count=7)

        if not lyrics.current_lyrics:
            no_lyrics = font_medium.render("No lyrics found for this song.", True, MUTED)
            screen.blit(no_lyrics, (400 - no_lyrics.get_width() // 2, 200))
        else:
            line_y = 75
            line_height = 36
            for text, is_current in lines:
                if not text:
                    line_y += line_height
                    continue
                if is_current:
                    color = TEXT_WHITE
                    font_use = font_medium
                else:
                    color = MUTED
                    font_use = font_small
                rendered = font_use.render(text, True, color)
                x = 400 - rendered.get_width() // 2
                screen.blit(rendered, (x, line_y))
                line_y += line_height

    else:
        art_rect = pygame.Rect(300, 70, 180, 180)
        pygame.draw.rect(screen, SURFACE, art_rect, border_radius=12)
        pygame.draw.rect(screen, BORDER, art_rect, width=1, border_radius=12)

        art_surface = spotify.get_album_art(size=(180, 180))
        if art_surface:
            # Create a rounded mask to clip the album art
            mask = pygame.Surface((180, 180), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, 180, 180), border_radius=16)

            # Apply mask — only keep pixels where mask is white
            rounded_art = art_surface.copy().convert_alpha()
            rounded_art.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            screen.blit(rounded_art, (art_rect.x, art_rect.y))
            pygame.draw.rect(screen, BORDER, art_rect, width=1, border_radius=16)
        else:
            note_icon = font_large.render("?", True, TEXT_DIM)
            screen.blit(note_icon, (art_rect.centerx - note_icon.get_width() // 2,
                                     art_rect.centery - note_icon.get_height() // 2))

        title_text = font_medium.render(spotify.current_track["title"], True, TEXT_WHITE)
        screen.blit(title_text, (400 - title_text.get_width() // 2, 260))

        artist_text = font_small.render(spotify.current_track["artist"], True, TEXT_DIM)
        screen.blit(artist_text, (400 - artist_text.get_width() // 2, 285))

    bar_x, bar_y, bar_width, bar_height = 150, 310, 500, 4
    pygame.draw.rect(screen, BORDER, (bar_x, bar_y, bar_width, bar_height), border_radius=2)
    duration = max(spotify.current_track["duration_seconds"], 1)
    elapsed = spotify.get_interpolated_elapsed()
    progress = min(elapsed / duration, 1.0)
    pygame.draw.rect(screen, ACCENT, (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=2)
    elapsed_label = font_tiny.render(format_time(int(spotify.get_interpolated_elapsed())), True, TEXT_DIM)    
    screen.blit(elapsed_label, (bar_x, bar_y + 10))
    total_label = font_tiny.render(format_time(spotify.current_track["duration_seconds"]), True, TEXT_DIM)
    screen.blit(total_label, (bar_x + bar_width - total_label.get_width(), bar_y + 10))

    pygame.draw.rect(screen, RAISED, prev_button, border_radius=25)
    prev_label = font_medium.render("|<", True, TEXT_DIM)
    screen.blit(prev_label, (prev_button.centerx - prev_label.get_width() // 2,
                              prev_button.centery - prev_label.get_height() // 2))

    pygame.draw.circle(screen, ACCENT, play_button.center, 30)
    play_symbol = "||" if spotify.current_track["is_playing"] else ">"
    play_label = font_medium.render(play_symbol, True, BLACK)
    screen.blit(play_label, (play_button.centerx - play_label.get_width() // 2,
                              play_button.centery - play_label.get_height() // 2))

    pygame.draw.rect(screen, RAISED, next_button, border_radius=25)
    next_label = font_medium.render(">|", True, TEXT_DIM)
    screen.blit(next_label, (next_button.centerx - next_label.get_width() // 2,
                              next_button.centery - next_label.get_height() // 2))

    pygame.draw.rect(screen, RAISED, vol_down_button, border_radius=25)
    vd_label = font_medium.render("v-", True, TEXT_DIM)
    screen.blit(vd_label, (vol_down_button.centerx - vd_label.get_width() // 2,
                            vol_down_button.centery - vd_label.get_height() // 2))

    pygame.draw.rect(screen, RAISED, vol_up_button, border_radius=25)
    vu_label = font_medium.render("v+", True, TEXT_DIM)
    screen.blit(vu_label, (vol_up_button.centerx - vu_label.get_width() // 2,
                            vol_up_button.centery - vu_label.get_height() // 2))

    vol_bar_x, vol_bar_y, vol_bar_width, vol_bar_height = 150, 400, 500, 4
    pygame.draw.rect(screen, BORDER, (vol_bar_x, vol_bar_y, vol_bar_width, vol_bar_height), border_radius=2)
    filled = int(vol_bar_width * state["volume"])
    pygame.draw.rect(screen, ACCENT, (vol_bar_x, vol_bar_y, filled, vol_bar_height), border_radius=2)
    vol_pct = font_tiny.render(f"VOL  {int(state['volume'] * 100)}%", True, TEXT_DIM)
    screen.blit(vol_pct, (vol_bar_x + vol_bar_width // 2 - vol_pct.get_width() // 2, vol_bar_y + 10))

    if spotify.current_track["is_playing"]:
        draw_bottom_bar(state["rocky_song_face"], state["rocky_song_comment"])
    else:
        draw_bottom_bar("[ . _ . ]", "Paused. Take your time, human.")


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
    card_height = 56
    gap = 10
    scroll_area_top = 130
    scroll_area_bottom = 370

    for index, speaker in enumerate(speakers):
        card_y = start_y + index * (card_height + gap) - state["speaker_scroll"]
        card_rect = pygame.Rect(40, card_y, 720, card_height)

        if card_y + card_height < scroll_area_top or card_y > scroll_area_bottom:
            speaker_card_rects.append({"rect": card_rect, "speaker": speaker})
            continue

        speaker_card_rects.append({"rect": card_rect, "speaker": speaker})

        border_color = ACCENT if (speaker["connected"] and speaker["on"]) else BORDER
        pygame.draw.rect(screen, SURFACE, card_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, card_rect, width=1, border_radius=10)

        dot_color = ACCENT if (speaker["connected"] and speaker["on"]) else MUTED
        pygame.draw.circle(screen, dot_color, (card_rect.x + 25, card_rect.centery), 6)

        name_label = font_medium.render(speaker["name"], True, TEXT_WHITE)
        screen.blit(name_label, (card_rect.x + 45, card_rect.y + 10))

        model_text = speaker["model"] if speaker["connected"] else speaker["model"] + " - not connected"
        model_label = font_small.render(model_text, True, TEXT_DIM)
        screen.blit(model_label, (card_rect.x + 45, card_rect.y + 32))

        toggle_rect = pygame.Rect(card_rect.right - 70, card_rect.centery - 12, 50, 24)
        toggle_color = ACCENT if speaker["on"] else MUTED
        pygame.draw.rect(screen, toggle_color, toggle_rect, border_radius=12)
        circle_x = toggle_rect.right - 12 if speaker["on"] else toggle_rect.left + 12
        pygame.draw.circle(screen, BLACK, (circle_x, toggle_rect.centery), 9)

    if connected_count == 0:
        draw_bottom_bar("[ - . - ]", "No speakers active right now.")
    elif connected_count == 1:
        draw_bottom_bar("[ o w o ]", "One speaker playing. Cozy.")
    else:
        draw_bottom_bar("[ ^ o ^ ]", f"{connected_count} speakers active. Sound everywhere!")


def draw_chat_screen():
    title = font_large.render("TALK TO ROCKY", True, ACCENT)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, BORDER, (0, 60), (SCREEN_WIDTH, 60), 1)

    # Message area - scrollable
    msg_area_top = 70
    msg_area_bottom = 370
    msg_y = msg_area_top - state["chat_scroll"]
    msg_height = 28

    for msg in state["chat_messages"]:
        if msg["role"] == "user":
            color = ACCENT
            prefix = "You: "
        else:
            color = TEXT_WHITE
            prefix = "Rocky: "

        # Word wrap long messages
        full_text = prefix + msg["text"]
        max_chars = 72
        words = full_text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += ("" if current_line == "" else " ") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for line in lines:
            if msg_area_top <= msg_y <= msg_area_bottom:
                rendered = font_small.render(line, True, color)
                screen.blit(rendered, (20, msg_y))
            msg_y += msg_height

        msg_y += 6  # gap between messages

    # Input box
    input_rect = pygame.Rect(20, 378, 580, 36)
    pygame.draw.rect(screen, SURFACE, input_rect, border_radius=8)
    pygame.draw.rect(screen, ACCENT, input_rect, width=1, border_radius=8)
    input_text = state["chat_input"] + "|"  # cursor
    input_rendered = font_small.render(input_text, True, TEXT_WHITE)
    screen.blit(input_rendered, (input_rect.x + 10, input_rect.y + 10))

    # Send button
    send_rect = pygame.Rect(612, 378, 148, 36)
    pygame.draw.rect(screen, ACCENT, send_rect, border_radius=8)
    send_label = font_small.render("Send", True, BLACK)
    screen.blit(send_label, (send_rect.centerx - send_label.get_width() // 2,
                              send_rect.centery - send_label.get_height() // 2))

    if rocky_brain.is_thinking():
        draw_bottom_bar("[ . . . ]", "Rocky is thinking...")
    elif not state["chat_messages"]:
        draw_bottom_bar("[ ? . ? ]", "Ask Rocky anything!")
    else:
        draw_bottom_bar("[ ^ w ^ ]", "Rocky is listening!")

def draw_playlists_screen():
    title = font_large.render("PLAYLISTS", True, ACCENT)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, BORDER, (0, 60), (SCREEN_WIDTH, 60), 1)

    if state["playlist_screen"] == "playlists":
        # Show list of playlists
        if not state["playlists"]:
            loading = font_medium.render("Loading playlists...", True, TEXT_DIM)
            screen.blit(loading, (400 - loading.get_width() // 2, 200))
        else:
            card_height = 56
            gap = 8
            start_y = 75
            scroll_area_bottom = 415

            for index, playlist in enumerate(state["playlists"]):
                card_y = start_y + index * (card_height + gap) - state["playlist_scroll"]
                card_rect = pygame.Rect(40, card_y, 720, card_height)

                if card_y + card_height < start_y or card_y > scroll_area_bottom:
                    continue

                pygame.draw.rect(screen, SURFACE, card_rect, border_radius=10)
                pygame.draw.rect(screen, BORDER, card_rect, width=1, border_radius=10)

                name_label = font_medium.render(playlist["name"], True, TEXT_WHITE)
                screen.blit(name_label, (card_rect.x + 20, card_rect.y + 10))

                count_label = font_small.render("tap to browse", True, TEXT_DIM)
                screen.blit(count_label, (card_rect.x + 20, card_rect.y + 32))

                # Play arrow on right
                arrow = font_medium.render(">", True, ACCENT)
                screen.blit(arrow, (card_rect.right - 40, card_rect.centery - arrow.get_height() // 2))

        draw_bottom_bar("[ * w * ]", "Pick a playlist to browse!")

    else:
        # Show tracks inside selected playlist
        playlist_name = state["selected_playlist"]["name"] if state["selected_playlist"] else ""
        subtitle = font_small.render(playlist_name, True, TEXT_DIM)
        screen.blit(subtitle, (20, 55))
        pygame.draw.line(screen, BORDER, (0, 75), (SCREEN_WIDTH, 75), 1)

        if not state["playlist_tracks"]:
            loading = font_medium.render("Loading tracks...", True, TEXT_DIM)
            screen.blit(loading, (400 - loading.get_width() // 2, 200))
        else:
            card_height = 52
            gap = 6
            start_y = 85
            scroll_area_bottom = 415

            for index, track in enumerate(state["playlist_tracks"]):
                card_y = start_y + index * (card_height + gap) - state["track_scroll"]
                card_rect = pygame.Rect(40, card_y, 720, card_height)

                if card_y + card_height < start_y or card_y > scroll_area_bottom:
                    continue

                pygame.draw.rect(screen, SURFACE, card_rect, border_radius=10)
                pygame.draw.rect(screen, BORDER, card_rect, width=1, border_radius=10)

                name_label = font_medium.render(track["name"], True, TEXT_WHITE)
                screen.blit(name_label, (card_rect.x + 20, card_rect.y + 8))

                artist_label = font_small.render(track["artist"], True, TEXT_DIM)
                screen.blit(artist_label, (card_rect.x + 20, card_rect.y + 30))

                duration_label = font_small.render(
                    format_time(track["duration_seconds"]), True, MUTED)
                screen.blit(duration_label, (card_rect.right - 70, card_rect.centery - 8))

        draw_bottom_bar("[ ^ ^ ^ ]", "Tap a song to play it!")


clock = pygame.time.Clock()

while True:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Swipe detection for home screen page switching
        if event.type == pygame.MOUSEBUTTONDOWN and current_screen == "home":
            state["swipe_start_x"] = event.pos[0]
            state["swipe_active"] = True

        if event.type == pygame.MOUSEBUTTONUP and current_screen == "home":
            if state["swipe_active"]:
                swipe_distance = event.pos[0] - state["swipe_start_x"]
                if swipe_distance < -80:  # swiped left
                    state["home_page"] = min(1, state["home_page"] + 1)
                elif swipe_distance > 80:  # swiped right
                    state["home_page"] = max(0, state["home_page"] - 1)
            state["swipe_active"] = False    

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if current_screen == "speakers":
                scroll_drag_start_y = event.pos[1]
                scroll_drag_start_offset = state["speaker_scroll"]

            if current_screen == "home":
                swipe_distance = abs(mouse_pos[0] - state["swipe_start_x"])

                if swipe_distance < 10:  # it's a tap not a swipe
                    if state["home_page"] == 0:
                        for i, button in enumerate(home_buttons):
                            if button["rect"].collidepoint(mouse_pos):
                                button_pressed = i
                                button_press_timer = 0.15
                                current_screen = button["goto"]
                                if button["goto"] == "playlists":
                                    state["playlists"] = []
                                    state["playlists_loaded"] = False
                                    state["playlist_scroll"] = 0
                                    state["playlist_screen"] = "playlists"
                                    state["playlist_tracks"] = []
                                    state["selected_playlist"] = None
                                    state["track_scroll"] = 0
                                if button["goto"] == "music":
                                    if not spotify.current_track["is_playing"]:
                                        spotify.play()

                    elif state["home_page"] == 1:
                        card_height = 60
                        gap = 10
                        start_y = 135
                        for index, device in enumerate(state["smarthome_devices"]):
                            card_y = start_y + index * (card_height + gap)
                            card_rect = pygame.Rect(40, card_y, 720, card_height)
                            if card_rect.collidepoint(mouse_pos):
                                home.toggle(device["device_key"])
                                device["on"] = not device["on"]
                                break

            elif current_screen == "music":
                if back_button["rect"].collidepoint(mouse_pos):
                    pygame.mixer.music.stop()
                    state["is_playing"] = False
                    state["elapsed_seconds"] = 0
                    current_screen = "home"
                elif play_button.collidepoint(mouse_pos):
                    if spotify.current_track["is_playing"]:
                        spotify.pause()
                    else:
                        spotify.play()
                elif next_button.collidepoint(mouse_pos):
                    spotify.next_track()
                elif prev_button.collidepoint(mouse_pos):
                    spotify.prev_track()
                elif vol_down_button.collidepoint(mouse_pos):
                    state["volume"] = max(0.0, state["volume"] - 0.1)
                    spotify.set_volume(int(state["volume"] * 100))
                elif vol_up_button.collidepoint(mouse_pos):
                    state["volume"] = min(1.0, state["volume"] + 0.1)
                    spotify.set_volume(int(state["volume"] * 100))
                elif lyrics_button.collidepoint(mouse_pos):
                    state["show_lyrics"] = not state["show_lyrics"]
                    if state["show_lyrics"]:
                        lyrics.current_song_key = None
                        lyrics.fetch_lyrics(
                            spotify.current_track["title"],
                            spotify.current_track["artist"],
                            spotify.current_track["duration_seconds"]
                        )

            elif current_screen == "speakers":
                if scroll_dragging:
                    pass
                elif back_button["rect"].collidepoint(mouse_pos):
                    current_screen = "home"
                    state["speaker_scroll"] = 0
                    scroll_dragging = False
                elif broadcast_button.collidepoint(mouse_pos):
                    any_on = any(s["on"] for s in speakers if s["connected"])
                    for s in speakers:
                        if s["connected"]:
                            s["on"] = not any_on
                else:
                    for entry in speaker_card_rects:
                        if entry["rect"].collidepoint(mouse_pos) and entry["speaker"]["connected"]:
                            entry["speaker"]["on"] = not entry["speaker"]["on"]

            elif current_screen == "playlists":
                if back_button["rect"].collidepoint(mouse_pos):
                    if state["playlist_screen"] == "tracks":
                        state["playlist_screen"] = "playlists"
                        state["track_scroll"] = 0
                    else:
                        current_screen = "home"
                else:
                    if state["playlist_screen"] == "playlists":
                        card_height = 56
                        gap = 8
                        start_y = 75
                        for index, playlist in enumerate(state["playlists"]):
                            card_y = start_y + index * (card_height + gap) - state["playlist_scroll"]
                            card_rect = pygame.Rect(40, card_y, 720, card_height)
                            if card_rect.collidepoint(mouse_pos):
                                state["selected_playlist"] = playlist
                                state["playlist_screen"] = "tracks"
                                state["track_scroll"] = 0
                                state["playlist_tracks"] = spotify.get_playlist_tracks(playlist["id"])
                                break
                    else:
                        card_height = 52
                        gap = 6
                        start_y = 85
                        for index, track in enumerate(state["playlist_tracks"]):
                            card_y = start_y + index * (card_height + gap) - state["track_scroll"]
                            card_rect = pygame.Rect(40, card_y, 720, card_height)
                            if card_rect.collidepoint(mouse_pos):
                                if track["uri"]:
                                    spotify.play_track(track["uri"])
                                    current_screen = "music"
                                    state["show_lyrics"] = False
                                break

            elif current_screen == "chat":
                send_rect = pygame.Rect(612, 378, 148, 36)
                if send_rect.collidepoint(mouse_pos):
                    if state["chat_input"].strip() and not rocky_brain.is_thinking():
                        user_msg = state["chat_input"].strip()
                        state["chat_messages"].append({"role": "user", "text": user_msg})
                        state["chat_input"] = ""
                        rocky_brain.ask_rocky(user_msg)
                elif back_button["rect"].collidepoint(mouse_pos):
                    current_screen = "home"

            else:
                if back_button["rect"].collidepoint(mouse_pos):
                    current_screen = "home"

        if event.type == pygame.MOUSEBUTTONUP:
            scroll_dragging = False

        if event.type == pygame.MOUSEMOTION and current_screen == "speakers" and event.buttons[0]:
            if not scroll_dragging:
                if abs(event.pos[1] - scroll_drag_start_y) > 5:
                    scroll_dragging = True

        if event.type == pygame.MOUSEMOTION and scroll_dragging and current_screen == "speakers":
            delta = scroll_drag_start_y - event.pos[1]
            total_height = len(speakers) * (56 + 10)
            max_scroll = max(0, total_height - 230)
            state["speaker_scroll"] = max(0, min(max_scroll, scroll_drag_start_offset + delta))

        if event.type == pygame.MOUSEWHEEL and current_screen == "speakers":
            total_height = len(speakers) * (56 + 10)
            max_scroll = max(0, total_height - 230)
            state["speaker_scroll"] = max(0, min(max_scroll, state["speaker_scroll"] - event.y * 20))

        if event.type == pygame.MOUSEWHEEL and current_screen == "playlists":
            if state["playlist_screen"] == "playlists":
                total_height = len(state["playlists"]) * (56 + 8)
                max_scroll = max(0, total_height - 340)
                state["playlist_scroll"] = max(0, min(max_scroll, state["playlist_scroll"] - event.y * 20))
            else:
                total_height = len(state["playlist_tracks"]) * (52 + 6)
                max_scroll = max(0, total_height - 330)
                state["track_scroll"] = max(0, min(max_scroll, state["track_scroll"] - event.y * 20))

        if event.type == pygame.KEYDOWN and current_screen == "chat":
            if event.key == pygame.K_RETURN:
                if state["chat_input"].strip() and not rocky_brain.is_thinking():
                    user_msg = state["chat_input"].strip()
                    state["chat_messages"].append({"role": "user", "text": user_msg})
                    state["chat_input"] = ""
                    rocky_brain.ask_rocky(user_msg)
            elif event.key == pygame.K_BACKSPACE:
                state["chat_input"] = state["chat_input"][:-1]
            else:
                if event.unicode and len(state["chat_input"]) < 80:
                    state["chat_input"] += event.unicode

    if current_screen == "chat":
        response = rocky_brain.get_pending_response()
        if response:
            state["chat_messages"].append({"role": "rocky", "text": response})
            state["chat_scroll"] = max(0, len(state["chat_messages"]) * 34 - 300)

    spotify.refresh()

    if current_screen == "music":
        lyrics.fetch_lyrics(
            spotify.current_track["title"],
            spotify.current_track["artist"],
            spotify.current_track["duration_seconds"]
        )

    current_title = spotify.current_track["title"]
    if current_title != state["last_reacted_song"] and current_title != "Nothing playing":
        state["last_reacted_song"] = current_title
        rocky_brain.react_to_song(current_title, spotify.current_track["artist"])

    reaction = rocky_brain.get_pending_response()
    if reaction and current_screen != "chat":
        state["rocky_song_comment"] = reaction
        state["rocky_song_face"] = "[ ^ w ^ ]"

    if current_screen == "playlists" and not state.get("playlists_loaded"):
        state["playlists_loaded"] = True
        state["playlists"] = spotify.get_playlists()
        print(f"Loaded {len(state['playlists'])} playlists")
        for p in state["playlists"]:
            print(f"  - {p['name']}")

    if button_press_timer > 0:
        button_press_timer -= dt
        if button_press_timer <= 0:
            button_pressed = None

    screen.fill(BLACK)

    if current_screen == "home":
        draw_home()
    elif current_screen == "music":
        draw_music_screen()
    elif current_screen == "speakers":
        draw_speakers_screen()
    elif current_screen == "chat":
        draw_chat_screen()
    elif current_screen == "playlists":
        draw_playlists_screen()

    draw_clock()
    pygame.display.flip()