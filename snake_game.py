import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple


CELL_SIZE = 20
GRID_W = 30
GRID_H = 25
SCREEN_W = CELL_SIZE * GRID_W
SCREEN_H = CELL_SIZE * GRID_H
FPS = 10

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (0,   200, 0)
DKGREEN= (0,   140, 0)
RED    = (200, 0,   0)
GRAY   = (40,  40,  40)


class Direction(Enum):
    UP    = (0, -1)
    DOWN  = (0,  1)
    LEFT  = (-1, 0)
    RIGHT = (1,  0)

    def opposite(self) -> "Direction":
        return {
            Direction.UP:    Direction.DOWN,
            Direction.DOWN:  Direction.UP,
            Direction.LEFT:  Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[self]


class Food:
    def __init__(self) -> None:
        self.pos: Tuple[int, int] = (0, 0)
        self.respawn([])

    def respawn(self, occupied: List[Tuple[int, int]]) -> None:
        while True:
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            if (x, y) not in occupied:
                self.pos = (x, y)
                return

    def draw(self, surface: pygame.Surface) -> None:
        r = pygame.Rect(self.pos[0] * CELL_SIZE, self.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, r)
        pygame.draw.rect(surface, WHITE, r, 1)


class Snake:
    def __init__(self) -> None:
        cx, cy = GRID_W // 2, GRID_H // 2
        self.body: List[Tuple[int, int]] = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = Direction.RIGHT
        self._next_dir = Direction.RIGHT
        self.grew = False

    # ── input ─────────────────────────────────────────────────────────────
    def set_direction(self, new_dir: Direction) -> None:
        if new_dir != self.direction.opposite():
            self._next_dir = new_dir

    # ── logic ─────────────────────────────────────────────────────────────
    def move(self) -> None:
        self.direction = self._next_dir
        dx, dy = self.direction.value
        head = (self.body[0][0] + dx, self.body[0][1] + dy)
        self.body.insert(0, head)
        if not self.grew:
            self.body.pop()
        self.grew = False

    def grow(self) -> None:
        self.grew = True

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def is_dead(self) -> bool:
        hx, hy = self.head
        if not (0 <= hx < GRID_W and 0 <= hy < GRID_H):
            return True
        if self.head in self.body[1:]:
            return True
        return False

    # ── rendering ─────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        for i, (x, y) in enumerate(self.body):
            color = GREEN if i == 0 else DKGREEN
            r = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, r)
            pygame.draw.rect(surface, BLACK, r, 1)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("monospace", 48, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 24)
        self._new_game()

    def _new_game(self) -> None:
        self.snake = Snake()
        self.food  = Food()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.running = True
        self.game_over = False

    # ── main loop ─────────────────────────────────────────────────────────
    def run(self) -> None:
        while True:
            self._handle_events()
            if not self.game_over:
                self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_events(self) -> None:
        key_map = {
            pygame.K_UP:    Direction.UP,
            pygame.K_DOWN:  Direction.DOWN,
            pygame.K_LEFT:  Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_w:     Direction.UP,
            pygame.K_s:     Direction.DOWN,
            pygame.K_a:     Direction.LEFT,
            pygame.K_d:     Direction.RIGHT,
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.game_over and event.key == pygame.K_RETURN:
                    self._new_game()
                    return
                if event.key in key_map:
                    self.snake.set_direction(key_map[event.key])

    def _update(self) -> None:
        self.snake.move()
        if self.snake.is_dead():
            self.game_over = True
            return
        if self.snake.head == self.food.pos:
            self.snake.grow()
            self.score += 10
            self.food.respawn(self.snake.body)

    # ── drawing ───────────────────────────────────────────────────────────
    def _draw(self) -> None:
        self.screen.fill(GRAY)
        self._draw_grid()
        self.food.draw(self.screen)
        self.snake.draw(self.screen)
        self._draw_hud()
        if self.game_over:
            self._draw_game_over()
        pygame.display.flip()

    def _draw_grid(self) -> None:
        for x in range(0, SCREEN_W, CELL_SIZE):
            pygame.draw.line(self.screen, (50, 50, 50), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, CELL_SIZE):
            pygame.draw.line(self.screen, (50, 50, 50), (0, y), (SCREEN_W, y))

    def _draw_hud(self) -> None:
        label = self.font_small.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(label, (8, 6))

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        go_surf = self.font_big.render("GAME OVER", True, RED)
        sc_surf = self.font_small.render(f"Score: {self.score}", True, WHITE)
        re_surf = self.font_small.render("Press ENTER to restart", True, WHITE)

        cx = SCREEN_W // 2
        self.screen.blit(go_surf, go_surf.get_rect(center=(cx, SCREEN_H // 2 - 50)))
        self.screen.blit(sc_surf, sc_surf.get_rect(center=(cx, SCREEN_H // 2 + 10)))
        self.screen.blit(re_surf, re_surf.get_rect(center=(cx, SCREEN_H // 2 + 50)))


if __name__ == "__main__":
    Game().run()
