import os
import random
import math
import pygame
from Jefes_enemigos import ImpalerBoss


pygame.init()

WIDTH = 1350
HEIGHT = 700
SUELO_Y = 590

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batalla contra ignis")

clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_fondo = os.path.join(BASE_DIR, "assets", "fondos", "fondo_mvp.png")

if os.path.exists(ruta_fondo):
    fondo = pygame.image.load(ruta_fondo).convert()
    fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
else:
    fondo = pygame.Surface((WIDTH, HEIGHT))
    fondo.fill((30, 30, 40))


class ParticulaFuego:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.0, 2.0)
        self.vy = random.uniform(-6.0, -2.5)
        self.radio = random.uniform(4, 9)
        self.vida = 1.0

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.radio = max(0, self.radio - dt * 5)
        self.vida -= dt * 1.8

    def draw(self, screen, alpha_global=255):
        if self.vida > 0 and self.radio > 0:
            alpha = int(self.vida * alpha_global)
            if self.vida > 0.65:
                color = (255, 255, 200, alpha)
            elif self.vida > 0.35:
                color = (255, 120, 0, alpha)
            else:
                color = (180, 20, 0, alpha)

            surf = pygame.Surface((int(self.radio * 2), int(self.radio * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(self.radio), int(self.radio)), int(self.radio))
            screen.blit(surf, (self.x - self.radio, self.y - self.radio))


class ZonaFuego:
    def __init__(self, ancho_pantalla=WIDTH, alto_pantalla=HEIGHT, suelo_y=SUELO_Y):
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.suelo_y = suelo_y

        self.estado = "inactivo"
        self.cooldown_aparicion = 6.0
        self.timer = self.cooldown_aparicion

        self.duracion_advertencia = 2.0
        self.duracion_fuego = 4.5
        self.duracion_desaparecer = 1.5

        self.lado_fuego = "izquierda"
        self.ancho_cobertura = 0.0
        self.max_ancho = self.ancho_pantalla * 0.45  
        self.alto_fuego_base = 280

        self.velocidad_expansion = self.max_ancho / 1.2
        self.alpha_opacidad = 255.0
        self.pos_y = self.suelo_y - self.alto_fuego_base

        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.particulas = []
        self.tiempo_fuego = 0

        self.alerta_surf = pygame.Surface((int(self.max_ancho), self.alto_fuego_base), pygame.SRCALPHA)
        self.alerta_surf.fill((255, 30, 0, 70))

    def activar_evento(self):
        if self.estado == "inactivo":
            self.estado = "advertencia"
            self.timer = self.duracion_advertencia
            self.ancho_cobertura = 0.0
            self.alpha_opacidad = 255.0
            self.lado_fuego = random.choice(["izquierda", "derecha"])
            self.particulas.clear()

    def update(self, player, enemy, dt):
        self.tiempo_fuego += dt * 8

        if getattr(enemy, "health", 0) <= 0 or getattr(enemy, "muerto_definitivo", False):
            self.estado = "inactivo"
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            self.particulas.clear()
            return

        if self.estado == "inactivo":
            self.timer -= dt
            if self.timer <= 0:
                self.activar_evento()
            return

        elif self.estado == "advertencia":
            self.timer -= dt
            if self.timer <= 0:
                self.estado = "activo"
                self.timer = self.duracion_fuego

        elif self.estado in ["activo", "desapareciendo"]:
            if self.estado == "activo":
                self.timer -= dt
                if self.ancho_cobertura < self.max_ancho:
                    self.ancho_cobertura += self.velocidad_expansion * dt
                    if self.ancho_cobertura > self.max_ancho:
                        self.ancho_cobertura = self.max_ancho
                if self.timer <= 0:
                    self.estado = "desapareciendo"
                    self.timer = self.duracion_desaparecer

            elif self.estado == "desapareciendo":
                self.timer -= dt
                self.alpha_opacidad = max(0.0, (self.timer / self.duracion_desaparecer) * 255.0)
                if self.timer <= 0:
                    self.estado = "inactivo"
                    self.timer = self.cooldown_aparicion
                    self.hitbox = pygame.Rect(0, 0, 0, 0)
                    self.particulas.clear()
                    return

            w = int(self.ancho_cobertura)
            if self.lado_fuego == "izquierda":
                self.hitbox = pygame.Rect(0, self.pos_y, w, self.alto_fuego_base)
            else:
                self.hitbox = pygame.Rect(self.ancho_pantalla - w, self.pos_y, w, self.alto_fuego_base)

            # Si el jugador toca el fuego, simplemente recibe daño
            if player.rect.colliderect(self.hitbox):
                player.take_damage(20 * dt)

            # Generar partículas
            if w > 0:
                for _ in range(6):
                    if self.lado_fuego == "izquierda":
                        px = random.uniform(0, w)
                    else:
                        px = random.uniform(self.ancho_pantalla - w, self.ancho_pantalla)
                    py = self.suelo_y - random.uniform(5, 70)
                    self.particulas.append(ParticulaFuego(px, py))

        for p in self.particulas[:]:
            p.update(dt)
            if p.vida <= 0 or p.radio <= 0:
                self.particulas.remove(p)

    def draw(self, screen):
        if self.estado == "inactivo":
            return

        if self.estado == "advertencia":
            if int(pygame.time.get_ticks() / 200) % 2 == 0:
                pos_x = 0 if self.lado_fuego == "izquierda" else self.ancho_pantalla - self.max_ancho
                screen.blit(self.alerta_surf, (pos_x, self.pos_y))

        elif self.estado in ["activo", "desapareciendo"]:
            if self.ancho_cobertura > 0:
                w = int(self.ancho_cobertura)
                alpha = int(self.alpha_opacidad)

                fuego_surf = pygame.Surface((w, self.alto_fuego_base), pygame.SRCALPHA)
                
                # Capas de fuego
                pygame.draw.rect(fuego_surf, (180, 20, 0, int(alpha * 0.6)), (0, 40, w, self.alto_fuego_base - 40))
                pygame.draw.rect(fuego_surf, (255, 90, 0, int(alpha * 0.8)), (0, 90, w, self.alto_fuego_base - 90))
                pygame.draw.rect(fuego_surf, (255, 210, 30, alpha), (0, 160, w, self.alto_fuego_base - 160))

                # Llama ondeante superior
                puntos_llamarada = []
                paso = max(10, w // 20)
                for x_pos in range(0, w + paso, paso):
                    x_pos = min(x_pos, w)
                    offset_y = math.sin(self.tiempo_fuego + x_pos * 0.05) * 20
                    puntos_llamarada.append((x_pos, 50 + offset_y))

                puntos_llamarada.append((w, self.alto_fuego_base))
                puntos_llamarada.append((0, self.alto_fuego_base))

                if len(puntos_llamarada) >= 3:
                    pygame.draw.polygon(fuego_surf, (255, 140, 0, int(alpha * 0.9)), puntos_llamarada)

                pos_x = 0 if self.lado_fuego == "izquierda" else self.ancho_pantalla - w
                screen.blit(fuego_surf, (pos_x, self.pos_y))

                for p in self.particulas:
                    p.draw(screen, alpha_global=alpha)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 90)
        self.speed = 6
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -13
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
        self.hitbox = pygame.Rect(0, 0, 0, 0)

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

        if self.rect.bottom >= SUELO_Y:
            self.rect.bottom = SUELO_Y
            self.velocity_y = 0
            self.on_ground = True

        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.hurtbox.topleft = self.rect.topleft

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

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
        if self.attack_cooldown > 0 or self.attacking:
            return

        self.attacking = True
        self.attack_timer = 0.15
        self.attack_cooldown = self.attack_cooldown_time
        self.has_hit = False

        if self.direction == "right":
            self.hitbox = pygame.Rect(self.rect.right, self.rect.y + 20, 60, 50)
        else:
            self.hitbox = pygame.Rect(self.rect.left - 60, self.rect.y + 20, 60, 50)

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def draw(self, screen):
        color = (0, 120, 255)
        pygame.draw.rect(screen, color, self.rect)


def dibujar_barras_vida(screen, player, enemy):
    fuente = pygame.font.SysFont("Arial", 16, bold=True)
    
    # Barra de vida del Jugador
    pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 20))
    pct_p = max(0, player.health / player.max_health)
    pygame.draw.rect(screen, (0, 220, 0), (20, 20, int(200 * pct_p), 20))
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20), 2)
    screen.blit(fuente.render(f"Jugador: {int(player.health)}", True, (255, 255, 255)), (20, 45))

    # Barra de vida del Jefe
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 320, 20, 300, 20))
    e_health = getattr(enemy, "health", 0)
    e_max_health = getattr(enemy, "max_health", 1)
    pct_e = max(0, e_health / e_max_health)
    pygame.draw.rect(screen, (220, 20, 20), (WIDTH - 320, 20, int(300 * pct_e), 20))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 320, 20, 300, 20), 2)
    screen.blit(fuente.render(f"Ignis:The infernal warrior = {int(e_health)}", True, (255, 255, 255)), (WIDTH - 320, 45))


player = Player(200, 500)
enemy = ImpalerBoss(900, 500)
zona_fuego = ZonaFuego()

running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player.attack()

    player.update(dt)
    enemy.update(player, dt, width=WIDTH)
    zona_fuego.update(player, enemy, dt)

    if player.attacking and not player.has_hit:
        if hasattr(enemy, "hurtbox") and player.hitbox.colliderect(enemy.hurtbox):
            enemy.take_damage(25)
            player.has_hit = True

    if getattr(enemy, "attacking", False) and not getattr(enemy, "has_hit", False):
        if hasattr(enemy, "hitbox") and enemy.hitbox.colliderect(player.hurtbox):
            player.take_damage(20)
            enemy.has_hit = True

    screen.blit(fondo, (0, 0))
    pygame.draw.line(screen, (200, 200, 200), (0, SUELO_Y), (WIDTH, SUELO_Y), 4)

    enemy.draw(screen)
    player.draw(screen)
    zona_fuego.draw(screen)
    dibujar_barras_vida(screen, player, enemy)

    pygame.display.flip()

pygame.quit()