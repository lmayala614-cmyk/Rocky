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
TEXT_WHITE = (232, 237, 245)
TEXT_DIM   = (136, 150, 170)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rocky")

font_large  = pygame.font.SysFont("monospace", 28, bold=True)
font_medium = pygame.font.SysFont("monospace", 18)
font_small  = pygame.font.SysFont("monospace", 12)

# ---- THIS IS THE NEW PART ----
# This variable tracks which screen we're currently showing.
# It starts on "home" and changes when you tap a button.
current_screen = "home"

# Each button is a rectangle (x, y, width, height) plus a label and a target screen.
# pygame.Rect just means "a box at this position with this size"
home_buttons = [
    {"rect": pygame.Rect(40, 120, 720, 50), "label": "Music Player",  "goto": "music"},
    {"rect": pygame.Rect(40, 185, 720, 50), "label": "Speakers",      "goto": "speakers"},
    {"rect": pygame.Rect(40, 250, 720, 50), "label": "Talk to Rocky", "goto": "chat"},
]

# A reusable back button for every screen except home
back_button = pygame.Rect(20, 420, 100, 40)


def draw_home():
    title = font_large.render("ROCKY", True, ACCENT)
    screen.blit(title, (20, 20))
    status = font_small.render("online . ready", True, TEXT_DIM)
    screen.blit(status, (22, 56))
    pygame.draw.line(screen, BORDER, (0, 75), (SCREEN_WIDTH, 75), 1)

    # Draw each button
    for button in home_buttons:
        pygame.draw.rect(screen, RAISED, button["rect"], border_radius=10)
        pygame.draw.rect(screen, BORDER, button["rect"], width=1, border_radius=10)
        label = font_medium.render(button["label"], True, TEXT_WHITE)
        # Center the text vertically inside the button
        text_y = button["rect"].y + (button["rect"].height - label.get_height()) // 2
        screen.blit(label, (button["rect"].x + 20, text_y))


def draw_music_screen():
    title = font_large.render("MUSIC PLAYER", True, ACCENT)
    screen.blit(title, (20, 20))
    msg = font_medium.render("Nothing playing yet.", True, TEXT_DIM)
    screen.blit(msg, (40, 120))
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
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # This fires when you click/tap the screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos  # (x, y) of where you clicked

            if current_screen == "home":
                # Check if the click landed inside any button's rectangle
                for button in home_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        current_screen = button["goto"]
            else:
                # On any other screen, check if "back" was clicked
                if back_button.collidepoint(mouse_pos):
                    current_screen = "home"

    screen.fill(BLACK)

    # Draw whichever screen is currently active
    if current_screen == "home":
        draw_home()
    elif current_screen == "music":
        draw_music_screen()
    elif current_screen == "speakers":
        draw_speakers_screen()
    elif current_screen == "chat":
        draw_chat_screen()

    pygame.display.flip()
    pygame.time.Clock().tick(60)