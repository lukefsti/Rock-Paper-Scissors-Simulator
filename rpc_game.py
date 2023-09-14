import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import random
import math
import tkinter as tk
from tkinter import simpledialog, messagebox, Entry, IntVar, Checkbutton, Button
import configparser

config = configparser.ConfigParser()
config.read('settings.ini')
# Initialize pygame
pygame.init()
pygame.mixer.init()
pygame.font.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SPEED_MULTIPLIER = 1.0

NORMAL_SPEED = 1.0
FLEEING_SPEED = 1.5
HUNTING_SPEED = 2.0

VIEW_RANGE = 500

rock_kill_score = 0
paper_kill_score = 0
scissors_kill_score = 0

paused = False

smart_move = True



# Font for counter
FONT = pygame.font.SysFont('Arial', 24)

# Window size
WIDTH, HEIGHT = 1200, 800

# Directions
DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]

paper_kill_sound = pygame.mixer.Sound('assets/paper.wav')
stone_kill_sound = pygame.mixer.Sound('assets/rock.wav')
scissors_kill_sound = pygame.mixer.Sound('assets/scissors.wav')
paper_kill_sound.set_volume(0.2)  # set to 50% volume
stone_kill_sound.set_volume(0.2)
scissors_kill_sound.set_volume(0.2)

class Element:
    # Load images for the elements
    # Original images
    rock_img_original = pygame.image.load("assets/rock.png")
    paper_img_original = pygame.image.load("assets/paper.png")
    scissors_img_original = pygame.image.load("assets/scissors.png")
    
    if smart_move:
        hunt_icon_original = pygame.image.load("assets/hunt_icon.png")
        flee_icon_original = pygame.image.load("assets/fleeing_icon.png")
        normal_icon_original = pygame.image.load("assets/normal_icon.png")
    
    # Desired size
    IMAGE_SIZE = (50, 50)
    MODE_SIZE = (20,20)
    
    # Scaled images
    rock_img = pygame.transform.scale(rock_img_original, IMAGE_SIZE)
    paper_img = pygame.transform.scale(paper_img_original, IMAGE_SIZE)
    scissors_img = pygame.transform.scale(scissors_img_original, IMAGE_SIZE)
    
    if smart_move:
        hunt_icon = pygame.transform.scale(hunt_icon_original, MODE_SIZE)
        flee_icon = pygame.transform.scale(flee_icon_original, MODE_SIZE)
        normal_icon = pygame.transform.scale(normal_icon_original, MODE_SIZE)
    
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.status = "normal"  # Can be 'hunt', 'flee', or 'normal'
        self.dx, self.dy = random.choice(DIRECTIONS)
    
    def within_boundaries(self, new_x, new_y):
        return 0 <= new_x <= WIDTH and 0 <= new_y <= HEIGHT

    def adjust_for_boundaries(self):
        if self.x + self.dx < 0:
            self.x = 0
            self.dx = -self.dx
        elif self.x + self.dx > WIDTH:
            self.x = WIDTH
            self.dx = -self.dx
        if self.y + self.dy < 0:
            self.y = 0
            self.dy = -self.dy
        elif self.y + self.dy > HEIGHT:
            self.y = HEIGHT
            self.dy = -self.dy


    def move(self):
        self.x += self.dx * SPEED_MULTIPLIER
        self.y += self.dy * SPEED_MULTIPLIER
        
        # Clamping values to ensure they remain within the screen
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))
        # Boundary conditions
        if self.x <= 0 or self.x >= WIDTH:
            self.dx = -self.dx
        if self.y <= 0 or self.y >= HEIGHT:
            self.dy = -self.dy
        
    def rotate_image(self, image, angle):
        orig_rect = image.get_rect()
        rotated_image = pygame.transform.rotate(image, -angle)  # The negative sign is to correct the rotation direction.
        rotated_rect = orig_rect.copy()
        rotated_rect.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rect).copy()
        return rotated_image



    def draw(self, screen):
        # Calculate angle based on movement
        angle = math.degrees(math.atan2(-self.dy, self.dx)) -15 # Negative on dy because Pygame's y is inverted.
        
        if self.type == "rock":
            rotated_image = self.rotate_image(Element.rock_img, angle)
            screen.blit(rotated_image, (self.x - rotated_image.get_width() // 2, self.y - rotated_image.get_height() // 2))
        elif self.type == "paper":
            rotated_image = self.rotate_image(Element.paper_img, angle)
            screen.blit(rotated_image, (self.x - rotated_image.get_width() // 2, self.y - rotated_image.get_height() // 2))
        elif self.type == "scissors":
            rotated_image = self.rotate_image(Element.scissors_img, angle)
            screen.blit(rotated_image, (self.x - rotated_image.get_width() // 2, self.y - rotated_image.get_height() // 2))

        # Adjust y-coordinate to display status icons below the main icons
        if smart_move:
            status_y_position = self.y + Element.IMAGE_SIZE[1] // 2
            if self.status == "hunt":
                screen.blit(Element.hunt_icon, (self.x + Element.IMAGE_SIZE[0]//2 - Element.MODE_SIZE[0]//2, status_y_position))
            elif self.status == "flee":
                screen.blit(Element.flee_icon, (self.x + Element.IMAGE_SIZE[0]//2 - Element.MODE_SIZE[0]//2, status_y_position))
            else:
                screen.blit(Element.normal_icon, (self.x + Element.IMAGE_SIZE[0]//2 - Element.MODE_SIZE[0]//2, status_y_position))

    
    def collide_and_bounce(self, other):
        global rock_kill_score, paper_kill_score, scissors_kill_score, stone_kill_sound, scissors_kill_sound, paper_kill_sound
    
        # When two elements collide
        if self.type == "rock" and other.type == "scissors":
            other.type = "rock"
            rock_kill_score += 1
            stone_kill_sound.play()
        elif self.type == "scissors" and other.type == "paper":
            other.type = "scissors"
            scissors_kill_score += 1
            scissors_kill_sound.play()
        elif self.type == "paper" and other.type == "rock":
            other.type = "paper"
            paper_kill_score += 1  # You were mistakenly incrementing paper_kill_sound here.
            paper_kill_sound.play()
        # Handle the vice-versa cases
        elif other.type == "rock" and self.type == "scissors":
            self.type = "rock"
        elif other.type == "scissors" and self.type == "paper":
            self.type = "scissors"
        elif other.type == "paper" and self.type == "rock":
            self.type = "paper"

        # Find midpoint between two elements
        mid_x = (self.x + other.x) / 2
        mid_y = (self.y + other.y) / 2

        # Push self element outwards a little
        angle = math.atan2(self.y - mid_y, self.x - mid_x)
        self.x += math.cos(angle) * 5
        self.y += math.sin(angle) * 5
        self.dx, self.dy = math.cos(angle), math.sin(angle)

        # Push other element outwards a little
        angle = math.atan2(other.y - mid_y, other.x - mid_x)
        other.x += math.cos(angle) * 5
        other.y += math.sin(angle) * 5
        other.dx, other.dy = math.cos(angle), math.sin(angle)


        
    def bounce(self, other):
        # Find the mid point between two elements
        mid_x = (self.x + other.x) / 2
        mid_y = (self.y + other.y) / 2

        # Adjust self element
        angle = math.atan2(self.y - mid_y, self.x - mid_x)
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)

        # Adjust other element
        angle = math.atan2(other.y - mid_y, other.x - mid_x)
        other.dx = math.cos(angle)
        other.dy = math.sin(angle)

    def collide(self, other):
        # When two elements collide
        if self.type == "rock" and other.type == "scissors":
            other.type = "rock"
        elif self.type == "scissors" and other.type == "paper":
            other.type = "scissors"
        elif self.type == "paper" and other.type == "rock":
            other.type = "paper"
        # Handle the vice-versa cases
        elif other.type == "rock" and self.type == "scissors":
            self.type = "rock"
        elif other.type == "scissors" and self.type == "paper":
            self.type = "scissors"
        elif other.type == "paper" and self.type == "rock":
            self.type = "paper"
            
    def hunt_and_flee(self, elements):
        hunt_targets = {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock"
        }

        flee_targets = {
            "rock": "paper",
            "scissors": "rock",
            "paper": "scissors"
        }

        vision_radius = VIEW_RANGE  # radius within which an entity can "see" others

        nearest_hunt_target = None
        nearest_flee_target = None

        nearest_hunt_distance = float('inf')
        nearest_flee_distance = float('inf')

        for elem in elements:
            if elem == self:  # skip itself
                continue
            dist = ((self.x - elem.x) ** 2 + (self.y - elem.y) ** 2) ** 0.5
            if dist < vision_radius:
                # Find the nearest target to hunt
                if elem.type == hunt_targets[self.type] and dist < nearest_hunt_distance:
                    nearest_hunt_distance = dist
                    nearest_hunt_target = elem
                # Find the nearest target to flee from
                elif elem.type == flee_targets[self.type] and dist < nearest_flee_distance:
                    nearest_flee_distance = dist
                    nearest_flee_target = elem
        
        

        if nearest_hunt_target:
            angle_to_target = math.atan2(nearest_hunt_target.y - self.y, nearest_hunt_target.x - self.x)
            self.dx = math.cos(angle_to_target) * HUNTING_SPEED
            self.dy = math.sin(angle_to_target) * HUNTING_SPEED
            self.status = "hunt"
        elif nearest_flee_target:
            angle_from_target = math.atan2(self.y - nearest_flee_target.y, self.x - nearest_flee_target.x)
            self.dx = math.cos(angle_from_target) * FLEEING_SPEED
            self.dy = math.sin(angle_from_target) * FLEEING_SPEED
            self.status = "flee"
        else:
            base_dx = math.copysign(NORMAL_SPEED, self.dx)
            base_dy = math.copysign(NORMAL_SPEED, self.dy)
            self.dx = base_dx
            self.dy = base_dy
            self.status = "normal"

        # Check and adjust for boundaries after deciding the direction
        if not self.within_boundaries(self.x + self.dx, self.y + self.dy):
            self.adjust_for_boundaries()

def clear_screen(screen, color=(0, 0, 0)):
    screen.fill(color)


def main(x, y, z):
    global SPEED_MULTIPLIER
    global rock_kill_score, paper_kill_score, scissors_kill_score
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Rock Paper Scissors Game')

    elements = []

    def valid_position(new_element):
        for e in elements:
            dist = ((e.x - new_element.x) ** 2 + (e.y - new_element.y) ** 2) ** 0.5
            required_distance = 2 * Element.IMAGE_SIZE[0]  # Assuming all elements have same image size for simplicity
            if dist < required_distance:
                return False
        return True

    def create_element(element_type):
        trials = 1000
        while trials > 0:  # Give it 1000 attempts to find a position, to avoid potential infinite loop
            new_element = Element(element_type, random.randint(0, WIDTH), random.randint(0, HEIGHT))
            if valid_position(new_element):
                elements.append(new_element)
                break
            trials -= 1

    for _ in range(x):
        create_element("rock")
    for _ in range(y):
        create_element("paper")
    for _ in range(z):
        create_element("scissors")

    running = True
    global paused  # ensure we use the global variable
    while running:
        screen.fill(WHITE)

        if not paused:  # Only update game state if not paused
            for i in range(len(elements)):
                for j in range(len(elements)):
                    if i != j:
                        collision_distance = (Element.rock_img.get_width() + Element.paper_img.get_width() + Element.scissors_img.get_width()) / 6.0
                        dist = ((elements[i].x - elements[j].x) ** 2 + (elements[i].y - elements[j].y) ** 2) ** 0.5
                        if dist < collision_distance:  # If they collide
                            elements[i].collide_and_bounce(elements[j])
            types = [e.type for e in elements]
            if len(set(types)) == 1:  # If only one type remains
                winner_type = types[0]
                clear_screen(screen)  # Clear the screen with black or your preferred color

                # Display the winner in the center of the screen
                if winner_type == "rock":
                    rotated_image = Element.rock_img
                elif winner_type == "paper":
                    rotated_image = Element.paper_img
                else:
                    rotated_image = Element.scissors_img

                center_x = screen.get_width() // 2 - rotated_image.get_width() // 2
                center_y = screen.get_height() // 2 - rotated_image.get_height() // 2
                screen.blit(rotated_image, (center_x, center_y))

                # Render and display the "won" text
                won_text = FONT.render(f"{winner_type} won!", True, (255, 255, 255))
                text_position = (screen.get_width() // 2 - won_text.get_width() // 2, center_y + rotated_image.get_height() + 10)
                screen.blit(won_text, text_position)

                # Render and display the statistics
                stats_start_y = text_position[1] + won_text.get_height() + 20  # 20 pixels gap from "won" text

                rock_score_text = FONT.render(f"Rock Kills: {rock_kill_score}", True, (255, 255, 255))
                screen.blit(rock_score_text, (screen.get_width() // 2 - rock_score_text.get_width() // 2, stats_start_y))

                paper_score_text = FONT.render(f"Paper Kills: {paper_kill_score}", True, (255, 255, 255))
                screen.blit(paper_score_text, (screen.get_width() // 2 - paper_score_text.get_width() // 2, stats_start_y + rock_score_text.get_height() + 10))

                scissors_score_text = FONT.render(f"Scissors Kills: {scissors_kill_score}", True, (255, 255, 255))
                screen.blit(scissors_score_text, (screen.get_width() // 2 - scissors_score_text.get_width() // 2, stats_start_y + rock_score_text.get_height() + paper_score_text.get_height() + 20))

                pygame.display.flip()  # Update the display

                pygame.time.wait(3000)  # Wait for 3 seconds (optional)

                running = False  # End the game loop

            for e in elements:
                if smart_move:
                    e.hunt_and_flee(elements)
                e.move()
                e.draw(screen)
        else:
            paused_font = pygame.font.SysFont('Arial', 48)
            paused_text = paused_font.render("Paused", True, (0, 0, 0))
            screen.blit(paused_text, (WIDTH/2 - paused_text.get_width()/2, HEIGHT/2 - paused_text.get_height()/2))

        render_counter(screen, elements)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:  # Increase speed
                    SPEED_MULTIPLIER += 0.1
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:  # Decrease speed
                    SPEED_MULTIPLIER -= 0.1
                    if SPEED_MULTIPLIER < 0.1:  # Ensure speed doesn't go negative or too slow
                        SPEED_MULTIPLIER = 0.1
                elif event.key == pygame.K_SPACE:  # Toggle pause
                    paused = not paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    SPEED_MULTIPLIER += 0.1
                elif event.button == 5:  # Scroll down
                    SPEED_MULTIPLIER -= 0.1
                    if SPEED_MULTIPLIER < 0.1:  # Ensure speed doesn't go negative or too slow
                        SPEED_MULTIPLIER = 0.1
    pygame.quit()

def settings_window():
    settings_win = tk.Tk()
    settings_win.title("Game Settings")
    # Default values
    default_values = {
        'SPEED_MULTIPLIER': '1.0',
        'NORMAL_SPEED': '1.0',
        'FLEEING_SPEED': '1.5',
        'HUNTING_SPEED': '2.0',
        'VIEW_RANGE': '500'
    }

    # Use StringVar for entries since we're dealing with strings in the ini file
    speed_multiplier_var = tk.StringVar(value=config['SETTINGS']['SPEED_MULTIPLIER'])
    normal_speed_var = tk.StringVar(value=config['SETTINGS']['NORMAL_SPEED'])
    fleeing_speed_var = tk.StringVar(value=config['SETTINGS']['FLEEING_SPEED'])
    hunting_speed_var = tk.StringVar(value=config['SETTINGS']['HUNTING_SPEED'])
    view_vange_var = tk.StringVar(value=config['SETTINGS']['VIEW_RANGE'])

    def submit_changes():
        config['SETTINGS']['SPEED_MULTIPLIER'] = speed_multiplier_var.get()
        config['SETTINGS']['NORMAL_SPEED'] = normal_speed_var.get()
        config['SETTINGS']['FLEEING_SPEED'] = fleeing_speed_var.get()
        config['SETTINGS']['HUNTING_SPEED'] = hunting_speed_var.get()
        config['SETTINGS']['VIEW_RANGE'] = view_vange_var.get()
        save_settings()
        settings_win.quit()

    # Labels with default values included
    tk.Label(settings_win, text=f"Speed Multiplier (Default: {default_values['SPEED_MULTIPLIER']}):").pack(pady=10)
    Entry(settings_win, textvariable=speed_multiplier_var).pack(pady=10)

    tk.Label(settings_win, text=f"Normal Speed (Default: {default_values['NORMAL_SPEED']}):").pack(pady=10)
    Entry(settings_win, textvariable=normal_speed_var).pack(pady=10)

    tk.Label(settings_win, text=f"Fleeing Speed (Default: {default_values['FLEEING_SPEED']}):").pack(pady=10)
    Entry(settings_win, textvariable=fleeing_speed_var).pack(pady=10)

    tk.Label(settings_win, text=f"Hunting Speed (Default: {default_values['HUNTING_SPEED']}):").pack(pady=10)
    Entry(settings_win, textvariable=hunting_speed_var).pack(pady=10)

    tk.Label(settings_win, text=f"View Range (Default: {default_values['VIEW_RANGE']}):").pack(pady=10)
    Entry(settings_win, textvariable=view_vange_var).pack(pady=10)

    Button(settings_win, text="Save Settings", command=submit_changes).pack(pady=20)
    settings_win.mainloop()
    settings_win.destroy()


def render_counter(screen, elements):
    rock_count = sum(1 for e in elements if e.type == "rock")
    paper_count = sum(1 for e in elements if e.type == "paper")
    scissors_count = sum(1 for e in elements if e.type == "scissors")

    rock_text = FONT.render(f'Rocks: {rock_count}', True, RED)
    paper_text = FONT.render(f'Papers: {paper_count}', True, GREEN)
    scissors_text = FONT.render(f'Scissors: {scissors_count}', True, BLUE)

    screen.blit(rock_text, (10, 10))
    screen.blit(paper_text, (10, 40))
    screen.blit(scissors_text, (10, 70))
    
    speed_text = FONT.render(f'Game Speed: {SPEED_MULTIPLIER:.1f}x', True, (0, 0, 0))
    screen.blit(speed_text, (10, 100))
    
def get_input(prompt):
    """Keep asking for input until a valid number less than or equal to 33 is given."""
    while True:
        try:
            val = int(input(prompt))
            if 0 <= val <= 33:
                return val
            else:
                print("Please enter a number between 0 and 33 inclusive.")
        except ValueError:
            print("Please enter a valid number.")

def load_settings():
    config.read('settings.ini')
    settings = config['SETTINGS']
    globals().update(settings)

def save_settings():
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

def get_game_parameters():
    window = tk.Tk()
    window.title("Rock Paper Scissors Setup")
    window.minsize(300, 200)

    # Disable resizing
    window.resizable(False, False)
    
    # Disable fullscreen toggle
    window.attributes('-fullscreen', False)

    # Variables to hold input values
    rock_var = IntVar()
    paper_var = IntVar()
    scissors_var = IntVar()
    ai_var = IntVar()  # 1 if AI should be turned on, 0 otherwise

    # Validation function for positive numbers
    def validate_positive_number(P):
        if not P:  # Allow empty input (will be treated as 0)
            return True
        if P.isdigit():
            return int(P) >= 0
        return False

    # Register the validation function
    validate_cmd = window.register(validate_positive_number)

    # Function to collect values and close window
    def submit():
        global x, y, z, ai_on
        x = rock_var.get()
        y = paper_var.get()
        z = scissors_var.get()
        
        if x <= 0 and y <= 0 and z <= 0:
            messagebox.showerror("Error", "At least one of the numbers must be greater than 0.")
            return

        ai_on = bool(ai_var.get())
        window.quit()

    # Input fields and labels
    tk.Label(window, text="Enter number of rocks:").pack(pady=10)
    Entry(window, textvariable=rock_var, validate="key", validatecommand=(validate_cmd, '%P')).pack(pady=10)

    tk.Label(window, text="Enter number of papers:").pack(pady=10)
    Entry(window, textvariable=paper_var, validate="key", validatecommand=(validate_cmd, '%P')).pack(pady=10)

    tk.Label(window, text="Enter number of scissors:").pack(pady=10)
    Entry(window, textvariable=scissors_var, validate="key", validatecommand=(validate_cmd, '%P')).pack(pady=10)

    # Checkbox for AI
    Checkbutton(window, text="Turn on AI", variable=ai_var).pack(pady=20)

    # Button to submit
    Button(window, text="Start Game", command=submit).pack(pady=20)

    Button(window, text="Settings", command=settings_window).pack(pady=20)

    window.mainloop()
    window.destroy()

    return x, y, z, ai_on


if __name__ == '__main__':
    x, y, z, ai_on = get_game_parameters()

    a = (x + y + z) / 1000
    SPEED_MULTIPLIER = a
    if SPEED_MULTIPLIER < 0.1: SPEED_MULTIPLIER = 0.1
    smart_move = ai_on
    main(x, y, z)