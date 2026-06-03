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
        # Improved ship sprite with panels and thrusters
        pygame.draw.polygon(surface, BLUE, [(self.x, self.y-20), (self.x-20, self.y+20), (self.x+20, self.y+20)])
        pygame.draw.rect(surface, WHITE, (self.x-8, self.y-8, 16, 16))  # cockpit
        pygame.draw.rect(surface, GRAY, (self.x-15, self.y+10, 30, 8))  # body panels
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
        self.log = ["Welcome. Press T for tutorial."]
        self.state = "play"
        self.current_npc = None
        self.dialog_text = ""
        self.show_tutorial = True

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
        pygame.draw.rect(screen, (0, 0, 0, 200), (100, 100, WIDTH-200, HEIGHT-200))
        text = big_font.render("TUTORIAL - Solo Voidfarer", True, GREEN)
        screen.blit(text, (WIDTH//2 - 200, 150))
        lines = [
            "Arrow keys move ship",
            "Click sidebar buttons for Moves",
            "Progress bars fill as you complete missions",
            "Resources deplete on Travel and Explore",
            "NPCs use Perilous Void tables for dialog",
            "Press T to close tutorial"
        ]
        for i, line in enumerate(lines):
            t = font.render(line, True, WHITE)
            screen.blit(t, (150, 220 + i*30))

    def draw_ui(self):
        # Sidebar buttons with hover glow
        buttons = ["Progress", "Travel", "Arrive", "Scavenge", "Explore", "Resources", "Combat", "Status"]
        for i, btn in enumerate(buttons):
            rect = pygame.Rect(WIDTH-200, 50 + i*60, 180, 50)
            color = BLUE
            if rect.collidepoint(pygame.mouse.get_pos()):
                color = (150, 200, 255)
            pygame.draw.rect(screen, color, rect)
            text = font.render(btn, True, WHITE)
            screen.blit(text, (WIDTH-190, 65 + i*60))

        # Improved status panel
        self.ship.draw(screen)
        for i, line in enumerate(self.log[-5:]):
            text = font.render(line, True, WHITE)
            screen.blit(text, (20, HEIGHT - 150 + i*25))

    def handle_button(self, btn):
        if btn == "Progress":
            successes, dice = self.roll_2d20()
            self.add_log(f"Progress roll {dice} -> {successes} successes")
            self.goals[0].mark(successes)

    def run(self):
        while True:
            screen.fill(BLACK)
            # Improved starfield with nebula lines
            for _ in range(80):
                pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
            pygame.draw.line(screen, (50, 0, 100), (200, 100), (400, 300), 2)  # nebula example

            self.ship.draw(screen)
            self.draw_ui()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        self.show_tutorial = False
                    if event.key == pygame.K_UP:
                        self.ship.y -= 10
                        self.ship.thrust = 5
                    if event.key == pygame.K_DOWN:
                        self.ship.y += 10
                    if event.key == pygame.K_LEFT:
                        self.ship.x -= 10
                    if event.key == pygame.K_RIGHT:
                        self.ship.x += 10
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if WIDTH - 200 < mx < WIDTH:
                        btn_index = (my - 50) // 60
                        if 0 <= btn_index < 8:
                            buttons = ["Progress", "Travel", "Arrive", "Scavenge", "Explore", "Resources", "Combat", "Status"]
                            self.handle_button(buttons[btn_index])

            if self.show_tutorial:
                self.draw_tutorial()

            pygame.display.flip()
            clock.tick(60)
            self.ship.thrust = max(0, self.ship.thrust - 1)

if __name__ == "__main__":
    game = Game()
    game.run()
