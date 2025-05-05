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

        self.pos += self.vel

        # Захват
        self.grabbing = keys[self.controls['grab']] or keys[self.controls['alt_grab']]
        if self.grabbing and self.rect.colliderect(other.rect):
            if not self.holding:
                self.holding = other
        elif not self.grabbing:
            self.holding = None

        if self.holding:
            offset = pygame.Vector2(0, -self.rect.height)
            other.pos = self.pos + offset
            other.vel.x = self.vel.x  # Копируем только горизонтальную скорость

        self.rect.topleft = self.pos

        # Коллизии с платформами
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

        # Стояние на другом игроке
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

# === Платформа ===
class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)

# === Шипы ===
class Spike:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self, surface):
        pygame.draw.polygon(surface, RED, [
            (self.rect.left, self.rect.bottom),
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.bottom)
        ])

# === Портал ===
class Portal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 80)

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect, border_radius=10)

# === Уровень ===
def load_level():
    platforms = [
        Platform(0, HEIGHT - 40, WIDTH, 40),
        Platform(300, 500, 200, 20),
        Platform(600, 400, 200, 20),
        Platform(850, 300, 100, 20),
    ]
    spikes = [
        Spike(500, HEIGHT - 80),
        Spike(540, HEIGHT - 80)
    ]
    portal = Portal(900, 220)
    return platforms, spikes, portal

# === Игроки ===
controls_p1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'grab': pygame.K_LSHIFT, 'alt_grab': pygame.K_RETURN}
controls_p2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'grab': pygame.K_RSHIFT, 'alt_grab': pygame.K_KP_ENTER}

player1 = Player(100, 100, BLUE, controls_p1)
player2 = Player(150, 100, PINK, controls_p2)

platforms, spikes, portal = load_level()

# === Игровой цикл ===
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
            player1.pos = pygame.Vector2(100, 100)
            player2.pos = pygame.Vector2(150, 100)
            player1.vel = pygame.Vector2(0, 0)
            player2.vel = pygame.Vector2(0, 0)

    # Проверка на портал
    if portal.rect.contains(player1.rect) and portal.rect.contains(player2.rect):
        print("Level Complete!")
        platforms, spikes, portal = load_level()
        player1.pos = pygame.Vector2(100, 100)
        player2.pos = pygame.Vector2(150, 100)
        player1.vel = player2.vel = pygame.Vector2(0, 0)

    for platform in platforms:
        platform.draw(screen)
    for spike in spikes:
        spike.draw(screen)
    portal.draw(screen)

    player1.draw(screen)
    player2.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
