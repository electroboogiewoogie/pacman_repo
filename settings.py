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
PLAYER_SPEED = 5
TIMER_EVENT_TYPE = 30
TIMER_DELAY = 100
FPS = 20

# ===================== Пути к ресурсам =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


# ===================== Функции загрузки =====================
def load_image(name):
    """Загружает изображение из папки data/.
    Завершает программу, если файл не найден."""
    fullname = os.path.join(DATA_DIR, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
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
