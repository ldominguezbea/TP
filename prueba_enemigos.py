import os
import pygame
from enemigos import Jokai
from enemigos import Karasu_tengu
from enemigos import OrcoRojo
from enemigos import HombreLoboRojo
from enemigos import HombreLoboNegro
from enemigos import Esqueleto_Guerrero
pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 1350
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plataformero")

clock = pygame.time.Clock()

partes_fondo = "assets/fondos/fondo_mvp.png".split("/")
ruta_fondo = os.path.join(BASE_DIR, *partes_fondo)
fondo = pygame.image.load(ruta_fondo)
fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))


class Player:

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 90)
        self.speed = 5
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -12
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

        suelo_y = 590
        if self.rect.bottom >= suelo_y:
            self.rect.bottom = suelo_y
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
                self.hitbox.topleft = (self.rect.left - 50, self.rect.y + 20)

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
            self.hitbox = pygame.Rect(
                self.rect.right, self.rect.y + 20, 50, 50
            )
        else:
            self.hitbox = pygame.Rect(
                self.rect.left - 50, self.rect.y + 20, 50, 50
            )

    def take_damage(self, damage):
        self.health -= damage
        print("Jugador recibió", damage, "de daño")
        print("Vida del jugador:", self.health)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 100, 255), self.rect)
        pygame.draw.rect(screen, (0, 255, 0), self.hurtbox, 2)
        if self.attacking:
            pygame.draw.rect(screen, (255, 255, 0), self.hitbox, 2)


player = Player(200, 500)
enemy =Esqueleto_Guerrero (550, 500)

player_damage = 20
enemy_damage = 12

running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player.attack()

    player.update(dt)
    enemy.update(player, dt)

    if player.attacking and not player.has_hit:
        if player.hitbox.colliderect(enemy.hurtbox):
            enemy.take_damage(player_damage)
            player.has_hit = True

    if enemy.attacking and not enemy.has_hit:
        if enemy.hitbox.colliderect(player.hurtbox):
            player.take_damage(enemy_damage)
            enemy.has_hit = True

    screen.blit(fondo, (0, 0))
    pygame.draw.line(screen, (100, 100, 100), (0, 590), (WIDTH, 590), 5)

    player.draw(screen)
    enemy.draw(screen)

    pygame.display.flip()

pygame.quit()