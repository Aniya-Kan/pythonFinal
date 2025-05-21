import pygame
import sys
import time

# === Настройки ===
WIDTH, HEIGHT = 1000, 600
FPS = 60
JUMP_FORCE = -12
MOVE_FORCE = 5
ROTATION_SPEED = 5
GRAVITY = 0.6
DOWN_GRAVITY_BOOST = 3
DOWN_TIME_LIMIT = 60
down_timer = 0

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
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Функция для воспроизведения музыки
def play_background_music():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("background_music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        print("🎵 Музыка воспроизводится.")
    except pygame.error as e:
        print(f"⚠️ Ошибка при загрузке или воспроизведении музыки: {e}")

play_background_music()

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
        self.held_by = None

    def update(self, keys, platforms, other):
        global down_timer

        if other.holding == self:
            self.held_by = other
        else:
            self.held_by = None

        was_on_ground = self.on_ground
        self.on_ground = False

        if not self.held_by:
            if keys[self.controls['left']]:
                self.vel.x = -MOVE_FORCE
                self.angle -= ROTATION_SPEED
            elif keys[self.controls['right']]:
                self.vel.x = MOVE_FORCE
                self.angle += ROTATION_SPEED
            else:
                self.vel.x = 0

            if keys[self.controls['jump']] and was_on_ground:
                self.vel.y = JUMP_FORCE

            if not self.on_ground:
                if keys[self.controls['down']]:
                    if down_timer < DOWN_TIME_LIMIT:
                        down_timer += 1
                        self.vel.y += GRAVITY * DOWN_GRAVITY_BOOST
                else:
                    down_timer = 0

                if down_timer == 0:
                    self.vel.y += GRAVITY
        else:
            self.vel = pygame.Vector2(0, 0)

        self.grabbing = keys[self.controls['grab']] or keys[self.controls['alt_grab']]
        if self.grabbing and self.rect.colliderect(other.rect):
            if not self.holding and not other.held_by:
                self.holding = other
        elif not self.grabbing:
            self.holding = None

        if not self.held_by:
            self.pos += self.vel
            self.rect.topleft = self.pos

            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel.y > 0:
                        self.pos.y = platform.rect.top - self.rect.height
                        self.vel.y = 0
                        self.on_ground = True
                    elif self.vel.y < 0:
                        self.pos.y = platform.rect.bottom
                        self.vel.y = 0
            self.rect.topleft = self.pos

            if self.rect.colliderect(other.rect) and self.vel.y > 0:
                self.pos.y = other.rect.top - self.rect.height
                self.vel.y = 0
                self.on_ground = True
                self.rect.topleft = self.pos

        if self.holding:
            offset = pygame.Vector2(0, -self.rect.height)
            self.holding.pos = self.pos + offset
            self.holding.rect.topleft = self.holding.pos

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

class Carrot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 30)
        self.collected = False
    def draw(self, surface):
        if not self.collected:
            pygame.draw.ellipse(surface, ORANGE, self.rect)

# === Уровни ===
levels = [
    {
        "platforms": [(0, HEIGHT - 40, WIDTH, 40), (300, 500, 200, 20), (600, 400, 200, 20), (850, 300, 100, 20)],
        "spikes": [(500, HEIGHT - 80), (540, HEIGHT - 80)],
        "portal": (900, 220),
        "start_pos": ((100, 100), (150, 100)),
        "carrots": []
    },
    {
        "platforms": [(0, HEIGHT - 40, WIDTH, 40), (200, 450, 150, 20), (400, 350, 150, 20), (600, 250, 150, 20)],
        "spikes": [(450, HEIGHT - 80)],
        "portal": (700, 170),
        "start_pos": ((100, 100), (150, 100)),
        "carrots": [(220, 420), (450, 320)]
    },
    {
        "platforms": [(0, HEIGHT - 40, WIDTH, 40), (250, 500, 100, 20), (400, 400, 100, 20), (550, 300, 100, 20)],
        "spikes": [(350, HEIGHT - 80), (750, HEIGHT - 80)],
        "portal": (600, 220),
        "start_pos": ((50, 100), (100, 100)),
        "carrots": [(270, 470), (420, 370)]
    },
    {
        "platforms": [(0, HEIGHT - 40, WIDTH, 40), (100, 450, 100, 20), (250, 350, 100, 20), (400, 250, 100, 20)],
        "spikes": [(150, HEIGHT - 80)],
        "portal": (420, 170),
        "start_pos": ((50, 100), (100, 100)),
        "carrots": [(120, 420), (270, 320)]
    },
    {
        "platforms": [(0, HEIGHT - 40, WIDTH, 40), (300, 500, 400, 20), (800, 400, 100, 20)],
        "spikes": [(600, HEIGHT - 80), (650, HEIGHT - 80)],
        "portal": (850, 320),
        "start_pos": ((100, 100), (150, 100)),
        "carrots": [(320, 470), (820, 370)]
    }
]

def load_level(index):
    data = levels[index]
    platforms = [Platform(*p) for p in data["platforms"]]
    spikes = [Spike(*s) for s in data["spikes"]]
    portal = Portal(*data["portal"])
    carrots = [Carrot(*c) for c in data.get("carrots", [])]
    start_pos = data["start_pos"]
    return platforms, spikes, portal, carrots, start_pos

controls_p1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'grab': pygame.K_LSHIFT, 'alt_grab': pygame.K_RETURN, 'down': pygame.K_s}
controls_p2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'grab': pygame.K_RSHIFT, 'alt_grab': pygame.K_KP_ENTER, 'down': pygame.K_DOWN}

def level_selection():
    font = pygame.font.SysFont("Arial", 36)
    levels_text = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Exit"]
    selected = 0
    while True:
        screen.fill(WHITE)
        for i, text in enumerate(levels_text):
            label = font.render(text, True, BLUE if i == selected else BLACK)
            screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 150 + i * 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected = (selected - 1) % len(levels_text)
                elif event.key == pygame.K_DOWN: selected = (selected + 1) % len(levels_text)
                elif event.key == pygame.K_RETURN:
                    if selected == len(levels_text) - 1: pygame.quit(); sys.exit()
                    else: return selected

level_stats = []

def show_win_screen():
    font = pygame.font.SysFont("Arial", 36)
    small_font = pygame.font.SysFont("Arial", 24)
    screen.fill(WHITE)
    label = font.render("Congratulations!! You passed all levels", True, YELLOW)
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 60))
    y = 150
    for level_num, time_spent, carrots in level_stats:
        stat_text = f"Level {level_num}: {time_spent} sec, Carrots: {carrots}"
        stat_label = small_font.render(stat_text, True, BLACK)
        screen.blit(stat_label, (WIDTH // 2 - stat_label.get_width() // 2, y))
        y += 40
    sub_label = small_font.render("Press Enter to return to menu", True, BLACK)
    screen.blit(sub_label, (WIDTH // 2 - sub_label.get_width() // 2, y + 20))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: return

while True:
    level_index = level_selection()
    while level_index < len(levels):
        platforms, spikes, portal, carrots, (p1_start, p2_start) = load_level(level_index)
        player1 = Player(*p1_start, BLUE, controls_p1)
        player2 = Player(*p2_start, PINK, controls_p2)
        start_time = time.time()
        collected_carrots = 0

        while True:
            screen.fill(WHITE)
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            player1.update(keys, platforms, player2)
            player2.update(keys, platforms, player1)

            for spike in spikes:
                if player1.rect.colliderect(spike.rect) or player2.rect.colliderect(spike.rect):
                    player1.pos = pygame.Vector2(p1_start)
                    player2.pos = pygame.Vector2(p2_start)
                    player1.vel = player2.vel = pygame.Vector2(0, 0)

            for carrot in carrots:
                if not carrot.collected and (player1.rect.colliderect(carrot.rect) or player2.rect.colliderect(carrot.rect)):
                    carrot.collected = True
                    collected_carrots += 1

            if portal.rect.colliderect(player1.rect) and portal.rect.colliderect(player2.rect):
                elapsed = round(time.time() - start_time, 2)
                level_stats.append((level_index + 1, elapsed, collected_carrots))

                font = pygame.font.SysFont("Arial", 36)
                small_font = pygame.font.SysFont("Arial", 24)
                screen.fill(WHITE)
                label = font.render(f"Level {level_index + 1} Complete!", True, GREEN)
                screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 100))
                time_label = small_font.render(f"Time: {elapsed} sec", True, BLACK)
                screen.blit(time_label, (WIDTH // 2 - time_label.get_width() // 2, 180))
                carrot_label = small_font.render(f"Carrots collected: {collected_carrots}", True, BLACK)
                screen.blit(carrot_label, (WIDTH // 2 - carrot_label.get_width() // 2, 220))
                next_label = small_font.render("Press Enter to continue", True, BLACK)
                screen.blit(next_label, (WIDTH // 2 - next_label.get_width() // 2, 280))
                pygame.display.flip()

                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            waiting = False

                level_index += 1
                break

            for platform in platforms: platform.draw(screen)
            for spike in spikes: spike.draw(screen)
            for carrot in carrots: carrot.draw(screen)
            portal.draw(screen)
            player1.draw(screen)
            player2.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)

    show_win_screen()
