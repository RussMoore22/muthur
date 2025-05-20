import pygame
import math

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

# Simulated "3D" projection of car points rotating around Z axis
def draw_mustang(surface, center, size, angle):
    cx, cy = center

    # Base polygon car shape (simple 8-point outline)
    car_points = [
        (-2, -1), (-1.5, -1.2), (1.5, -1.2), (2, -1),
        (2, 1), (1.5, 1.2), (-1.5, 1.2), (-2, 1)
    ]

    # Wheel anchor positions (before rotation)
    wheel_points = [
        (-1.6, 1.3),  # rear
        (1.6, 1.3)    # front
    ]

    rotated_car = []
    for x, y in car_points:
        angle_rad = math.radians(angle)
        z = math.sin(angle_rad) * x
        scale = 1 + 0.3 * z  # simulate depth
        x_rot = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        y_rot = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        rotated_car.append((cx + x_rot * size * scale, cy + y_rot * size * scale * 0.6))

    pygame.draw.polygon(surface, NEON_GREEN, rotated_car, 2)

    # Draw wheels with same transformation logic
    for wx, wy in wheel_points:
        angle_rad = math.radians(angle)
        z = math.sin(angle_rad) * wx
        scale = 1 + 0.3 * z
        x_rot = wx * math.cos(angle_rad) - wy * math.sin(angle_rad)
        y_rot = wx * math.sin(angle_rad) + wy * math.cos(angle_rad)
        px = cx + x_rot * size * scale
        py = cy + y_rot * size * scale * 0.6
        wheel_radius = 10 * scale
        pygame.draw.circle(surface, NEON_GREEN, (int(px), int(py)), int(wheel_radius), 2)

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