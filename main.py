"""
Главный модуль игры Pac-Man.
Точка входа: инициализация pygame, игровой цикл, обработка событий.
"""

import pygame
from settings import (
    WINDOW_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, TIMER_EVENT_TYPE, TIMER_DELAY, FPS,
    load_level, load_image
)

# Инициализируем pygame и создаём окно ДО импорта sprites,
# потому что sprites.py загружает изображения при импорте,
# а .convert_alpha() требует инициализированный дисплей
pygame.init()
pygame.display.set_caption('Pac-Man')
screen = pygame.display.set_mode(WINDOW_SIZE)

from sprites import (
    all_sprites, generate_level, points_group
)


def main():
    """Основная функция — запускает игру."""
    clock = pygame.time.Clock()

    # загружаем уровень и создаём объекты
    player, level_x, level_y, ghosts = generate_level(load_level('level_blue.txt'))

    score = 0
    font = pygame.font.SysFont(None, 36)

    # запускаем таймер анимации
    pygame.time.set_timer(TIMER_EVENT_TYPE, TIMER_DELAY)

    # Окно ожидания старта
    waiting = True
    while waiting:
        screen.fill('black')
        all_sprites.draw(screen)
        
        # Инструкция
        start_text = font.render("PRESS ANY KEY TO START", True, (255, 255, 0))
        screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, WINDOW_HEIGHT // 2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                waiting = False

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

        # проверяем съеденные точки
        points_hit = pygame.sprite.spritecollide(player, points_group, True)
        if points_hit:
            score += 10 * len(points_hit)

        # проверяем столкновение Пакмэна с привидениями
        ghost_hit = player.check_ghost_collision()
        if ghost_hit:
            print("Game Over! Пакмэна поймало привидение!")
            running = False
            
        # проверяем условие победы
        if len(points_group) == 0:
            print("Победа! Все точки собраны!")
            running = False

        # ===================== Отрисовка =====================
        screen.fill('black')
        all_sprites.draw(screen)
        
        # рисуем счёт
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(score_text, (10, WINDOW_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(FPS)

    # после завершения цикла показываем результат
    if ghost_hit:
        game_over_img = pygame.transform.scale(load_image('gameover.png'), WINDOW_SIZE)
        screen.blit(game_over_img, (0, 0))
    else:
        win_text = font.render("YOU WIN!", True, (0, 255, 0))
        screen.blit(win_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2))
        
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == '__main__':
    main()
