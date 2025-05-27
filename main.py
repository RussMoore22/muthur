import pygame
import math
import os
import logging
import subprocess
import select
import json

bluetooth_agent = None
bluetooth_log_lines = []
running = True


def self_destruct():
    global running
    running = False

# Configure logging
logging.basicConfig(
    filename="/home/rcmoore/muthur/muthur.log",
    filemode='a',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_pairing_code():
    try:
        with open("/home/rcmoore/muthur/bluetooth_code.json", "r") as f:
            return json.load(f)
    except:
        return {"Passkey": ""}
    

def is_device_connected():
    try:
        output = subprocess.check_output("echo 'devices' | bluetoothctl", shell=True, text=True).splitlines()
        for line in output:
            if "Device" in line:
                mac = line.split()[1]
                detail = subprocess.check_output(f"echo 'info {mac}' | bluetoothctl", shell=True, text=True)
                if "Connected: yes" in detail:
                    return True
        return False
    except Exception as e:
        logging.warning(f"Failed to check connection status: {e}")
        return False

def enable_bluetooth_mode():
    commands = [
        ['bluetoothctl', 'discoverable', 'on'],
        ['bluetoothctl', 'pairable', 'on'],
        ['bluetoothctl', 'agent', 'NoInputNoOutput'],
        ['bluetoothctl', 'default-agent']
    ]
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
            logging.info(f"Ran: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed: {' '.join(cmd)} with error: {e}")


def start_bluetooth_agent():
    try:
        return subprocess.Popen(
            ["python3", "/home/rcmoore/muthur/bluetooth_pairing_agent.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
    except Exception as e:
        logging.error(f"Bluetooth agent start failed: {e}")
        return None
    
def get_bluetooth_metadata():
    try:
        with open("/home/rcmoore/muthur/bluetooth_metadata.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Failed to read metadata: {e}")
        return {}
    
    
def disconnect_bluetooth_device():
    global bluetooth_log_lines, bluetooth_agent
    bluetooth_log_lines = []
    bluetooth_agent = None

    try:
        # Get MAC of connected device
        info_output = subprocess.check_output(
            "echo 'devices' | bluetoothctl", shell=True, text=True
        ).splitlines()

        connected_mac = None
        for line in info_output:
            if "Device" in line:
                mac = line.split()[1]
                # Check connection status
                detail = subprocess.check_output(
                    f"echo 'info {mac}' | bluetoothctl", shell=True, text=True
                )
                if "Connected: yes" in detail:
                    connected_mac = mac
                    break

        if connected_mac:
            subprocess.run(["bluetoothctl", "disconnect", connected_mac], check=True)
            logging.info(f"Disconnected device {connected_mac}")
        else:
            logging.info("No connected device found to disconnect.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to disconnect device: {e}")

    # Clear metadata file to remove stale info
    try:
        os.remove("/home/rcmoore/muthur/bluetooth_metadata.json")
        os.remove("/home/rcmoore/muthur/bluetooth_code.json")
        logging.info("Cleared Bluetooth metadata cache")
    except Exception as e:
        logging.error(f"Failed to clear metadata cache: {e}")

def render_metadata(screen, font, start_y=300):
    metadata = get_bluetooth_metadata()
    y = start_y
    for key in ["Title", "Artist", "Album"]:
        value = metadata.get(key, "")
        text = font.render(f"{key}: {value}", True, NEON_GREEN)
        screen.blit(text, (20, y))
        y += 30

    if not is_device_connected():
        pairing = get_pairing_code()
        code = pairing.get("Passkey", "")
        if code:
            text = font.render(f"Pairing Code: {code}", True, NEON_GREEN)
            screen.blit(text, (400, y))


    metadata = get_bluetooth_metadata()
    y = start_y
    for key in ["Title", "Artist", "Album"]:
        value = metadata.get(key, "")
        text = font.render(f"{key}: {value}", True, NEON_GREEN)
        screen.blit(text, (20, y))
        y += 30


pygame.init()
enable_bluetooth_mode()
# at startup
metadata_listener = subprocess.Popen(
    ["python3", "/home/rcmoore/muthur/bluetooth_metadata_listener.py"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

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
def no_action():
    logging.info("this button has no action")
            
# Button class
class Button:
    def __init__(self, x, y, w, h, label, redirect: View, action=no_action):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.redirect = redirect
        self.action = action

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GREEN, self.rect, border_radius=5)
        pygame.draw.rect(surface, NEON_GREEN, self.rect, 2, border_radius=5)
        text = font.render(self.label, True, NEON_GREEN)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def is_pressed(self, pos):
        return self.rect.collidepoint(pos)
    
    def change_view(self, current_view):
        self.action()
        return self.redirect


        
# create views:
pair_view = View(name="pair_view")
analyze_view = View(name="analyze_view")

home_view = View(
    name="home",
    children=[pair_view, analyze_view],
)

pair_view.parent = home_view

home_view.buttons = [
        Button(50, 100, 250, 60, "SCAN INFECTION", pair_view),
        Button(50, 180, 250, 60, "ANALYZE", analyze_view),
        Button(50, 260, 250, 60, "SELF DESTRUCT", home_view, self_destruct),
    ]

pair_view.buttons = [
    Button(50, 100, 250, 60, "ESCAPE", home_view),
    Button(50, 180, 250, 60, "REMOVE PARASITE", home_view, disconnect_bluetooth_device)
]
analyze_view.buttons = [
    Button(50, 100, 250, 60, "ESCAPE", home_view),
]


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

try:
    while running:
        if current_view.name == "pair_view" and bluetooth_agent:
            rlist, _, _ = select.select([bluetooth_agent.stdout], [], [], 0.01)
            if rlist:
                output = bluetooth_agent.stdout.readline()
                if output:
                    bluetooth_log_lines.append(output.strip())
                    bluetooth_log_lines = bluetooth_log_lines[-10:]

            y = 50
            for line in bluetooth_log_lines:
                text = font.render(line, True, NEON_GREEN)
                screen.blit(text, (20, y))
                y += 30

        buttons = current_view.buttons
        screen.fill(BLACK)

        # Draw the rotating Mustang
        if current_view.name == "home":
            draw_mustang(screen, center=(600, 240), angle=angle)
            angle = (angle + 5) % 360
        if current_view.name == "pair_view":
            render_metadata(screen, font=pygame.font.SysFont('Courier', 28, bold=True))


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
                        if current_view.name == "pair_view" and bluetooth_agent is None:
                            bluetooth_agent = start_bluetooth_agent()

        pygame.display.update()
        clock.tick(60)
except Exception as e:
    logging.exception(f"Unhandled exception in main loop: {e}")
    pygame.quit()

pygame.quit()