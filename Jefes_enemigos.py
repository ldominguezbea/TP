import os
import re
import random
import pygame

try:
    from enemigos import Enemigo
except ImportError:
    class Enemigo(pygame.sprite.Sprite):
        def __init__(self, nombre, vida, x, y):
            super().__init__()
            self.nombre = nombre
            self.health = vida * 50
            self.max_health = self.health
            self.rect = pygame.Rect(x, y, 110, 180)
            self.hurtbox = self.rect.copy()
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            self.attacking = False
            self.has_hit = False
            self.direction = "right"

WIDTH = 1350
SUELO_Y = 590

def extraer_numero(nombre_archivo):
    numeros = re.findall(r'\d+', nombre_archivo)
    return int(numeros[0]) if numeros else 0

def cargar_animacion_carpeta(ruta_carpeta, alto_deseado=260):
    frames = []
    if os.path.exists(ruta_carpeta):
        try:
            archivos = os.listdir(ruta_carpeta)
            archivos.sort(key=extraer_numero)

            for archivo in archivos:
                if archivo.lower().endswith(".png"):
                    path_completo = os.path.join(ruta_carpeta, archivo)
                    img = pygame.image.load(path_completo).convert_alpha()
                    
                    ancho_orig, alto_orig = img.get_size()
                    if alto_orig > 0:
                        ancho_nuevo = int(ancho_orig * (alto_deseado / alto_orig))
                        img = pygame.transform.scale(img, (ancho_nuevo, alto_deseado))
                    
                    frames.append(img)
        except Exception as e:
            print(f"Error cargando {ruta_carpeta}: {e}")
    return frames


class ImpalerBoss(Enemigo):

    def __init__(self, x=900, y=500):
        super().__init__("Impaler Boss", 10, x, y)

        base_path = os.path.join("assets", "Jefes", "Impaler Boss")

        # Variable para controlar la altura total del jefe en píxeles
        ALTO_JEFE = 260

        self.animaciones = {
            "idle": cargar_animacion_carpeta(os.path.join(base_path, "idle"), alto_deseado=ALTO_JEFE),
            "correr": cargar_animacion_carpeta(os.path.join(base_path, "walk"), alto_deseado=ALTO_JEFE),
            "saltar": cargar_animacion_carpeta(os.path.join(base_path, "jump"), alto_deseado=ALTO_JEFE),
            "muerte": cargar_animacion_carpeta(os.path.join(base_path, "death"), alto_deseado=ALTO_JEFE),
            "attack1": cargar_animacion_carpeta(os.path.join(base_path, "attack1"), alto_deseado=ALTO_JEFE),
            "attack2": cargar_animacion_carpeta(os.path.join(base_path, "attack2"), alto_deseado=ALTO_JEFE),
            "attack3": cargar_animacion_carpeta(os.path.join(base_path, "attack3"), alto_deseado=ALTO_JEFE),
            "attack4": cargar_animacion_carpeta(os.path.join(base_path, "attack4"), alto_deseado=ALTO_JEFE),
            "attack5": cargar_animacion_carpeta(os.path.join(base_path, "attack5"), alto_deseado=ALTO_JEFE),
            "attack6": cargar_animacion_carpeta(os.path.join(base_path, "attack6"), alto_deseado=ALTO_JEFE),
        }

        self.estado_actual = "idle"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.25 

        self.image = None
        for estado, frames in self.animaciones.items():
            if len(frames) > 0:
                self.image = frames[0]
                self.estado_actual = estado
                break

        if self.image is None:
            self.image = pygame.Surface((120, 200))
            self.image.fill((200, 0, 50))

        # Cuerpo del jefe escalado
        self.rect = pygame.Rect(x, y, 110, 180)
        self.hurtbox = self.rect.copy()
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        # Física de Salto
        self.velocity_y = 0
        self.gravity = 0.6
        self.jump_force = -13
        self.on_ground = True
        self.cooldown_salto = 0.0

        self.direction = "right"
        self.attacking = False
        self.has_hit = False
        
        self.esta_rojo = False
        self.hit_timer = 0.0

        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado and nuevo_estado in self.animaciones:
            if len(self.animaciones[nuevo_estado]) > 0:
                self.estado_actual = nuevo_estado
                self.frame_actual = 0.0

    def seleccionar_ataque_aleatorio(self):
        ataques = ["attack1", "attack2", "attack3", "attack4", "attack5", "attack6"]
        disponibles = [a for a in ataques if len(self.animaciones.get(a, [])) > 0]
        return random.choice(disponibles) if disponibles else "idle"

    def realizar_salto(self):
        if self.on_ground and len(self.animaciones.get("saltar", [])) > 0:
            self.velocity_y = self.jump_force
            self.on_ground = False
            self.cambiar_estado("saltar")

    def actualizar_hitbox_ataque(self):
        """Hitbox invisible adaptada al nuevo tamaño."""
        if self.attacking:
            ancho_hitbox = 140
            alto_hitbox = 160
            if self.direction == "left":
                self.hitbox = pygame.Rect(self.rect.left - ancho_hitbox, self.rect.y, ancho_hitbox, alto_hitbox)
            else:
                self.hitbox = pygame.Rect(self.rect.right, self.rect.y, ancho_hitbox, alto_hitbox)
        else:
            self.hitbox = pygame.Rect(0, 0, 0, 0)

    def actualizar_animacion(self):
        frames = self.animaciones.get(self.estado_actual, [])
        if not frames:
            return

        self.frame_actual += self.velocidad_animacion

        if self.estado_actual == "muerte":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual.startswith("attack"):
            if self.frame_actual >= len(frames):
                self.attacking = False
                self.has_hit = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)
                self.cambiar_estado("idle" if self.on_ground else "saltar")
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        idx = int(self.frame_actual) % len(frames)
        imagen_frame = frames[idx]

        if self.direction == "left":
            imagen_frame = pygame.transform.flip(imagen_frame, True, False)

        if self.esta_rojo:
            imagen_frame = imagen_frame.copy()
            imagen_frame.fill((255, 60, 60), special_flags=pygame.BLEND_RGB_MULT)

        self.image = imagen_frame

    def update(self, player, dt, width=WIDTH):
        if self.muerto_definitivo:
            return

        if self.esta_rojo:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.esta_rojo = False

        if self.cooldown_salto > 0:
            self.cooldown_salto -= dt

        if self.health <= 0:
            self.health = 0
            self.cambiar_estado("muerte")
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True
            self.actualizar_animacion()
            return

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= SUELO_Y:
            self.rect.bottom = SUELO_Y
            self.velocity_y = 0
            self.on_ground = True

        distancia = player.rect.centerx - self.rect.centerx

        if self.on_ground and self.cooldown_salto <= 0 and not self.attacking:
            if player.rect.y < self.rect.y - 50 or random.random() < 0.02:
                self.realizar_salto()
                self.cooldown_salto = 3.0

        if abs(distancia) > 120:
            self.direction = "right" if distancia > 0 else "left"
            velocidad = 2.5
            self.rect.x += velocidad if self.direction == "right" else -velocidad
            if self.on_ground and not self.attacking:
                self.cambiar_estado("correr")
        elif not self.attacking:
            self.direction = "right" if distancia > 0 else "left"
            self.attacking = True
            self.has_hit = False
            ataque = self.seleccionar_ataque_aleatorio()
            self.cambiar_estado(ataque)

        self.actualizar_hitbox_ataque()
        self.hurtbox = self.rect.copy()

        self.actualizar_animacion()

    def take_damage(self, damage):
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        self.esta_rojo = True
        self.hit_timer = 0.15

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))