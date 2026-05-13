#!/usr/bin/env python3
"""
俄罗斯方块 — 使用 pygame。运行前请先激活 venv 并安装依赖。
"""

import random
import sys

import pygame

# 窗口与网格
CELL = 32
COLS, ROWS = 10, 20
SIDEBAR = 180
WIDTH = COLS * CELL + SIDEBAR
HEIGHT = ROWS * CELL
FPS = 60

# 颜色
BLACK = (18, 18, 24)
GRID_LINE = (40, 42, 55)
BG_TOP = (28, 30, 42)
TEXT = (220, 222, 235)
ACCENT = (130, 180, 255)

# 七种方块颜色 (I O T S Z J L)
COLORS = {
    "I": (80, 220, 250),
    "O": (250, 230, 80),
    "T": (180, 80, 220),
    "S": (80, 220, 120),
    "Z": (240, 80, 90),
    "J": (80, 120, 240),
    "L": (240, 160, 60),
}

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}


def rotate_matrix(m):
    return [list(row) for row in zip(*m[::-1])]


class Piece:
    def __init__(self, kind=None):
        self.kind = kind or random.choice(list(SHAPES.keys()))
        self.cells = [row[:] for row in SHAPES[self.kind]]
        self.x = COLS // 2 - len(self.cells[0]) // 2
        self.y = 0

    def rotate(self):
        self.cells = rotate_matrix(self.cells)


def valid(board, piece, dx=0, dy=0, cells=None):
    c = cells if cells is not None else piece.cells
    for py, row in enumerate(c):
        for px, v in enumerate(row):
            if not v:
                continue
            nx, ny = piece.x + px + dx, piece.y + py + dy
            if nx < 0 or nx >= COLS or ny >= ROWS:
                return False
            if ny >= 0 and board[ny][nx]:
                return False
    return True


def merge(board, piece):
    for py, row in enumerate(piece.cells):
        for px, v in enumerate(row):
            if v and piece.y + py >= 0:
                board[piece.y + py][piece.x + px] = piece.kind


def clear_lines(board):
    new = [r for r in board if any(c == 0 for c in r)]
    cleared = ROWS - len(new)
    empty = [[0] * COLS for _ in range(cleared)]
    return empty + new, cleared


def new_piece():
    return Piece()


def draw_cell(surface, gx, gy, color, border=True):
    x, y = gx * CELL, gy * CELL
    pygame.draw.rect(surface, color, (x + 1, y + 1, CELL - 2, CELL - 2), border_radius=4)
    if border:
        lighter = tuple(min(255, c + 40) for c in color)
        pygame.draw.rect(surface, lighter, (x + 1, y + 1, CELL - 2, CELL - 2), width=2, border_radius=4)


def draw_board(surface, board, ghost_piece=None, current=None):
    for gy in range(ROWS):
        for gx in range(COLS):
            k = board[gy][gx]
            if k:
                draw_cell(surface, gx, gy, COLORS[k])
            else:
                pygame.draw.rect(
                    surface,
                    GRID_LINE,
                    (gx * CELL, gy * CELL, CELL, CELL),
                    width=1,
                )
    if ghost_piece and current:
        for py, row in enumerate(current.cells):
            for px, v in enumerate(row):
                if not v:
                    continue
                gx, gy = current.x + px, ghost_piece.y + py
                if gy >= 0 and not board[gy][gx]:
                    c = COLORS[current.kind]
                    dim = tuple(max(0, c // 4) for c in c)
                    draw_cell(surface, gx, gy, dim, border=False)

    if current:
        for py, row in enumerate(current.cells):
            for px, v in enumerate(row):
                if not v:
                    continue
                gx, gy = current.x + px, current.y + py
                if gy >= 0:
                    draw_cell(surface, gx, gy, COLORS[current.kind])


def ghost_y(board, piece):
    gy = piece.y
    while valid(board, piece, dy=gy - piece.y + 1):
        gy += 1
    return gy


def draw_sidebar(surface, font, score, level, lines, game_over):
    bx = COLS * CELL + 12
    pygame.draw.line(surface, GRID_LINE, (COLS * CELL, 0), (COLS * CELL, HEIGHT), 2)
    y = 24
    for label, val in [
        ("分数", str(score)),
        ("等级", str(level)),
        ("消除行", str(lines)),
    ]:
        t = font.render(label, True, ACCENT)
        surface.blit(t, (bx, y))
        y += 28
        t2 = font.render(val, True, TEXT)
        surface.blit(t2, (bx, y))
        y += 48
    help_lines = [
        "← → 移动",
        "↑ 旋转",
        "↓ 软降",
        "空格 硬降",
        "P 暂停",
        "R 重开",
    ]
    y = HEIGHT // 2 - 40
    small = pygame.font.Font(None, 22)
    for line in help_lines:
        surface.blit(small.render(line, True, TEXT), (bx, y))
        y += 26
    if game_over:
        overlay = pygame.Surface((COLS * CELL, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        big = pygame.font.Font(None, 48)
        msg = big.render("游戏结束", True, (255, 100, 100))
        surface.blit(msg, msg.get_rect(center=(COLS * CELL // 2, HEIGHT // 2 - 20)))
        hint = small.render("按 R 重新开始", True, TEXT)
        surface.blit(hint, hint.get_rect(center=(COLS * CELL // 2, HEIGHT // 2 + 24)))


def main():
    pygame.init()
    pygame.display.set_caption("俄罗斯方块 Tetris")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)

    board = [[0] * COLS for _ in range(ROWS)]
    piece = new_piece()
    if not valid(board, piece):
        print("棋盘已满，请重开。")
        pygame.quit()
        sys.exit(1)

    score = 0
    lines_total = 0
    level = 1
    fall_ms = 800
    fall_acc = 0
    game_over = False
    paused = False

    ghost = Piece()
    ghost.x, ghost.y = piece.x, ghost_y(board, piece)
    ghost.cells = [r[:] for r in piece.cells]
    ghost.kind = piece.kind

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = [[0] * COLS for _ in range(ROWS)]
                    piece = new_piece()
                    score = lines_total = 0
                    level = 1
                    fall_ms = 800
                    game_over = paused = False
                if game_over:
                    continue
                if event.key == pygame.K_p:
                    paused = not paused
                if paused:
                    continue
                if event.key == pygame.K_LEFT and valid(board, piece, dx=-1):
                    piece.x -= 1
                elif event.key == pygame.K_RIGHT and valid(board, piece, dx=1):
                    piece.x += 1
                elif event.key == pygame.K_DOWN and valid(board, piece, dy=1):
                    piece.y += 1
                    score += 1
                elif event.key == pygame.K_UP:
                    rotated = rotate_matrix(piece.cells)
                    if valid(board, piece, cells=rotated):
                        piece.cells = rotated
                elif event.key == pygame.K_SPACE:
                    gy = ghost_y(board, piece)
                    drop = gy - piece.y
                    piece.y = gy
                    score += drop * 2

        if not game_over and not paused:
            fall_acc += dt
            while fall_acc >= fall_ms:
                fall_acc -= fall_ms
                if valid(board, piece, dy=1):
                    piece.y += 1
                else:
                    merge(board, piece)
                    board, n = clear_lines(board)
                    if n:
                        lines_total += n
                        mul = {1: 100, 2: 300, 3: 500, 4: 800}.get(n, 800)
                        score += mul * level
                        level = 1 + lines_total // 10
                        fall_ms = max(120, 800 - (level - 1) * 70)
                    piece = new_piece()
                    if not valid(board, piece):
                        game_over = True
                    break

        ghost.x, ghost.y = piece.x, ghost_y(board, piece)
        ghost.cells = [r[:] for r in piece.cells]
        ghost.kind = piece.kind

        screen.fill(BG_TOP)
        draw_board(screen, board, ghost, piece if not game_over else None)
        draw_sidebar(screen, font, score, level, lines_total, game_over)
        if paused and not game_over:
            s = pygame.Surface((COLS * CELL, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 120))
            screen.blit(s, (0, 0))
            t = pygame.font.Font(None, 40).render("暂停", True, TEXT)
            screen.blit(t, t.get_rect(center=(COLS * CELL // 2, HEIGHT // 2)))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
