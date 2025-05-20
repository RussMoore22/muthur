import os
import pygame

# Use the framebuffer directly (if no desktop environment)
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')

pygame.init()
pygame.mouse.set_visible(True)

# Screen setup (adjust if needed)
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
BLACK = (0, 0, 0)
NEON_GREEN = (0, 255, 0)
DEEP_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

# Font
font = pygame.font.SysFont("Courier", 28, bold=True)

# Button class
class Button:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label

    def draw(self, surface):
        pygame.draw.rect(surface, DEEP_GREEN, self.rect, border_radius=6)
        pygame.draw.rect(surface, NEON_GREEN, self.rect, 2, border_radius=6)
        text = font.render(self.label, True, NEON_GREEN)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def is_pressed(self, pos):
        return self.rect.collidepoint(pos)

# Buttons
buttons = [
    Button(50, 100, 250, 60, "INITIATE"),
    Button(50, 180, 250, 60, "OVERRIDE"),
    Button(50, 260, 250, 60, "SELF DESTRUCT"),
]

# Main loop
running = True
while running:
    screen.fill(BLACK)

    for button in buttons:
        button.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for button in buttons:
                if button.is_pressed(pos):
                    print(f">>> {button.label} PRESSED <<<")
                    if button.label == "SELF DESTRUCT":
                        running = False

    pygame.display.flip()

pygame.quit()