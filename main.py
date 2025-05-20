import pygame
import math
import os

pygame.init()
screen = pygame.display.set_mode((800, 480))
pygame.display.set_caption("MUTHUR - Foxbody Display")
pygame.mouse.set_visible(True)
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
NEON_GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)

font = pygame.font.SysFont('Courier', 28, bold=True)

# Button class
class Button:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GREEN, self.rect, border_radius=5)
        pygame.draw.rect(surface, NEON_GREEN, self.rect, 2, border_radius=5)
        text = font.render(self.label, True, NEON_GREEN)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def is_pressed(self, pos):
        return self.rect.collidepoint(pos)

buttons = [
    Button(50, 100, 250, 60, "INITIATE"),
    Button(50, 180, 250, 60, "OVERRIDE"),
    Button(50, 260, 250, 60, "SELF DESTRUCT"),
]

def draw_mustang(surface, center, angle):
    cx, cy = center

    # Normalize angle to 0–359
    normalized = int(angle) % 360

    # Round angle to nearest multiple of 45 (or 30, 22.5 for smoother rotation)
    frame_angle = round(normalized / 45) * 45
    frame_path = f"/home/pi/muthur/sprites/mustang_{frame_angle:03}.png"

    # Load and cache the image
    if not os.path.exists(frame_path):
        print(f"[Warning] Sprite not found: {frame_path}")
        return

    image = pygame.image.load(frame_path).convert_alpha()

    # Flip if facing backward
    if 180 <= normalized < 360:
        image = pygame.transform.flip(image, True, False)

    # Center image on screen
    image_rect = image.get_rect(center=(cx, cy))
    surface.blit(image, image_rect)

angle = 0
running = True
while running:
    screen.fill(BLACK)

    # Draw the rotating Mustang
    draw_mustang(screen, center=(600, 240), size=40, angle=angle)
    angle = (angle + 0.5) % 360

    # Draw UI buttons
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

    pygame.display.update()
    clock.tick(60)

pygame.quit()