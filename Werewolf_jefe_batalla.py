import os
import pygame
from Jefes_enemigos import WerewolfBoss

pygame.init()

WIDTH = 1350
HEIGHT = 700
SUELO_Y = 590

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Prueba de Jefe 2 - Werewolf")

clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_fondo = os.path.join(BASE_DIR, "assets", "fondos", "fondo_mvp.png")

if os.path.exists(ruta_fondo):
    fondo = pygame.image.load(ruta_fondo).convert()
    fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
else:
    fondo = pygame.Surface((WIDTH, HEIGHT))
    fondo.fill((30, 30, 40))


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 90)
        self.speed = 6
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -13
        self.on_ground = False

        self.health = 150
        self.max_health = 150

        self.direction = "right"
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.3
        self.has_hit = False

        self.hurtbox = pygame.Rect(x, y, 60, 90)
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"

        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"

        if keys[pygame.K_w] and self.on_ground:
            self.velocity_y = self.jump_force
            self.on_ground = False

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= SUELO_Y:
            self.rect.bottom = SUELO_Y
            self.velocity_y = 0
            self.on_ground = True

        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.hurtbox.topleft = self.rect.topleft

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.attacking:
            if self.direction == "right":
                self.hitbox.topleft = (self.rect.right, self.rect.y + 20)
            else:
                self.hitbox.topleft = (self.rect.left - 60, self.rect.y + 20)

            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False
                self.has_hit = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self):
        if self.attack_cooldown > 0 or self.attacking:
            return

        self.attacking = True
        self.attack_timer = 0.15
        self.attack_cooldown = self.attack_cooldown_time
        self.has_hit = False

        if self.direction == "right":
            self.hitbox = pygame.Rect(self.rect.right, self.rect.y + 20, 60, 50)
        else:
            self.hitbox = pygame.Rect(self.rect.left - 60, self.rect.y + 20, 60, 50)

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def draw(self, screen):
        color = (0, 120, 255) if self.health > 0 else (100, 100, 100)
        pygame.draw.rect(screen, color, self.rect)


def dibujar_barras_vida(screen, player, enemy):
    fuente = pygame.font.SysFont("Arial", 16, bold=True)

    # Barra del Jugador
    pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 20))
    pct_p = max(0, player.health / player.max_health)
    pygame.draw.rect(screen, (0, 220, 0), (20, 20, int(200 * pct_p), 20))
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20), 2)
    screen.blit(
        fuente.render(f"Jugador: {player.health}", True, (255, 255, 255)),
        (20, 45),
    )

    # Barra del Werewolf Boss
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 320, 20, 300, 20))
    e_health = getattr(enemy, "health", 0)
    e_max_health = getattr(enemy, "max_health", 1)
    pct_e = max(0, e_health / e_max_health)
    pygame.draw.rect(screen, (180, 0, 0), (WIDTH - 320, 20, int(300 * pct_e), 20))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 320, 20, 300, 20), 2)
    screen.blit(
        fuente.render(f"Werewolf Boss: {e_health}", True, (255, 255, 255)),
        (WIDTH - 320, 45),
    )


player = Player(400, 500)
enemy = WerewolfBoss(900, 450)

running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player.attack()

    player.update(dt)
    enemy.update(player, dt, width=WIDTH)

    # Colisiones de ataques del jugador al jefe
    if player.attacking and not player.has_hit:
        if hasattr(enemy, "hurtbox") and player.hitbox.colliderect(enemy.hurtbox):
            enemy.take_damage(30)
            player.has_hit = True

    # Colisiones de ataques del jefe al jugador
    if getattr(enemy, "attacking", False) and not getattr(enemy, "has_hit", False):
        if hasattr(enemy, "hitbox") and enemy.hitbox.colliderect(player.hurtbox):
            player.take_damage(25)
            enemy.has_hit = True

    screen.blit(fondo, (0, 0))
    pygame.draw.line(screen, (200, 200, 200), (0, SUELO_Y), (WIDTH, SUELO_Y), 4)

    enemy.draw(screen)
    player.draw(screen)
    dibujar_barras_vida(screen, player, enemy)

    pygame.display.flip()

pygame.quit()