import os
import random
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def cargar_spritesheet_jokai(ruta_relativa, filas, columnas):
    partes_ruta = ruta_relativa.replace("\\", "/").split("/")
    ruta_completa = os.path.join(BASE_DIR, *partes_ruta)

    sheet = pygame.image.load(ruta_completa).convert_alpha()
    ancho_frame = sheet.get_width() // columnas
    alto_frame = sheet.get_height() // filas

    frames = []
    for fila in range(filas):
        for col in range(columnas):
            rect = pygame.Rect(
                col * ancho_frame, fila * alto_frame, ancho_frame, alto_frame
            )
            frame = sheet.subsurface(rect)
            frames.append(frame)

    return frames


WIDTH = 1350


class Enemigo:

    def __init__(self, name, speed, x=550, y=500):
        self.name = name
        self.speed = speed
        self.rect = pygame.Rect(x, y, 60, 90)
        self.health = 120
        self.max_health = 120
        self.direction = "left"
        self.hurtbox = pygame.Rect(x, y, 60, 90)
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.8
        self.has_hit = False

        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -12
        self.on_ground = False

    def aplicar_gravedad_y_suelo(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        suelo_y = 590
        if self.rect.bottom >= suelo_y:
            self.rect.bottom = suelo_y
            self.velocity_y = 0
            self.on_ground = True

    def update(self, player, dt, width=WIDTH):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
            self.direction = "right"
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed
            self.direction = "left"

        if player.rect.bottom < self.rect.top - 30 and self.on_ground:
            self.velocity_y = self.jump_force
            self.on_ground = False

        self.aplicar_gravedad_y_suelo()

        self.rect.x = max(0, min(width - self.rect.width, self.rect.x))
        self.hurtbox.topleft = self.rect.topleft

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        distance_x = abs(self.rect.centerx - player.rect.centerx)
        distance_y = abs(self.rect.centery - player.rect.centery)

        if distance_x < 100 and distance_y < 80:
            if not self.attacking:
                self.attack()

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
        if self.attack_cooldown > 0:
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
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        print(
            f"{self.name} recibió {damage} de daño. Vida restante: {self.health}"
        )


class OrcoRojo(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Orco_Rojo", 2, x, y)
        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/Orco_rojo/Run.png", 1, 6
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Orco_rojo/Attack_1.png", 1, 4
            ),
            "dano": cargar_spritesheet_jokai(
                "assets/enemigos/Orco_rojo/Hurt.png", 1, 2
            ),
            "muerte": cargar_spritesheet_jokai(
                "assets/enemigos/Orco_rojo/Dead.png", 1, 4
            ),
            "saltar": cargar_spritesheet_jokai(
                "assets/enemigos/Orco_rojo/Jump.png", 1, 5
            ),
        }

        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []
        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            frames_saltar_normalizados.append(
                pygame.transform.scale(f, (nuevo_ancho, alto_base))
            )
        self.animaciones["saltar"] = frames_saltar_normalizados

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.esta_rojo = False
        self.image = self.animaciones[self.estado_actual][0]

        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado:
            self.estado_actual = nuevo_estado
            self.frame_actual = 0.0

    def actualizar_animacion(self):
        frames = self.animaciones[self.estado_actual]
        self.frame_actual += self.velocidad_animacion

        if self.estado_actual == "muerte":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual in ("golpear", "dano"):
            if self.frame_actual >= len(frames):
                self.esta_rojo = False
                self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = frames[int(self.frame_actual)]

        if self.direction == "left":
            imagen_frame = pygame.transform.flip(imagen_frame, True, False)

        if self.esta_rojo:
            imagen_frame = imagen_frame.copy()
            imagen_frame.fill(
                (255, 50, 50), special_flags=pygame.BLEND_RGB_MULT
            )

        self.image = imagen_frame

    def take_damage(self, damage):
        if self.health <= 0:
            return

        super().take_damage(damage)
        self.esta_rojo = True
        self.attacking = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        if self.health <= 0:
            self.cambiar_estado("muerte")
        else:
            self.cambiar_estado("dano")

    def update(self, player, dt, width=WIDTH):
        if self.muerto_definitivo:
            return

        if self.estado_actual == "muerte":
            self.aplicar_gravedad_y_suelo()
            self.hurtbox = pygame.Rect(0, 0, 0, 0)

            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True

        elif self.estado_actual == "dano":
            self.aplicar_gravedad_y_suelo()
            self.hurtbox.topleft = self.rect.topleft
        else:
            super().update(player, dt, width)

            if not self.on_ground:
                self.cambiar_estado("saltar")
            elif self.attacking:
                self.cambiar_estado("golpear")
            else:
                self.cambiar_estado("correr")

        self.actualizar_animacion()

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        pos_x = self.rect.centerx - self.image.get_width() // 2
        pos_y = self.rect.bottom - self.image.get_height()

        screen.blit(self.image, (pos_x, pos_y))
    


class Carnicero(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Carnicero", 3, x, y)


class MinotauroNaranja(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Minotauro Naranja", 2, x, y)


class Jokai(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Jokai", 2, x, y)

        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/Jokai/Run.png", 1, 8
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Jokai/Attack_2.png", 1, 6
            ),
            "dano": cargar_spritesheet_jokai(
                "assets/enemigos/Jokai/Hurt.png", 1, 3
            ),
            "muerte": cargar_spritesheet_jokai(
                "assets/enemigos/Jokai/Dead.png", 1, 6
            ),
            "saltar": cargar_spritesheet_jokai(
                "assets/enemigos/Jokai/Jump.png", 1, 15
            ),
        }

        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []
        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            frames_saltar_normalizados.append(
                pygame.transform.scale(f, (nuevo_ancho, alto_base))
            )
        self.animaciones["saltar"] = frames_saltar_normalizados

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.esta_rojo = False
        self.image = self.animaciones[self.estado_actual][0]

        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado:
            self.estado_actual = nuevo_estado
            self.frame_actual = 0.0

    def actualizar_animacion(self):
        frames = self.animaciones[self.estado_actual]
        self.frame_actual += self.velocidad_animacion

        if self.estado_actual == "muerte":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual in ("golpear", "dano"):
            if self.frame_actual >= len(frames):
                self.esta_rojo = False
                self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = frames[int(self.frame_actual)]

        if self.direction == "left":
            imagen_frame = pygame.transform.flip(imagen_frame, True, False)

        if self.esta_rojo:
            imagen_frame = imagen_frame.copy()
            imagen_frame.fill(
                (255, 50, 50), special_flags=pygame.BLEND_RGB_MULT
            )

        self.image = imagen_frame

    def take_damage(self, damage):
        if self.health <= 0:
            return

        super().take_damage(damage)
        self.esta_rojo = True
        self.attacking = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        if self.health <= 0:
            self.cambiar_estado("muerte")
        else:
            self.cambiar_estado("dano")

    def update(self, player, dt, width=WIDTH):
        if self.muerto_definitivo:
            return

        if self.estado_actual == "muerte":
            self.aplicar_gravedad_y_suelo()
            self.hurtbox = pygame.Rect(0, 0, 0, 0)

            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True

        elif self.estado_actual == "dano":
            self.aplicar_gravedad_y_suelo()
            self.hurtbox.topleft = self.rect.topleft
        else:
            super().update(player, dt, width)

            if not self.on_ground:
                self.cambiar_estado("saltar")
            elif self.attacking:
                self.cambiar_estado("golpear")
            else:
                self.cambiar_estado("correr")

        self.actualizar_animacion()

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        pos_x = self.rect.centerx - self.image.get_width() // 2
        pos_y = self.rect.bottom - self.image.get_height()

        screen.blit(self.image, (pos_x, pos_y))

class Karasu_tengu(Enemigo):
    def __init__(self, x=550, y=500):
            super().__init__("Karasu_tengu", 2, x, y)
    
            self.animaciones = {
                "correr": cargar_spritesheet_jokai(
                    "assets/enemigos/Karasu_tengu/Run.png", 1, 8
                ),
                "golpear": cargar_spritesheet_jokai(
                    "assets/enemigos/Karasu_tengu/Attack_2.png", 1, 4
                ),
                "dano": cargar_spritesheet_jokai(
                    "assets/enemigos/Karasu_tengu/Hurt.png", 1, 3
                ),
                "muerte": cargar_spritesheet_jokai(
                    "assets/enemigos/Karasu_tengu/Dead.png", 1, 6
                ),
                "saltar": cargar_spritesheet_jokai(
                    "assets/enemigos/Karasu_tengu/Jump.png", 1, 15
                ),
            }
    
            alto_base = self.animaciones["correr"][0].get_height()
            frames_saltar_normalizados = []
            for f in self.animaciones["saltar"]:
                escala = alto_base / f.get_height()
                nuevo_ancho = int(f.get_width() * escala)
                frames_saltar_normalizados.append(
                    pygame.transform.scale(f, (nuevo_ancho, alto_base))
                )
            self.animaciones["saltar"] = frames_saltar_normalizados
    
            self.estado_actual = "correr"
            self.frame_actual = 0.0
            self.velocidad_animacion = 0.15
            self.esta_rojo = False
            self.image = self.animaciones[self.estado_actual][0]
    
            self.desaparecer_timer = 3.0
            self.muerto_definitivo = False
    
    def cambiar_estado(self, nuevo_estado):
            if self.estado_actual != nuevo_estado:
                self.estado_actual = nuevo_estado
                self.frame_actual = 0.0
    
    def actualizar_animacion(self):
            frames = self.animaciones[self.estado_actual]
            self.frame_actual += self.velocidad_animacion
    
            if self.estado_actual == "muerte":
                if self.frame_actual >= len(frames):
                    self.frame_actual = len(frames) - 1
            elif self.estado_actual in ("golpear", "dano"):
                if self.frame_actual >= len(frames):
                    self.esta_rojo = False
                    self.cambiar_estado("correr")
            elif self.estado_actual == "saltar":
                if self.frame_actual >= len(frames):
                    self.frame_actual = len(frames) - 1
            else:
                if self.frame_actual >= len(frames):
                    self.frame_actual = 0.0
    
            imagen_frame = frames[int(self.frame_actual)]
    
            if self.direction == "left":
                imagen_frame = pygame.transform.flip(imagen_frame, True, False)
    
            if self.esta_rojo:
                imagen_frame = imagen_frame.copy()
                imagen_frame.fill(
                    (255, 50, 50), special_flags=pygame.BLEND_RGB_MULT
                )
    
            self.image = imagen_frame
    
    def take_damage(self, damage):
            if self.health <= 0:
                return
    
            super().take_damage(damage)
            self.esta_rojo = True
            self.attacking = False
            self.hitbox = pygame.Rect(0, 0, 0, 0)
    
            if self.health <= 0:
                self.cambiar_estado("muerte")
            else:
                self.cambiar_estado("dano")
    
    def update(self, player, dt, width=WIDTH):
            if self.muerto_definitivo:
                return
    
            if self.estado_actual == "muerte":
                self.aplicar_gravedad_y_suelo()
                self.hurtbox = pygame.Rect(0, 0, 0, 0)
    
                self.desaparecer_timer -= dt
                if self.desaparecer_timer <= 0:
                    self.muerto_definitivo = True
    
            elif self.estado_actual == "dano":
                self.aplicar_gravedad_y_suelo()
                self.hurtbox.topleft = self.rect.topleft
            else:
                super().update(player, dt, width)
    
                if not self.on_ground:
                    self.cambiar_estado("saltar")
                elif self.attacking:
                    self.cambiar_estado("golpear")
                else:
                    self.cambiar_estado("correr")
    
            self.actualizar_animacion()
    
    def draw(self, screen):
            if self.muerto_definitivo:
                return
    
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
    
            screen.blit(self.image, (pos_x, pos_y))

class HombreLoboRojo(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("HombreLoboRojo", 2, x, y)



class Cthulhu(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Cthulhu", 3, x, y)


class Cerbero(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Cerbero", 3, x, y)


class OrcoRojo2(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Orco Rojo 2", 3, x, y)


class Demonio(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Demonio", 2, x, y)


class CaballeroInfernal(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Caballero Infernal", 3, x, y)


class Dragon(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Dragon", 2, x, y)


enemigos_nivel_1 = [
    OrcoRojo,
]
enemigos_normales = [
    OrcoRojo,
    MinotauroNaranja,
    Jokai,
    HombreLoboRojo,
    Demonio,
    Dragon,
]
enemigos_jefes = [Carnicero, Cthulhu, Cerbero, OrcoRojo2, CaballeroInfernal]


def crear_enemigo_aleatorio(x=550, y=500):
    clase_enemigo = random.choice(enemigos_normales)
    nuevo_enemigo = clase_enemigo(x, y)
    return nuevo_enemigo