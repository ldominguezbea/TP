from animacion_menu import GAME_WIDTH, GAME_HEIGHT
import pygame
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

fondo = pygame.image.load("assets/fondos/fondo_mvp.png")
fondo = pygame.transform.scale(fondo, (GAME_WIDTH, GAME_HEIGHT))

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

        self.animacion_correr = []
        for i in range(1, 9):
            imagen = pygame.image.load(
                f"assets/Heroes/p_fuego/fire_knight/run_{i}.png"
            ).convert_alpha()
            imagen = pygame.transform.scale(imagen, (60, 90))
            self.animacion_correr.append(imagen)

        self.frame_correr = 0
        self.timer_correr = 0
        self.velocidad_animacion = 0.08
        self.imagen = self.animacion_correr[0]

        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.3
        self.has_hit = False

        self.hurtbox = pygame.Rect(x, y, 60, 90)
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        moviendo = False

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
            moviendo = True

        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
            moviendo = True

        if moviendo:
            self.timer_correr += dt
            if self.timer_correr >= self.velocidad_animacion:
                self.frame_correr += 1
                if self.frame_correr >= 8:
                    self.frame_correr = 0
                self.timer_correr = 0
        else:
            self.frame_correr = 0
            self.timer_correr = 0

        self.imagen = self.animacion_correr[self.frame_correr]

        if self.direction == "left":
            self.imagen = pygame.transform.flip(self.imagen, True, False)

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

        self.rect.x = max(0, min(GAME_WIDTH - self.rect.width, self.rect.x))

        self.hurtbox.topleft = self.rect.topleft

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.attacking:
            if self.direction == "right":
                self.hitbox.topleft = (
                    self.rect.right,
                    self.rect.y + 20
                )
            else:
                self.hitbox.topleft = (
                    self.rect.left - 50,
                    self.rect.y + 20
                )

            self.attack_timer -= dt

            if self.attack_timer <= 0:
                self.attacking = False
                self.has_hit = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self):
        if self.attack_cooldown > 0:
            return

        if self.attacking:
            return

        self.attacking = True
        self.attack_timer = 0.15
        self.attack_cooldown = self.attack_cooldown_time
        self.has_hit = False

        if self.direction == "right":
            self.hitbox = pygame.Rect(
                self.rect.right,
                self.rect.y + 20,
                50,
                50
            )
        else:
            self.hitbox = pygame.Rect(
                self.rect.left - 50,
                self.rect.y + 20,
                50,
                50
            )

    def take_damage(self, damage):
        self.health -= damage
        print("Jugador recibió", damage, "de daño")
        print("Vida del jugador:", self.health)

    def draw(self):
        screen.blit(self.imagen, self.rect)

        pygame.draw.rect(
            screen,
            (0, 255, 0),
            self.hurtbox,
            2
        )

        if self.attacking:
            pygame.draw.rect(
                screen,
                (255, 255, 0),
                self.hitbox,
                2
            )
player = Player(200, 500)

player.draw()

pygame.display.flip()

pygame.quit()