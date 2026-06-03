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

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BLUE
        self.hovered = False

    def draw(self, surface):
        color = (150, 200, 255) if self.hovered else BLUE
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.ship = Ship()
        self.goals = [Goal("Reach next sector", "Normal"), Goal("Upgrade scanner", "Easy")]
        self.log = ["Welcome. Tap buttons to play."]
        self.state = "play"
        self.show_tutorial = True
        
        # Mobile-friendly buttons
        self.buttons = [
            Button(WIDTH-200, 50, 180, 50, "Progress"),
            Button(WIDTH-200, 110, 180, 50, "Travel"),
            Button(WIDTH-200, 170, 180, 50, "Arrive"),
            Button(WIDTH-200, 230, 180, 50, "Scavenge"),
            Button(WIDTH-200, 290, 180, 50, "Explore"),
            Button(WIDTH-200, 350, 180, 50, "Resources"),
            Button(WIDTH-200, 410, 180, 50, "Combat"),
            Button(WIDTH-200, 470, 180, 50, "Status"),
        ]
        
        # Movement buttons for mobile
        self.move_buttons = [
            Button(WIDTH//2 - 40, 100, 80, 80, "↑"),
            Button(50, HEIGHT-150, 80, 80, "←"),
            Button(150, HEIGHT-150, 80, 80, "↓"),
            Button(250, HEIGHT-150, 80, 80, "→"),
        ]

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
        overlay = pygame.Surface((WIDTH-200, HEIGHT-200))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (100, 100))
        
        text = big_font.render("TUTORIAL - Solo Voidfarer", True, GREEN)
        screen.blit(text, (WIDTH//2 - 200, 150))
        lines = [
            "Tap arrow buttons to move ship",
            "Tap sidebar buttons for Moves",
            "Progress bars fill as you complete missions",
            "Resources deplete on Travel and Explore",
            "NPCs use Perilous Void tables for dialog",
        ]
        for i, line in enumerate(lines):
            t = font.render(line, True, WHITE)
            screen.blit(t, (150, 220 + i*30))
        
        close_btn = Button(WIDTH//2 - 50, HEIGHT - 150, 100, 50, "Close")
        close_btn.draw(screen)
        return close_btn.rect

    def draw_ui(self):
        # Draw sidebar buttons
        for btn in self.buttons:
            btn.draw(screen)
        
        # Draw movement buttons
        for btn in self.move_buttons:
            btn.draw(screen)
        
        # Draw ship
        self.ship.draw(screen)
        
        # Draw log
        for i, line in enumerate(self.log[-5:]):
            text = font.render(line, True, WHITE)
            screen.blit(text, (20, HEIGHT - 150 + i*25))

    def handle_button(self, btn_text):
        if btn_text == "Progress":
            successes, dice = self.roll_2d20()
            self.add_log(f"Progress roll {dice} -> {successes} successes")
            self.goals[0].mark(successes)

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            screen.fill(BLACK)
            # Starfield
            for _ in range(80):
                pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
            pygame.draw.line(screen, (50, 0, 100), (200, 100), (400, 300), 2)

            self.draw_ui()

            # Update button hovers
            for btn in self.buttons:
                btn.update(mouse_pos)
            for btn in self.move_buttons:
                btn.update(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check movement buttons
                    if self.move_buttons[0].is_clicked(event.pos):  # Up
                        self.ship.y -= 10
                        self.ship.thrust = 5
                    elif self.move_buttons[1].is_clicked(event.pos):  # Left
                        self.ship.x -= 10
                    elif self.move_buttons[2].is_clicked(event.pos):  # Down
                        self.ship.y += 10
                        self.ship.thrust = 5
                    elif self.move_buttons[3].is_clicked(event.pos):  # Right
                        self.ship.x += 10
                    
                    # Check action buttons
                    for btn in self.buttons:
                        if btn.is_clicked(event.pos):
                            self.handle_button(btn.text)
                    
                    # Check tutorial close
                    if self.show_tutorial:
                        tutorial_close = pygame.Rect(WIDTH//2 - 50, HEIGHT - 150, 100, 50)
                        if tutorial_close.collidepoint(event.pos):
                            self.show_tutorial = False

            if self.show_tutorial:
                self.draw_tutorial()

            pygame.display.flip()
            clock.tick(60)
            self.ship.thrust = max(0, self.ship.thrust - 1)

if __name__ == "__main__":
    game = Game()
    game.run()
