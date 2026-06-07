"""
Главный модуль игры Pac-Man.
Точка входа: инициализация pygame, игровой цикл, обработка событий.
"""

import pygame
from settings import (
    WINDOW_SIZE, TIMER_EVENT_TYPE, TIMER_DELAY, FPS,
    load_level
)
from sprites import (
    all_sprites, generate_level
)


def main():
    """Основная функция — запускает игру."""
    pygame.init()
    pygame.display.set_caption('Pac-Man')
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    # загружаем уровень и создаём объекты
    player, level_x, level_y, ghosts = generate_level(load_level('level_blue.txt'))

    # запускаем таймер анимации
    pygame.time.set_timer(TIMER_EVENT_TYPE, TIMER_DELAY)

    running = True
    while running:
        # ===================== Обработка событий =====================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == TIMER_EVENT_TYPE:
                player.forced_image_change()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.rotate_right()
                    player.dx = player.speed
                    player.dy = 0
                elif event.key == pygame.K_LEFT:
                    player.rotate_left()
                    player.dx = -player.speed
                    player.dy = 0
                elif event.key == pygame.K_DOWN:
                    player.rotate_down()
                    player.dx = 0
                    player.dy = player.speed
                elif event.key == pygame.K_UP:
                    player.rotate_up()
                    player.dx = 0
                    player.dy = -player.speed

        # ===================== Обновление состояния =====================
        player.teleport()
        all_sprites.update()

        # проверяем столкновение Пакмэна с привидениями
        ghost_hit = player.check_ghost_collision()
        if ghost_hit:
            print("Game Over! Пакмэна поймало привидение!")
            running = False

        # ===================== Отрисовка =====================
        screen.fill('black')
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
