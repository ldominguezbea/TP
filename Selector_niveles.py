import pygame
import sys
import math
import subprocess
import os

# Inicialización de Pygame
pygame.init()
pygame.font.init()

# Configuración de ventana
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Selector de Niveles - Estilo LittleBigPlanet")
clock = pygame.time.Clock()

# Colores
BLACK = (10, 12, 18)
BG_GRID = (18, 22, 35)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
CYAN = (0, 210, 255)
RED = (255, 40, 40)
DARK_RED = (140, 10, 10)
ORANGE = (255, 120, 0)

# Colores del Planeta Tierra
EARTH_WATER = (20, 80, 170)
EARTH_LAND = (35, 160, 80)

# Colores de Gehena
GEHENA_BASE = (100, 15, 15)
GEHENA_LAVA = (230, 80, 10)

# Fuentes
title_font = pygame.font.SysFont("Consolas", 36, bold=True)
label_font = pygame.font.SysFont("Consolas", 16, bold=True)
hud_font = pygame.font.SysFont("Consolas", 15, bold=True)
arrow_font = pygame.font.SysFont("Consolas", 28, bold=True)

# Parámetros del planeta
PLANET_RADIUS = 140
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2 + 15

# Definición de niveles con coordenadas esféricas (Latitud, Longitud separadas)
tierra_levels = [
    {"id": "Nivel 2", "name": "Nivel 2", "file": None, "lat": 0, "lon": -110},
    {"id": "Nivel 1", "name": "Nivel 1", "file": "nivel_1.py", "lat": 25, "lon": 0},
    {"id": "Nivel 3", "name": "Nivel 3", "file": None, "lat": 0, "lon": 110}
]

gehena_levels = [
    {"id": "Nivel 4", "name": "Nivel 4", "file": None, "lat": 20, "lon": -80},
    {"id": "Nivel Secreto", "name": "Nivel Secreto", "file": None, "lat": -10, "lon": 80}
]

# Estado inicial del selector
current_planet = "TIERRA"
active_levels = tierra_levels
current_index = 1  # Inicia enfocado en Nivel 1
planet_rotation = 0.0
target_rotation = 0.0

def ejecutar_nivel(script_name):
    """Ejecuta el script del nivel seleccionado."""
    if script_name and os.path.exists(script_name):
        subprocess.Popen([sys.executable, script_name])
        pygame.quit()
        sys.exit()
    elif script_name:
        print(f"[Aviso] El archivo '{script_name}' no existe en el directorio.")
    else:
        print("[Aviso] Este nivel aún no está disponible.")

def draw_background():
    """Fondo oscuro con patrón de rejilla espacial similar al fondo de la referencia."""
    screen.fill(BLACK)
    grid_size = 40
    for x in range(0, WIDTH, grid_size):
        pygame.draw.line(screen, BG_GRID, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(screen, BG_GRID, (0, y), (WIDTH, y), 1)

def draw_planet(planet_type, rotation):
    """Dibuja el planeta en 3D limpio y el anillo orbital luminoso de la foto."""
    surf = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    
    base_color = EARTH_WATER if planet_type == "TIERRA" else GEHENA_BASE
    land_color = EARTH_LAND if planet_type == "TIERRA" else GEHENA_LAVA

    # 1. Base del planeta
    pygame.draw.circle(surf, base_color, (PLANET_RADIUS, PLANET_RADIUS), PLANET_RADIUS)

    # 2. Continentes/Masas giratorias en 3D
    num_continents = 7
    for i in range(num_continents):
        angle = (i * (360 / num_continents) + rotation) % 360
        rad = math.radians(angle)
        sin_v = math.sin(rad)
        cos_v = math.cos(rad)

        # Renderizar solo en la cara frontal del mapa
        if sin_v > -0.2:
            cx = PLANET_RADIUS + sin_v * (PLANET_RADIUS * 0.75)
            cy = PLANET_RADIUS + math.sin(i * 2.1) * (PLANET_RADIUS * 0.4)
            c_w = max(4, int(35 * max(0.1, cos_v)))
            c_h = int(25 + math.sin(i) * 8)
            
            cont_surf = pygame.Surface((c_w * 2, c_h * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(cont_surf, land_color, (0, 0, c_w * 2, c_h * 2))
            surf.blit(cont_surf, (cx - c_w, cy - c_h))

    # Cortar bordes para que quede perfectamente esférico
    mask = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (PLANET_RADIUS, PLANET_RADIUS), PLANET_RADIUS)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Dibujar el planeta en pantalla
    screen.blit(surf, (CENTER_X - PLANET_RADIUS, CENTER_Y - PLANET_RADIUS))

    # 3. Anillo de órbita luminoso (Como la línea azul/roja rodeando el mundo en la foto)
    ring_color = CYAN if planet_type == "TIERRA" else RED
    rect_ring = pygame.Rect(CENTER_X - PLANET_RADIUS - 15, CENTER_Y - PLANET_RADIUS // 2 - 5,
                            (PLANET_RADIUS + 15) * 2, PLANET_RADIUS + 10)
    pygame.draw.ellipse(screen, ring_color, rect_ring, 2)

def draw_level_node(screen_x, screen_y, name, is_selected, ticks):
    """Dibuja el orbe de nivel estilo imagen de referencia (anillo rojo con destellos)."""
    pulse = math.sin(ticks * 0.008) * 3 if is_selected else 0
    r = int(14 + pulse)
    
    # Destellos / Picos rojos exteriores (fiel al estilo de la foto)
    spike_color = ORANGE if is_selected else RED
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        sx = screen_x + math.cos(rad) * (r + 7)
        sy = screen_y + math.sin(rad) * (r + 7)
        pygame.draw.line(screen, spike_color, (screen_x, screen_y), (sx, sy), 2)
        
    # Anillo rojo brillante y centro oscuro
    pygame.draw.circle(screen, RED, (screen_x, screen_y), r + 3)
    pygame.draw.circle(screen, BLACK, (screen_x, screen_y), r - 2)
    pygame.draw.circle(screen, GOLD if is_selected else WHITE, (screen_x, screen_y), 3)

    # Cartel con el nombre del nivel
    lbl_color = GOLD if is_selected else WHITE
    text_surf = label_font.render(name, True, lbl_color)
    text_rect = text_surf.get_rect(center=(screen_x, screen_y + 28))

    bg_rect = text_rect.inflate(12, 6)
    pygame.draw.rect(screen, (10, 10, 15), bg_rect, border_radius=4)
    pygame.draw.rect(screen, lbl_color, bg_rect, 2 if is_selected else 1, border_radius=4)
    screen.blit(text_surf, text_rect)

    return pygame.Rect(screen_x - 20, screen_y - 20, 40, 40)

# Bucle Principal
running = True
while running:
    ticks = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()
    
    # Animación fluida de rotación hacia el nivel activo
    target_rotation = -active_levels[current_index]["lon"]
    planet_rotation += (target_rotation - planet_rotation) * 0.1

    draw_background()
    draw_planet(current_planet, planet_rotation)

    # Renderizado de Nodos de Nivel con ocultación trasera 3D
    clickable_nodes = []
    for idx, node in enumerate(active_levels):
        # Conversión a coordenadas 3D sobre la superficie del planeta
        rad_lon = math.radians(node["lon"] + planet_rotation)
        rad_lat = math.radians(node["lat"])
        
        # Posición 3D (Z representa la profundidad)
        x_3d = PLANET_RADIUS * math.cos(rad_lat) * math.sin(rad_lon)
        y_3d = -PLANET_RADIUS * math.sin(rad_lat)
        z_3d = PLANET_RADIUS * math.cos(rad_lat) * math.cos(rad_lon)

        # OCULTAR SI ESTÁ EN LA CARA POSTERIOR DEL PLANETA (Z <= 10)
        if z_3d > 10:
            screen_x = int(CENTER_X + x_3d)
            screen_y = int(CENTER_Y + y_3d)
            is_selected = (idx == current_index)
            
            node_rect = draw_level_node(screen_x, screen_y, node["name"], is_selected, ticks)
            clickable_nodes.append((node_rect, idx))

    # UI Superior - Nombre del Planeta
    title_txt = title_font.render(current_planet, True, WHITE)
    title_rect = title_txt.get_rect(center=(WIDTH // 2, 40))
    planet_border = CYAN if current_planet == "TIERRA" else RED
    pygame.draw.rect(screen, (15, 18, 28), title_rect.inflate(35, 10), border_radius=6)
    pygame.draw.rect(screen, planet_border, title_rect.inflate(35, 10), 2, border_radius=6)
    screen.blit(title_txt, title_rect)

    # Botón Viajar de Planeta (Tierra <-> Gehena)
    planet_switch_btn = pygame.Rect(WIDTH - 180, 20, 160, 40)
    is_hover_p_btn = planet_switch_btn.collidepoint(mouse_pos)
    btn_p_color = GOLD if is_hover_p_btn else WHITE
    
    target_p_text = "Ir a Gehena ▶" if current_planet == "TIERRA" else "◀ Ir a Tierra"
    p_txt_surf = label_font.render(target_p_text, True, btn_p_color)
    pygame.draw.rect(screen, (25, 28, 40), planet_switch_btn, border_radius=6)
    pygame.draw.rect(screen, btn_p_color, planet_switch_btn, 2, border_radius=6)
    screen.blit(p_txt_surf, p_txt_surf.get_rect(center=planet_switch_btn.center))

    # Botones Flecha laterales en pantalla para girar entre niveles
    btn_left = pygame.Rect(40, HEIGHT // 2 - 25, 50, 50)
    btn_right = pygame.Rect(WIDTH - 90, HEIGHT // 2 - 25, 50, 50)

    for btn, symbol in [(btn_left, "◀"), (btn_right, "▶")]:
        hover = btn.collidepoint(mouse_pos)
        c = GOLD if hover else WHITE
        pygame.draw.rect(screen, (25, 28, 40), btn, border_radius=8)
        pygame.draw.rect(screen, c, btn, 2, border_radius=8)
        txt = arrow_font.render(symbol, True, c)
        screen.blit(txt, txt.get_rect(center=btn.center))

    # Leyenda de controles inferior
    info_txt = hud_font.render("Usa A / D o FLECHAS para girar el planeta | Clic o ENTER para seleccionar", True, WHITE)
    screen.blit(info_txt, info_txt.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # Manejo de Eventos
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
            # Click en flechas en pantalla
            if btn_left.collidepoint(event.pos):
                current_index = max(0, current_index - 1)
            elif btn_right.collidepoint(event.pos):
                current_index = min(len(active_levels) - 1, current_index + 1)
                
            # Click en botón para cambiar de planeta
            elif planet_switch_btn.collidepoint(event.pos):
                if current_planet == "TIERRA":
                    current_planet = "GEHENA"
                    active_levels = gehena_levels
                else:
                    current_planet = "TIERRA"
                    active_levels = tierra_levels
                current_index = 0

            # Click directo sobre un botón de nivel visible
            for rect, idx in clickable_nodes:
                if rect.collidepoint(event.pos):
                    current_index = idx
                    ejecutar_nivel(active_levels[current_index]["file"])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()