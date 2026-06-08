"""
Модуль настроек игры Pac-Man.
Содержит все константы: размеры окна, тайлов, скорость, а также
вспомогательные функции загрузки ресурсов (изображения, уровни).
"""

import os
import sys
import pygame

# ===================== Параметры окна =====================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# ===================== Размеры тайлов и игрока =====================
TILE_WIDTH = 30
TILE_HEIGHT = 30
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 20

# ===================== Игровые параметры =====================
PLAYER_SPEED = 2.2
TIMER_EVENT_TYPE = 30
TIMER_DELAY = 40
FPS = 60
GHOST_SPEED_CHASE = 2      # в chase — такой же как у Пакмэна (должен делить TILE_WIDTH)
GHOST_SPEED_SCATTER = 2    # в scatter — такой же (ИИ делает их "тупее")
GHOST_SPEED_FRIGHTENED = 1 # в frightened — медленнее (1 делит 30)
GHOST_SPEED_EATEN = 5      # съеденный призрак быстро бежит домой (5 делит 30)
GHOST_FRIGHTENED_DURATION = 6  # секунд в frightened-режиме

# Задержки выхода из базы (в секундах). Blinky = 0, сразу на поле.
GHOST_EXIT_DELAYS = {
    'red': 0,
    'pink': 3,
    'blue': 6,
    'orange': 9,
}

# Волновой алгоритм scatter/chase для уровня 1 (в секундах)
# (режим, длительность). Последний chase — бесконечный.
WAVE_TIMINGS = [
    ('scatter', 7),
    ('chase', 20),
    ('scatter', 7),
    ('chase', 20),
    ('scatter', 5),
    ('chase', 20),
    ('scatter', 5),
    ('chase', None),  # бесконечный chase
]

# Углы scatter для каждого типа призрака
SCATTER_CORNERS = {
    'red':    (WINDOW_WIDTH, 0),              # правый верхний
    'pink':   (0, 0),                          # левый верхний
    'blue':   (WINDOW_WIDTH, WINDOW_HEIGHT),   # правый нижний
    'orange': (0, WINDOW_HEIGHT),              # левый нижний
}

# ===================== Пути к ресурсам =====================
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


# ===================== Функции загрузки =====================
def load_image(name):
    """Загружает изображение из папки data/.
    Завершает программу, если файл не найден."""
    fullname = os.path.join(DATA_DIR, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname).convert_alpha()
    return image


def load_level(filename):
    """Загружает карту уровня из текстового файла.
    Каждая строка файла — строка лабиринта.
    Символы: '#' — стена, '.' — пустая клетка, '@' — Пакмэн, 'g' — привидение."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r') as map_file:
        level_map = [line.strip() for line in map_file]

    # подсчитываем максимальную ширину и дополняем короткие строки
    max_width = max(map(len, level_map))
    return list(map(lambda row: row.ljust(max_width, '.'), level_map))
