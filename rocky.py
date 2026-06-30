import pygame
import sys

# Initialize pygame - this is the library that draws Rocky's screen
pygame.init()

# Set the screen size - this matches the Pi touchscreen resolution
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Colors - we'll use these everywhere
BLACK      = (10,  13,  20)
SURFACE    = (17,  21,  32)
ACCENT     = (0,   212, 255)
TEXT_WHITE = (232, 237, 245)
TEXT_DIM   = (136, 150, 170)

# Create the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rocky")

# Font setup
font_large  = pygame.font.SysFont("monospace", 28, bold=True)
font_medium = pygame.font.SysFont("monospace", 16)
font_small  = pygame.font.SysFont("monospace", 12)

# This is Rocky's main loop - it runs forever until you close it
# Think of it like a heartbeat - it redraws the screen 60 times per second
while True:

    # Check for events (touches, clicks, keyboard, closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Draw the background
    screen.fill(BLACK)

    # Draw Rocky's name at the top
    title = font_large.render("ROCKY", True, ACCENT)
    screen.blit(title, (20, 20))

    status = font_small.render("online · ready", True, TEXT_DIM)
    screen.blit(status, (22, 56))

    # Draw a divider line
    pygame.draw.line(screen, (31, 42, 64), (0, 75), (SCREEN_WIDTH, 75), 1)

    # Draw placeholder sections
    msg = font_medium.render("Music Player    →    coming soon", True, TEXT_DIM)
    screen.blit(msg, (40, 120))

    msg2 = font_medium.render("Speakers        →    coming soon", True, TEXT_DIM)
    screen.blit(msg2, (40, 160))

    msg3 = font_medium.render("Talk to Rocky   →    coming soon", True, TEXT_DIM)
    screen.blit(msg3, (40, 200))

    # Push everything to the screen
    pygame.display.flip()

    # Cap at 60 frames per second
    pygame.time.Clock().tick(60)