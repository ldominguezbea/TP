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

        self.rect = pygame.Rect(
            x,
            y,
            60,
            90
        )

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
                f"assets/Heroes/p_tierra/run/run_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_correr.append(imagen)

        self.frame_correr = 0
        self.timer_correr = 0
        self.velocidad_animacion = 0.08

        self.animacion_idle = []

        for i in range(1, 7):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/idle/idle_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_idle.append(imagen)

        self.frame_idle = 0
        self.timer_idle = 0
        self.velocidad_idle = 0.1

        self.animacion_salto = []

        for i in range(1, 4):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/j_up/j_up_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_salto.append(imagen)

        self.frame_salto = 0
        self.timer_salto = 0
        self.velocidad_salto = 0.1

        self.animacion_caer = []

        for i in range(1, 4):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/j_down/j_down_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_caer.append(imagen)

        self.frame_caer = 0
        self.timer_caer = 0
        self.velocidad_caer = 0.1

        self.animacion_hurt = []

        for i in range(1, 7):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/take_hit/take_hit_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_hurt.append(imagen)

        self.frame_hurt = 0
        self.timer_hurt = 0
        self.velocidad_hurt = 0.08

        self.recibiendo_golpe = False

        self.animacion_muerte = []

        for i in range(1, 19):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/death/death_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_muerte.append(imagen)

        self.frame_muerte = 0
        self.timer_muerte = 0
        self.velocidad_muerte = 0.10

        self.muerto = False
        self.muerte_terminada = False

        self.animacion_defensa = []

        for i in range(1, 14):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/defend/defend_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_defensa.append(imagen)

        self.frame_defensa = 0
        self.timer_defensa = 0
        self.velocidad_defensa = 0.08

        self.defendiendo = False
        self.defensa_terminada = False

        self.animacion_rodar = []

        for i in range(1, 7):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/roll/roll_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_rodar.append(imagen)

        self.frame_rodar = 0
        self.timer_rodar = 0
        self.velocidad_rodar = 0.08

        self.rodando = False
        self.velocidad_rodar_movimiento = 14

        self.animacion_ataque = []

        for i in range(1, 7):

            imagen = pygame.image.load(
                f"assets/Heroes/p_tierra/1_atk/1_atk_{i}.png"
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (600, 300)
            )

            self.animacion_ataque.append(imagen)

        self.frame_ataque = 0
        self.timer_ataque = 0
        self.velocidad_ataque = 0.08

        self.imagen = self.animacion_idle[0]

        self.attacking = False

        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.3

        self.has_hit = False

        self.hurtbox = pygame.Rect(
            x,
            y,
            30,
            80
        )

        self.hitbox = pygame.Rect(
            0,
            0,
            0,
            0
        )

    def update(self, dt):

        if self.muerto:

            if not self.muerte_terminada:

                self.timer_muerte += dt

                if self.timer_muerte >= self.velocidad_muerte:

                    self.frame_muerte += 1
                    self.timer_muerte = 0

                    if self.frame_muerte >= len(self.animacion_muerte):

                        self.frame_muerte = len(self.animacion_muerte) - 1
                        self.muerte_terminada = True

                self.imagen = self.animacion_muerte[
                    self.frame_muerte
                ]

                self.velocity_y = 0
                self.attacking = False

                self.hitbox = pygame.Rect(
                    0,
                    0,
                    0,
                    0
                )

            else:

                self.imagen = self.animacion_muerte[-1]

                self.velocity_y = 0
                self.attacking = False

                self.hitbox = pygame.Rect(
                    0,
                    0,
                    0,
                    0
                )

            self.hurtbox.topleft = self.rect.topleft

            return

        if self.rodando:

            if self.direction == "right":
                self.rect.x += self.velocidad_rodar_movimiento
            else:
                self.rect.x -= self.velocidad_rodar_movimiento

            self.timer_rodar += dt

            if self.timer_rodar >= self.velocidad_rodar:

                self.frame_rodar += 1
                self.timer_rodar = 0

                if self.frame_rodar >= len(self.animacion_rodar):

                    self.frame_rodar = len(self.animacion_rodar) - 1
                    self.rodando = False

            self.imagen = self.animacion_rodar[
                self.frame_rodar
            ]

            self.velocity_y = 0
            self.attacking = False
            self.has_hit = False

            self.hitbox = pygame.Rect(
                0,
                0,
                0,
                0
            )

            self.hurtbox.topleft = self.rect.topleft

            self.rect.x = max(
                0,
                min(
                    WIDTH - self.rect.width,
                    self.rect.x
                )
            )

            self.hurtbox.topleft = self.rect.topleft

            return

        if self.defendiendo:

            self.timer_defensa += dt

            if self.timer_defensa >= self.velocidad_defensa:

                self.frame_defensa += 1
                self.timer_defensa = 0

                if self.frame_defensa >= len(self.animacion_defensa):

                    self.frame_defensa = len(self.animacion_defensa) - 1

                    self.defendiendo = False
                    self.defensa_terminada = True

            self.imagen = self.animacion_defensa[
                self.frame_defensa
            ]

            self.velocity_y = 0
            self.attacking = False
            self.has_hit = False

            self.hitbox = pygame.Rect(
                0,
                0,
                0,
                0
            )

            self.hurtbox.topleft = self.rect.topleft

            return

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

        if keys[pygame.K_w] and self.on_ground:

            self.velocity_y = self.jump_force
            self.on_ground = False

            self.frame_salto = 0
            self.timer_salto = 0

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        suelo_y = 590

        if self.rect.bottom >= suelo_y:

            self.rect.bottom = suelo_y

            self.velocity_y = 0
            self.on_ground = True

            self.frame_caer = 0
            self.timer_caer = 0

        if self.recibiendo_golpe:

            self.timer_hurt += dt

            if self.timer_hurt >= self.velocidad_hurt:

                self.frame_hurt += 1
                self.timer_hurt = 0

                if self.frame_hurt >= len(self.animacion_hurt):

                    self.frame_hurt = 0
                    self.recibiendo_golpe = False

            self.imagen = self.animacion_hurt[
                self.frame_hurt
            ]

        elif self.attacking:

            self.timer_ataque += dt

            if self.timer_ataque >= self.velocidad_ataque:

                self.frame_ataque += 1
                self.timer_ataque = 0

                if self.frame_ataque >= len(self.animacion_ataque):

                    self.frame_ataque = len(self.animacion_ataque) - 1

                    self.attacking = False
                    self.has_hit = False

                    self.hitbox = pygame.Rect(
                        0,
                        0,
                        0,
                        0
                    )

            if self.attacking:

                self.imagen = self.animacion_ataque[
                    self.frame_ataque
                ]

        else:

            if not self.on_ground:

                if self.velocity_y < 0:

                    self.timer_salto += dt

                    if self.timer_salto >= self.velocidad_salto:

                        self.frame_salto += 1

                        if self.frame_salto >= len(self.animacion_salto):

                            self.frame_salto = len(self.animacion_salto) - 1

                        self.timer_salto = 0

                    self.imagen = self.animacion_salto[
                        self.frame_salto
                    ]

                else:

                    self.timer_caer += dt

                    if self.timer_caer >= self.velocidad_caer:

                        self.frame_caer += 1

                        if self.frame_caer >= len(self.animacion_caer):

                            self.frame_caer = len(self.animacion_caer) - 1

                        self.timer_caer = 0

                    self.imagen = self.animacion_caer[
                        self.frame_caer
                    ]

            else:

                if moviendo:

                    self.timer_correr += dt

                    if self.timer_correr >= self.velocidad_animacion:

                        self.frame_correr += 1

                        if self.frame_correr >= len(self.animacion_correr):

                            self.frame_correr = 0

                        self.timer_correr = 0

                    self.imagen = self.animacion_correr[
                        self.frame_correr
                    ]

                else:

                    self.timer_idle += dt

                    if self.timer_idle >= self.velocidad_idle:

                        self.frame_idle += 1

                        if self.frame_idle >= len(self.animacion_idle):

                            self.frame_idle = 0

                        self.timer_idle = 0

                    self.imagen = self.animacion_idle[
                        self.frame_idle
                    ]

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

    def rodar(self):

        if self.muerto:
            return

        if self.recibiendo_golpe:
            return

        if self.defendiendo:
            return

        if self.attacking:
            return

        if self.rodando:
            return

        self.rodando = True

        self.frame_rodar = 0
        self.timer_rodar = 0

        self.velocity_y = 0

        self.attacking = False
        self.has_hit = False

        self.hitbox = pygame.Rect(
            0,
            0,
            0,
            0
        )

    def defender(self):

        if self.muerto:
            return

        if self.recibiendo_golpe:
            return

        if self.attacking:
            return

        if self.defendiendo:
            return

        if self.rodando:
            return

        self.defendiendo = True
        self.defensa_terminada = False

        self.frame_defensa = 0
        self.timer_defensa = 0

        self.velocity_y = 0

        self.attacking = False

        self.hitbox = pygame.Rect(
            0,
            0,
            0,
            0
        )

    def attack(self):

        if self.muerto:
            return

        if self.defendiendo:
            return

        if self.rodando:
            return

        if self.attack_cooldown > 0:
            return

        if self.attacking:
            return

        self.attacking = True

        self.frame_ataque = 0
        self.timer_ataque = 0

        self.attack_timer = 0.88

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

        if self.rodando:

            print("El jugador esquivó el ataque rodando")
            return

        if self.defendiendo:

            print("El jugador bloqueó el ataque")
            return

        if self.muerto:
            return

        self.health -= damage

        print(
            "Jugador recibió",
            damage,
            "de daño"
        )

        print(
            "Vida del jugador:",
            self.health
        )

        if self.health <= 0:

            self.health = 0

            self.muerto = True

            self.muerte_terminada = False

            self.frame_muerte = 0
            self.timer_muerte = 0

            self.recibiendo_golpe = False
            self.defendiendo = False
            self.rodando = False
            self.attacking = False
            self.has_hit = False

            self.hitbox = pygame.Rect(
                0,
                0,
                0,
                0
            )

            self.velocity_y = 0

        else:

            self.recibiendo_golpe = True

            self.frame_hurt = 0
            self.timer_hurt = 0

    def draw(self):

        imagen_rect = self.imagen.get_rect()

        imagen_rect.midbottom = self.hurtbox.midbottom

        if self.direction == "left":

            imagen_dibujar = pygame.transform.flip(
                self.imagen,
                True,
                False
            )

        else:

            imagen_dibujar = self.imagen

        screen.blit(
            imagen_dibujar,
            imagen_rect
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
            x,
            y,
            60,
            90
        )

        self.speed = 2
        self.direction = "left"

        self.health = 100
        self.max_health = 100

        self.hurtbox = pygame.Rect(
            x,
            y,
            60,
            90
        )

        self.attacking = False

        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.8

        self.attack_damage = 12
        self.has_hit = False

        self.hitbox = pygame.Rect(
            0,
            0,
            0,
            0
        )

    def update(self, player, dt):

        if self.attack_cooldown > 0:

            self.attack_cooldown -= dt

        distancia_x = abs(
            self.rect.centerx -
            player.rect.centerx
        )

        distancia_y = abs(
            self.rect.centery -
            player.rect.centery
        )

        if not self.attacking:

            if distancia_x > 100:

                if self.rect.centerx < player.rect.centerx:

                    self.rect.x += self.speed
                    self.direction = "right"

                elif self.rect.centerx > player.rect.centerx:

                    self.rect.x -= self.speed
                    self.direction = "left"

            elif distancia_x <= 100 and distancia_y < 80:

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
                    0,
                    0,
                    0,
                    0
                )

        self.hurtbox.topleft = self.rect.topleft

        self.rect.x = max(
            0,
            min(
                WIDTH - self.rect.width,
                self.rect.x
            )
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

        print(
            "Enemigo recibió",
            damage,
            "de daño"
        )

        print(
            "Vida del enemigo:",
            self.health
        )

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
                (255, 255, 0),
                self.hitbox,
                2
            )


player = Player(
    200,
    500
)

enemy = Enemy(
    550,
    500
)

player_damage = 20

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_f:

                player.attack()

            if event.key == pygame.K_r:

                player.defender()

            if event.key == pygame.K_q:

                player.rodar()

    player.update(dt)

    enemy.update(
        player,
        dt
    )

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
                    enemy.attack_damage
                )

                enemy.has_hit = True

    screen.blit(
        fondo,
        (0, 0)
    )

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
