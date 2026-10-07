import os
import re
import random
import pygame
import math
from Carnicero_demonio_jefe_batalla import Enemigo, Proyectil, cargar_animacion_con_altura_maxima

try:
    from enemigos import Enemigo
except ImportError:
    class Enemigo(pygame.sprite.Sprite):
        def __init__(self, nombre, vida, x, y):
            super().__init__()
            self.nombre = nombre
            self.health = vida * 50
            self.max_health = self.health
            self.rect = pygame.Rect(x, y, 125, 155)
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

def cargar_animacion_con_altura_maxima(ruta_carpeta, altura_maxima=135, rango_frames=None):
    """
    Carga cada frame, recorta bordes transparentes y escala la imagen
    de forma proporcional para que su altura no supere la 'altura_maxima' (135px).
    """
    frames = []
    if os.path.exists(ruta_carpeta):
        try:
            archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(".png")]
            archivos.sort(key=extraer_numero)

            for archivo in archivos:
                num = extraer_numero(archivo)
                if rango_frames is not None:
                    if num < rango_frames[0] or num > rango_frames[1]:
                        continue

                path_completo = os.path.join(ruta_carpeta, archivo)
                img = pygame.image.load(path_completo).convert_alpha()
                
                # Recorte de bordes transparentes sobrantes
                bbox = img.get_bounding_rect()
                if bbox.width > 0 and bbox.height > 0:
                    img = img.subsurface(bbox)

                ancho_orig, alto_orig = img.get_size()
                if alto_orig > 0:
                    # Reescalado proporcional fijando la altura máxima a altura_maxima (135)
                    factor_escala = altura_maxima / float(alto_orig)
                    nuevo_ancho = max(1, int(ancho_orig * factor_escala))
                    nuevo_alto = int(altura_maxima)
                    img = pygame.transform.scale(img, (nuevo_ancho, nuevo_alto))
                
                frames.append(img)
        except Exception as e:
            print(f"Error cargando {ruta_carpeta}: {e}")
    return frames

import json
import math
import os
import random
 
import pygame
 
ESCALA = 2                                                  # pixel-perfect: x2 en pantalla
CARPETA_SPRITES = os.path.join("assets", "imagenes", "Jefes", "Ciervo")
 
 
# ----------------------------------------------------------------------------



# --- CLASES AUXILIARES ---

# --- JEFES ---

class ImpalerBoss(Enemigo):

    def __init__(self, x=900, y=500):
        super().__init__("Impaler Boss", 10, x, y)

        base_path = os.path.join("assets", "Jefes", "Impaler Boss")
        ALTURA_MAX = 150

        self.animaciones = {
            "idle": cargar_animacion_con_altura_maxima(os.path.join(base_path, "idle"), ALTURA_MAX),
            "correr": cargar_animacion_con_altura_maxima(os.path.join(base_path, "walk"), ALTURA_MAX),
            "saltar": cargar_animacion_con_altura_maxima(os.path.join(base_path, "jump"), ALTURA_MAX),
            "muerte": cargar_animacion_con_altura_maxima(os.path.join(base_path, "death"), ALTURA_MAX),
            "attack1": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack1"), ALTURA_MAX),
            "attack2": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack2"), ALTURA_MAX),
            "attack3": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack3"), ALTURA_MAX),
            "attack4": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack4"), ALTURA_MAX),
            "attack5": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack5"), ALTURA_MAX),
            "attack6": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack6"), ALTURA_MAX),
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
            self.image = pygame.Surface((110, ALTURA_MAX))
            self.image.fill((200, 0, 50))

        self.rect = pygame.Rect(x, y, 110, ALTURA_MAX)
        self.hurtbox = self.rect.copy()
        self.hitbox = pygame.Rect(0, 0, 0, 0)

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
        if self.attacking:
            ancho_hitbox = 130
            alto_hitbox = 135
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


class WerewolfBoss(Enemigo):

    def __init__(self, x=900, y=500):
        super().__init__("Werewolf Boss", 12, x, y)

        base_path = os.path.join("assets", "Jefes", "werewolf")
        ALTURA_MAX = 100

        self.animaciones = {
            "idle": cargar_animacion_con_altura_maxima(os.path.join(base_path, "idle"), ALTURA_MAX),
            "correr": cargar_animacion_con_altura_maxima(os.path.join(base_path, "walk"), ALTURA_MAX),
            "muerte": cargar_animacion_con_altura_maxima(os.path.join(base_path, "death"), ALTURA_MAX),
            "volar": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack 3"), ALTURA_MAX, rango_frames=(6, 6)),
            "attack1": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack 1"), ALTURA_MAX),
            "attack2": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack 2"), ALTURA_MAX),
            "attack4": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack 4"), ALTURA_MAX),
            "attack5": cargar_animacion_con_altura_maxima(os.path.join(base_path, "attack 5"), ALTURA_MAX),
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
            self.image = pygame.Surface((110, ALTURA_MAX))
            self.image.fill((100, 50, 150))

        ANCHO_BASE = 110
        self.rect = pygame.Rect(x, SUELO_Y - ALTURA_MAX, ANCHO_BASE, ALTURA_MAX)
        self.hurtbox = self.rect.copy()
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.velocity_y = 0
        self.gravity = 0.6
        self.on_ground = True

        self.direction = "right"
        self.attacking = False
        self.has_hit = False
        self.dano_ataque = 15

        self.cooldown_ataque = 0.0

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
        ataques = ["attack1", "attack2", "attack4", "attack5"]
        disponibles = [a for a in ataques if len(self.animaciones.get(a, [])) > 0]
        return random.choice(disponibles) if disponibles else "idle"

    def actualizar_hitbox_ataque(self):
        if self.attacking:
            ancho_hitbox = 140
            alto_hitbox = 135
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
        elif self.estado_actual.startswith("attack"):
            if self.frame_actual >= len(frames):
                self.attacking = False
                self.has_hit = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)
                self.cooldown_ataque = 1.0 
                self.cambiar_estado("idle")
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

        if self.health <= 0:
            self.health = 0
            self.cambiar_estado("muerte")
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True
            self.actualizar_animacion()
            return

        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= dt

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= SUELO_Y:
            self.rect.bottom = SUELO_Y
            self.velocity_y = 0
            self.on_ground = True

        distancia = player.rect.centerx - self.rect.centerx

        if abs(distancia) > 130:
            self.direction = "right" if distancia > 0 else "left"
            velocidad = 3.2
            
            if self.attacking:
                self.rect.x += velocidad * 1.2 if self.direction == "right" else -velocidad * 1.2
            else:
                self.rect.x += velocidad if self.direction == "right" else -velocidad
                if self.on_ground:
                    self.cambiar_estado("correr")
        elif not self.attacking and self.cooldown_ataque <= 0:
            self.direction = "right" if distancia > 0 else "left"
            self.attacking = True
            self.has_hit = False
            ataque = self.seleccionar_ataque_aleatorio()
            self.cambiar_estado(ataque)
        elif not self.attacking:
            self.cambiar_estado("idle")

        self.actualizar_hitbox_ataque()
        self.hurtbox = self.rect.copy()

        if self.attacking and not self.has_hit and self.hitbox.width > 0:
            cuerpo_jugador = getattr(player, 'hurtbox', player.rect)
            if self.hitbox.colliderect(cuerpo_jugador):
                if hasattr(player, 'take_damage'):
                    player.take_damage(self.dano_ataque)
                elif hasattr(player, 'recibir_danio'):
                    player.recibir_danio(self.dano_ataque)
                elif hasattr(player, 'health'):
                    player.health -= self.dano_ataque
                self.has_hit = True

        self.actualizar_animacion()

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        if self.image:
            pos_x = self.rect.centerx - (self.image.get_width() // 2)
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))



class CarniceroBoss(Enemigo):
    def __init__(self, x=920, y=310):
        ALTURA_MAX = 300
        super().__init__("Athros :The bloodred", 100, x, y)

        base_path = os.path.join("assets", "Jefes", "Carnicero")

        self.animaciones = {
            "idle": cargar_animacion_con_altura_maxima(os.path.join(base_path, "01_demon_idle"), ALTURA_MAX),
            "correr": cargar_animacion_con_altura_maxima(os.path.join(base_path, "02_demon_walk"), ALTURA_MAX),
            "attack1": cargar_animacion_con_altura_maxima(os.path.join(base_path, "03_demon_cleave"), ALTURA_MAX),
            "take_hit": cargar_animacion_con_altura_maxima(os.path.join(base_path, "04_demon_take_hit"), ALTURA_MAX),
            "muerte": cargar_animacion_con_altura_maxima(os.path.join(base_path, "05_demon_death"), ALTURA_MAX),
        }

        self.estado_actual = "idle"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.20 

        self.image = None
        for estado, frames in self.animaciones.items():
            if len(frames) > 0:
                self.image = frames[0]
                self.estado_actual = estado
                break

        if self.image is None:
            self.image = pygame.Surface((195, ALTURA_MAX))
            self.image.fill((200, 0, 50))

        self.rect = pygame.Rect(x, y, 195, ALTURA_MAX)
        self.hurtbox = self.rect.copy()
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.velocity_y = 0
        self.gravity = 0.6
        self.jump_force = -13
        self.on_ground = True
        self.cooldown_salto = 0.0

        self.direction = "left"
        self.attacking = False
        self.has_hit = False
        
        self.esta_rojo = False
        self.hit_timer = 0.0

        self.muerte_completada = False
        self.muerto_definitivo = False

        self.proyectiles = []
        self.fase_actual = 1
        
        self.timer_espiral = 0.0
        self.angulo_espiral = 0.0

        self.timer_cortina = 0.0
        self.sub_fase_cortina = 0

        self.timer_chispa = 0.0
        self.timer_estocada = 0.0
        self.en_estocada = False
        self.direccion_estocada = "left"

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado and nuevo_estado in self.animaciones:
            if len(self.animaciones[nuevo_estado]) > 0:
                self.estado_actual = nuevo_estado
                self.frame_actual = 0.0

    def seleccionar_ataque_aleatorio(self):
        ataques = ["attack1"]
        disponibles = [a for a in ataques if len(self.animaciones.get(a, [])) > 0]
        return random.choice(disponibles) if disponibles else "idle"

    def realizar_salto(self):
        if self.on_ground:
            self.velocity_y = self.jump_force
            self.on_ground = False

    def actualizar_hitbox_ataque(self):
        """
        Hitbox ajustada a la hojaza gris del machete en cada frame.
        """
        if not (self.attacking and self.estado_actual.startswith("attack")):
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            return

        frame_int = int(self.frame_actual)

        # Durante la estocada de la Fase 3, mantener la hitbox activa en frame de impacto
        if self.en_estocada and frame_int > 3:
            frame_int = 3

        hitboxes_machete_gris = {
            1: (20, 180, 120, 45),   # Machete iniciando recorrido
            2: (50, 210, 150, 50),   # Bajando hacia el frente
            3: (70, 225, 175, 55),   # Impacto pleno
            4: (30, 235, 160, 50),   # Barrido final cerca del suelo
        }

        if frame_int in hitboxes_machete_gris:
            off_x, off_y, ancho, alto = hitboxes_machete_gris[frame_int]

            if self.direction == "left":
                rect_x = self.rect.left - off_x
            else:
                rect_x = self.rect.right + off_x - ancho

            rect_y = self.rect.y + off_y
            self.hitbox = pygame.Rect(rect_x, rect_y, ancho, alto)
        else:
            self.hitbox = pygame.Rect(0, 0, 0, 0)

    def actualizar_animacion(self):
        frames = self.animaciones.get(self.estado_actual, [])
        if not frames:
            return

        if self.estado_actual == "muerte":
            self.frame_actual += self.velocidad_animacion
            if self.frame_actual >= len(frames) - 1:
                self.frame_actual = float(len(frames) - 1)
                self.muerte_completada = True
            
            idx = min(int(self.frame_actual), len(frames) - 1)
        else:
            self.frame_actual += self.velocidad_animacion
            if self.estado_actual == "take_hit":
                if self.frame_actual >= len(frames):
                    self.cambiar_estado("idle")
            elif self.estado_actual.startswith("attack"):
                if self.frame_actual >= len(frames):
                    if self.en_estocada:
                        # Mantener cuadro de ataque mientras siga embistiendo
                        self.frame_actual = float(len(frames) - 2)
                    else:
                        self.attacking = False
                        self.has_hit = False
                        self.hitbox = pygame.Rect(0, 0, 0, 0)
                        self.cambiar_estado("idle")
            else:
                if self.frame_actual >= len(frames):
                    self.frame_actual = 0.0

            idx = min(int(self.frame_actual), len(frames) - 1)

        imagen_frame = frames[idx]

        if self.direction == "right":
            imagen_frame = pygame.transform.flip(imagen_frame, True, False)

        if self.esta_rojo:
            imagen_frame = imagen_frame.copy()
            imagen_frame.fill((255, 60, 60), special_flags=pygame.BLEND_RGB_MULT)

        self.image = imagen_frame

    def ejecutar_mecanica_bullet_hell(self, player, dt, width=1280, suelo_y=610):
        pct_vida = self.health / self.max_health if self.max_health > 0 else 0

        if pct_vida > 0.60:
            self.fase_actual = 1
        elif pct_vida > 0.20:
            self.fase_actual = 2
        else:
            self.fase_actual = 3

        if self.fase_actual == 1:
            self.timer_espiral += dt
            if self.timer_espiral >= 0.40:
                self.timer_espiral = 0.0
                self.angulo_espiral = (self.angulo_espiral + 25) % 360
                
                origen_x = self.rect.centerx
                origen_y = self.rect.top + 45
                
                rad = math.radians(self.angulo_espiral)
                speed = 200
                vx = math.cos(rad) * speed
                vy = math.sin(rad) * speed
                self.proyectiles.append(Proyectil(origen_x, origen_y, vx, vy, radio=7, color=(255, 120, 20), duracion=5.0))

        elif self.fase_actual == 2:
            centro_x = width // 2 - self.rect.width // 2
            if abs(self.rect.x - centro_x) > 10 and not self.attacking:
                self.direction = "right" if self.rect.x < centro_x else "left"
                self.rect.x += 180 * dt if self.direction == "right" else -180 * dt
                self.cambiar_estado("correr")

            self.timer_cortina += dt
            if self.timer_cortina >= 1.8:
                self.timer_cortina = 0.0
                self.sub_fase_cortina = (self.sub_fase_cortina + 1) % 2

                if self.sub_fase_cortina == 0:
                    hueco_y = random.choice([suelo_y - 60, suelo_y - 130])
                    for y_pos in range(120, suelo_y, 50):
                        if abs(y_pos - hueco_y) > 65:
                            self.proyectiles.append(Proyectil(0, y_pos, 300, 0, radio=8, color=(255, 60, 0), duracion=4.5))
                            self.proyectiles.append(Proyectil(width, y_pos, -300, 0, radio=8, color=(255, 60, 0), duracion=4.5))

                else:
                    hueco_x = player.rect.centerx + random.choice([-60, 0, 60])
                    hueco_x = max(100, min(width - 100, hueco_x))
                    for x_pos in range(50, width - 50, 70):
                        if abs(x_pos - hueco_x) > 85:
                            self.proyectiles.append(Proyectil(x_pos, 0, 0, 260, radio=8, color=(255, 140, 0), duracion=3.5))

        elif self.fase_actual == 3:
            # Apuntar hacia el jugador cuando no esté en estocada
            if not self.en_estocada and not self.attacking:
                self.direction = "left" if player.rect.centerx < self.rect.centerx else "right"

            self.timer_chispa += dt
            if self.timer_chispa >= 0.45 and len(self.proyectiles) < 12:
                self.timer_chispa = 0.0
                vx = random.choice([-1, 1]) * random.randint(180, 260)
                vy = random.choice([-1, 1]) * random.randint(180, 260)
                px = self.rect.centerx + random.randint(-30, 30)
                py = self.rect.top + random.randint(20, 80)
                self.proyectiles.append(Proyectil(px, py, vx, vy, radio=7, color=(255, 230, 60), rebota=True, duracion=5.0))

            self.timer_estocada += dt
            if self.timer_estocada >= 2.5 and not self.en_estocada:
                self.timer_estocada = 0.0
                self.en_estocada = True
                self.direccion_estocada = "left" if player.rect.centerx < self.rect.centerx else "right"
                self.direction = self.direccion_estocada
                self.cambiar_estado("attack1")
                self.attacking = True
                self.has_hit = False

            if self.en_estocada:
                velocidad_dash = 650
                if self.direccion_estocada == "left":
                    self.rect.x -= velocidad_dash * dt
                else:
                    self.rect.x += velocidad_dash * dt

                # Finalizar embestida al llegar a los bordes
                if self.rect.left <= 60 or self.rect.right >= width - 60:
                    self.en_estocada = False
                    self.attacking = False
                    self.has_hit = False
                    self.hitbox = pygame.Rect(0, 0, 0, 0)
                    self.cambiar_estado("idle")

    def update(self, player, dt, width=1280, suelo_y=610):
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
            self.proyectiles.clear()
            
            if self.estado_actual != "muerte":
                self.cambiar_estado("muerte")

            if self.muerte_completada:
                self.muerto_definitivo = True
                return

            self.actualizar_animacion()
            return

        for proj in self.proyectiles[:]:
            proj.update(dt, width=width, suelo_y=suelo_y)
            if proj.duracion <= 0:
                self.proyectiles.remove(proj)

        self.ejecutar_mecanica_bullet_hell(player, dt, width=width, suelo_y=suelo_y)

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= suelo_y:
            self.rect.bottom = suelo_y
            self.velocity_y = 0
            self.on_ground = True

        distancia = player.rect.centerx - self.rect.centerx

        if self.fase_actual == 1:
            if abs(distancia) > 150 and not self.attacking:
                self.direction = "right" if distancia > 0 else "left"
                self.rect.x += 2.5 if self.direction == "right" else -2.5
                if self.on_ground:
                    self.cambiar_estado("correr")
            elif not self.attacking:
                self.direction = "right" if distancia > 0 else "left"
                self.attacking = True
                self.has_hit = False
                self.cambiar_estado(self.seleccionar_ataque_aleatorio())

        self.actualizar_hitbox_ataque()
        self.hurtbox = self.rect.copy()
        self.actualizar_animacion()

    def take_damage(self, damage):
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        self.esta_rojo = True
        self.hit_timer = 0.15
        if not self.attacking and self.health > 0 and self.fase_actual != 3:
            self.cambiar_estado("take_hit")

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        for proj in self.proyectiles:
            proj.draw(screen)

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))