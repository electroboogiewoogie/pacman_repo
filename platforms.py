import os
import sys

import pygame

TIMER_EVENT_TYPE = 30
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 600
size = WINDOW_WIDTH, WINDOW_HEIGHT


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(name):
    fullname = os.path.join('../pacman_repo/data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


tile_images = {
    'wall': pygame.transform.scale(load_image('box.png'), (70, 70)),
    'empty': pygame.transform.scale(load_image('grass.png'), (70, 70))
}
player_image = pygame.transform.scale(load_image('pacman_1.png'), (50, 50))

tile_width = tile_height = 70
p_width = p_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Pacman(pygame.sprite.Sprite):
    image_1 = pygame.transform.scale(load_image('pacman_1.png'), (50, 50))
    image_eat = pygame.transform.scale(load_image('hungry_pacman.png'), (50, 50))
    image_fed = pygame.transform.scale(load_image('fed_pacman.png'), (50, 50))
    image_2 = pygame.transform.scale(load_image('pacman_1.png'), (50, 50))
    ROTATION = 0

    def __init__(self, x, y, all_sprites):
        self.image = Pacman.image_1
        self.Num_Image = 0
        super().__init__(player_group, all_sprites)
        self.x = x
        self.y = y
        self.delay = 100
        pygame.time.set_timer(TIMER_EVENT_TYPE, self.delay)
        self.eating = True
        # self.rect = pygame.Rect(x, y, 20, 20)
        self.spawn(x, y)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y

        self.Num_Image = (self.Num_Image + 1) % 4  # открывание и закрывание рта пакмэна
        im = [
            Pacman.image_1,
            Pacman.image_eat,
            Pacman.image_2,
            Pacman.image_fed,
        ]

        tempImage = im[self.Num_Image]

        self.image = pygame.transform.rotate(tempImage, self.ROTATION)

    def check_babah(self, lst_sprites):
        a = []
        for II, b in enumerate(lst_sprites):
            # if II == 0:
            #     continue
            b = b.rect

            def check(a, b, trace):
                PXS = a.x + trace[0]
                PXE = a.x + a.width + trace[0]
                PYS = a.y + trace[1]
                PYE = a.y + a.height + + trace[1]
                BXS = b.x + trace[2]
                BXE = b.x + b.width + trace[2]
                BYS = b.y + trace[3]
                BYE = b.y + b.height + + trace[3]
                checkPacmenLeft = (PXS >= BXS and PXS <= BXE)
                checkPacmenRight = (PXE >= BXS and PXE <= BXE)
                checkPacmenUP = (PYS >= BYS and PYS <= BYE)
                checkPacmenDown = (PYE >= BYS and PYE <= BYE)

                return (checkPacmenLeft or checkPacmenRight) and (checkPacmenUP or checkPacmenDown)

            a.append(check(self.rect, b, [trace[0], trace[1], 0, 0]) or check(b, self.rect, [0, 0, trace[0], trace[1]]))
        b = any(a)
        return b

    def update(self):
        a = horizontal_borders.sprites()[1].rect
        selfPoz = self.rect
        raz = selfPoz.x + selfPoz.width - a.x
        # print(raz)
        # if pygame.sprite.spritecollideany(self, horizontal_borders):
        # tempself=copy.deepcopy(self)
        # tempself.move(trace[0], trace[1])
        # if pygame.sprite.spritecollideany(self, horizontal_borders):
        if self.check_babah(list(horizontal_borders.sprites())):
            # print(f"корд пак: {selfPoz} | корд ст: {a}")
            self.move(0, 0)
            self.eating = False
            return True
        # elif pygame.sprite.spritecollideany(self, vertical_borders):
        #     self.move(0, 0)
        #     self.eating = False
        #     return True
        # else:
        #     self.move(trace[0], trace[1])
        #     self.eating = True
        elif self.check_babah(list(vertical_borders.sprites())):
            self.move(0, 0)
            self.eating = False
            return True
            # elif pygame.sprite.spritecollideany(self, horizontal_borders):
            #     self.move(0, 0)
            #     self.eating = False
            #     return True
        else:
            self.move(trace[0], trace[1])
            self.eating = True

    def spawn(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)

    def rotate_UP(self):
        # self.image = pygame.transform.rotate(Pacman.image_1, 90)
        self.ROTATION = 90

    def rotate_LEFT(self):
        # self.image = pygame.transform.rotate(Pacman.image_1, 180)
        self.ROTATION = 180

    def rotate_DOWN(self):
        # self.image = pygame.transform.rotate(Pacman.image_1, -90)
        self.ROTATION = -90

    def rotate_RIGHT(self):
        # self.image = pygame.transform.rotate(Pacman.image_1, 0)
        self.ROTATION = 0

    def forcedImageChange(self):
        # self.image = pygame.transform.rotate(Pacman.image_1, 0)
        if self.eating:
            self.Num_Image = (self.Num_Image + 1) % 4


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        # super().__init__(all_sprites)
        # self.add(vertical_borders)
        # self.image = pygame.Surface([50, 10])
        # self.image.fill((125, 125, 125))
        # self.rect = pygame.Rect(x1, y1, 50, 10)
        super().__init__(all_sprites)
        # if x1 == x2:  # вертикальная стенка
        #     self.add(vertical_borders)
        #     self.image = pygame.Surface([100, 10])
        #     self.image.fill((125, 125, 125))
        #     self.rect = pygame.Rect(x1, y1, 100, 10)
        # else:  # горизонтальная стенка
        self.add(horizontal_borders)
        self.image = pygame.Surface([x2, y2])
        self.image.fill((125, 125, 125))
        self.rect = pygame.Rect(x1, y1, x2, y2)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('пакпак')
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))
    running = True
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    clock = pygame.time.Clock()
    tetric = '0'
    b = False

    Border(0, 0, WINDOW_WIDTH, 15)
    Border(0, 0, 15, WINDOW_HEIGHT)
    Border(0, WINDOW_WIDTH - 15, WINDOW_WIDTH, 15)
    Border(WINDOW_HEIGHT - 15, 0, 15, WINDOW_HEIGHT)
    Border(WINDOW_HEIGHT - 15, 0, 15, WINDOW_HEIGHT)

    trace = (10, 0)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == TIMER_EVENT_TYPE:
                tetric.forcedImageChange()
                # tetric.(trace[0], trace[1])
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if not b:
                        tetric = Pacman(event.pos[0], event.pos[1], all_sprites)
                        b = not b
                    else:
                        tetric.spawn(event.pos[0], event.pos[1])
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    tetric.rotate_RIGHT()
                    trace = (5, 0)
                    # tetric.move(trace[0], trace[1])
                if event.key == pygame.K_LEFT:
                    tetric.rotate_LEFT()
                    trace = (- 5, 0)
                    # tetric.move(trace[0], trace[1])

                if event.key == pygame.K_DOWN:
                    trace = (0, 5)
                    # tetric.move(trace[0], trace[1])
                    tetric.rotate_DOWN()

                if event.key == pygame.K_UP:
                    trace = (0, - 5)
                    # tetric.move(trace[0], trace[1])
                    tetric.rotate_UP()
                if event.key == pygame.K_SPACE:
                    all_sprites.update()
        all_sprites.update()
        screen.fill('black')
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(20)
