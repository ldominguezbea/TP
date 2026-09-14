import pygame

pygame.init()

WIDTH = 1350
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("REQUIEM")

clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 90)

        self.speed = 5
        self.health = 150
        self.max_health = 150
        self.direction = "right"
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.3
        self.has_hit = False
        self.hurtbox = pygame.Rect(
            x, y, 60, 90
        )
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

        if keys[pygame.K_w]:
            self.rect.y -= self.speed

        if keys[pygame.K_s]:
            self.rect.y += self.speed
        self.rect.x = max(
            0,
            min(WIDTH - self.rect.width, self.rect.x)
        )
        self.rect.y = max(
            10,
            min(590 - self.rect.height, self.rect.y)
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
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed
        self.rect.x = max(
            0,
            min(WIDTH - self.rect.width, self.rect.x)
        )
        self.rect.y = max(
            10,
            min(590 - self.rect.height, self.rect.y)
        )
        self.hurtbox.topleft = self.rect.topleft
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
player = Player(200, 200)
enemy = Enemy(550, 200)
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
            if player.hitbox.colliderect(enemy.hurtbox):
                enemy.take_damage(player_damage)
                player.has_hit = True
    if enemy.attacking:
        if not enemy.has_hit:
            if enemy.hitbox.colliderect(player.hurtbox):
                player.take_damage(enemy_damage)
                enemy.has_hit = True
    screen.fill((30, 30, 30))
    player.draw()
    enemy.draw()
    pygame.display.flip()
pygame.quit()