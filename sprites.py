"""
Модуль спрайтов игры Pac-Man.
Содержит все игровые классы: Tile, Player, Pacman, Ghost.
"""

import pygame
from settings import (
    TILE_WIDTH, TILE_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT,
    PLAYER_SPEED, TIMER_EVENT_TYPE, TIMER_DELAY,
    WINDOW_WIDTH, load_image
)


# ===================== Загрузка изображений =====================
tile_images = {
    'wall': pygame.transform.scale(load_image('blue.png'), (TILE_WIDTH, TILE_HEIGHT))
}

pacman_images = {
    'default': pygame.transform.scale(load_image('pacman_1.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    'eating': pygame.transform.scale(load_image('hungry_pacman.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    'fed': pygame.transform.scale(load_image('fed_pacman.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)),
}

ghost_images = {
    'pink': pygame.transform.scale(load_image('pink_left.png'), (TILE_WIDTH, TILE_HEIGHT))
}


# ===================== Группы спрайтов =====================
# Инициализируются на уровне модуля, чтобы классы могли
# регистрировать себя в группах при создании
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
ghosts_group = pygame.sprite.Group()


# ===================== Tile (стена) =====================
class Tile(pygame.sprite.Sprite):
    """Тайл лабиринта (стена). Размещается на поле по координатам сетки."""

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


# ===================== Player (базовый класс) =====================
class Player(pygame.sprite.Sprite):
    """Базовый класс для всех подвижных персонажей (Пакмэн, привидения).
    Содержит общие методы: move, teleport, spawn."""

    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.dx = 0
        self.dy = 0

    def move(self, dx, dy):
        """Сдвигает персонажа на dx, dy пикселей."""
        self.rect.x += dx
        self.rect.y += dy

    def teleport(self):
        """Телепортирует персонажа на противоположный край экрана."""
        if self.rect.x > WINDOW_WIDTH + PLAYER_WIDTH:
            self.rect.x = -PLAYER_WIDTH
        if self.rect.x < -PLAYER_WIDTH:
            self.rect.x = WINDOW_WIDTH + PLAYER_WIDTH

    def spawn(self, x, y):
        """Устанавливает начальную позицию персонажа."""
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)


# ===================== Pacman =====================
class Pacman(Player):
    """Класс Пакмэна — управляемый игроком персонаж.
    Умеет двигаться, анимировать рот, проверять столкновения со стенами
    и привидениями."""

    ROTATION = 0

    def __init__(self, x, y):
        self.image = pacman_images['default']
        self.anim_frame = 0
        super().__init__(x, y, player_group, all_sprites)
        self.dx = self.speed  # начальное направление — вправо
        self.dy = 0
        self.eating = True
        self.spawn(x, y)
        # кадры анимации: открытый/закрытый рот
        self.anim_sequence = [
            pacman_images['default'],
            pacman_images['eating'],
            pacman_images['default'],
            pacman_images['fed'],
        ]

    def move_and_animate(self, dx, dy):
        """Перемещает Пакмэна и переключает кадр анимации рта."""
        self.rect.x += dx
        self.rect.y += dy

        self.anim_frame = (self.anim_frame + 1) % len(self.anim_sequence)
        current_frame = self.anim_sequence[self.anim_frame]
        self.image = pygame.transform.rotate(current_frame, self.ROTATION)

    def check_wall_collision(self, dx, dy):
        """Проверяет, столкнётся ли Пакмэн со стеной при движении на (dx, dy).
        Создаёт «будущий» прямоугольник и проверяет пересечение с каждой стеной.
        Возвращает True, если столкновение произойдёт."""
        future_rect = self.rect.move(dx, dy)
        for wall in tiles_group:
            if future_rect.colliderect(wall.rect):
                return True
        return False

    def check_ghost_collision(self):
        """Проверяет столкновение Пакмэна с любым привидением.
        Использует pygame.sprite.spritecollideany().
        Возвращает объект Ghost при столкновении, или None."""
        return pygame.sprite.spritecollideany(self, ghosts_group)

    def update(self):
        """Обновляет состояние Пакмэна на каждом кадре:
        1. Проверяет стены — если впереди стена, стоит на месте.
        2. Иначе двигается в текущем направлении (self.dx, self.dy)."""
        if self.check_wall_collision(self.dx, self.dy):
            # стена впереди — стоим, но анимация продолжается
            self.move_and_animate(0, 0)
            self.eating = False
        else:
            # путь свободен — двигаемся
            self.move_and_animate(self.dx, self.dy)
            self.eating = True

    def rotate_up(self):
        self.ROTATION = 90

    def rotate_left(self):
        self.ROTATION = 180

    def rotate_down(self):
        self.ROTATION = -90

    def rotate_right(self):
        self.ROTATION = 0

    def forced_image_change(self):
        """Принудительно переключает кадр анимации (по таймеру)."""
        if self.eating:
            self.anim_frame = (self.anim_frame + 1) % len(self.anim_sequence)


# ===================== Ghost (привидение) =====================
class Ghost(Player):
    """Класс привидения — преследует Пакмэна.
    Пока без ИИ (заготовка для будущих алгоритмов)."""

    def __init__(self, x, y, ghost_type='pink'):
        self.image = ghost_images.get(ghost_type, ghost_images['pink'])
        super().__init__(x, y, ghosts_group, player_group, all_sprites)
        self.ghost_type = ghost_type
        self.spawn(x, y)

    def update(self):
        """Обновление привидения (заготовка для ИИ).
        Пока вызывает только телепорт."""
        self.teleport()


# ===================== Генерация уровня =====================
def generate_level(level):
    """Создаёт игровые объекты по карте уровня.
    Возвращает: (Pacman, level_width, level_height, list[Ghost])."""
    new_player = None
    ghosts = []
    x, y = 0, 0
    for y in range(len(level)):
        for x in range(len(level[y])):
            char = level[y][x]
            if char == '.':
                continue
            elif char == '#':
                Tile('wall', x, y)
            elif char == '@':
                new_player = Pacman(x * TILE_WIDTH, y * TILE_HEIGHT)
            elif char == 'g':
                ghost = Ghost(x * TILE_WIDTH, y * TILE_HEIGHT)
                ghosts.append(ghost)
    return new_player, x, y, ghosts
