import pygame
import time

# Initialize pygame's audio mixer
pygame.mixer.init()

# Load and play the file through whatever Mac's default output is
# (which you just set to your Charlie)
pygame.mixer.music.load("test.mp3")
pygame.mixer.music.set_volume(0.8)  # 80% volume, 0.0 to 1.0
pygame.mixer.music.play()

print("Playing through default output device...")
print("Check your Charlie speaker!")

# Keep the script alive until the song finishes
while pygame.mixer.music.get_busy():
    time.sleep(0.5)

print("Done!")