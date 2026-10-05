import pygame
import sys
import math
import subprocess
import os
import random

# Inicialización
pygame.init()
pygame.font.init()

# Ventana
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Selector de Niveles - Mundo Estilo LittleBigPlanet")
clock = pygame.time.Clock()

# Paleta de Colores
BLACK = (5, 6, 12)
DARK_SPACE = (2, 3, 8)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
CYAN = (0, 220, 255)
FIRE_ORANGE = (255, 120, 0)
FIRE_RED = (255, 40, 0)
FIRE_YELLOW = (255, 230, 50)

# Colores Tierra Plastilina
EARTH_WATER = (25, 95, 190)
EARTH_GREEN_DARK = (30, 130, 60)
EARTH_GREEN_LIGHT = (50, 180, 80)

# Colores Gehena
GEHENA_ASH = (45, 40, 48)
GEHENA_LAVA = (235, 75, 15)
GEHENA_BUBBLE = (255, 170, 30)

# Fuentes
title_font = pygame.font.SysFont("Impact", 42)
level_font = pygame.font.SysFont("Verdana", 16, bold=True)
hud_font = pygame.font.SysFont("Consolas", 15, bold=True)
arrow_font = pygame.font.SysFont("Consolas", 32, bold=True)

# Parámetros Aumentados del Planeta
PLANET_RADIUS = 180
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2 + 30

# Partículas y Burbujas
lava_bubbles = [{'x': random.randint(-150, 150), 'y': random.randint(-150, 150), 
                 'r': random.randint(3, 8), 'max_r': random.randint(12, 22), 
                 'life': random.randint(0, 100)} for _ in range(25)]

gehena_debris = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 
                  'size': random.randint(6, 18), 'speed': random.uniform(0.2, 0.8),
                  'rot': random.uniform(0, 360)} for _ in range(35)]

# Configuración de Niveles
tierra_levels = [
    {"id": "Nivel 2", "name": "Nivel 2", "file": None, "lat": 0, "lon": -100, "boss": 2, "bg_color": (60, 20, 30)},
    {"id": "Nivel 1", "name": "Nivel 1", "file": "nivel_1.py", "lat": 20, "lon": 0, "boss": 1, "bg_color": (40, 50, 70)},
    {"id": "Nivel 3", "name": "Nivel 3", "file": None, "lat": 0, "lon": 100, "boss": 3, "bg_color": (35, 20, 50)}
]

gehena_levels = [
    {"id": "Nivel 4", "name": "Nivel 4", "file": None, "lat": 15, "lon": -75, "boss": 4, "bg_color": (80, 25, 15)},
    {"id": "Nivel Secreto", "name": "Nivel Secreto", "file": None, "lat": -10, "lon": 75, "boss": 5, "bg_color": (20, 10, 25)}
]

current_planet = "TIERRA"
active_levels = tierra_levels
current_index = 1
planet_rotation = 0.0

def ejecutar_nivel(script_name):
    """Abre el archivo Python correspondiente."""
    if script_name and os.path.exists(script_name):
        subprocess.Popen([sys.executable, script_name])
        pygame.quit()
        sys.exit()
    elif script_name:
        print(f"[Aviso] El archivo '{script_name}' no existe.")
    else:
        print("[Aviso] Este nivel aún no está disponible.")

def draw_space_background(planet_type, rotation):
    """Dibuja el espacio, el Sol orbital en la Tierra o neblina/meteoritos en Gehena."""
    if planet_type == "TIERRA":
        screen.fill(BLACK)
        # Estrellas
        for i in range(100):
            sx = (i * 137) % WIDTH
            sy = (i * 269) % HEIGHT
            pygame.draw.circle(screen, (200, 220, 255), (sx, sy), (i % 2) + 1)
        
        # Sol orbital que gira coordinado con la navegación del mundo
        sun_rad = math.radians(-rotation - 90)
        sun_dist = 420
        sun_x = int(CENTER_X + math.cos(sun_rad) * sun_dist)
        sun_y = int(CENTER_Y + math.sin(sun_rad) * 120)
        
        # Resplandor solar
        for r in range(80, 20, -10):
            alpha = int(255 * (1.0 - (r / 80)))
            sun_glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(sun_glow, (255, 200, 50, alpha // 4), (r, r), r)
            screen.blit(sun_glow, (sun_x - r, sun_y - r))
        pygame.draw.circle(screen, (255, 245, 200), (sun_x, sun_y), 32)
        
    else:  # GEHENA
        screen.fill(DARK_SPACE)
        # Neblina espacial infernal
        for i in range(5):
            fog_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fx = (pygame.time.get_ticks() * 0.02 + i * 200) % WIDTH
            pygame.draw.circle(fog_surf, (90, 15, 10, 25), (int(fx), HEIGHT // 2), 280)
            screen.blit(fog_surf, (0, 0))
            
        # Meteoritos y fragmentos de tierra desprendidos
        for deb in gehena_debris:
            deb['y'] += deb['speed']
            if deb['y'] > HEIGHT:
                deb['y'] = -20
                deb['x'] = random.randint(0, WIDTH)
            
            pts = [
                (deb['x'] + math.cos(math.radians(deb['rot'] + a)) * deb['size'],
                 deb['y'] + math.sin(math.radians(deb['rot'] + a)) * deb['size'])
                for a in [0, 72, 144, 216, 288]
            ]
            pygame.draw.polygon(screen, GEHENA_ASH, pts)
            pygame.draw.polygon(screen, GEHENA_LAVA, pts, 1)

def draw_tierra_planet(rotation):
    """Mundo Plastilina: Esferas de plastilina verde sobre masa esférica azul."""
    surf = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, EARTH_WATER, (PLANET_RADIUS, PLANET_RADIUS), PLANET_RADIUS)

    # Globos de plastilina verde distribuidos
    blobs = [
        (0, 0, 55), (-45, 30, 40), (50, -20, 45), (-80, -30, 35),
        (90, 40, 50), (140, -10, 42), (-130, 20, 38)
    ]
    
    for b_lon, b_lat, size in blobs:
        rad_lon = math.radians(b_lon + rotation)
        rad_lat = math.radians(b_lat)
        
        sin_lon = math.sin(rad_lon)
        cos_lon = math.cos(rad_lon)
        
        if sin_lon > -0.2:  # Cara frontal
            cx = PLANET_RADIUS + sin_lon * (PLANET_RADIUS * 0.78)
            cy = PLANET_RADIUS - math.sin(rad_lat) * (PLANET_RADIUS * 0.78)
            
            r_x = max(2, int(size * max(0.15, cos_lon)))
            r_y = int(size * 0.85)
            
            # Textura de plastilina (círculos concéntricos)
            pygame.draw.ellipse(surf, EARTH_GREEN_DARK, (cx - r_x, cy - r_y, r_x * 2, r_y * 2))
            if r_x > 6:
                pygame.draw.ellipse(surf, EARTH_GREEN_LIGHT, (cx - r_x + 3, cy - r_y + 3, (r_x - 3) * 2, (r_y - 3) * 2))

    # Máscara circular
    mask = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (PLANET_RADIUS, PLANET_RADIUS), PLANET_RADIUS)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(surf, (CENTER_X - PLANET_RADIUS, CENTER_Y - PLANET_RADIUS))

def draw_gehena_planet(rotation):
    """Mundo Gehena: Lava hirviente con burbujas que estallan e islas de ceniza."""
    surf = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, GEHENA_LAVA, (PLANET_RADIUS, PLANET_RADIUS), PLANET_RADIUS)

    # Animación de Burbujas de Lava que explotan
    for bub in lava_bubbles:
        bub['life'] += 1
        bub['r'] += 0.2
        if bub['r'] >= bub['max_r'] or bub['life'] > 80:
            # Explosión / Reinicio
            bub['r'] = 2
            bub['life'] = 0
            bub['x'] = random.randint(-PLANET_RADIUS + 20, PLANET_RADIUS - 20)
            bub['y'] = random.randint(-PLANET_RADIUS + 20, PLANET_RADIUS - 20)
        
        bx, by = PLANET_RADIUS + bub['x'], PLANET_RADIUS + bub['y']
        if math.hypot(bub['x'], bub['y']) < PLANET_RADIUS - 10:
            pygame.draw.circle(surf, GEHENA_BUBBLE, (int(bx), int(by)), int(bub['r']), 2)

    # Continentales de Ceniza
    ash_lands = [(10, -20, 60), (-60, 30, 48), (80, 40, 52), (-110, -10, 45)]
    for a_lon, a_lat, size in ash_lands:
        rad_lon = math.radians(a_lon + rotation)
        rad_lat = math.radians(a_lat)
        sin_lon = math.sin(rad_lon)
        cos_lon = math.cos(rad_lon)
        
        if sin_lon > -0.2:
            cx = PLANET_RADIUS + sin_lon * (PLANET_RADIUS * 0.78)
            cy = PLANET_RADIUS - math.sin(rad_lat) * (PLANET_RADIUS * 0.78)
            r_x = max(2, int(size * max(0.15, cos_lon)))
            r_y = int(size * 0.8)
            pygame.draw.ellipse(surf, GEHENA_ASH, (cx - r_x, cy - r_y, r_x * 2, r_y * 2))

    # Máscara circular
    mask = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (PLANET_RADIUS, PLANET_RADIUS), PLANET_RADIUS)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(surf, (CENTER_X - PLANET_RADIUS, CENTER_Y - PLANET_RADIUS))

def draw_boss_silhouette(surface, boss_id, cx, cy, color):
    """Dibuja las siluetas vectoriales de los jefes basados en las imágenes adjuntas."""
    if boss_id == 1:
        # Demonio con cuernos, gran cuchilla y bolas de fuego flotantes (Imagen 1)
        pygame.draw.circle(surface, FIRE_YELLOW, (cx - 18, cy - 28), 5)
        pygame.draw.circle(surface, FIRE_YELLOW, (cx + 18, cy - 28), 5)
        # Cabeza y cuernos
        pygame.draw.polygon(surface, color, [(cx - 8, cy - 10), (cx + 8, cy - 10), (cx, cy - 22)])
        pygame.draw.polygon(surface, color, [(cx - 7, cy - 15), (cx - 14, cy - 26), (cx - 3, cy - 18)])
        pygame.draw.polygon(surface, color, [(cx + 7, cy - 15), (cx + 14, cy - 26), (cx + 3, cy - 18)])
        # Cuerpo y machete gigante
        pygame.draw.ellipse(surface, color, (cx - 16, cy - 10, 32, 28))
        pygame.draw.rect(surface, color, (cx - 20, cy + 8, 38, 12), border_radius=2)

    elif boss_id == 2:
        # Mandíbula de bestia/dragón con zarpazo rojo (Imagen 2)
        pts = [(cx - 22, cy + 12), (cx - 5, cy - 18), (cx + 18, cy - 8), (cx + 8, cy + 10)]
        pygame.draw.polygon(surface, color, pts)
        # Rasguño sangriento diagonal
        pygame.draw.line(surface, FIRE_RED, (cx - 18, cy - 15), (cx + 18, cy + 15), 4)
        pygame.draw.line(surface, FIRE_RED, (cx - 12, cy - 20), (cx + 22, cy + 10), 3)

    elif boss_id == 3:
        # Cíclope encapuchado púrpura con guadaña/espada curva (Imagen 3)
        pygame.draw.polygon(surface, color, [(cx, cy - 24), (cx - 15, cy - 8), (cx + 15, cy - 8)])
        pygame.draw.ellipse(surface, color, (cx - 12, cy - 8, 24, 28))
        # Ojo cíclope
        pygame.draw.circle(surface, FIRE_ORANGE, (cx, cy - 14), 4)
        # Guadaña curva
        pygame.draw.arc(surface, color, (cx - 22, cy - 5, 25, 30), 0.5, 3.14, 4)

    elif boss_id == 4:
        # Guerrero con casco de cuernos embistiendo con ráfaga de fuego (Imagen 4)
        pygame.draw.polygon(surface, color, [(cx - 15, cy - 10), (cx - 5, cy - 22), (cx + 5, cy - 10)])
        pygame.draw.line(surface, color, (cx - 18, cy), (cx + 10, cy - 5), 4)
        # Ráfaga de llamas de la lanza
        pygame.draw.polygon(surface, FIRE_ORANGE, [(cx + 10, cy - 5), (cx + 28, cy - 18), (cx + 22, cy + 8)])

    else:
        # Nivel Secreto: Entidad misteriosa con brillo central
        pygame.draw.circle(surface, color, (cx, cy), 16)
        pygame.draw.circle(surface, FIRE_YELLOW, (cx, cy), 6)

def draw_level_button(screen_x, screen_y, level_data, is_selected, ticks):
    """Botón grande con borde de fuego animado, escenario y silueta del Boss."""
    btn_r = 38 if is_selected else 32
    
    # 1. Borde de fuego animado (partículas/picos rotatorios)
    num_flames = 16
    for i in range(num_flames):
        angle = math.radians(i * (360 / num_flames) + ticks * 0.2)
        flame_len = btn_r + (6 if is_selected else 4) + math.sin(ticks * 0.01 + i) * 4
        fx = screen_x + math.cos(angle) * flame_len
        fy = screen_y + math.sin(angle) * flame_len
        color = FIRE_YELLOW if i % 2 == 0 else FIRE_ORANGE
        pygame.draw.line(screen, color, (screen_x, screen_y), (int(fx), int(fy)), 3)

    # 2. Fondo del escenario de batalla
    btn_surf = pygame.Surface((btn_r * 2, btn_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(btn_surf, level_data["bg_color"], (btn_r, btn_r), btn_r)
    
    # Detalle de escenario (suelo de arena/roca)
    pygame.draw.rect(btn_surf, (20, 15, 25), (0, btn_r + 8, btn_r * 2, btn_r))

    # 3. Silueta del Boss en el centro
    draw_boss_silhouette(btn_surf, level_data["boss"], btn_r, btn_r - 2, BLACK)
    
    # Máscara circular para el botón
    b_mask = pygame.Surface((btn_r * 2, btn_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(b_mask, (255, 255, 255, 255), (btn_r, btn_r), btn_r)
    btn_surf.blit(b_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Anillo exterior
    pygame.draw.circle(btn_surf, GOLD if is_selected else FIRE_RED, (btn_r, btn_r), btn_r, 3)
    screen.blit(btn_surf, (screen_x - btn_r, screen_y - btn_r))

    # 4. Etiqueta del Nivel Stylized
    lbl_color = GOLD if is_selected else WHITE
    txt_surf = level_font.render(level_data["name"], True, lbl_color)
    txt_rect = txt_surf.get_rect(center=(screen_x, screen_y + btn_r + 20))
    
    bg_rect = txt_rect.inflate(16, 8)
    pygame.draw.rect(screen, (12, 10, 20), bg_rect, border_radius=6)
    pygame.draw.rect(screen, lbl_color, bg_rect, 2, border_radius=6)
    screen.blit(txt_surf, txt_rect)

    return pygame.Rect(screen_x - btn_r, screen_y - btn_r, btn_r * 2, btn_r * 2)

# Bucle Principal
running = True
while running:
    ticks = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    # Rotación suave del mundo hacia el nivel activo
    target_rotation = -active_levels[current_index]["lon"]
    planet_rotation += (target_rotation - planet_rotation) * 0.1

    # Fondo Espacial
    draw_space_background(current_planet, planet_rotation)

    # Dibujar Planeta
    if current_planet == "TIERRA":
        draw_tierra_planet(planet_rotation)
    else:
        draw_gehena_planet(planet_rotation)

    # Renderizar Nodos de Nivel con Ocultación Trasera (Z-Culling)
    clickable_nodes = []
    for idx, node in enumerate(active_levels):
        rad_lon = math.radians(node["lon"] + planet_rotation)
        rad_lat = math.radians(node["lat"])

        x_3d = PLANET_RADIUS * math.cos(rad_lat) * math.sin(rad_lon)
        y_3d = -PLANET_RADIUS * math.sin(rad_lat)
        z_3d = PLANET_RADIUS * math.cos(rad_lat) * math.cos(rad_lon)

        # Solo renderiza los botones en la cara frontal visible
        if z_3d > 15:
            screen_x = int(CENTER_X + x_3d)
            screen_y = int(CENTER_Y + y_3d)
            is_selected = (idx == current_index)

            rect = draw_level_button(screen_x, screen_y, node, is_selected, ticks)
            clickable_nodes.append((rect, idx))

    # Banner Estilizado Superior para TIERRA / GEHENA
    title_surf = title_font.render(current_planet, True, WHITE)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 45))
    
    banner_bg = title_rect.inflate(50, 14)
    pygame.draw.rect(screen, (15, 12, 25), banner_bg, border_radius=10)
    pygame.draw.rect(screen, CYAN if current_planet == "TIERRA" else FIRE_RED, banner_bg, 3, border_radius=10)
    screen.blit(title_surf, title_rect)

    # Botón Cambio de Planeta
    planet_btn = pygame.Rect(WIDTH - 190, 25, 170, 42)
    is_hover_p = planet_btn.collidepoint(mouse_pos)
    btn_p_col = GOLD if is_hover_p else WHITE
    
    p_label = "Ir a Gehena ▶" if current_planet == "TIERRA" else "◀ Ir a Tierra"
    p_txt = level_font.render(p_label, True, btn_p_col)
    pygame.draw.rect(screen, (25, 20, 35), planet_btn, border_radius=8)
    pygame.draw.rect(screen, btn_p_col, planet_btn, 2, border_radius=8)
    screen.blit(p_txt, p_txt.get_rect(center=planet_btn.center))

    # Flechas laterales en pantalla
    btn_left = pygame.Rect(35, HEIGHT // 2 - 25, 50, 50)
    btn_right = pygame.Rect(WIDTH - 85, HEIGHT // 2 - 25, 50, 50)

    for btn, symbol in [(btn_left, "◀"), (btn_right, "▶")]:
        hover = btn.collidepoint(mouse_pos)
        c = GOLD if hover else WHITE
        pygame.draw.rect(screen, (25, 20, 35), btn, border_radius=10)
        pygame.draw.rect(screen, c, btn, 2, border_radius=10)
        txt = arrow_font.render(symbol, True, c)
        screen.blit(txt, txt.get_rect(center=btn.center))

    # Barra Informativa Inferior
    info_txt = hud_font.render("Controles: A / D o FLECHAS para rotar el mundo | CLICK o ENTER para seleccionar", True, WHITE)
    screen.blit(info_txt, info_txt.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                current_index = max(0, current_index - 1)
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                current_index = min(len(active_levels) - 1, current_index + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                ejecutar_nivel(active_levels[current_index]["file"])

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_left.collidepoint(event.pos):
                current_index = max(0, current_index - 1)
            elif btn_right.collidepoint(event.pos):
                current_index = min(len(active_levels) - 1, current_index + 1)
            elif planet_btn.collidepoint(event.pos):
                if current_planet == "TIERRA":
                    current_planet = "GEHENA"
                    active_levels = gehena_levels
                else:
                    current_planet = "TIERRA"
                    active_levels = tierra_levels
                current_index = 0

            for rect, idx in clickable_nodes:
                if rect.collidepoint(event.pos):
                    current_index = idx
                    ejecutar_nivel(active_levels[current_index]["file"])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()