import os
import random
import math

import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_sonidos_accion = {}
_audio_disponible = None
_perfiles_sonido = {
    "Lobo_rojo": (115, 0),
    "Lobo_negro": (82, 1),
    "Mushroom": (310, 2),
}


def _crear_sonido_accion(nombre, accion):
    global _audio_disponible

    if _audio_disponible is False:
        return None

    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error as error:
            print(f"No se pudo iniciar el audio de los enemigos: {error}")
            _audio_disponible = False
            return None

    frecuencia_mixer, formato, canales = pygame.mixer.get_init()
    if formato != -16:
        print(
            "No se pueden reproducir los sonidos de enemigos: "
            f"el mixer usa formato {formato}, se necesita -16."
        )
        _audio_disponible = False
        return None

    perfil = _perfiles_sonido.get(nombre)
    if perfil is None:
        semilla = sum((indice + 1) * ord(letra) for indice, letra in enumerate(nombre))
        perfil = (90 + semilla % 220, semilla % 3)

    frecuencia_base, forma_onda = perfil
    duraciones = {
        "ataque": 0.20,
        "danio": 0.13,
        "muerte": 0.32,
        "salto": 0.10,
        "esquive": 0.09,
        "paso": 0.08,
    }
    duracion = duraciones[accion]
    cantidad_muestras = int(frecuencia_mixer * duracion)
    muestras = array("h")
    ruido = random.Random(f"{nombre}-{accion}")

    for indice in range(cantidad_muestras):
        progreso = indice / cantidad_muestras
        muestra_ruido = ruido.uniform(-1.0, 1.0)
        if accion == "paso":
            fase = 2 * math.pi * frecuencia_base * indice / frecuencia_mixer
            envolvente = (1.0 - progreso) ** 5
            onda = 0.28 * muestra_ruido + 0.18 * math.sin(fase)
        elif accion == "ataque":
            golpe = math.exp(-((progreso - 0.18) / 0.055) ** 2)
            resonancia = math.exp(-progreso * 11)
            fase = (
                2 * math.pi * frecuencia_base * (1 - progreso * 0.35)
                * indice / frecuencia_mixer
            )
            envolvente = 0.08 + golpe * 0.85 + resonancia * 0.25
            onda = muestra_ruido * (0.85 if golpe > 0.3 else 0.12)
            onda += math.sin(fase) * 0.45 * resonancia
        elif accion in ("salto", "esquive"):
            envolvente = math.sin(math.pi * progreso) ** 1.5
            onda = muestra_ruido * 0.6 + math.sin(
                2 * math.pi * frecuencia_base * (2 + progreso) * indice
                / frecuencia_mixer
            ) * 0.2
        elif accion == "danio":
            fase = 2 * math.pi * frecuencia_base * 0.8 * indice / frecuencia_mixer
            envolvente = (1.0 - progreso) ** 6
            onda = muestra_ruido * 0.65 + math.sin(fase) * 0.55
        else:
            frecuencia = frecuencia_base * (1.0 - progreso * 0.65)
            fase = 2 * math.pi * frecuencia * indice / frecuencia_mixer
            if forma_onda == 1:
                onda = 0.6 * math.sin(fase) + 0.4 * (
                    1 if math.sin(fase) >= 0 else -1
                )
            elif forma_onda == 2:
                onda = 2 * math.asin(math.sin(fase)) / math.pi
            else:
                onda = math.sin(fase)
            envolvente = (1.0 - progreso) ** 1.2

        volumen = 3500 if accion == "paso" else 12000
        muestra = int(volumen * envolvente * onda)
        for _ in range(canales):
            muestras.append(muestra)

    sonido = pygame.mixer.Sound(buffer=muestras.tobytes())
    _sonidos_accion[(nombre, accion)] = sonido
    return sonido


def _reproducir_sonido_accion(nombre, accion):
    clave = (nombre, accion)
    sonido = _sonidos_accion.get(clave)
    if sonido is None:
        sonido = _crear_sonido_accion(nombre, accion)
    if sonido is not None:
        sonido.play()


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


def obtener_frame_seguro(frames, indice):
    return frames[max(0, min(len(frames) - 1, int(indice)))]


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
        self.attack_cooldown_time = 1.15
        self.has_hit = False
        self.ataque_coordinado = False
        self.attack_windup = 0.22
        self.attack_active_time = 0.30

        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -12
        self.on_ground = False
        self.suelo_y = 590
        self.plataformas = []
        self.flank_side = 1
        self.preferred_distance = 80
        self.strafe_timer = 1.0
        self.strafe_direction = 1
        self.jump_cooldown = 0.0
        self.dodge_timer = 0.0
        self.allies = []
        self.attack_range = 140
        self.combat_phase = "approach"
        self.phase_timer = 0.0
        self.dodge_direction = 1
        self.dodge_cooldown = 0.0
        self.footstep_timer = 0.0

        # Distancia mínima para detenerse antes de empujar o traspasar al jugador
        self.stop_distance = 35

    def aplicar_gravedad_y_suelo(self):
        bottom_anterior = self.rect.bottom
        self.on_ground = False
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.velocity_y >= 0:
            for plataforma in self.plataformas:
                zona_suelo = plataforma.inflate(-20, 0)
                pisa_plataforma = (
                    bottom_anterior <= zona_suelo.top
                    and self.rect.bottom >= zona_suelo.top
                    and self.rect.right > zona_suelo.left
                    and self.rect.left < zona_suelo.right
                )
                if pisa_plataforma:
                    self.rect.bottom = zona_suelo.top
                    self.velocity_y = 0
                    self.on_ground = True
                    break

        if not self.on_ground and self.rect.bottom >= self.suelo_y:
            self.rect.bottom = self.suelo_y
            self.velocity_y = 0
            self.on_ground = True

    def update(self, player, dt, width=WIDTH):
        self.footstep_timer = max(0, self.footstep_timer - dt)
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - dt)

        if self.attacking:
            self.attack_timer -= dt
            if self.combat_phase == "windup" and self.attack_timer <= 0:
                self.combat_phase = "attack"
                self.attack_timer = self.attack_active_time
                self.hitbox = self.crear_hitbox_ataque()
            elif self.combat_phase == "attack" and self.attack_timer <= 0:
                self.attacking = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)
                self.combat_phase = "approach"
                self.phase_timer = 0

        target = getattr(player, "jugador", player)
        target_x = getattr(player, "pos_x", target.rect.centerx)
        target_hurtbox = getattr(
            player, "hurtbox", getattr(target, "hurtbox", target.rect)
        )
        dx = target_x - self.rect.centerx
        distance_x = abs(dx)
        distance_y = abs(target_hurtbox.centery - self.rect.centery)
        target_attacking = getattr(target, "atacando", False)
        self.dodge_cooldown = max(0, self.dodge_cooldown - dt)

        player_hitbox = getattr(target, "hitbox", pygame.Rect(0, 0, 0, 0))
        attack_nearby = (
            target_attacking
            and distance_x < 260
            and (
                player_hitbox.colliderect(self.rect.inflate(100, 40))
                or distance_x < 165
            )
        )
        if (
            attack_nearby
            and self.dodge_cooldown <= 0
            and not self.attacking
            and self.combat_phase != "dodge"
        ):
            self.combat_phase = "dodge"
            self.phase_timer = 0.24
            self.dodge_direction = -1 if dx > 0 else 1
            self.dodge_cooldown = 1.6
            _reproducir_sonido_accion(self.name, "esquive")

        desired_x = target_x + self.flank_side * self.preferred_distance
        approach_dx = desired_x - self.rect.centerx
        move_x = 0
        if self.combat_phase == "dodge" and not self.attacking:
            self.phase_timer -= dt
            move_x = self.dodge_direction
            if self.phase_timer <= 0:
                self.combat_phase = "approach"
        elif self.combat_phase == "retreat" and not self.attacking:
            self.phase_timer -= dt
            move_x = -1 if dx > 0 else 1
            if self.phase_timer <= 0:
                self.combat_phase = "approach"
        elif not self.attacking:
            if abs(approach_dx) > 18:
                move_x = 1 if approach_dx > 0 else -1

        x_anterior = self.rect.x
        if not self.attacking:
            move_speed = self.speed * 60 * dt
            if self.combat_phase == "retreat":
                move_speed += 60 * dt
            if self.combat_phase == "approach":
                distance_to_slot = abs(approach_dx)
                move_speed = min(move_speed, max(0, distance_to_slot))
            self.rect.x += round(move_x * move_speed)
        if (
            self.rect.x != x_anterior
            and move_x
            and self.on_ground
            and self.footstep_timer <= 0
        ):
            _reproducir_sonido_accion(self.name, "paso")
            self.footstep_timer = 0.48
        if dx:
            self.direction = "right" if dx > 0 else "left"

        self.jump_cooldown = max(0, self.jump_cooldown - dt)
        should_jump = (
            getattr(self, "can_jump", True)
            and not self.attacking
            and self.on_ground
            and self.jump_cooldown <= 0
            and (
                attack_nearby and self.combat_phase == "dodge"
                or target_hurtbox.bottom < self.rect.top - 35
            )
        )
        if should_jump:
            self.velocity_y = self.jump_force
            self.on_ground = False
            self.jump_cooldown = random.uniform(2.8, 4.5)
            _reproducir_sonido_accion(self.name, "salto")

        self.aplicar_gravedad_y_suelo()
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x))
        self.hurtbox.topleft = self.rect.topleft
        distance_x = abs(target_x - self.rect.centerx)
        distance_y = abs(target_hurtbox.centery - self.rect.centery)

        if (
            not self.ataque_coordinado
            and not self.attacking
            and self.attack_cooldown <= 0
            and self.combat_phase == "approach"
            and distance_x <= self.attack_range
            and distance_y <= 95
        ):
            self.attack()

    def attack(self):
        if self.attack_cooldown > 0:
            return
        self.attacking = True
        self.combat_phase = "windup"
        self.attack_timer = self.attack_windup
        self.attack_cooldown = self.attack_cooldown_time
        self.has_hit = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        _reproducir_sonido_accion(self.name, "ataque")

    def crear_hitbox_ataque(self):
        hitbox_x = (
            self.rect.right
            if self.direction == "right"
            else self.rect.left - 140
        )
        return pygame.Rect(hitbox_x, self.rect.centery - 55, 140, 110)

    def take_damage(self, damage):
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        accion = "muerte" if self.health <= 0 else "danio"
        _reproducir_sonido_accion(self.name, accion)
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
        self.velocidad_animacion = 0.12
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
                if self.estado_actual == "golpear" and self.attacking:
                    self.frame_actual = len(frames) - 1
                else:
                    self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = frames[max(0, min(len(frames) - 1, int(self.frame_actual)))]

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
        self.velocidad_animacion = 0.12
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
                if self.estado_actual == "golpear" and self.attacking:
                    self.frame_actual = len(frames) - 1
                else:
                    self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = obtener_frame_seguro(frames, self.frame_actual)

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
    DANO_PROYECTIL = 10
    ALTURA_VUELO = 70   # px sobre el suelo a los que flota el CENTRO del ojo
 
    class Proyectil:
 
        def __init__(self, x, y, direccion, dano=10, objetivo=None):
            self.direccion = direccion
            self.dano = dano
            self.velocidad = 350
            if objetivo is None:
                self.velocidad_x = -self.velocidad if direccion == "left" else self.velocidad
                self.velocidad_y = 0
            else:
                dx = objetivo[0] - x
                dy = objetivo[1] - y
                distancia = max(1, math.hypot(dx, dy))
                self.velocidad_x = self.velocidad * dx / distancia
                self.velocidad_y = self.velocidad * dy / distancia
            self.frame_actual = 0.0
            self.velocidad_anim = 0.15
            self.destruido = False
            self.estado = "vuelo"
            self.x_inicial = x
            self.alcance_max = 1500  # px desde donde fue disparado
 
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
 
            frame_img = self.image
 
            if self.estado == "vuelo":
                self.rect.x += round(self.velocidad_x * dt)
                self.rect.y += round(self.velocidad_y * dt)
 
                self.frame_actual += self.velocidad_anim
                if self.frame_actual >= len(self.frames_vuelo):
                    self.frame_actual = 0.0
 
                frame_img = obtener_frame_seguro(self.frames_vuelo, self.frame_actual)
 
                if player:
                    # Hurtbox del jugador en coordenadas de MUNDO
                    target_box = getattr(player, "hurtbox", player.rect).copy()
                    if hasattr(player, "pos_x"):
                        target_box.centerx = int(player.pos_x)
 
                    if self.rect.colliderect(target_box):
                        if hasattr(player, "take_damage"):
                            player.take_damage(self.dano)
                        self.estado = "impacto"
                        self.frame_actual = 0.0
 
                if abs(self.rect.centerx - self.x_inicial) > self.alcance_max:
                    self.destruido = True
 
            elif self.estado == "impacto":
                self.frame_actual += self.velocidad_anim
                if self.frame_actual >= len(self.frames_explosion):
                    self.destruido = True
                    return
 
                frame_img = obtener_frame_seguro(self.frames_explosion, self.frame_actual)
 
            if self.direccion == "left":
                frame_img = pygame.transform.flip(frame_img, True, False)
 
            self.image = frame_img
 
        def draw(self, screen, scroll_x=0):
            if not self.destruido and self.image:
                screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))
 
    def __init__(self, x=550, y=500, escala_enemigo=1.8, suelo_y=620):
        super().__init__("Ojo volador", 2, x, y)
 
        self.suelo_y = suelo_y
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
        self.velocidad_animacion = 0.12
        self.image = self.animaciones["correr"][0]
 
        # Flota a ALTURA_VUELO px sobre el suelo
        self.rect = self.image.get_rect(
            center=(x, self.suelo_y - self.ALTURA_VUELO)
        )
 
        # Se queda a esta distancia horizontal del jugador (alcance de la espada)
        self.stop_distance = 140
 
        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False
 
        self.proyectiles = []
        self.disparado_en_este_ataque = False
        self.cooldown_ataque = 0.0
        self.tiempo_cooldown = 1.35
        self.distancia_disparo = 350
        self.objetivo_ataque = None
        self.flank_side = 1
        self.preferred_distance = random.randint(255, 285)
        self.strafe_timer = 1.0
        self.strafe_direction = 1
        self.altura_orbita = random.randint(-50, 45)
        self.velocidad_vuelo = 180
        self.distancia_minima_vuelo = 170

        self.actualizar_hurtbox()
 
    def actualizar_hurtbox(self):
        """Hurtbox centrada en el sprite actual (60% de ancho, 70% de alto)."""
        if self.health <= 0:
            self.hurtbox = pygame.Rect(0, 0, 0, 0)
            return
 
        ancho = int(self.rect.width * 0.6)
        alto = int(self.rect.height * 0.7)
        self.hurtbox = pygame.Rect(0, 0, ancho, alto)
        self.hurtbox.center = self.rect.center
 
    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado:
            self.estado_actual = nuevo_estado
            self.frame_actual = 0.0
            if nuevo_estado == "golpear":
                self.disparado_en_este_ataque = False
 
    def disparar(self, objetivo=None):
        destino = None
        if objetivo is not None:
            destino_x = getattr(objetivo, "pos_x", objetivo.rect.centerx)
            destino = (destino_x, objetivo.rect.centery)
        nuevo = self.Proyectil(
            self.rect.centerx, self.rect.centery,
            self.direction, dano=self.DANO_PROYECTIL, objetivo=destino
        )
        self.proyectiles.append(nuevo)
 
    def actualizar_animacion(self):
        frames = self.animaciones[self.estado_actual]
        self.frame_actual += self.velocidad_animacion
 
        if self.estado_actual == "golpear":
            if int(self.frame_actual) >= 2 and not self.disparado_en_este_ataque:
                self.disparar(self.objetivo_ataque)
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
 
        imagen_frame = obtener_frame_seguro(frames, self.frame_actual)
 
        if self.direction == "left":
            imagen_frame = pygame.transform.flip(imagen_frame, True, False)
 
        if self.esta_rojo:
            imagen_frame = imagen_frame.copy()
            imagen_frame.fill((255, 50, 50), special_flags=pygame.BLEND_RGB_MULT)
 
        self.image = imagen_frame
        # El rect sigue al sprite manteniendo el CENTRO (el ojo flota)
        self.rect = self.image.get_rect(center=self.rect.center)
 
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
 
        # Seguro: si la vida llegó a 0 por otro lado, entra igual en "muerte"
        if self.health <= 0 and self.estado_actual != "muerte":
            self.cambiar_estado("muerte")
 
        if self.estado_actual == "muerte":
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True
 
        elif self.estado_actual == "dano":
            pass
 
        else:
            if self.cooldown_ataque > 0:
                self.cooldown_ataque = max(0, self.cooldown_ataque - dt)
 
            if player and self.estado_actual != "golpear":
                px = getattr(player, "pos_x", player.rect.centerx)
                dx = px - self.rect.centerx
                distancia = abs(dx)
 
                if dx < -5:
                    self.direction = "left"
                elif dx > 5:
                    self.direction = "right"
 
                jugador_real = getattr(player, "jugador", player)
                desplazamiento_x = 0
                if distancia < self.distancia_minima_vuelo:
                    desplazamiento_x = -1 if dx > 0 else 1
                elif distancia > self.preferred_distance + 25:
                    desplazamiento_x = 1 if dx > 0 else -1
                self.rect.x += round(desplazamiento_x * self.velocidad_vuelo * dt)

                altura_objetivo = max(
                    190,
                    min(
                        self.suelo_y - 65,
                        jugador_real.rect.centery - 100 + self.altura_orbita,
                    ),
                )
                delta_y = altura_objetivo - self.rect.centery
                self.rect.centery += max(-3, min(3, delta_y))
 
                if (
                    self.distancia_minima_vuelo <= distancia <= self.distancia_disparo
                    and self.cooldown_ataque <= 0
                ):
                    self.objetivo_ataque = jugador_real
                    self.cambiar_estado("golpear")
                    self.cooldown_ataque = self.tiempo_cooldown
 
        self.actualizar_animacion()
 
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x))
        self.actualizar_hurtbox()
 
    def draw(self, screen, scroll_x=0):
        for p in self.proyectiles:
            p.draw(screen, scroll_x)
 
        if self.muerto_definitivo:
            return
 
        if self.image:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))
 


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
        self.velocidad_animacion = 0.12
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
                if self.estado_actual == "golpear" and self.attacking:
                    self.frame_actual = len(frames) - 1
                else:
                    self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = obtener_frame_seguro(frames, self.frame_actual)

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
        self.velocidad_animacion = 0.12
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
                if self.estado_actual == "golpear" and self.attacking:
                    self.frame_actual = len(frames) - 1
                else:
                    self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = obtener_frame_seguro(frames, self.frame_actual)

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
        self.velocidad_animacion = 0.12
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
                if self.estado_actual == "golpear" and self.attacking:
                    self.frame_actual = len(frames) - 1
                else:
                    self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = obtener_frame_seguro(frames, self.frame_actual)

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


class Mushroom(Enemigo):

    def __init__(self, x=550, y=500):
        super().__init__("Mushroom", 2, x, y)

        self.animaciones = {
            "correr": cargar_spritesheet_jokai(
                "assets/enemigos/Mushroom/Run.png", 1, 8
            ),
            "golpear": cargar_spritesheet_jokai(
                "assets/enemigos/Mushroom/Attack.png", 1, 8
            ),
            "dano": cargar_spritesheet_jokai(
                "assets/enemigos/Mushroom/Take Hit.png", 1, 4
            ),
            "muerte": cargar_spritesheet_jokai(
                "assets/enemigos/Mushroom/Death.png", 1, 4
            ),
            "saltar": cargar_spritesheet_jokai(
                "assets/enemigos/Mushroom/Idle.png", 1, 4
            ),
        }
        bounds = [
            frame.get_bounding_rect()
            for frames in self.animaciones.values()
            for frame in frames
        ]
        frame_width = max(bound.width for bound in bounds)
        frame_height = max(bound.height for bound in bounds)
        for estado, frames in self.animaciones.items():
            frames_ajustados = []
            for frame in frames:
                visible = frame.get_bounding_rect()
                recortado = frame.subsurface(visible).copy()
                ajustado = pygame.Surface(
                    (frame_width, frame_height), pygame.SRCALPHA
                )
                ajustado.blit(
                    recortado,
                    (
                        (frame_width - visible.width) // 2,
                        frame_height - visible.height,
                    ),
                )
                frames_ajustados.append(
                    pygame.transform.scale(
                        ajustado,
                        (int(frame_width * 2.2), int(frame_height * 2.2)),
                    )
                )
            self.animaciones[estado] = frames_ajustados
        self.rect.inflate_ip(10, 10)
        self.hurtbox = self.rect.copy()
        self.can_jump = False

        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.12
        self.image = self.animaciones["correr"][0]
        self.esta_rojo = False
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
            self.frame_actual = min(self.frame_actual, len(frames) - 1)
        elif self.estado_actual in ("golpear", "dano"):
            if self.frame_actual >= len(frames):
                self.esta_rojo = False
                if self.estado_actual == "golpear" and self.attacking:
                    self.frame_actual = len(frames) - 1
                else:
                    self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            self.frame_actual = min(self.frame_actual, len(frames) - 1)
        elif self.frame_actual >= len(frames):
            self.frame_actual = 0.0

        imagen_frame = obtener_frame_seguro(frames, self.frame_actual)
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
        self.velocidad_animacion = 0.12
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
                if self.estado_actual == "golpear" and self.attacking:
                    self.frame_actual = len(frames) - 1
                else:
                    self.cambiar_estado("correr")
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        imagen_frame = obtener_frame_seguro(frames, self.frame_actual)

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