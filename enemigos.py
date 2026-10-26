import pygame
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WIDTH = 1350

def abrir_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                print(linea.strip().split(","))
    except FileNotFoundError:
        print("No se encontro un archivo en la ruta enviada.")

def cargar_spritesheet_jokai(ruta_relativa, filas, columnas):
    # Procesa la ruta utilizando objetos pathlib.Path limpios
    partes_ruta = Path(ruta_relativa).parts
    ruta_completa = BASE_DIR.joinpath(*partes_ruta)
    
    # Executa la lectura limpia sin usar metodos binarios .load()
    abrir_archivo(ruta_completa)

    # Genera superficies simuladas proporcionales para la animación por frames
    frames = []
    for fila in range(filas):
        for col in range(columnas):
            frame_mock = pygame.Surface((70, 90), pygame.SRCALPHA)
            pygame.draw.rect(frame_mock, (140, 20, 20), (0, 0, 70, 90))
            frames.append(frame_mock)
            
    return frames

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
        dx = player.rect.centerx - self.rect.centerx
        if dx < -5:
            self.direction = "left"
        elif dx > 5:
            self.direction = "right"

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
        if distance_x < 100 and distance_y < 80 and not self.attacking:
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
            self.hitbox = pygame.Rect(self.rect.right, self.rect.y + 20, 50, 50)
        else:
            self.hitbox = pygame.Rect(self.rect.left - 50, self.rect.y + 20, 50, 50)

    def take_damage(self, damage):
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        print(f"{self.name} recibió {damage} de daño. Vida restante: {self.health}")

    def draw(self, screen):
        color = (200, 50, 50) if self.direction == "left" else (50, 200, 50)
        pygame.draw.rect(screen, color, self.rect)


class OrcoRojo(Enemigo):
    def __init__(self, x=550, y=500):
        super().__init__("Orco_Rojo", 2, x, y)
        self.animaciones = {
            "correr": cargar_spritesheet_jokai("assets/enemigos/Orco_rojo/Run.txt", 1, 6),
            "golpear": cargar_spritesheet_jokai("assets/enemigos/Orco_rojo/Attack_3.txt", 1, 2),
            "dano": cargar_spritesheet_jokai("assets/enemigos/Orco_rojo/Hurt.txt", 1, 2),
            "muerte": cargar_spritesheet_jokai("assets/enemigos/Orco_rojo/Dead.txt", 1, 4),
            "saltar": cargar_spritesheet_jokai("assets/enemigos/Orco_rojo/Jump.txt", 1, 5),
        }
        self.estado_actual = "correr"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.15
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
        if self.frame_actual >= len(frames):
            if self.estado_actual in ("muerte", "saltar"):
                self.frame_actual = len(frames) - 1
            else:
                self.frame_actual = 0.0
                if self.estado_actual in ("golpear", "dano"):
                    self.cambiar_estado("correr")

        self.image = frames[int(self.frame_actual)]

    def update(self, player, dt, width=WIDTH):
        if self.muerto_definitivo: return
        if self.estado_actual == "muerte":
            self.aplicar_gravedad_y_suelo()
            self.hurtbox = pygame.Rect(0, 0, 0, 0)
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0: self.muerto_definitivo = True
        elif self.estado_actual == "dano":
            self.aplicar_gravedad_y_suelo()
            self.hurtbox.topleft = self.rect.topleft
        else:
            super().update(player, dt, width)
            if not self.on_ground: self.cambiar_estado("saltar")
            elif self.attacking: self.cambiar_estado("golpear")
            else: self.cambiar_estado("correr")
        self.actualizar_animacion()

    def draw(self, screen):
        if self.muerto_definitivo: return
        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))

# Definición de herencias estructurales limpias basadas en archivos de texto
class Jokai(OrcoRojo): pass
class Karasu_tengu(OrcoRojo): pass
class HombreLoboRojo(OrcoRojo): pass
class HombreLoboNegro(OrcoRojo): pass
class Carnicero(Enemigo): pass
class MinotauroNaranja(Enemigo): pass
class Cthulhu(Enemigo): pass
class Cerbero(Enemigo): pass
class OrcoRojo2(Enemigo): pass
class Demonio(Enemigo): pass
class CaballeroInfernal(Enemigo): pass
class Dragon(Enemigo): pass

enemigos_normales = [OrcoRojo, MinotauroNaranja, Jokai, HombreLoboRojo, HombreLoboNegro, Karasu_tengu, Demonio, Dragon]

def crear_enemigo_aleatorio(x=550, y=500):
    clase_enemigo = random.choice(enemigos_normales)
    return clase_enemigo(x, y)
