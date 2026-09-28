import os
import re
import pygame
import enemigos

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

    def update(self, player, dt, width=800):
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

def cargar_animacion_carpeta(ruta_carpeta):
    """Carga y ordena automáticamente todos los archivos PNG de una carpeta."""
    frames = []
    if not os.path.exists(ruta_carpeta):
        return frames
    
    # Ordena numéricamente los nombres de archivos (ej: atk1, atk2... atk12)
    archivos = os.listdir(ruta_carpeta)
    archivos_ordenados = sorted(
        archivos,
        key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)]
    )
    
    for archivo in archivos_ordenados:
        if archivo.lower().endswith('.png'):
            ruta = os.path.join(ruta_carpeta, archivo)
            imagen = pygame.image.load(ruta).convert_alpha()
            frames.append(imagen)
            
    return frames


class ImpalerBoss(Enemigo):

    def __init__(self, x=550, y=500, escala=1.5):
        super().__init__("Impaler Boss", 2, x, y)

        ruta_base = "assets/Jefes/Impaler Boss"

        # Carga automática de todas las carpetas detectadas
        self.animaciones = {
            "idle": cargar_animacion_carpeta(f"{ruta_base}/idle"),
            "correr": cargar_animacion_carpeta(f"{ruta_base}/walk"),
            "saltar": cargar_animacion_carpeta(f"{ruta_base}/idle"),
            "dano": cargar_animacion_carpeta(f"{ruta_base}/idle"),
            "muerte": cargar_animacion_carpeta(f"{ruta_base}/death"),
            
            # Ataques individuales
            "golpear_1": cargar_animacion_carpeta(f"{ruta_base}/attack1"),
            "golpear_2": cargar_animacion_carpeta(f"{ruta_base}/attack2"),
            "golpear_3": cargar_animacion_carpeta(f"{ruta_base}/attack3"),
            "golpear_4": cargar_animacion_carpeta(f"{ruta_base}/attack4"),
            "golpear_5": cargar_animacion_carpeta(f"{ruta_base}/attack5"),
            "golpear_6": cargar_animacion_carpeta(f"{ruta_base}/attack6"),
        }

        # 'golpear' estándar usa el attack1 por defecto
        self.animaciones["golpear"] = self.animaciones["golpear_1"]

        self.normalizar_saltos()

        if escala != 1.0:
            self.escalar_animaciones(escala)

        self.estado_actual = "idle"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
        self.image = self.animaciones["idle"][0]

        self.esta_rojo = False
        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def ejecutar_ataque_aleatorio(self):
        """Permite al jefe seleccionar un ataque entre attack1 y attack6 al azar."""
        import random
        num_ataque = random.randint(1, 6)
        self.animaciones["golpear"] = self.animaciones[f"golpear_{num_ataque}"]
        self.cambiar_estado("golpear")

    def escalar_animaciones(self, factor):
        for estado, frames in self.animaciones.items():
            nuevos_frames = []
            for f in frames:
                nuevo_ancho = int(f.get_width() * factor)
                nuevo_alto = int(f.get_height() * factor)
                f_escalado = pygame.transform.scale(f, (nuevo_ancho, nuevo_alto))
                nuevos_frames.append(f_escalado)
            self.animaciones[estado] = nuevos_frames

    def normalizar_saltos(self):
        if not self.animaciones["correr"]:
            return
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
        if not frames:
            return

        self.frame_actual += self.velocidad_animacion

        if self.estado_actual == "muerte":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual in ("golpear", "dano"):
            if self.frame_actual >= len(frames):
                self.esta_rojo = False
                self.cambiar_estado("idle")
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
            imagen_frame.fill((255, 50, 50), special_flags=pygame.BLEND_RGB_MULT)

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

    def update(self, player, dt, width=800):
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
                if self.estado_actual != "golpear":
                    self.ejecutar_ataque_aleatorio()
            elif abs(self.rect.x - player.rect.x) > self.stop_distance:
                self.cambiar_estado("correr")
            else:
                self.cambiar_estado("idle")

        self.actualizar_animacion()

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))