import os
import random
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def cargar_spritesheet_jokai(ruta_relativa, filas, columnas):
    ruta_completa = os.path.join(
        BASE_DIR, *ruta_relativa.replace("\\", "/").split("/")
    )

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

        # Distancia mínima para detenerse antes de empujar o traspasar al jugador
        self.stop_distance = 50

    def aplicar_gravedad_y_suelo(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        suelo_y = 590
        if self.rect.bottom >= suelo_y:
            self.rect.bottom = suelo_y
            self.velocity_y = 0
            self.on_ground = True

    def update(self, player, dt, width=WIDTH):
        # --- SOLUCIÓN TEMBLOR / GIRO LOUCO ---
        # Calculamos la distancia usando los centros en X
        dx = player.rect.centerx - self.rect.centerx

        # Margen de tolerancia para que no cambie de lado a cada frame
        if dx < -5:
            self.direction = "left"
        elif dx > 5:
            self.direction = "right"

        # Solo avanza si está más lejos que la distancia de parada
        if abs(dx) > self.stop_distance:
            if self.direction == "right":
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed

        if player.rect.bottom < self.rect.top - 30 and self.on_ground:
            self.velocity_y = self.jump_force
            self.on_ground = False

        self.aplicar_gravedad_y_suelo()

        self.rect.x = max(0, min(width - self.rect.width, self.rect.x))
        self.hurtbox.topleft = self.rect.topleft

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        distance_x = abs(dx)
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

    def draw(self, screen):
        color = (200, 50, 50) if self.direction == "left" else (50, 200, 50)
        pygame.draw.rect(screen, color, self.rect)

def escalar_animaciones(self, factor):
        """Escala únicamente las imágenes de las animaciones sin alterar las hitboxes."""
        if hasattr(self, "animaciones"):
            for estado, frames in self.animaciones.items():
                nuevos_frames = []
                for f in frames:
                    nuevo_ancho = int(f.get_width() * factor)
                    nuevo_alto = int(f.get_height() * factor)
                    f_escalado = pygame.transform.scale(
                        f, (nuevo_ancho, nuevo_alto)
                    )
                    nuevos_frames.append(f_escalado)
                self.animaciones[estado] = nuevos_frames

class OrcoRojo(Enemigo):

    def __init__(self, x=550, y=500, escala=2):
        super().__init__("Orco_Rojo", 2, x, y)

        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/Orco_rojo/Run.png", 1, 6
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Orco_rojo/Attack_3.png", 1, 2
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

        self.normalizar_saltos()

        # Llama a la función para redimensionar los frames
        if escala != 1.0:
            self.escalar_animaciones(escala)

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["correr"][0]

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def escalar_animaciones(self, factor):
        """Redimensiona todas las animaciones sin modificar self.rect ni self.hurtbox."""
        for estado, frames in self.animaciones.items():
            nuevos_frames = []
            for f in frames:
                nuevo_ancho = int(f.get_width() * factor)
                nuevo_alto = int(f.get_height() * factor)
                f_escalado = pygame.transform.scale(
                    f, (nuevo_ancho, nuevo_alto)
                )
                nuevos_frames.append(f_escalado)
            self.animaciones[estado] = nuevos_frames

    def normalizar_saltos(self):
        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []

        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            f_escalado = pygame.transform.scale(f, (nuevo_ancho, alto_base))
            frames_saltar_normalizados.append(f_escalado)

        self.animaciones["saltar"] = frames_saltar_normalizados

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

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))


class Jokai(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Jokai", 2, x, y)

        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/Jokai/Run.png", 1, 8
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Jokai/Attack_1.png", 1, 3
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

        self.normalizar_saltos()

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["correr"][0]

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def normalizar_saltos(self):
        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []

        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            f_escalado = pygame.transform.scale(f, (nuevo_ancho, alto_base))
            frames_saltar_normalizados.append(f_escalado)

        self.animaciones["saltar"] = frames_saltar_normalizados

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

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))


class OjoVolador(Enemigo):

    class Proyectil:

        def __init__(self, x, y, direccion, dano=1):
            self.direccion = direccion
            self.dano = dano
            self.velocidad = 350
            self.frame_actual = 0.0
            self.velocidad_anim = 0.2
            self.destruido = False
            self.estado = "vuelo"

            try:
                todos_los_frames = cargar_spritesheet_jokai(
                    "assets/enemigos/Ojo volador/projectile_sprite.png", 1, 8
                )
                self.frames_vuelo = todos_los_frames[:3]
                self.frames_explosion = todos_los_frames[3:]
            except Exception:
                surf_vacio = pygame.Surface((16, 16))
                self.frames_vuelo = [surf_vacio]
                self.frames_explosion = [surf_vacio]

            self.image = self.frames_vuelo[0]
            self.rect = self.image.get_rect(center=(x, y))

        def update(self, dt, player):
            if self.destruido:
                return

            if self.estado == "vuelo":
                dir_mult = -1 if self.direccion == "left" else 1
                self.rect.x += int(self.velocidad * dt * dir_mult)

                self.frame_actual += self.velocidad_anim
                if self.frame_actual >= len(self.frames_vuelo):
                    self.frame_actual = 0.0

                frame_img = self.frames_vuelo[int(self.frame_actual)]

                if player:
                    target_box = getattr(player, "hurtbox", player.rect)
                    if self.rect.colliderect(target_box):
                        if hasattr(player, "take_damage"):
                            player.take_damage(self.dano)
                        self.estado = "impacto"
                        self.frame_actual = 0.0

                if self.rect.right < -200 or self.rect.left > 3000:
                    self.destruido = True

            elif self.estado == "impacto":
                self.frame_actual += self.velocidad_anim
                if self.frame_actual >= len(self.frames_explosion):
                    self.destruido = True
                    return

                frame_img = self.frames_explosion[int(self.frame_actual)]

            if self.direccion == "left":
                frame_img = pygame.transform.flip(frame_img, True, False)

            self.image = frame_img

        def draw(self, screen):
            if not self.destruido and self.image:
                screen.blit(self.image, self.rect)

    def __init__(self, x=550, y=500, escala_enemigo=1.8, offset_y=120):
        super().__init__("Ojo volador", 2, x, y)

        ruta_base = "assets/enemigos/Ojo volador/"

        def cargar_anim(nombre_archivo, filas, columnas):
            try:
                frames = cargar_spritesheet_jokai(
                    ruta_base + nombre_archivo, filas, columnas
                )
            except FileNotFoundError:
                frames = cargar_spritesheet_jokai(
                    ruta_base + "Attack3.png", 1, 6
                )

            if escala_enemigo != 1.0:
                frames = [
                    pygame.transform.scale(
                        f,
                        (
                            int(f.get_width() * escala_enemigo),
                            int(f.get_height() * escala_enemigo),
                        ),
                    )
                    for f in frames
                ]

            return frames

        self.animaciones = {
            "correr": cargar_anim("Flight.png", 1, 8),
            "golpear": cargar_anim("Attack3.png", 1, 6),
            "dano": cargar_anim("Hurt.png", 1, 3),
            "muerte": cargar_anim("Dead.png", 1, 6),
        }

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["correr"][0]

        # Ajustar posición inicial con la escala y el desplazamiento hacia abajo
        self.offset_y = offset_y
        self.rect = self.image.get_rect(topleft=(x, y + self.offset_y))

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

        self.proyectiles = []
        self.disparado_en_este_ataque = False
        self.cooldown_ataque = 0.0
        self.tiempo_cooldown = 2.0
        self.distancia_disparo = 400

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado:
            self.estado_actual = nuevo_estado
            self.frame_actual = 0.0
            if nuevo_estado == "golpear":
                self.disparado_en_este_ataque = False

    def disparar(self):
        origen_x = self.rect.centerx
        origen_y = self.rect.centery
        nuevo_proyectil = self.Proyectil(origen_x, origen_y, self.direction)
        self.proyectiles.append(nuevo_proyectil)

    def actualizar_animacion(self):
        frames = self.animaciones[self.estado_actual]
        self.frame_actual += self.velocidad_animacion

        if self.estado_actual == "golpear":
            if (
                int(self.frame_actual) >= 2
                and not self.disparado_en_este_ataque
            ):
                self.disparar()
                self.disparado_en_este_ataque = True

            if self.frame_actual >= len(frames):
                self.cambiar_estado("correr")
                return

        elif self.estado_actual == "muerte":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual == "dano":
            if self.frame_actual >= len(frames):
                self.esta_rojo = False
                self.cambiar_estado("correr")
                return
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
        if self.health <= 0:
            self.cambiar_estado("muerte")
        else:
            self.cambiar_estado("dano")

    def update(self, player, dt, width=WIDTH):
        for p in self.proyectiles:
            p.update(dt, player)
        self.proyectiles = [p for p in self.proyectiles if not p.destruido]

        if self.muerto_definitivo:
            return

        if self.estado_actual == "muerte":
            if hasattr(self, "aplicar_gravedad_y_suelo"):
                self.aplicar_gravedad_y_suelo()
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True

        elif self.estado_actual == "dano":
            if hasattr(self, "aplicar_gravedad_y_suelo"):
                self.aplicar_gravedad_y_suelo()
        else:
            if self.cooldown_ataque > 0:
                self.cooldown_ataque -= dt

            if player and self.estado_actual != "golpear":
                distancia = abs(player.rect.centerx - self.rect.centerx)
                if (
                    distancia <= self.distancia_disparo
                    and self.cooldown_ataque <= 0
                ):
                    self.direction = (
                        "left"
                        if player.rect.centerx < self.rect.centerx
                        else "right"
                    )
                    self.cambiar_estado("golpear")
                    self.cooldown_ataque = self.tiempo_cooldown

            if self.estado_actual != "golpear":
                super().update(player, dt, width)

        self.actualizar_animacion()

    def draw(self, screen):
        for p in self.proyectiles:
            p.draw(screen)

        if self.muerto_definitivo:
            return

        if self.image and hasattr(self, "rect"):
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
                "assets/enemigos/Karasu_tengu/Attack_3.png", 1, 3
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

        self.normalizar_saltos()

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["correr"][0]

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def normalizar_saltos(self):
        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []

        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            f_escalado = pygame.transform.scale(f, (nuevo_ancho, alto_base))
            frames_saltar_normalizados.append(f_escalado)

        self.animaciones["saltar"] = frames_saltar_normalizados

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

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))


class HombreLoboRojo(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Lobo_rojo", 2, x, y)

        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_rojo/Run.png", 1, 9
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_rojo/Attack_2.png", 1, 4
            ),
            "dano": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_rojo/Hurt.png", 1, 2
            ),
            "muerte": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_rojo/Dead.png", 1, 2
            ),
            "saltar": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_rojo/Jump.png", 1, 11
            ),
        }

        self.normalizar_saltos()

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["correr"][0]

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def normalizar_saltos(self):
        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []

        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            f_escalado = pygame.transform.scale(f, (nuevo_ancho, alto_base))
            frames_saltar_normalizados.append(f_escalado)

        self.animaciones["saltar"] = frames_saltar_normalizados

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

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))


class HombreLoboNegro(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Lobo_negro", 2, x, y)

        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_negro/walk.png", 1, 11
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_negro/Attack_2.png", 1, 4
            ),
            "dano": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_negro/Hurt.png", 1, 2
            ),
            "muerte": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_negro/Dead.png", 1, 2
            ),
            "saltar": cargar_spritesheet_jokai(
                "assets/enemigos/Lobo_negro/Jump.png", 1, 11
            ),
        }

        self.normalizar_saltos()

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["correr"][0]

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def normalizar_saltos(self):
        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []

        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            f_escalado = pygame.transform.scale(f, (nuevo_ancho, alto_base))
            frames_saltar_normalizados.append(f_escalado)

        self.animaciones["saltar"] = frames_saltar_normalizados

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

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))

class Esqueleto_Guerrero(Enemigo):

    def __init__(self, x=550, y=500, escala=1.5):  # Modifica 'escala' al tamaño que quieras
        super().__init__("Esqueleto Guerrero", 2, x, y)

        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/skeleton_Warrior/Run.png", 1, 8
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Skeleton_Warrior/Attack_3.png", 1, 4
            ),
            "dano": cargar_spritesheet_jokai(
                "assets/enemigos/Skeleton_Warrior/Hurt.png", 1, 2
            ),
            "muerte": cargar_spritesheet_jokai(
                "assets/enemigos/Skeleton_Warrior/Dead.png", 1, 4
            ),
            "saltar": cargar_spritesheet_jokai(
                "assets/enemigos/Skeleton_Warrior/Idle.png", 1, 7
            ),
        }

        self.normalizar_saltos()

        # Escala solo las imágenes sin afectar rect ni hurtbox
        if escala != 1.0:
            self.escalar_animaciones(escala)

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["correr"][0]

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def escalar_animaciones(self, factor):
        """Redimensiona los sprites visuales de las animaciones."""
        for estado, frames in self.animaciones.items():
            nuevos_frames = []
            for f in frames:
                nuevo_ancho = int(f.get_width() * factor)
                nuevo_alto = int(f.get_height() * factor)
                f_escalado = pygame.transform.scale(
                    f, (nuevo_ancho, nuevo_alto)
                )
                nuevos_frames.append(f_escalado)
            self.animaciones[estado] = nuevos_frames

    def normalizar_saltos(self):
        alto_base = self.animaciones["correr"][0].get_height()
        frames_saltar_normalizados = []

        for f in self.animaciones["saltar"]:
            escala = alto_base / f.get_height()
            nuevo_ancho = int(f.get_width() * escala)
            f_escalado = pygame.transform.scale(f, (nuevo_ancho, alto_base))
            frames_saltar_normalizados.append(f_escalado)

        self.animaciones["saltar"] = frames_saltar_normalizados

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

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))
            


    def draw(self, screen):
        if self.muerto_definitivo:
            return

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))


class Carnicero(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Carnicero", 3, x, y)


class MinotauroNaranja(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Minotauro Naranja", 2, x, y)


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
    OrcoRojo,Esqueleto_Guerrero,Karasu_tengu
]

enemigos_normales = [
    OrcoRojo,
    MinotauroNaranja,
    Jokai,
    HombreLoboRojo,
    HombreLoboNegro,
    Karasu_tengu,
    Demonio,
    Dragon,
]

enemigos_jefes = [Carnicero, Cthulhu, Cerbero, OrcoRojo2, CaballeroInfernal]


def crear_enemigo_aleatorio(x=550, y=500):
    clase_enemigo = random.choice(enemigos_normales)
    return clase_enemigo(x, y)