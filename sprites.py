"""
Модуль спрайтов игры Pac-Man.
Содержит все игровые классы: Tile, Player, Pacman, Ghost.
"""

import pygame
from settings import (
    TILE_WIDTH, TILE_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT,
    PLAYER_SPEED, TIMER_EVENT_TYPE, TIMER_DELAY,
    WINDOW_WIDTH, WINDOW_HEIGHT, load_image
)

def scale_image(image, target_size):
    """Масштабирует изображение, сохраняя пропорции, вписывая в target_size."""
    w, h = image.get_size()
    ratio = min(target_size / w, target_size / h)
    new_size = (int(w * ratio), int(h * ratio))
    return pygame.transform.smoothscale(image, new_size)

def recolor_ghost(image, target_color):
    """Перекрашивает розового призрака в target_color. Вызывать после scale!"""
    new_image = image.copy()
    w, h = new_image.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, a = new_image.get_at((x, y))
            # Если пиксель розоватый — меняем цвет
            if a > 0 and r > 200 and g < 200 and b > 180:
                lum = (r + g + b) / (3 * 255)
                new_r = min(255, int(target_color[0] * lum * 1.2))
                new_g = min(255, int(target_color[1] * lum * 1.2))
                new_b = min(255, int(target_color[2] * lum * 1.2))
                new_image.set_at((x, y), (new_r, new_g, new_b, a))
    return new_image


# ===================== Загрузка изображений =====================
tile_images = {
    'wall': pygame.transform.scale(load_image('blue.png'), (TILE_WIDTH, TILE_HEIGHT))
}

pacman_images = {
    'default': pygame.transform.scale(load_image('pacman_1.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    'eating': pygame.transform.scale(load_image('hungry_pacman.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)),
    'fed': pygame.transform.scale(load_image('fed_pacman.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)),
}

# базовое изображение розового призрака, смасштабированное до 30x30
base_pink_ghost = pygame.transform.scale(load_image('pink_left.png'), (TILE_WIDTH, TILE_HEIGHT))

ghost_images = {
    'red': recolor_ghost(base_pink_ghost, (255, 0, 0)),        # Blinky
    'pink': base_pink_ghost,                                   # Pinky
    'blue': recolor_ghost(base_pink_ghost, (0, 255, 255)),     # Inky
    'orange': recolor_ghost(base_pink_ghost, (255, 165, 0)),   # Clyde
    'frightened': scale_image(load_image('frightened_ghost.png'), TILE_WIDTH)
}

point_image = pygame.transform.scale(load_image('point.png'), (10, 10))

# ===================== Группы спрайтов =====================
# Инициализируются на уровне модуля, чтобы классы могли
# регистрировать себя в группах при создании
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
ghosts_group = pygame.sprite.Group()
points_group = pygame.sprite.Group()

# ===================== Point (точка) =====================
class Point(pygame.sprite.Sprite):
    """Точка для сбора. Даёт очки."""
    def __init__(self, pos_x, pos_y):
        super().__init__(points_group, all_sprites)
        self.image = point_image
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x * TILE_WIDTH + TILE_WIDTH // 2
        self.rect.centery = pos_y * TILE_HEIGHT + TILE_HEIGHT // 2


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
        Player.__init__(self, x, y, player_group, all_sprites)
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
        """Перемещает Пакмэна и применяет текущий кадр анимации.
        Смена кадра происходит не здесь, а по таймеру в forced_image_change()."""
        self.rect.x += dx
        self.rect.y += dy
        # применяем текущий кадр анимации с поворотом
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
        """Переключает кадр анимации рта (вызывается по таймеру каждые 100мс)."""
        if self.eating:
            self.anim_frame = (self.anim_frame + 1) % len(self.anim_sequence)
            current_frame = self.anim_sequence[self.anim_frame]
            self.image = pygame.transform.rotate(current_frame, self.ROTATION)


# ===================== Ghost (базовое привидение) =====================
class Ghost(Player):
    """Базовый класс привидения с логикой выбора направления на перекрёстках."""

    def __init__(self, x, y, ghost_type, pacman, blinky=None):
        self.image = ghost_images.get(ghost_type, ghost_images['red'])
        Player.__init__(self, x, y, ghosts_group, player_group, all_sprites)
        self.ghost_type = ghost_type
        self.pacman = pacman
        self.blinky = blinky
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2 # скорость должна делить TILE_WIDTH без остатка
        self.dx = -self.speed # по умолчанию идём влево
        self.dy = 0

    def is_on_tile(self):
        """Проверяет, находится ли привидение точно в ячейке сетки."""
        return self.rect.x % TILE_WIDTH == 0 and self.rect.y % TILE_HEIGHT == 0

    def get_target(self):
        """Возвращает целевую точку (x, y). Переопределяется в подклассах."""
        return self.pacman.rect.centerx, self.pacman.rect.centery

    def choose_direction(self, target):
        """Выбирает направление движения на перекрёстке по дистанции до target."""
        directions = {
            'up':    (0, -self.speed),
            'down':  (0, self.speed),
            'left':  (-self.speed, 0),
            'right': (self.speed, 0),
        }
        
        opposite = (-self.dx, -self.dy)
        available = []
        
        for name, (dx, dy) in directions.items():
            # нельзя идти назад, если мы уже двигались
            if (dx, dy) == opposite and (self.dx != 0 or self.dy != 0):
                continue
            
            # проверяем стены
            future_rect = self.rect.move(dx, dy)
            wall_hit = any(future_rect.colliderect(w.rect) for w in tiles_group)
            if not wall_hit:
                available.append((dx, dy))
        
        if not available:
            # тупик — можно идти назад
            if opposite != (0, 0):
                available.append(opposite)
            else:
                return
                
        best_direction = available[0]
        best_distance = float('inf')
        
        # выбираем направление с минимальным расстоянием до цели
        for dx, dy in available:
            next_x = self.rect.x + dx
            next_y = self.rect.y + dy
            # квадрат евклидова расстояния
            dist = (next_x - target[0]) ** 2 + (next_y - target[1]) ** 2
            if dist < best_distance:
                best_distance = dist
                best_direction = (dx, dy)
        
        self.dx, self.dy = best_direction

    def update(self):
        """Обновление привидения."""
        if self.is_on_tile():
            target = self.get_target()
            self.choose_direction(target)
            
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.teleport()


# ===================== Разные виды привидений =====================
class Blinky(Ghost):
    """Красный призрак — преследует Пакмэна напрямую."""
    def __init__(self, x, y, pacman):
        super().__init__(x, y, 'red', pacman)
        
    def get_target(self):
        return self.pacman.rect.centerx, self.pacman.rect.centery


class Pinky(Ghost):
    """Розовый призрак — целится на 4 клетки впереди Пакмэна."""
    def __init__(self, x, y, pacman):
        super().__init__(x, y, 'pink', pacman)
        
    def get_target(self):
        speed = self.pacman.speed if self.pacman.speed != 0 else 1
        dx_tiles = (self.pacman.dx / speed) * TILE_WIDTH * 4
        dy_tiles = (self.pacman.dy / speed) * TILE_HEIGHT * 4
        return self.pacman.rect.centerx + dx_tiles, self.pacman.rect.centery + dy_tiles


class Inky(Ghost):
    """Голубой призрак — использует позицию Пакмэна и позицию Blinky."""
    def __init__(self, x, y, pacman, blinky):
        super().__init__(x, y, 'blue', pacman, blinky)
        
    def get_target(self):
        speed = self.pacman.speed if self.pacman.speed != 0 else 1
        pivot_x = self.pacman.rect.centerx + (self.pacman.dx / speed) * TILE_WIDTH * 2
        pivot_y = self.pacman.rect.centery + (self.pacman.dy / speed) * TILE_HEIGHT * 2
        
        if self.blinky:
            bx, by = self.blinky.rect.centerx, self.blinky.rect.centery
            # вектор от Blinky до pivot умножаем на 2
            tx = pivot_x + (pivot_x - bx)
            ty = pivot_y + (pivot_y - by)
            return tx, ty
        return pivot_x, pivot_y


class Clyde(Ghost):
    """Оранжевый призрак — преследует, пока далеко, но уходит в свой угол, если близко."""
    def __init__(self, x, y, pacman):
        super().__init__(x, y, 'orange', pacman)
        
    def get_target(self):
        dist_sq = (self.rect.centerx - self.pacman.rect.centerx)**2 + (self.rect.centery - self.pacman.rect.centery)**2
        if dist_sq > (8 * TILE_WIDTH)**2:
            return self.pacman.rect.centerx, self.pacman.rect.centery
        else:
            return 0, WINDOW_HEIGHT  # нижний левый угол


# ===================== Генерация уровня =====================
def generate_level(level):
    """Создаёт игровые объекты по карте уровня.
    Возвращает: (Pacman, level_width, level_height, list[Ghost])."""
    # Сначала находим Пакмэна, так как он нужен привидениям
    ghosts = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                new_player = Pacman(x * TILE_WIDTH, y * TILE_HEIGHT)

    # Затем создаём остальные объекты
    blinky_ref = None
    for y in range(len(level)):
        for x in range(len(level[y])):
            char = level[y][x]
            if char == '.':
                Point(x, y)
            elif char == '#':
                Tile('wall', x, y)
            elif char == 'b':
                blinky_ref = Blinky(x * TILE_WIDTH, y * TILE_HEIGHT, new_player)
                ghosts.append(blinky_ref)
            elif char == 'p':
                ghosts.append(Pinky(x * TILE_WIDTH, y * TILE_HEIGHT, new_player))
            elif char == 'i':
                ghosts.append(Inky(x * TILE_WIDTH, y * TILE_HEIGHT, new_player, blinky_ref))
            elif char == 'c':
                ghosts.append(Clyde(x * TILE_WIDTH, y * TILE_HEIGHT, new_player))
    
    return new_player, x, y, ghosts
