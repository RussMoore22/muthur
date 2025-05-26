import pygame
import math
import os
import logging

# Configure logging
logging.basicConfig(
    filename="/home/rcmoore/muthur/muthur.log",
    filemode='a',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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





class View:
    def __init__(self, name, parent=None, children=None, buttons=None):
        self.name = name
        self.parent = parent
        self.children = children if children else []
        self.buttons = buttons if buttons else []
    
    def switch_view(self, name=None, home=False):
        
        if home == True:
            view = self
            while view.parent is not None:
                view = view.parent
            return view

        if name == None:
            return self.parent
        
        for child in self.children:
            if child.name == name:
                return child
# Button class
class Button:
    def __init__(self, x, y, w, h, label, redirect: View):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.redirect = redirect

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GREEN, self.rect, border_radius=5)
        pygame.draw.rect(surface, NEON_GREEN, self.rect, 2, border_radius=5)
        text = font.render(self.label, True, NEON_GREEN)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def is_pressed(self, pos):
        return self.rect.collidepoint(pos)
        

# create views:

pair_view = View(name="pair_view")
analyze_view = View(name="analyze_view")

home_view = View(
    name="home",
    children=[pair_view, analyze_view],
)
home_view.buttons = [
        Button(50, 100, 250, 60, "SCAN INFECTION", pair_view),
        Button(50, 180, 250, 60, "ANALYZE", analyze_view),
        Button(50, 260, 250, 60, "SELF DESTRUCT", home_view),
    ]

pair_view.parent = home_view

def draw_mustang(surface, center, angle):
    flip = True
    if angle > 180:
        d_angle = angle - 180
        angle -= 2*d_angle
        flip = False
    cx, cy = center

    # Normalize angle to 0–359
    normalized = int(angle) % 360

    # Round angle to nearest multiple of 45 (or 30, 22.5 for smoother rotation)
    frame_angle = round(normalized / 45) * 45
    frame_path = f"/home/rcmoore/muthur/sprites/mustang_{frame_angle:03}.png"

    if not os.path.exists(frame_path):
        logging.warning(f"Sprite not found: {frame_path}")
        return

    image = pygame.image.load(frame_path).convert_alpha()

    if flip:
        image = pygame.transform.flip(image, True, False)
    # Scale the image to fit within 300x200
    max_width, max_height = 300, 200
    original_width, original_height = image.get_size()

    scale = min(max_width / original_width, max_height / original_height, 1.0)
    new_size = (int(original_width * scale), int(original_height * scale))
    image = pygame.transform.smoothscale(image, new_size)

    # Re-center after scaling (and flipping)
    image_rect = image.get_rect(center=(cx, cy))
    surface.blit(image, image_rect)

current_view = home_view

angle = 180
running = True
while running:
    screen.fill(BLACK)
    buttons = current_view.buttons

    # Draw the rotating Mustang
    if current_view.name == "home":
        draw_mustang(screen, center=(600, 240), angle=angle)
        angle = (angle + 5) % 360

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
                    logging.info(f"{button.label} button pressed")
                    current_view = button.redirect

    pygame.display.update()
    clock.tick(60)

pygame.quit()