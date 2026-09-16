import pygame

pygame.init()

WIDTH = 1350
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plataformero")

clock = pygame.time.Clock()

fondo = pygame.image.load("assets/fondos/fondo_mvp.png")
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

        self.hitbox = pygame.Rect(
            0, 0, 0, 0
        )

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

        self.rect.x = max(
            0,
            min(
                WIDTH - self.rect.width,
                self.rect.x
            )
        )

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

                self.hitbox = pygame.Rect(
                    0, 0, 0, 0
                )

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

        pygame.draw.rect(
            screen,
            (0, 100, 255),
            self.rect
        )

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


class Enemy:

    def __init__(self, x, y):

        self.rect = pygame.Rect(
            x, y, 60, 90
        )

        self.speed = 2

        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -11
        self.on_ground = False

        self.health = 120
        self.max_health = 120

        self.direction = "left"

        self.hurtbox = pygame.Rect(
            x, y, 60, 90
        )

        self.hitbox = pygame.Rect(
            0, 0, 0, 0
        )

        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.8
        self.has_hit = False

    def update(self, player, dt):

        if self.rect.x < player.rect.x:

            self.rect.x += self.speed
            self.direction = "right"

        elif self.rect.x > player.rect.x:

            self.rect.x -= self.speed
            self.direction = "left"

        self.velocity_y += self.gravity

        self.rect.y += self.velocity_y

        suelo_y = 590

        if self.rect.bottom >= suelo_y:

            self.rect.bottom = suelo_y

            self.velocity_y = 0

            self.on_ground = True

        self.hurtbox.topleft = self.rect.topleft

        self.rect.x = max(
            0,
            min(
                WIDTH - self.rect.width,
                self.rect.x
            )
        )

        if self.attack_cooldown > 0:

            self.attack_cooldown -= dt

        distance_x = abs(
            self.rect.centerx -
            player.rect.centerx
        )

        distance_y = abs(
            self.rect.centery -
            player.rect.centery
        )

        if distance_x < 100 and distance_y < 80:

            if not self.attacking:

                self.attack()

        if (
            player.rect.bottom < self.rect.top - 30
            and self.on_ground
        ):

            self.velocity_y = self.jump_force

            self.on_ground = False

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

                self.hitbox = pygame.Rect(
                    0, 0, 0, 0
                )

    def attack(self):

        if self.attack_cooldown > 0:
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

        print("Enemigo recibió", damage, "de daño")
        print("Vida del enemigo:", self.health)

    def draw(self):

        pygame.draw.rect(
            screen,
            (255, 50, 50),
            self.rect
        )

        pygame.draw.rect(
            screen,
            (0, 255, 0),
            self.hurtbox,
            2
        )

        if self.attacking:

            pygame.draw.rect(
                screen,
                (255, 150, 0),
                self.hitbox,
                2
            )


player = Player(200, 500)

enemy = Enemy(550, 500)

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

    if player.attacking:

        if not player.has_hit:

            if player.hitbox.colliderect(
                enemy.hurtbox
            ):

                enemy.take_damage(
                    player_damage
                )

                player.has_hit = True

    if enemy.attacking:

        if not enemy.has_hit:

            if enemy.hitbox.colliderect(
                player.hurtbox
            ):

                player.take_damage(
                    enemy_damage
                )

                enemy.has_hit = True

    screen.blit(fondo, (0, 0))

    pygame.draw.line(
        screen,
        (100, 100, 100),
        (0, 590),
        (WIDTH, 590),
        5
    )

    player.draw()

    enemy.draw()

    pygame.display.flip()

pygame.quit()