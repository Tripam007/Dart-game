import math
import sys
import random
import pygame
from pygame import gfxdraw

"""
Darts Arcade (Click-To-Throw with Realistic Throws)
---------------------------------------------------
- Single player: 10 darts. Click the dartboard to "throw" a dart.
- Dart throws are now slightly random, simulating real-life inaccuracy.
- Scores calculated according to standard dartboard rules.
- After 10 throws, total is displayed. Press R to restart, ESC to quit.

Requirements:
- Python 3.8+
- pygame (pip install pygame)
"""

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
BOARD_RADIUS = 250
CENTER = (WIDTH // 2, HEIGHT // 2)
THROWS_PER_GAME = 10
DEVIATION = 20  # pixels of inaccuracy per throw

# Board ring radii as proportions of BOARD_RADIUS
R_OUTER_BOARD = 1.00
R_DOUBLE_INNER = 0.90
R_SINGLE_OUTER = 0.62
R_TRIPLE_OUTER = 0.57
R_TRIPLE_INNER = 0.47
R_SINGLE_INNER = 0.25
R_OUTER_BULL  = 0.12
R_INNER_BULL  = 0.05

# Standard dartboard numbering (clockwise, with 20 at the top)
DART_NUMBERS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17,
                3, 19, 7, 16, 8, 11, 14, 9, 12, 5]

# Colors
BG_COLOR = (18, 20, 26)
WHITE = (240, 240, 240)
BLACK = (10, 10, 10)
RED = (180, 30, 30)
GREEN = (30, 150, 60)
GOLD = (210, 170, 30)
RING_LINE = (40, 40, 40)
HIT_DOT = (240, 240, 240)

def draw_aa_filled_circle(surface, x, y, r, color):
    gfxdraw.filled_circle(surface, x, y, r, color)
    gfxdraw.aacircle(surface, x, y, r, color)

def draw_wedge(surface, center, r_outer, r_inner, angle_start_deg, angle_end_deg, color):
    cx, cy = center
    steps = max(16, int((angle_end_deg - angle_start_deg) / 2))
    pts = []
    for i in range(steps + 1):
        a = math.radians(angle_start_deg + (angle_end_deg - angle_start_deg) * i / steps)
        x = cx + int(math.cos(a) * r_outer)
        y = cy + int(math.sin(a) * r_outer)
        pts.append((x, y))
    for i in range(steps + 1):
        a = math.radians(angle_end_deg - (angle_end_deg - angle_start_deg) * i / steps)
        x = cx + int(math.cos(a) * r_inner)
        y = cy + int(math.sin(a) * r_inner)
        pts.append((x, y))
    pygame.gfxdraw.aapolygon(surface, pts, color)
    pygame.gfxdraw.filled_polygon(surface, pts, color)

def angle_to_number(angle_deg):
    a = (angle_deg - 90) % 360
    a_cw = (-a) % 360
    sector = int(a_cw // 18) % 20
    return DART_NUMBERS[sector]

def point_to_score(px, py):
    cx, cy = CENTER
    dx = px - cx
    dy = py - cy
    r = math.hypot(dx, dy)
    if r > BOARD_RADIUS:
        return 0, "Miss"
    angle = math.degrees(math.atan2(dy, dx))
    number = angle_to_number(angle)
    rnorm = r / BOARD_RADIUS
    if rnorm <= R_INNER_BULL:
        return 50, "Inner Bull (50)"
    elif rnorm <= R_OUTER_BULL:
        return 25, "Outer Bull (25)"
    elif rnorm <= R_SINGLE_INNER:
        return number, f"Single {number}"
    elif rnorm <= R_TRIPLE_INNER:
        return number, f"Single {number}"
    elif rnorm <= R_TRIPLE_OUTER:
        return 3 * number, f"Triple {number}"
    elif rnorm <= R_SINGLE_OUTER:
        return number, f"Single {number}"
    elif rnorm <= R_DOUBLE_INNER:
        return 2 * number, f"Double {number}"
    else:
        return 0, "Miss"

def draw_board(surface):
    cx, cy = CENTER
    surface.fill(BG_COLOR)
    draw_aa_filled_circle(surface, cx, cy, BOARD_RADIUS, BLACK)
    for i in range(20):
        start = -90 - i * 18
        end = start - 18
        base_color = GREEN if i % 2 == 0 else RED
        draw_wedge(surface, CENTER,
                   int(BOARD_RADIUS * R_SINGLE_OUTER),
                   int(BOARD_RADIUS * R_TRIPLE_OUTER),
                   end, start, base_color)
        draw_wedge(surface, CENTER,
                   int(BOARD_RADIUS * R_TRIPLE_INNER),
                   int(BOARD_RADIUS * R_SINGLE_INNER),
                   end, start, base_color)
    for i in range(20):
        start = -90 - i * 18
        end = start - 18
        color = GOLD if i % 2 == 0 else WHITE
        draw_wedge(surface, CENTER,
                   int(BOARD_RADIUS * R_TRIPLE_OUTER),
                   int(BOARD_RADIUS * R_TRIPLE_INNER),
                   end, start, color)
    for i in range(20):
        start = -90 - i * 18
        end = start - 18
        color = GOLD if i % 2 == 0 else WHITE
        draw_wedge(surface, CENTER,
                   int(BOARD_RADIUS * R_OUTER_BOARD),
                   int(BOARD_RADIUS * R_DOUBLE_INNER),
                   end, start, color)
    draw_aa_filled_circle(surface, cx, cy, int(BOARD_RADIUS * R_OUTER_BULL), GREEN)
    draw_aa_filled_circle(surface, cx, cy, int(BOARD_RADIUS * R_INNER_BULL), RED)
    for rprop in [R_DOUBLE_INNER, R_SINGLE_OUTER, R_TRIPLE_OUTER, R_TRIPLE_INNER,
                  R_SINGLE_INNER, R_OUTER_BULL, R_INNER_BULL]:
        pygame.gfxdraw.aacircle(surface, cx, cy, int(BOARD_RADIUS * rprop), RING_LINE)
    font = pygame.font.SysFont(None, 28, bold=True)
    for i, num in enumerate(DART_NUMBERS):
        ang_deg = -90 - i * 18 - 9
        a = math.radians(ang_deg)
        rx = int(math.cos(a) * (BOARD_RADIUS + 25))
        ry = int(math.sin(a) * (BOARD_RADIUS + 25))
        text = font.render(str(num), True, WHITE)
        rect = text.get_rect(center=(cx + rx, cy + ry))
        surface.blit(text, rect)

def main():
    pygame.init()
    pygame.display.set_caption("Darts Arcade (Realistic Throws)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    big = pygame.font.SysFont(None, 48, bold=True)
    mid = pygame.font.SysFont(None, 32)
    small = pygame.font.SysFont(None, 24)
    throws_left = THROWS_PER_GAME
    score_total = 0
    last_shot_text = "Click the board to throw!"
    hits = []
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    throws_left = THROWS_PER_GAME
                    score_total = 0
                    last_shot_text = "New game! Click the board to throw!"
                    hits.clear()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if throws_left > 0:
                    mx, my = pygame.mouse.get_pos()
                    # --- Randomized throw ---
                    mx_real = mx + random.randint(-DEVIATION, DEVIATION)
                    my_real = my + random.randint(-DEVIATION, DEVIATION)
                    s, desc = point_to_score(mx_real, my_real)
                    score_total += s
                    throws_left -= 1
                    last_shot_text = f"{desc}: +{s} points"
                    hits.append((mx_real, my_real))

        draw_board(screen)
        for (hx, hy) in hits:
            pygame.gfxdraw.filled_circle(screen, hx, hy, 5, HIT_DOT)
            pygame.gfxdraw.aacircle(screen, hx, hy, 5, BLACK)

        panel_y = 40
        title = big.render("DARTS ARCADE", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, panel_y)))
        info_text = mid.render(f"Throws left: {throws_left}   Total: {score_total}", True, WHITE)
        screen.blit(info_text, info_text.get_rect(center=(WIDTH//2, panel_y + 40)))
        last = mid.render(last_shot_text, True, WHITE)
        screen.blit(last, last.get_rect(center=(WIDTH//2, panel_y + 80)))
        hint1 = small.render("Controls: Left-click = throw | R = restart | ESC = quit", True, WHITE)
        screen.blit(hint1, hint1.get_rect(center=(WIDTH//2, HEIGHT - 30)))
        if throws_left == 0:
            over = big.render(f"Game Over! Final Score: {score_total}", True, WHITE)
            screen.blit(over, over.get_rect(center=(WIDTH//2, HEIGHT - 70)))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
