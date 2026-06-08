"""
Главный модуль игры Pac-Man.
Точка входа: инициализация pygame, игровой цикл, обработка событий.
"""

import pygame
from settings import (
    WINDOW_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, TIMER_EVENT_TYPE, TIMER_DELAY, FPS,
    load_level, load_image, WAVE_TIMINGS
)

# Инициализируем pygame и создаём окно ДО импорта sprites,
# потому что sprites.py загружает изображения при импорте,
# а .convert_alpha() требует инициализированный дисплей
pygame.init()
pygame.display.set_caption('Pac-Man')
screen = pygame.display.set_mode(WINDOW_SIZE)

from sprites import (
    all_sprites, generate_level, points_group, pellets_group
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

    # Волновой таймер scatter/chase
    wave_index = 0
    wave_timer = WAVE_TIMINGS[0][1] * FPS  # первая волна — scatter 7с
    current_wave_mode = WAVE_TIMINGS[0][0]
    wave_paused = False  # пауза во время frightened

    running = True
    ghost_hit = None
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

        # --- Волновой таймер scatter/chase ---
        any_frightened = any(g.mode == 'frightened' for g in ghosts)
        if not any_frightened:
            if wave_timer is not None:
                wave_timer -= 1
                if wave_timer <= 0:
                    wave_index += 1
                    if wave_index < len(WAVE_TIMINGS):
                        current_wave_mode, duration = WAVE_TIMINGS[wave_index]
                        wave_timer = duration * FPS if duration else None
                        for g in ghosts:
                            if g.mode != 'frightened':
                                g.set_mode(current_wave_mode)
                    else:
                        wave_timer = None  # бесконечный chase

        # проверяем съеденные точки
        points_hit = pygame.sprite.spritecollide(player, points_group, True)
        if points_hit:
            score += 10 * len(points_hit)

        # проверяем съеденные power pellets
        pellets_hit = pygame.sprite.spritecollide(player, pellets_group, True)
        if pellets_hit:
            score += 50 * len(pellets_hit)
            for g in ghosts:
                g.enter_frightened()

        # проверяем столкновение Пакмэна с привидениями
        ghost_hit = player.check_ghost_collision()
        if ghost_hit:
            if ghost_hit.mode == 'frightened':
                # Пакмэн ест испуганного призрака: +200 очков, призрак бежит домой
                score += 200
                ghost_hit.get_eaten()
                ghost_hit = None  # не game over
            elif ghost_hit.mode in ('eaten', 'in_house'):
                # столкновение с глазами / призраком в доме — игнорируем
                ghost_hit = None
            else:
                # нормальный призрак — game over
                print("Game Over! Пакмэна поймало привидение!")
                running = False
            
        # проверяем условие победы (все точки и pellets собраны)
        if len(points_group) == 0 and len(pellets_group) == 0:
            print("Победа! Все точки собраны!")
            running = False

        # ===================== Отрисовка =====================
        screen.fill('black')
        all_sprites.draw(screen)
        
        # рисуем счёт и текущий режим призраков
        mode_text = current_wave_mode.upper()
        if any_frightened:
            mode_text = "FRIGHTENED"
        score_text = font.render(f'Score: {score}  |  {mode_text}', True, (255, 255, 255))
        screen.blit(score_text, (10, WINDOW_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(FPS)

    # после завершения цикла показываем результат
    if ghost_hit:
        game_over_img = pygame.transform.scale(load_image('gameover.png'), WINDOW_SIZE)
        screen.blit(game_over_img, (0, 0))
    else:
        # win_text = font.render("YOU WIN!", True, (0, 255, 0))
        winner_img = pygame.transform.scale(load_image('you_won!.jpeg'), WINDOW_SIZE)
        screen.blit(winner_img, (0, 0)) 
        # screen.blit(win_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2))
        
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == '__main__':
    main()
