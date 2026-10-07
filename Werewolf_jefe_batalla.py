import os
import math
import random
import pygame

from Jefes_enemigos import WerewolfBoss


# ============================================================
# INICIALIZACIÓN
# ============================================================

pygame.init()

WIDTH = 1350
HEIGHT = 700
SUELO_Y = 590

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "Red Fang - The Guardian of the Red Eclipse"
)

clock = pygame.time.Clock()


# ============================================================
# FONDO
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ruta_fondo = os.path.join(
    BASE_DIR,
    "imagenes",
    "Nivel2",
    "Nivel2_imagen1.png"
)

if os.path.exists(ruta_fondo):
    fondo = pygame.image.load(ruta_fondo).convert()
    fondo = pygame.transform.scale(
        fondo,
        (WIDTH, HEIGHT)
    )
else:
    fondo = pygame.Surface(
        (WIDTH, HEIGHT)
    )
    fondo.fill((25, 20, 35))


# ============================================================
# FUENTES
# ============================================================

fuente_nombre = pygame.font.SysFont(
    "arial",
    20,
    bold=True
)

fuente_jefe = pygame.font.SysFont(
    "cinzel",
    18,
    bold=True
) if "cinzel" in pygame.font.get_fonts() else pygame.font.SysFont("georgia", 18, bold=True)

fuente_grande = pygame.font.SysFont(
    "arial",
    58,
    bold=True
)


# ============================================================
# JUGADOR
# ============================================================

class Player:

    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x,
            y,
            60,
            90
        )

        self.speed = 6
        self.gravity = 0.5
        self.jump_power = -13
        self.velocity_y = 0

        self.health = 150
        self.max_health = 150

        self.direction = 1

        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.has_hit = False

        self.hurtbox = self.rect.copy()

        # Hitbox invisible
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def update(self, dt):
        keys = pygame.key.get_pressed()

        dx = 0

        if keys[pygame.K_a]:
            dx -= self.speed
            self.direction = -1

        if keys[pygame.K_d]:
            dx += self.speed
            self.direction = 1

        self.rect.x += dx

        # Límites
        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        # Salto
        if (
            keys[pygame.K_w]
            and self.rect.bottom >= SUELO_Y
        ):
            self.velocity_y = self.jump_power

        # Gravedad
        self.velocity_y += self.gravity

        self.rect.y += int(self.velocity_y)

        # Suelo
        if self.rect.bottom >= SUELO_Y:
            self.rect.bottom = SUELO_Y
            self.velocity_y = 0

        self.hurtbox = self.rect.copy()

        # Cooldown del ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Duración del ataque
        if self.attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False

        # Hitbox invisible
        if self.attacking:
            if self.direction == 1:
                self.hitbox = pygame.Rect(
                    self.rect.right,
                    self.rect.y + 20,
                    60,
                    50
                )
            else:
                self.hitbox = pygame.Rect(
                    self.rect.left - 60,
                    self.rect.y + 20,
                    60,
                    50
                )
        else:
            self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self):
        if self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_timer = 0.15
            self.attack_cooldown = 0.3
            self.has_hit = False

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def draw(self, screen):
        # Cuerpo
        pygame.draw.rect(
            screen,
            (40, 110, 255),
            self.rect
        )

        # Cabeza
        pygame.draw.rect(
            screen,
            (80, 150, 255),
            (
                self.rect.x + 12,
                self.rect.y - 20,
                36,
                25
            )
        )


# ============================================================
# BARRAS DE VIDA
# ============================================================

def dibujar_barras_vida(player, enemy, fase):

    # --------------------------------------------------------
    # BARRA DEL JUGADOR
    # --------------------------------------------------------
    p_x, p_y = 25, 38
    p_w, p_h = 240, 22

    txt_p = fuente_nombre.render(
        f"JUGADOR  {int(player.health)}/{player.max_health}",
        True,
        (220, 230, 255)
    )
    screen.blit(txt_p, (p_x, p_y - 28))

    pygame.draw.rect(screen, (15, 15, 25), (p_x - 3, p_y - 3, p_w + 6, p_h + 6), border_radius=4)
    pygame.draw.rect(screen, (35, 40, 50), (p_x, p_y, p_w, p_h), border_radius=3)

    pct_p = max(0.0, player.health / player.max_health)
    w_p = int(p_w * pct_p)
    if w_p > 0:
        pygame.draw.rect(screen, (30, 180, 80), (p_x, p_y, w_p, p_h), border_radius=3)
        pygame.draw.rect(screen, (100, 240, 140), (p_x, p_y, w_p, p_h // 2), border_top_left_radius=3, border_top_right_radius=3)

    pygame.draw.rect(screen, (210, 170, 50), (p_x - 3, p_y - 3, p_w + 6, p_h + 6), width=2, border_radius=4)

    # --------------------------------------------------------
    # BARRA DEL JEFE (ESTILO FANTASÍA / SIN NÚMEROS)
    # --------------------------------------------------------
    b_w, b_h = 620, 20
    b_x = (WIDTH // 2) - (b_w // 2)
    b_y = 45

    # Texto solo con el nombre (sin cantidad numérica de vida)
    nombre_jefe = "RED FANG, THE GUARDIAN OF THE RED ECLIPSE"
    color_texto = (255, 100, 100) if fase == 2 else (230, 210, 170)
    txt_b = fuente_jefe.render(nombre_jefe, True, color_texto)
    screen.blit(txt_b, (WIDTH // 2 - txt_b.get_width() // 2, b_y - 26))

    # Base negra de fondo
    pygame.draw.rect(screen, (10, 5, 12), (b_x - 6, b_y - 6, b_w + 12, b_h + 12))
    pygame.draw.rect(screen, (25, 12, 18), (b_x, b_y, b_w, b_h))

    # Relleno de vida
    pct_b = max(0.0, enemy.health / enemy.max_health)
    w_b = int(b_w * pct_b)
    if w_b > 0:
        color_base = (190, 15, 30) if fase == 2 else (140, 20, 30)
        color_brillo = (255, 70, 80) if fase == 2 else (200, 60, 60)

        pygame.draw.rect(screen, color_base, (b_x, b_y, w_b, b_h))
        pygame.draw.rect(screen, color_brillo, (b_x, b_y, w_b, b_h // 3))

    # Marco gótico / Adornos metálicos
    color_marco = (230, 70, 80) if fase == 2 else (180, 140, 60)
    color_borde_ext = (120, 20, 30) if fase == 2 else (90, 70, 30)

    # Borde exterior e interior
    pygame.draw.rect(screen, color_borde_ext, (b_x - 6, b_y - 6, b_w + 12, b_h + 12), 2)
    pygame.draw.rect(screen, color_marco, (b_x - 2, b_y - 2, b_w + 4, b_h + 4), 2)

    # Detalle en las esquinas (Gemas / Adornos)
    tam_gema = 8
    esquinas = [
        (b_x - 6, b_y - 6),
        (b_x + b_w + 6 - tam_gema, b_y - 6),
        (b_x - 6, b_y + b_h + 6 - tam_gema),
        (b_x + b_w + 6 - tam_gema, b_y + b_h + 6 - tam_gema)
    ]
    for ex, ey in esquinas:
        pygame.draw.rect(screen, color_marco, (ex, ey, tam_gema, tam_gema))
        pygame.draw.rect(screen, (255, 230, 150) if fase != 2 else (255, 180, 180), (ex + 2, ey + 2, tam_gema - 4, tam_gema - 4))


# ============================================================
# LUNA ROJA
# ============================================================

def dibujar_luna_roja(screen, tiempo):

    # Coordenadas ajustadas sobre la luna del fondo Nivel2_imagen1.png
    x = 890
    y = 140

    for radio, alpha in [
        (110, 12),
        (95, 18),
        (80, 25)
    ]:
        halo = pygame.Surface(
            (radio * 2, radio * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            halo,
            (255, 0, 30, alpha),
            (radio, radio),
            radio
        )

        screen.blit(
            halo,
            (x - radio, y - radio)
        )

    pygame.draw.circle(
        screen,
        (105, 0, 10),
        (x, y),
        62
    )

    pygame.draw.circle(
        screen,
        (210, 18, 28),
        (x, y),
        53
    )

    # Cráteres
    pygame.draw.circle(screen, (150, 5, 15), (x - 20, y - 12), 8)
    pygame.draw.circle(screen, (145, 5, 15), (x + 17, y + 18), 11)
    pygame.draw.circle(screen, (165, 8, 18), (x + 4, y - 25), 6)
    pygame.draw.circle(screen, (130, 3, 12), (x - 25, y + 25), 5)

    pulso = int(
        math.sin(tiempo * 4) * 4
    )

    pygame.draw.circle(
        screen,
        (255, 50, 60),
        (x, y),
        63 + pulso,
        2
    )


# ============================================================
# DEMONIOS VIOLETAS
# ============================================================

def crear_demonios_violetas():
    return [
        {"x": 250, "y": 210, "fase": 0},
        {"x": WIDTH // 2, "y": 150, "fase": 2},
        {"x": 1100, "y": 210, "fase": 4}
    ]


def dibujar_demonio_violeta(screen, demonio, tiempo):
    x = demonio["x"]
    y = demonio["y"] + math.sin(tiempo * 3 + demonio["fase"]) * 8

    # Aura
    aura = pygame.Surface((110, 110), pygame.SRCALPHA)
    pygame.draw.circle(aura, (150, 30, 255, 35), (55, 55), 50)
    pygame.draw.circle(aura, (210, 60, 255, 25), (55, 55), 40)
    screen.blit(aura, (x - 55, y - 55))

    # Alas
    pygame.draw.polygon(screen, (70, 20, 100), [(x - 18, y - 5), (x - 48, y - 25), (x - 38, y + 18), (x - 12, y + 12)])
    pygame.draw.polygon(screen, (70, 20, 100), [(x + 18, y - 5), (x + 48, y - 25), (x + 38, y + 18), (x + 12, y + 12)])

    # Cuerpo
    pygame.draw.polygon(screen, (75, 15, 110), [(x, y - 30), (x - 25, y - 5), (x - 18, y + 30), (x, y + 42), (x + 18, y + 30), (x + 25, y - 5)])

    # Cabeza y cuernos
    pygame.draw.circle(screen, (105, 20, 145), (x, y - 12), 20)
    pygame.draw.polygon(screen, (45, 10, 70), [(x - 13, y - 25), (x - 25, y - 45), (x - 8, y - 32)])
    pygame.draw.polygon(screen, (45, 10, 70), [(x + 13, y - 25), (x + 25, y - 45), (x + 8, y - 32)])

    # Ojos
    pygame.draw.circle(screen, (255, 40, 70), (x - 8, y - 14), 4)
    pygame.draw.circle(screen, (255, 40, 70), (x + 8, y - 14), 4)

    # Núcleo
    pulso = int(math.sin(tiempo * 6) * 3)
    pygame.draw.circle(screen, (190, 40, 255), (x, y + 10), 9 + pulso)
    pygame.draw.circle(screen, (240, 150, 255), (x, y + 10), 4)


def dibujar_proyectil_demonio(screen, proyectil):
    x = proyectil["rect"].centerx
    y = proyectil["rect"].centery

    pygame.draw.line(screen, (110, 20, 180), (x, y - 30), (x, y + 8), 8)
    pygame.draw.circle(screen, (150, 30, 230), (x, y), 14)
    pygame.draw.circle(screen, (210, 80, 255), (x, y), 8)
    pygame.draw.circle(screen, (255, 190, 255), (x, y), 3)


# ============================================================
# ESCUDO DE INVULNERABILIDAD MEJORADO
# ============================================================

def dibujar_escudo_invulnerable(screen, enemy, tiempo):
    cx = enemy.rect.centerx
    cy = enemy.rect.centery
    radio_base = max(enemy.rect.width, enemy.rect.height) // 2 + 30

    # Halo brillante
    halo = pygame.Surface((radio_base * 4, radio_base * 4), pygame.SRCALPHA)
    pulso = math.sin(tiempo * 6) * 6
    r_dinamico = int(radio_base + pulso)

    pygame.draw.circle(halo, (140, 20, 255, 45), (radio_base * 2, radio_base * 2), r_dinamico + 20)
    pygame.draw.circle(halo, (200, 60, 255, 35), (radio_base * 2, radio_base * 2), r_dinamico + 10)
    screen.blit(halo, (cx - radio_base * 2, cy - radio_base * 2))

    # Anillo exterior
    num_orbes = 6
    for i in range(num_orbes):
        angulo = tiempo * 2 + (i * (2 * math.pi / num_orbes))
        ox = cx + math.cos(angulo) * (r_dinamico + 5)
        oy = cy + math.sin(angulo) * (r_dinamico + 5)
        pygame.draw.circle(screen, (220, 130, 255), (int(ox), int(oy)), 6)
        pygame.draw.circle(screen, (255, 255, 255), (int(ox), int(oy)), 3)

    # Esfera de energía
    escudo_surf = pygame.Surface((r_dinamico * 2 + 10, r_dinamico * 2 + 10), pygame.SRCALPHA)
    pygame.draw.circle(escudo_surf, (150, 30, 240, 80), (r_dinamico + 5, r_dinamico + 5), r_dinamico)
    pygame.draw.circle(escudo_surf, (220, 160, 255, 230), (r_dinamico + 5, r_dinamico + 5), r_dinamico, 3)
    pygame.draw.circle(escudo_surf, (255, 255, 255, 255), (r_dinamico + 5, r_dinamico + 5), r_dinamico - 4, 1)

    screen.blit(escudo_surf, (cx - r_dinamico - 5, cy - r_dinamico - 5))


# ============================================================
# BOLAS DE FUEGO VIOLETAS MÚLTIPLES
# ============================================================

bolas_fuego = []
bola_fuego_timer = 0


def actualizar_bolas_fuego(dt, player):
    global bola_fuego_timer

    bola_fuego_timer -= dt
    if bola_fuego_timer <= 0:
        bola_fuego_timer = random.uniform(1.8, 3.0)
        cantidad = random.randint(2, 4)
        for _ in range(cantidad):
            pos_x = random.randint(80, WIDTH - 80)
            bolas_fuego.append({
                "x": pos_x,
                "y": -50,
                "speed": random.randint(380, 520),
                "aviso_timer": 0.7,
                "radio": random.randint(14, 20)
            })

    for b in bolas_fuego[:]:
        if b["aviso_timer"] > 0:
            b["aviso_timer"] -= dt
            continue

        b["y"] += b["speed"] * dt
        rect = pygame.Rect(b["x"] - b["radio"], b["y"] - b["radio"], b["radio"] * 2, b["radio"] * 2)

        if rect.colliderect(player.hurtbox):
            player.take_damage(12)
            bolas_fuego.remove(b)
            continue

        if b["y"] >= SUELO_Y:
            bolas_fuego.remove(b)


def dibujar_bolas_fuego(screen):
    for b in bolas_fuego:
        if b["aviso_timer"] > 0:
            aviso = pygame.Surface((50, 12), pygame.SRCALPHA)
            aviso.fill((180, 40, 255, 140))
            screen.blit(aviso, (b["x"] - 25, SUELO_Y - 6))
            pygame.draw.rect(screen, (230, 130, 255), (b["x"] - 25, SUELO_Y - 6, 50, 12), 2)
        else:
            for i in range(3):
                offset_y = (i + 1) * 12
                r_estela = max(2, b["radio"] - (i * 4))
                pygame.draw.circle(
                    screen,
                    (140, 20, 220),
                    (int(b["x"]), int(b["y"] - offset_y)),
                    r_estela
                )

            pygame.draw.circle(screen, (160, 30, 240), (int(b["x"]), int(b["y"])), b["radio"])
            pygame.draw.circle(screen, (220, 110, 255), (int(b["x"]), int(b["y"])), int(b["radio"] * 0.65))
            pygame.draw.circle(screen, (255, 230, 255), (int(b["x"]), int(b["y"])), int(b["radio"] * 0.3))


# ============================================================
# CREAR JUGADOR Y JEFE
# ============================================================

player = Player(400, 500)
enemy = WerewolfBoss(900, 450)


# ============================================================
# VARIABLES DE ESTADO
# ============================================================

FASE = 1
fase2_activada = False
transicion_fase = False
transicion_timer = 0
luna_roja = False

furia_estado = 0
furia_timer = 0

jefe_congelado = False
demonios_activos = False
demonios_timer = 0
demonios = []
proyectiles_demonio = []
proyectiles_demonio_timer = 0

salto_activo = False
salto_timer = 0

zonas_peligro = []
onda_roja = None

enemy_damage_cooldown = 0
ENEMY_DAMAGE_INTERVAL = 0.75
ENEMY_DAMAGE = 25

# Control de fases de muerte
fase_muerte = 0  # 0: Vivo, 1: Desintegración/Temblor inicial, 2: Animación Sprite Sheet
muerte_timer = 0.0
MUERTE_INICIAL_DURACION = 2.0
particulas_muerte = []

running = True
victory = False


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

while running:

    dt = clock.tick(60) / 1000.0
    tiempo_actual = pygame.time.get_ticks() / 1000.0

    # ========================================================
    # EVENTOS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if not victory and not transicion_fase and fase_muerte == 0:
                    player.attack()

    # ========================================================
    # COOLDOWNS Y FASES
    # ========================================================

    if enemy_damage_cooldown > 0:
        enemy_damage_cooldown -= dt

    if (
        FASE == 1
        and enemy.health <= enemy.max_health * 0.5
        and not fase2_activada
    ):
        FASE = 2
        fase2_activada = True
        transicion_fase = True
        transicion_timer = 3
        luna_roja = False
        furia_estado = 0
        furia_timer = 0

    if transicion_fase:
        transicion_timer -= dt
        if transicion_timer <= 0:
            transicion_fase = False
            luna_roja = True
            furia_estado = 0
            furia_timer = 5

    # ========================================================
    # ACTUALIZAR ENTIDADES
    # ========================================================

    if not victory and not transicion_fase:
        player.update(dt)

    if jefe_congelado and fase_muerte == 0:
        if hasattr(enemy, "state") and enemy.state != "idle":
            enemy.state = "idle"
            if hasattr(enemy, "frame_index"):
                enemy.frame_index = 0
        
        if hasattr(enemy, "velocity_y"):
            enemy.velocity_y = 0
            
        enemy.rect.bottom = SUELO_Y
        enemy.hurtbox = enemy.rect.copy()

        if hasattr(enemy, "animate"):
            enemy.animate(dt)
        elif hasattr(enemy, "update_animation"):
            enemy.update_animation(dt)

    elif not victory and not transicion_fase and fase_muerte == 0:
        enemy.update(player, dt, width=WIDTH)

    if FASE == 2 and not transicion_fase and not victory and fase_muerte == 0:
        actualizar_bolas_fuego(dt, player)

    # ========================================================
    # SECUENCIA DE MUERTE DEL JEFE
    # ========================================================

    if fase_muerte == 1:
        muerte_timer -= dt

        if random.random() < 0.6:
            particulas_muerte.append({
                "x": enemy.rect.centerx + random.randint(-40, 40),
                "y": enemy.rect.centery + random.randint(-40, 40),
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-4, -1),
                "life": random.uniform(0.4, 0.8),
                "color": random.choice([(255, 30, 50), (180, 20, 200), (255, 200, 50)])
            })

        for p in particulas_muerte[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= dt
            if p["life"] <= 0:
                particulas_muerte.remove(p)

        if muerte_timer <= 0:
            fase_muerte = 2
            particulas_muerte.clear()
            if hasattr(enemy, "state"):
                enemy.state = "death"
            if hasattr(enemy, "frame_index"):
                enemy.frame_index = 0

    elif fase_muerte == 2:
        enemy.update(player, dt, width=WIDTH)

        is_dead = getattr(enemy, "is_dead", False) or getattr(enemy, "dead", False)
        
        if not is_dead and hasattr(enemy, "animations") and "death" in enemy.animations:
            if enemy.frame_index >= len(enemy.animations["death"]) - 1:
                is_dead = True

        if is_dead:
            fase_muerte = 0
            victory = True

    # ========================================================
    # LÓGICA DE LA FASE 2 DEL JEFE
    # ========================================================

    if FASE == 2 and not transicion_fase and not victory and fase_muerte == 0:

        if furia_estado == 0:
            furia_timer -= dt
            if furia_timer <= 0:
                furia_estado = 1
                furia_timer = 2

        elif furia_estado == 1:
            furia_timer -= dt

            if not salto_activo:
                salto_activo = True
                salto_timer = 0.8

            salto_timer -= dt

            if salto_timer <= 0:
                salto_activo = False

                zonas_peligro.append({
                    "rect": pygame.Rect(
                        enemy.rect.centerx - 80,
                        SUELO_Y - 10,
                        160,
                        10
                    ),
                    "timer": 1.5
                })

                onda_roja = {
                    "x": enemy.rect.centerx,
                    "radio": 20,
                    "max_radio": 500,
                    "timer": 0.6
                }

                furia_estado = 2
                demonios_activos = True
                jefe_congelado = True
                demonios_timer = 6
                proyectiles_demonio.clear()
                proyectiles_demonio_timer = 0.5
                demonios = crear_demonios_violetas()

                if hasattr(enemy, "state"):
                    enemy.state = "idle"
                if hasattr(enemy, "frame_index"):
                    enemy.frame_index = 0
                if hasattr(enemy, "velocity_y"):
                    enemy.velocity_y = 0
                
                enemy.rect.bottom = SUELO_Y
                enemy.hurtbox = enemy.rect.copy()
                if hasattr(enemy, "animations") and "idle" in enemy.animations and len(enemy.animations["idle"]) > 0:
                    enemy.image = enemy.animations["idle"][0]

        elif furia_estado == 2:
            demonios_timer -= dt
            proyectiles_demonio_timer -= dt

            if proyectiles_demonio_timer <= 0:
                for demonio in demonios:
                    dx = player.rect.centerx - demonio["x"]
                    dy = player.rect.centery - demonio["y"]
                    distancia = math.hypot(dx, dy)
                    if distancia == 0:
                        distancia = 1

                    velocidad = 6
                    vx = (dx / distancia) * velocidad
                    vy = (dy / distancia) * velocidad

                    proyectiles_demonio.append({
                        "x": demonio["x"],
                        "y": demonio["y"],
                        "vx": vx,
                        "vy": vy,
                        "rect": pygame.Rect(
                            demonio["x"] - 8,
                            demonio["y"] - 8,
                            16,
                            16
                        )
                    })

                proyectiles_demonio_timer = 1.6

            for proyectil in proyectiles_demonio[:]:
                proyectil["x"] += proyectil["vx"]
                proyectil["y"] += proyectil["vy"]
                proyectil["rect"].center = (
                    int(proyectil["x"]),
                    int(proyectil["y"])
                )

                if proyectil["rect"].colliderect(player.hurtbox):
                    player.take_damage(10)
                    proyectiles_demonio.remove(proyectil)
                    continue

                if (
                    proyectil["x"] < -50
                    or proyectil["x"] > WIDTH + 50
                    or proyectil["y"] < -50
                    or proyectil["y"] > HEIGHT + 50
                ):
                    proyectiles_demonio.remove(proyectil)

            if demonios_timer <= 0:
                demonios.clear()
                proyectiles_demonio.clear()
                demonios_activos = False
                jefe_congelado = False
                furia_estado = 0
                furia_timer = 5

    # ========================================================
    # COLISIONES DE AMBIENTE Y ONDAS
    # ========================================================

    for zona in zonas_peligro[:]:
        zona["timer"] -= dt

        if zona["rect"].colliderect(player.hurtbox):
            player.take_damage(5)

        if zona["timer"] <= 0:
            zonas_peligro.remove(zona)

    if onda_roja:
        onda_roja["timer"] -= dt
        onda_roja["radio"] += 15

        distancia = abs(player.rect.centerx - onda_roja["x"])

        if (
            distancia < onda_roja["radio"] + 15
            and distancia > onda_roja["radio"] - 30
        ):
            player.take_damage(15)

        if onda_roja["timer"] <= 0:
            onda_roja = None

    # ========================================================
    # ATAQUE DEL JUGADOR
    # ========================================================

    if (
        player.attacking
        and not player.has_hit
        and player.hitbox.colliderect(enemy.hurtbox)
        and fase_muerte == 0
    ):
        if not jefe_congelado:
            damage = 25 if FASE == 2 else 30
            enemy.take_damage(damage)
            player.has_hit = True

    # ========================================================
    # DAÑO RECIBIDO POR EL JUGADOR DEL JEFE
    # ========================================================

    if (
        not transicion_fase
        and not victory
        and not jefe_congelado
        and fase_muerte == 0
        and enemy_damage_cooldown <= 0
    ):
        if enemy.rect.colliderect(player.hurtbox):
            player.take_damage(ENEMY_DAMAGE)
            enemy_damage_cooldown = ENEMY_DAMAGE_INTERVAL

    if player.health < 0:
        player.health = 0

    if enemy.health <= 0 and fase_muerte == 0 and not victory:
        enemy.health = 0
        fase_muerte = 1
        muerte_timer = MUERTE_INICIAL_DURACION
        demonios_activos = False
        demonios.clear()
        proyectiles_demonio.clear()

    # ========================================================
    # RENDERIZADO
    # ========================================================

    screen.blit(fondo, (0, 0))

    if FASE == 2:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((35, 0, 20, 90))
        screen.blit(overlay, (0, 0))
        dibujar_luna_roja(screen, tiempo_actual)

    # Zonas de impacto y ondas
    for zona in zonas_peligro:
        rect = zona["rect"]
        pygame.draw.rect(screen, (130, 0, 20), rect)
        pygame.draw.rect(screen, (255, 40, 40), rect, 2)

    if onda_roja:
        pygame.draw.circle(
            screen,
            (255, 40, 40),
            (int(onda_roja["x"]), SUELO_Y),
            int(onda_roja["radio"]),
            5
        )

    # DIBUJAR JEFE
    if fase_muerte == 1:
        shake_x = random.randint(-4, 4)
        shake_y = random.randint(-4, 4)
        enemy.rect.x += shake_x
        enemy.rect.y += shake_y

        enemy.draw(screen)

        enemy.rect.x -= shake_x
        enemy.rect.y -= shake_y

        for p in particulas_muerte:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), int(p["life"] * 8))

    elif fase_muerte == 2:
        enemy.draw(screen)

    elif not victory:
        enemy.draw(screen)

    # DIBUJAR ESCUDO SI ES INVULNERABLE
    if jefe_congelado and fase_muerte == 0:
        dibujar_escudo_invulnerable(screen, enemy, tiempo_actual)

    # Demonios y proyectiles
    if demonios_activos:
        for demonio in demonios:
            dibujar_demonio_violeta(screen, demonio, tiempo_actual)

    for proyectil in proyectiles_demonio:
        dibujar_proyectil_demonio(screen, proyectil)

    # Bolas de fuego violetas
    if FASE == 2 and fase_muerte == 0:
        dibujar_bolas_fuego(screen)

    # Jugador
    player.draw(screen)

    # UI y Barras de vida
    dibujar_barras_vida(player, enemy, FASE)

    # Transición de fase
    if transicion_fase:
        texto = fuente_grande.render("FURIA NOCTURNA", True, (255, 50, 60))
        screen.blit(texto, (WIDTH // 2 - texto.get_width() // 2, HEIGHT // 2 - 80))

    # PANTALLA DE VICTORIA
    if victory:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        texto = fuente_grande.render("VICTORIA", True, (255, 220, 80))
        screen.blit(texto, (WIDTH // 2 - texto.get_width() // 2, HEIGHT // 2 - 40))

    pygame.display.flip()

pygame.quit()