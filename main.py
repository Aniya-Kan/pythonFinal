import pygame
import sys

# === Настройки ===
WIDTH, HEIGHT = 1000, 600
FPS = 60
JUMP_FORCE = -12
MOVE_FORCE = 5
ROTATION_SPEED = 5
GRAVITY = 0.6

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Super Bunny Physics")

# === Цвета ===
WHITE = (255, 255, 255)
BLUE = (80, 80, 255)
PINK = (255, 100, 180)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

# === Игрок ===
class Player:
    def __init__(self, x, y, color, controls):
        self.color = color
        self.rect = pygame.Rect(x, y, 40, 60)
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0
        self.on_ground = False
        self.controls = controls
        self.grabbing = False
        self.holding = None

    def update(self, keys, platforms, other):
        # Движение
        if keys[self.controls['left']]:
            self.vel.x = -MOVE_FORCE
            self.angle -= ROTATION_SPEED
        elif keys[self.controls['right']]:
            self.vel.x = MOVE_FORCE
            self.angle += ROTATION_SPEED
        else:
            self.vel.x = 0

        # Прыжок
        if keys[self.controls['jump']] and self.on_ground:
            self.vel.y = JUMP_FORCE
            self.on_ground = False

        # Гравитация
        if not self.on_ground:
            self.vel.y += GRAVITY
        else:
            # Если на земле, скорость по Y обнуляется
            if self.vel.y > 0:
                self.vel.y = 0

        self.pos += self.vel

        # Захват
        self.grabbing = keys[self.controls['grab']] or keys[self.controls['alt_grab']]
        if self.grabbing and self.rect.colliderect(other.rect):
            if not self.holding:
                self.holding = other
        elif not self.grabbing:
            self.holding = None

        # Если держим другого игрока, не изменяем его вертикальную скорость
        if self.holding:
            offset = pygame.Vector2(0, -self.rect.height)
            other.pos = self.pos + offset
            other.vel.x = self.vel.x  # Применяем только горизонтальную скорость

        self.rect.topleft = self.pos

        # Проверка коллизий с платформами
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y > 0:
                    self.pos.y = platform.rect.top - self.rect.height
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.pos.y = platform.rect.bottom
                    self.vel.y = 0

        # Проверка на взаимодействие с другим игроком
        if self.rect.colliderect(other.rect) and self.vel.y > 0:
            self.pos.y = other.rect.top - self.rect.height
            self.vel.y = 0
            self.on_ground = True

        self.rect.topleft = self.pos

    def draw(self, surface):
        rotated_image = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.rect(rotated_image, self.color, (0, 0, 40, 60))
        rotated_image = pygame.transform.rotate(rotated_image, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, rotated_rect.topleft)

# === Объекты уровня ===
class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)

class Spike:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
    def draw(self, surface):
        pygame.draw.polygon(surface, RED, [
            (self.rect.left, self.rect.bottom),
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.bottom)
        ])

class Portal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 80)
    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect, border_radius=10)

# === Уровни ===
levels = [
    {
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40),
            (300, 500, 200, 20),
            (600, 400, 200, 20),
            (850, 300, 100, 20),
        ],
        "spikes": [
            (500, HEIGHT - 80),
            (540, HEIGHT - 80)
        ],
        "portal": (900, 220),
        "start_pos": ((100, 100), (150, 100))
    },
    {
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40),
            (200, 450, 150, 20),
            (400, 370, 150, 20),
            (650, 290, 150, 20),
            (850, 210, 100, 20),
        ],
        "spikes": [
            (350, HEIGHT - 80),
            (700, HEIGHT - 80),
            (740, HEIGHT - 80)
        ],
        "portal": (900, 130),
        "start_pos": ((50, 100), (100, 100))
    },
    {
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40),
            (300, 500, 200, 20),
            (500, 400, 150, 20),
            (700, 300, 100, 20),
        ],
        "spikes": [
            (400, HEIGHT - 80),
            (600, HEIGHT - 80)
        ],
        "portal": (900, 220),
        "start_pos": ((100, 100), (150, 100))
    },
    {
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40),
            (200, 500, 150, 20),
            (400, 450, 150, 20),
            (600, 400, 100, 20),
        ],
        "spikes": [
            (500, HEIGHT - 80),
            (700, HEIGHT - 80),
            (740, HEIGHT - 80)
        ],
        "portal": (900, 180),
        "start_pos": ((100, 100), (150, 100))
    },
    {
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40),
            (300, 500, 200, 20),
            (500, 400, 200, 20),
            (850, 300, 100, 20),
        ],
        "spikes": [
            (500, HEIGHT - 80),
            (600, HEIGHT - 80)
        ],
        "portal": (900, 220),
        "start_pos": ((100, 100), (150, 100))
    }
]

def load_level(index):
    data = levels[index]
    platforms = [Platform(*p) for p in data["platforms"]]
    spikes = [Spike(*s) for s in data["spikes"]]
    portal = Portal(*data["portal"])
    start_pos = data["start_pos"]
    return platforms, spikes, portal, start_pos

# === Меню выбора уровня ===
def level_selection():
    font = pygame.font.Font(None, 74)
    text = font.render("Select Level", True, BLUE)
    screen.fill(WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
    
    level_texts = ["Level " + str(i + 1) for i in range(len(levels))]
    selected_level = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected_level > 0:
                    selected_level -= 1
                elif event.key == pygame.K_DOWN and selected_level < len(levels) - 1:
                    selected_level += 1
                elif event.key == pygame.K_RETURN:
                    return selected_level

        # Отрисовка меню выбора уровня
        for i, level in enumerate(level_texts):
            level_label = font.render(level, True, BLUE)
            screen.blit(level_label, (WIDTH // 2 - level_label.get_width() // 2, HEIGHT // 2 + i * 60))
        selected_label = font.render(">", True, BLUE)
        screen.blit(selected_label, (WIDTH // 2 - selected_label.get_width() // 2 - 50, HEIGHT // 2 + selected_level * 60))
        pygame.display.flip()

# === Игроки и первый уровень ===
controls_p1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'grab': pygame.K_LSHIFT, 'alt_grab': pygame.K_RETURN}
controls_p2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'grab': pygame.K_RSHIFT, 'alt_grab': pygame.K_KP_ENTER}

# === Игровой цикл ===
level_index = level_selection()  # Показываем меню выбора уровня
platforms, spikes, portal, (p1_start, p2_start) = load_level(level_index)

player1 = Player(*p1_start, BLUE, controls_p1)
player2 = Player(*p2_start, PINK, controls_p2)

while True:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    player1.update(keys, platforms, player2)
    player2.update(keys, platforms, player1)

    # Проверка на шипы
    for spike in spikes:
        if player1.rect.colliderect(spike.rect) or player2.rect.colliderect(spike.rect):
            player1.pos = pygame.Vector2(p1_start)
            player2.pos = pygame.Vector2(p2_start)
            player1.vel = player2.vel = pygame.Vector2(0, 0)

    # Проверка на портал: если оба игрока касаются портала
    if portal.rect.colliderect(player1.rect) and portal.rect.colliderect(player2.rect):
        level_index += 1
        if level_index >= len(levels):
            print("Game complete!")
            pygame.quit()
            sys.exit()
        platforms, spikes, portal, (p1_start, p2_start) = load_level(level_index)
        player1.pos = pygame.Vector2(p1_start)
        player2.pos = pygame.Vector2(p2_start)
        player1.vel = player2.vel = pygame.Vector2(0, 0)

    # Отрисовка
    for platform in platforms:
        platform.draw(screen)
    for spike in spikes:
        spike.draw(screen)
    portal.draw(screen)

    player1.draw(screen)
    player2.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
