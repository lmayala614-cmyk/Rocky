import pygame
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Colors
BLACK      = (10,  13,  20)
SURFACE    = (17,  21,  32)
RAISED     = (24,  30,  46)
BORDER     = (31,  42,  64)
ACCENT     = (0,   212, 255)
PURPLE     = (124, 58,  237)
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

# ---- FAKE SONG DATA ----
# Later this will come from real Spotify info. For now we make it up.
current_song = {
    "title": "Mr. Brightside",
    "artist": "The Killers",
    "album": "Hot Fuss",
    "duration_seconds": 222,  # 3:42
}

# Tracks how many seconds into the song we are. Starts at 0.
elapsed_seconds = 0.0

# Whether the song is playing or paused
is_playing = True

# ---- MUSIC SCREEN BUTTONS ----
play_button = pygame.Rect(370, 350, 60, 60)
prev_button = pygame.Rect(290, 365, 50, 50)
next_button = pygame.Rect(460, 365, 50, 50)


def format_time(seconds):
    """Turns 142 seconds into '2:22' for display."""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"  # :02d means always show 2 digits, like 05 not 5


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

    # --- Album art placeholder ---
    art_rect = pygame.Rect(300, 80, 200, 200)
    pygame.draw.rect(screen, SURFACE, art_rect, border_radius=12)
    pygame.draw.rect(screen, BORDER, art_rect, width=1, border_radius=12)
    note_icon = font_large.render("\u266B", True, TEXT_DIM)  # music note symbol
    icon_x = art_rect.centerx - note_icon.get_width() // 2
    icon_y = art_rect.centery - note_icon.get_height() // 2
    screen.blit(note_icon, (icon_x, icon_y))

    # --- Song info, centered under the art ---
    title_text = font_medium.render(current_song["title"], True, TEXT_WHITE)
    screen.blit(title_text, (400 - title_text.get_width() // 2, 295))

    artist_text = font_small.render(current_song["artist"], True, TEXT_DIM)
    screen.blit(artist_text, (400 - artist_text.get_width() // 2, 320))

    # --- Progress bar ---
    bar_x, bar_y, bar_width, bar_height = 250, 250, 300, 4
    pygame.draw.rect(screen, BORDER, (bar_x, bar_y, bar_width, bar_height), border_radius=2)

    # What fraction of the song has played? (0.0 to 1.0)
    progress = elapsed_seconds / current_song["duration_seconds"]
    progress = min(progress, 1.0)  # never go above 100%
    filled_width = int(bar_width * progress)
    pygame.draw.rect(screen, ACCENT, (bar_x, bar_y, filled_width, bar_height), border_radius=2)

    # Time labels on either side of the bar
    elapsed_label = font_tiny.render(format_time(elapsed_seconds), True, TEXT_DIM)
    screen.blit(elapsed_label, (bar_x, bar_y + 10))

    total_label = font_tiny.render(format_time(current_song["duration_seconds"]), True, TEXT_DIM)
    screen.blit(total_label, (bar_x + bar_width - total_label.get_width(), bar_y + 10))

    # --- Playback controls ---
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
    title = font_large.render("SPEAKERS", True, ACCENT)
    screen.blit(title, (20, 20))
    msg = font_medium.render("No speakers connected yet.", True, TEXT_DIM)
    screen.blit(msg, (40, 120))
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


# ---- MAIN LOOP ----
clock = pygame.time.Clock()

while True:
    # dt = "delta time" = how many seconds passed since the last loop.
    # We use this to advance the song progress smoothly no matter how fast the computer runs.
    dt = clock.tick(60) / 1000  # tick(60) returns milliseconds, divide by 1000 for seconds

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
                    is_playing = not is_playing  # flip true/false
                elif next_button.collidepoint(mouse_pos):
                    elapsed_seconds = 0  # pretend we skipped to a new song
                elif prev_button.collidepoint(mouse_pos):
                    elapsed_seconds = 0

            else:
                if back_button.collidepoint(mouse_pos):
                    current_screen = "home"

    # If we're on the music screen and playing, advance the clock
    if current_screen == "music" and is_playing:
        elapsed_seconds += dt
        if elapsed_seconds >= current_song["duration_seconds"]:
            elapsed_seconds = 0  # loop back to start when song "ends"

    screen.fill(BLACK)

    if current_screen == "home":
        draw_home()
    elif current_screen == "music":
        draw_music_screen()
    elif current_screen == "speakers":
        draw_speakers_screen()
    elif current_screen == "chat":
        draw_chat_screen()

    pygame.display.flip()