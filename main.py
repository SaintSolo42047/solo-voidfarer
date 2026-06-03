import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solo Voidfarer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 32)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
GRAY = (80, 80, 80)

class Ship:
    def __init__(self):
        self.modules = {"engine": 1, "scanner": 1, "shield": 1, "weapon": 1, "cargo": 1}
        self.resources = {"fuel": 10, "oxygen": 10, "data": 10}
        self.action_points = 3
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.thrust = 0

    def draw(self, surface):
        pygame.draw.polygon(surface, BLUE, [(self.x, self.y-20), (self.x-20, self.y+20), (self.x+20, self.y+20)])
        pygame.draw.rect(surface, WHITE, (self.x-8, self.y-8, 16, 16))
        pygame.draw.rect(surface, GRAY, (self.x-15, self.y+10, 30, 8))
        if self.thrust > 0:
            pygame.draw.polygon(surface, RED, [(self.x-10, self.y+20), (self.x, self.y+30), (self.x+10, self.y+20)])

class Goal:
    def __init__(self, name, difficulty):
        self.name = name
        self.difficulty = difficulty
        self.progress = 0

    def mark(self, amount):
        self.progress = min(10, self.progress + amount)

class Game:
    def __init__(self):
        self.ship = Ship()
        self.goals = [Goal("Reach next sector", "Normal"), Goal("Upgrade scanner", "Easy")]
        self.log = ["Welcome. Use arrow keys to move, 1-8 for actions."]
        self.state = "play"
        self.show_tutorial = True
        
        # Keyboard action mapping
        self.key_actions = {
            pygame.K_1: "Progress",
            pygame.K_2: "Travel",
            pygame.K_3: "Arrive",
            pygame.K_4: "Scavenge",
            pygame.K_5: "Explore",
            pygame.K_6: "Resources",
            pygame.K_7: "Combat",
            pygame.K_8: "Status",
        }

    def add_log(self, text):
        self.log.append(text)
        if len(self.log) > 8:
            self.log.pop(0)

    def roll_2d20(self, advantage=False):
        dice = [random.randint(1, 20) for _ in range(3 if advantage else 2)]
        if advantage:
            dice = sorted(dice)[:2]
        successes = sum(1 for d in dice if d <= 10)
        return successes, dice

    def draw_tutorial(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        text = big_font.render("TUTORIAL - Solo Voidfarer", True, GREEN)
        screen.blit(text, (WIDTH//2 - 200, 100))
        lines = [
            "Arrow Keys - Move ship",
            "1 - Progress   2 - Travel    3 - Arrive    4 - Scavenge",
            "5 - Explore    6 - Resources 7 - Combat    8 - Status",
            "Progress bars fill as you complete missions",
            "Resources deplete on Travel and Explore",
            "NPCs use Perilous Void tables for dialog",
            "Press SPACE to close this tutorial",
        ]
        for i, line in enumerate(lines):
            t = font.render(line, True, WHITE)
            screen.blit(t, (WIDTH//2 - 300, 180 + i*40))

    def draw_ui(self):
        # Draw ship
        self.ship.draw(screen)
        
        # Draw goals
        for i, goal in enumerate(self.goals):
            goal_text = font.render(f"{goal.name} ({goal.progress}/10)", True, GREEN)
            screen.blit(goal_text, (20, 20 + i*30))
        
        # Draw resources
        resources_text = font.render(f"Fuel: {self.ship.resources['fuel']} | O2: {self.ship.resources['oxygen']} | Data: {self.ship.resources['data']}", True, BLUE)
        screen.blit(resources_text, (20, HEIGHT - 40))
        
        # Draw log
        for i, line in enumerate(self.log[-5:]):
            text = font.render(line, True, WHITE)
            screen.blit(text, (20, HEIGHT - 150 + i*25))
        
        # Draw key bindings hint
        hint_text = font.render("Press H for help", True, GRAY)
        screen.blit(hint_text, (WIDTH - 200, 20))

    def handle_action(self, action):
        if action == "Progress":
            successes, dice = self.roll_2d20()
            self.add_log(f"Progress roll {dice} -> {successes} successes")
            self.goals[0].mark(successes)
        elif action == "Travel":
            self.add_log("Engaging FTL drive...")
            self.ship.resources["fuel"] -= 2
        elif action == "Arrive":
            self.add_log("Dropping out of FTL...")
        elif action == "Scavenge":
            amount = random.randint(1, 5)
            self.ship.resources["data"] += amount
            self.add_log(f"Scavenged {amount} data units")
        elif action == "Explore":
            self.add_log("Beginning survey...")
            self.ship.resources["oxygen"] -= 1
        elif action == "Resources":
            fuel = self.ship.resources["fuel"]
            oxygen = self.ship.resources["oxygen"]
            data = self.ship.resources["data"]
            self.add_log(f"Resources: Fuel={fuel} O2={oxygen} Data={data}")
        elif action == "Combat":
            self.add_log("Red alert! Battle stations!")
        elif action == "Status":
            self.add_log(f"Position: ({self.ship.x}, {self.ship.y})")

    def run(self):
        while True:
            screen.fill(BLACK)
            # Starfield
            for _ in range(80):
                pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
            pygame.draw.line(screen, (50, 0, 100), (200, 100), (400, 300), 2)

            self.draw_ui()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    # Movement keys
                    if event.key == pygame.K_UP:
                        self.ship.y -= 10
                        self.ship.thrust = 5
                    elif event.key == pygame.K_DOWN:
                        self.ship.y += 10
                        self.ship.thrust = 5
                    elif event.key == pygame.K_LEFT:
                        self.ship.x -= 10
                    elif event.key == pygame.K_RIGHT:
                        self.ship.x += 10
                    
                    # Action keys (1-8)
                    elif event.key in self.key_actions:
                        action = self.key_actions[event.key]
                        self.handle_action(action)
                    
                    # Tutorial
                    elif event.key == pygame.K_SPACE:
                        self.show_tutorial = False
                    elif event.key == pygame.K_h:
                        self.show_tutorial = True

            if self.show_tutorial:
                self.draw_tutorial()

            pygame.display.flip()
            clock.tick(60)
            self.ship.thrust = max(0, self.ship.thrust - 1)

if __name__ == "__main__":
    game = Game()
    game.run()
