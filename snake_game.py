import pygame
import sys
import random
import os

pygame.init()

CELL = 20
WIDTH, HEIGHT = 20, 20
SCREEN_W, SCREEN_H = CELL * WIDTH, CELL * HEIGHT
FPS = 10

THEMES = {
    "dark": {
        "bg": (0, 0, 0),
        "fg": (255, 255, 255),
        "snake": (255, 255, 255),
        "food": (255, 255, 255),
        "grid": (30, 30, 30),
    },
    "light": {
        "bg": (255, 255, 255),
        "fg": (0, 0, 0),
        "snake": (0, 0, 0),
        "food": (0, 0, 0),
        "grid": (230, 230, 230),
    },
}

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def move(self):
        head = self.body[0]
        dx, dy = self.direction
        new_head = ((head[0] + dx) % WIDTH, (head[1] + dy) % HEIGHT)

        if new_head in self.body:
            return False

        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        return True

    def change_direction(self, direction):
        dx, dy = self.direction
        nx, ny = direction
        if (nx, ny) != (-dx, -dy):
            self.direction = (nx, ny)

    def eat(self):
        self.grow = True

    def get_head(self):
        return self.body[0]


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn([])

    def spawn(self, snake_body):
        available = [(x, y) for x in range(WIDTH) for y in range(HEIGHT) if (x, y) not in snake_body]
        if available:
            self.position = random.choice(available)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 18, bold=True)
        self.theme_mode = "dark"
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.direction_queue = []

    @property
    def theme(self):
        return THEMES[self.theme_mode]

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.direction_queue.append((0, -1))
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.direction_queue.append((0, 1))
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    self.direction_queue.append((-1, 0))
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.direction_queue.append((1, 0))
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    else:
                        self.toggle_theme()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused

        if self.direction_queue:
            next_dir = self.direction_queue.pop(0)
            self.snake.change_direction(next_dir)

    def update(self):
        if self.game_over or self.paused:
            return

        if not self.snake.move():
            self.game_over = True
            return

        if self.snake.get_head() == self.food.position:
            self.snake.eat()
            self.food.spawn(self.snake.body)
            self.score += 1

    def draw(self):
        self.screen.fill(self.theme["bg"])

        for x in range(WIDTH):
            for y in range(HEIGHT):
                rect = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)
                if (x, y) in self.snake.body:
                    pygame.draw.rect(self.screen, self.theme["snake"], rect)
                elif (x, y) == self.food.position:
                    pygame.draw.rect(self.screen, self.theme["food"], rect)

        if self.paused:
            self.draw_text("PAUSED", (SCREEN_W // 2, SCREEN_H // 2 - 20))
            self.draw_text("Press P to resume", (SCREEN_W // 2, SCREEN_H // 2 + 10), 14)
        elif self.game_over:
            self.draw_text("GAME OVER", (SCREEN_W // 2, SCREEN_H // 2 - 20))
            self.draw_text(f"Score: {self.score}", (SCREEN_W // 2, SCREEN_H // 2 + 10), 14)
            self.draw_text("Space to restart", (SCREEN_W // 2, SCREEN_H // 2 + 30), 14)

        self.draw_text(f"Score: {self.score}", (10, 10), 16)
        theme_indicator = "DARK" if self.theme_mode == "dark" else "LIGHT"
        self.draw_text(f"Theme: {theme_indicator} [Space]", (SCREEN_W - 170, 10), 12)

        pygame.display.flip()

    def draw_text(self, text, pos, size=18):
        font = pygame.font.SysFont("monospace", size, bold=True)
        surface = font.render(text, True, self.theme["fg"])
        rect = surface.get_rect()
        if pos[0] == SCREEN_W // 2:
            rect.center = pos
        else:
            rect.topleft = pos
        self.screen.blit(surface, rect)

    def reset(self):
        self.snake.reset()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.game_over = False
        self.direction_queue = []

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    os.environ["SDL_VIDEO_WINDOW_POS"] = "400,100"
    game = Game()
    game.run()
