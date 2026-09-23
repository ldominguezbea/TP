import pygame
import random
import math
import sys
import os
import animacion_menu


def main():
    time_counter = 0
running = True

while running:
    time_counter += 0.05
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scaled_mouse_x = mouse_x * (GAME_WIDTH / SCREEN_WIDTH)
    scaled_mouse_y = mouse_y * (GAME_HEIGHT / SCREEN_HEIGHT)

    # 1. CAPTURAR EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # "NEW GAME"
                        game_state = "PROLOGUE"
                    elif selected_option == 4:  # "EXIT"
                        running = False

            elif game_state == "PROLOGUE":
                if event.key == pygame.K_RETURN:
                    game_state = "GAMEPLAY"

    # 2. DIBUJAR PANTALLA
    if game_state == "MENU":
        draw_scenery(canvas, time_counter)

        for fd in flying_demons:
            fd["x"] += fd["speed"] * fd["dir"]
            if fd["dir"] == -1 and fd["x"] < -30:
                fd["x"] = GAME_WIDTH + 30
                fd["y"] = random.randint(15, 65)
            elif fd["dir"] == 1 and fd["x"] > GAME_WIDTH + 30:
                fd["x"] = -30
                fd["y"] = random.randint(15, 65)
            draw_flying_demon(canvas, fd["x"], fd["y"], fd["dir"], time_counter, fd["wing_offset"])

        for d in demons:
            d["x"] += d["speed"] * d["dir"]
            if d["x"] < -30:
                d["x"] = GAME_WIDTH + random.randint(30, 80)
            draw_cool_demon(canvas, d["x"], d["y"], d["dir"], time_counter)

        for c in civilians:
            c["x"] += c["speed"] * c["dir"]
            if c["x"] < -20:
                c["x"] = GAME_WIDTH + random.randint(10, 50)
            draw_detailed_civilian(canvas, c["x"], c["y"], c["dir"], time_counter)

        for s in smoke_particles:
            s["y"] -= s["speed_y"]
            s["x"] += s["speed_x"] + math.sin(time_counter + s["y"] * 0.03) * 0.15
            if s["y"] < -20:
                s["y"] = GAME_HEIGHT + 10
                s["x"] = random.randint(0, GAME_WIDTH)
            
            smoke_surf = pygame.Surface((s["radius"] * 2, s["radius"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surf, (40, 25, 25, s["alpha"]), (s["radius"], s["radius"]), s["radius"])
            canvas.blit(smoke_surf, (int(s["x"]) - s["radius"], int(s["y"]) - s["radius"]))

        for p in sparks:
            p["y"] -= p["speed_y"]
            p["x"] += p["speed_x"]
            if p["y"] < 0:
                p["y"] = GAME_HEIGHT
                p["x"] = random.randint(0, GAME_WIDTH)
            canvas.set_at((int(p["x"]), int(p["y"])), p["color"])

        # UI del Menú
        title_surf = font_title.render("REQUIEM", True, (0, 0, 0))
        canvas.blit(title_surf, (12, 8))
        title_surf_red = font_title.render("REQUIEM", True, (120, 10, 10))
        canvas.blit(title_surf_red, (10, 6))

        sub_surf = font_sub.render('"EL JUICIO FINAL"', True, (220, 40, 0))
        canvas.blit(sub_surf, (20, 36))

        start_y = 58
        for i, option in enumerate(menu_options):
            btn_rect = pygame.Rect(26, start_y + (i * 18), 80, 13)
            
            if btn_rect.collidepoint(scaled_mouse_x, scaled_mouse_y):
                selected_option = i
                
            is_selected = (i == selected_option)
            
            if is_selected:
                pulse = abs(math.sin(time_counter * 4))
                glow_color = (255, int(40 + pulse * 60), 0)
                pygame.draw.rect(canvas, (40, 5, 5), btn_rect)
                pygame.draw.rect(canvas, glow_color, btn_rect, 1, border_radius=2)
                text_surf = font_menu.render(option, True, (255, 255, 255))
                draw_cool_indicator_demon(canvas, btn_rect.x - 18, btn_rect.y, time_counter)
            else:
                text_surf = font_menu.render(option, True, (180, 30, 30))
                
            text_x = btn_rect.x + (btn_rect.width - text_surf.get_width()) // 2
            canvas.blit(text_surf, (text_x, btn_rect.y + 1))

    elif game_state == "PROLOGUE":
        canvas.fill((5, 2, 2))
        
        prologue_surf = font_prologue.render("EL COMIENZO DEL FIN...", True, (200, 30, 30))
        px = (GAME_WIDTH - prologue_surf.get_width()) // 2
        py = (GAME_HEIGHT - prologue_surf.get_height()) // 2 - 10
        canvas.blit(prologue_surf, (px, py))

        if int(time_counter * 2) % 2 == 0:
            prompt_surf = font_sub.render("Presiona ENTER para continuar", True, (150, 150, 150))
            prompt_x = (GAME_WIDTH - prompt_surf.get_width()) // 2
            canvas.blit(prompt_surf, (prompt_x, py + 25))

    elif game_state == "GAMEPLAY":
        canvas.blit(school_bg, (0, 0))

    scaled_surface = pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
main()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("\n" + "=" * 50)
print("ARCHIVOS DETECTADOS EN TU CARPETA:")
print(os.listdir(BASE_DIR))
print("=" * 50 + "\n")


SCREEN_WIDTH = 1360
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("REQUIEM: El juicio final")
clock = pygame.time.Clock()

# Canvas Pixel Art interno
GAME_WIDTH = 320
GAME_HEIGHT = 180
canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

# 2. Carga segura de la imagen (evita que el programa crashee)
ruta_imagen = os.path.join(BASE_DIR, "fondo_escuela.png")

try:
    school_bg = pygame.image.load(ruta_imagen).convert_alpha()
    school_bg = pygame.transform.scale(school_bg, (GAME_WIDTH, GAME_HEIGHT))
    print("-> La imagen 'fondo_escuela.png' se cargó con éxito.")
except FileNotFoundError:
    print("-> ADVERTENCIA: No se encontró 'fondo_escuela.png'. Se usará un fondo gris provisorio.")
    school_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    school_bg.fill((50, 50, 60))

# Fuentes
font_title = pygame.font.SysFont("Impact", 28)
font_sub = pygame.font.SysFont("Arial", 8, bold=True)
font_menu = pygame.font.SysFont("Arial", 8, bold=True)
font_prologue = pygame.font.SysFont("Arial", 12, bold=True)

menu_options = ["NEW GAME", "CONTINUE", "CONTROLS", "TROPHIES", "EXIT"]
selected_option = 0

# Estado inicial
game_state = "MENU"

# Partículas de Humo
smoke_particles = []
for _ in range(30):
    smoke_particles.append({
        "x": random.randint(0, GAME_WIDTH),
        "y": random.randint(0, GAME_HEIGHT),
        "radius": random.randint(8, 20),
        "alpha": random.randint(30, 80),
        "speed_y": random.uniform(0.1, 0.25),
        "speed_x": random.uniform(0.05, 0.2)
    })

# Partículas de Chispas
sparks = []
for _ in range(40):
    sparks.append({
        "x": random.randint(0, GAME_WIDTH),
        "y": random.randint(0, GAME_HEIGHT),
        "speed_y": random.uniform(0.2, 0.6),
        "speed_x": random.uniform(-0.15, 0.15),
        "color": random.choice([(255, 100, 0), (255, 200, 0), (200, 30, 0)])
    })

civilians = [
    {"x": 60, "y": 166, "speed": 0.45, "dir": -1},
    {"x": 120, "y": 166, "speed": 0.48, "dir": -1},
    {"x": 180, "y": 166, "speed": 0.42, "dir": -1},
    {"x": 260, "y": 166, "speed": 0.50, "dir": -1},
    {"x": 80, "y": 156, "speed": 0.38, "dir": -1},
    {"x": 190, "y": 156, "speed": 0.40, "dir": -1},
    {"x": 290, "y": 156, "speed": 0.36, "dir": -1}
]

demons = [
    {"x": 230, "y": 146, "speed": 0.45, "dir": -1},
    {"x": 320, "y": 146, "speed": 0.38, "dir": -1}
]

flying_demons = [
    {"x": 280, "y": 35, "speed": 0.6, "dir": -1, "wing_offset": 0},
    {"x": 50, "y": 20, "speed": 0.45, "dir": 1, "wing_offset": 2.0},
    {"x": 200, "y": 55, "speed": 0.5, "dir": -1, "wing_offset": 4.0}
]

def draw_cool_indicator_demon(surface, x, y, time):
    pulse = abs(math.sin(time * 6))
    glow_surf = pygame.Surface((18, 18), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (255, 30, 0, int(60 + pulse * 80)), (9, 9), 8)
    surface.blit(glow_surf, (x - 2, y - 2))
    
    pygame.draw.polygon(surface, (180, 10, 10), [
        (x + 3, y + 3), (x + 11, y + 3), (x + 13, y + 7), (x + 7, y + 13), (x + 1, y + 7)
    ])
    pygame.draw.polygon(surface, (255, 50, 0), [(x + 2, y + 3), (x - 1, y - 3), (x + 4, y + 1)])
    pygame.draw.polygon(surface, (255, 50, 0), [(x + 12, y + 3), (x + 15, y - 3), (x + 10, y + 1)])
    surface.set_at((x - 1, y - 3), (255, 200, 0))
    surface.set_at((x + 15, y - 3), (255, 200, 0))
    
    pygame.draw.line(surface, (255, 255, 100), (x + 3, y + 6), (x + 5, y + 7), 1)
    pygame.draw.line(surface, (255, 255, 100), (x + 11, y + 6), (x + 9, y + 7), 1)
    
    pygame.draw.line(surface, (20, 0, 0), (x + 4, y + 10), (x + 10, y + 10), 1)
    surface.set_at((x + 5, y + 11), (255, 255, 255))
    surface.set_at((x + 9, y + 11), (255, 255, 255))

def draw_detailed_civilian(surface, x, y, direction, time):
    leg_swing = math.sin(time * 16) * 4 * direction
    arm_swing = math.sin(time * 16 + math.pi) * 3 * direction
    ix, iy = int(x), int(y)
    
    pygame.draw.ellipse(surface, (5, 2, 2), (ix - 3, iy + 7, 10, 4))
    pygame.draw.line(surface, (25, 25, 35), (ix + 2, iy + 4), (ix + 1 + int(leg_swing), iy + 8), 2)
    pygame.draw.line(surface, (25, 25, 35), (ix + 3, iy + 4), (ix + 4 - int(leg_swing), iy + 8), 2)
    surface.set_at((ix + 1 + int(leg_swing), iy + 8), (200, 200, 200))
    surface.set_at((ix + 4 - int(leg_swing), iy + 8), (200, 200, 200))
    
    pygame.draw.rect(surface, (30, 80, 170), (ix, iy - 1, 5, 5))
    pygame.draw.rect(surface, (30, 110, 40), (ix, iy + 2, 5, 2))
    
    pygame.draw.line(surface, (215, 160, 125), (ix + 1, iy), (ix - int(arm_swing), iy + 3), 1)
    pygame.draw.line(surface, (215, 160, 125), (ix + 4, iy), (ix + 4 + int(arm_swing), iy + 3), 1)
    pygame.draw.rect(surface, (215, 160, 125), (ix + 1, iy - 5, 4, 4))

    eye_x = ix + 1 if direction < 0 else ix + 3
    surface.set_at((eye_x, iy - 3), (0, 0, 0))

def draw_cool_demon(surface, x, y, direction, time):
    leg_swing = math.sin(time * 12) * 4 * direction
    wing_flap = math.sin(time * 8) * 3
    ix, iy = int(x), int(y)
    
    pygame.draw.ellipse(surface, (5, 2, 2), (ix - 5, iy + 9, 14, 3))
    
    w_off = int(wing_flap)
    wing_pts_l = [(ix + 2, iy - 2), (ix - 10 * direction, iy - 10 + w_off), (ix - 4 * direction, iy + 3)]
    wing_pts_r = [(ix + 4, iy - 2), (ix + 12 * direction, iy - 10 + w_off), (ix + 6 * direction, iy + 3)]
    pygame.draw.polygon(surface, (80, 0, 0), wing_pts_l)
    pygame.draw.polygon(surface, (140, 10, 10), wing_pts_l, 1)
    pygame.draw.polygon(surface, (80, 0, 0), wing_pts_r)
    pygame.draw.polygon(surface, (140, 10, 10), wing_pts_r, 1)
    
    pygame.draw.line(surface, (120, 10, 10), (ix + 2, iy + 4), (ix + int(leg_swing), iy + 9), 2)
    pygame.draw.line(surface, (120, 10, 10), (ix + 5, iy + 4), (ix + 6 - int(leg_swing), iy + 9), 2)
    
    pygame.draw.polygon(surface, (180, 20, 20), [(ix, iy - 4), (ix + 7, iy - 4), (ix + 5, iy + 5), (ix + 2, iy + 5)])
    pygame.draw.polygon(surface, (110, 10, 10), [(ix + 2, iy - 2), (ix + 5, iy - 2), (ix + 4, iy + 4), (ix + 3, iy + 4)])
    
    pygame.draw.line(surface, (230, 30, 30), (ix + 1, iy - 2), (ix - 2 * direction, iy + 2), 1)
    
    pygame.draw.rect(surface, (200, 25, 25), (ix + 1, iy - 8, 5, 5))
    pygame.draw.polygon(surface, (255, 80, 0), [(ix + 1, iy - 7), (ix - 3 * direction, iy - 13), (ix + 2, iy - 7)])
    pygame.draw.polygon(surface, (255, 80, 0), [(ix + 5, iy - 7), (ix + 8 * direction, iy - 13), (ix + 4, iy - 7)])
    
    eye_x = ix + 1 if direction < 0 else ix + 4
    surface.set_at((eye_x, iy - 6), (255, 230, 0))
    surface.set_at((eye_x + direction, iy - 6), (255, 100, 0))

def draw_flying_demon(surface, x, y, direction, time, offset):
    wing_flap = math.sin(time * 10 + offset) * 5
    float_y = math.sin(time * 3 + offset) * 2
    ix, iy = int(x), int(y + float_y)
    
    w_off = int(wing_flap)
    
    wing_l = [(ix + 1, iy), (ix - 12 * direction, iy - 8 + w_off), (ix - 5 * direction, iy + 4)]
    wing_r = [(ix + 3, iy), (ix + 14 * direction, iy - 8 + w_off), (ix + 7 * direction, iy + 4)]
    
    pygame.draw.polygon(surface, (100, 0, 0), wing_l)
    pygame.draw.polygon(surface, (180, 20, 20), wing_l, 1)
    pygame.draw.polygon(surface, (100, 0, 0), wing_r)
    pygame.draw.polygon(surface, (180, 20, 20), wing_r, 1)
    
    pygame.draw.ellipse(surface, (160, 15, 15), (ix - 1, iy - 2, 6, 4))
    pygame.draw.line(surface, (120, 10, 10), (ix + 2, iy + 2), (ix - 4 * direction, iy + 6), 1)
    
    eye_x = ix if direction < 0 else ix + 3
    surface.set_at((eye_x, iy - 1), (255, 255, 0))

def draw_giant_demon(surface, time):
    float_y = math.sin(time * 1.5) * 2
    gx = 118
    gy = int(-2 + float_y)

    giant_surf = pygame.Surface((100, 140), pygame.SRCALPHA)
    pygame.draw.polygon(giant_surf, (20, 3, 3), [(25, 50), (55, 50), (75, 140), (5, 140)])
    pygame.draw.polygon(giant_surf, (15, 2, 2), [(35, 50), (45, 50), (50, 140), (30, 140)])

    pygame.draw.polygon(giant_surf, (30, 5, 5), [(10, 25), (-5, -5), (20, 15)])
    pygame.draw.polygon(giant_surf, (30, 5, 5), [(70, 25), (85, -5), (60, 15)])

    pygame.draw.polygon(giant_surf, (25, 4, 4), [(15, 10), (65, 10), (55, 50), (25, 50)])

    pygame.draw.rect(giant_surf, (255, 230, 0), (24, 20, 10, 6))
    pygame.draw.rect(giant_surf, (255, 230, 0), (46, 20, 10, 6))
    pygame.draw.rect(giant_surf, (200, 0, 0), (28, 20, 2, 6))
    pygame.draw.rect(giant_surf, (200, 0, 0), (50, 20, 2, 6))

    pygame.draw.polygon(giant_surf, (0, 0, 0), [(22, 34), (58, 34), (50, 48), (30, 48)])

    for tx in range(24, 56, 4):
        pygame.draw.polygon(giant_surf, (255, 255, 255), [(tx, 34), (tx + 2, 34), (tx + 1, 38)])
    for tx in range(28, 50, 4):
        pygame.draw.polygon(giant_surf, (255, 255, 255), [(tx, 48), (tx + 2, 48), (tx + 1, 44)])

    surface.blit(giant_surf, (gx, gy))

def draw_scenery(surface, time):
    surface.fill((10, 2, 2))
    glow = pygame.Surface((GAME_WIDTH, 90), pygame.SRCALPHA)
    pygame.draw.rect(glow, (140, 25, 0, 45), (0, 0, GAME_WIDTH, 90))
    surface.blit(glow, (0, GAME_HEIGHT - 90))

    draw_giant_demon(surface, time)

    buildings = [
        {"x": 60, "y": 40, "w": 45, "h": 100, "antenna": True},
        {"x": 110, "y": 25, "w": 55, "h": 115, "antenna": False},
        {"x": 170, "y": 50, "w": 40, "h": 90, "antenna": True},
        {"x": 215, "y": 30, "w": 50, "h": 110, "antenna": False},
        {"x": 270, "y": 60, "w": 50, "h": 80, "antenna": True}
    ]

    for b in buildings:
        bx, by, bw, bh = b["x"], b["y"], b["w"], b["h"]
        pygame.draw.rect(surface, (18, 6, 6), (bx, by, bw, bh))
        pygame.draw.rect(surface, (45, 12, 12), (bx, by, bw, bh), 1)
        pygame.draw.rect(surface, (30, 8, 8), (bx - 2, by - 2, bw + 4, 3))
        pygame.draw.rect(surface, (55, 15, 15), (bx - 2, by - 2, bw + 4, 3), 1)

        if b["antenna"]:
            pygame.draw.line(surface, (60, 20, 20), (bx + bw // 2, by - 2), (bx + bw // 2, by - 12), 1)
            surface.set_at((bx + bw // 2, by - 12), (255, 60, 0))

        for wx in range(bx + 4, bx + bw - 6, 8):
            for wy in range(by + 8, by + bh - 10, 10):
                if (wx * 7 + wy * 3) % 5 == 0:
                    pygame.draw.rect(surface, (230, 100, 0), (wx, wy, 4, 5))
                    pygame.draw.rect(surface, (255, 200, 50), (wx + 1, wy + 1, 2, 3))
                else:
                    pygame.draw.rect(surface, (10, 3, 3), (wx, wy, 4, 5))

    pygame.draw.rect(surface, (15, 12, 12), (0, 140, GAME_WIDTH, GAME_HEIGHT - 140))
    pygame.draw.rect(surface, (22, 18, 18), (0, 152, GAME_WIDTH, GAME_HEIGHT - 152))
    pygame.draw.line(surface, (45, 35, 35), (0, 140), (GAME_WIDTH, 140), 1)
    pygame.draw.line(surface, (38, 28, 28), (0, 152), (GAME_WIDTH, 152), 1)

    pygame.draw.line(surface, (255, 60, 0), (30, 165), (55, 168), 1)
    pygame.draw.line(surface, (255, 60, 0), (140, 146), (160, 148), 1)
    pygame.draw.line(surface, (255, 60, 0), (230, 160), (255, 163), 1)

    for fx in range(0, GAME_WIDTH, 8):
        fh = int(abs(math.sin(fx * 0.3 + time * 4) * 5) + abs(math.cos(fx * 0.1 + time * 3) * 3))
        if fh > 1:
            pygame.draw.rect(surface, (255, 40, 0), (fx, 140 - fh, 3, fh))
            pygame.draw.rect(surface, (255, 180, 0), (fx + 1, 140 - fh + 2, 1, fh - 2))

# Bucle Principal
time_counter = 0
running = True

while running:
    time_counter += 0.05
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scaled_mouse_x = mouse_x * (GAME_WIDTH / SCREEN_WIDTH)
    scaled_mouse_y = mouse_y * (GAME_HEIGHT / SCREEN_HEIGHT)

    # 1. CAPTURAR EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # "NEW GAME"
                        game_state = "PROLOGUE"
                    elif selected_option == 4:  # "EXIT"
                        running = False

            elif game_state == "PROLOGUE":
                if event.key == pygame.K_RETURN:
                    game_state = "GAMEPLAY"

    # 2. DIBUJAR PANTALLA
    if game_state == "MENU":
        draw_scenery(canvas, time_counter)

        for fd in flying_demons:
            fd["x"] += fd["speed"] * fd["dir"]
            if fd["dir"] == -1 and fd["x"] < -30:
                fd["x"] = GAME_WIDTH + 30
                fd["y"] = random.randint(15, 65)
            elif fd["dir"] == 1 and fd["x"] > GAME_WIDTH + 30:
                fd["x"] = -30
                fd["y"] = random.randint(15, 65)
            draw_flying_demon(canvas, fd["x"], fd["y"], fd["dir"], time_counter, fd["wing_offset"])

        for d in demons:
            d["x"] += d["speed"] * d["dir"]
            if d["x"] < -30:
                d["x"] = GAME_WIDTH + random.randint(30, 80)
            draw_cool_demon(canvas, d["x"], d["y"], d["dir"], time_counter)

        for c in civilians:
            c["x"] += c["speed"] * c["dir"]
            if c["x"] < -20:
                c["x"] = GAME_WIDTH + random.randint(10, 50)
            draw_detailed_civilian(canvas, c["x"], c["y"], c["dir"], time_counter)

        for s in smoke_particles:
            s["y"] -= s["speed_y"]
            s["x"] += s["speed_x"] + math.sin(time_counter + s["y"] * 0.03) * 0.15
            if s["y"] < -20:
                s["y"] = GAME_HEIGHT + 10
                s["x"] = random.randint(0, GAME_WIDTH)
            
            smoke_surf = pygame.Surface((s["radius"] * 2, s["radius"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surf, (40, 25, 25, s["alpha"]), (s["radius"], s["radius"]), s["radius"])
            canvas.blit(smoke_surf, (int(s["x"]) - s["radius"], int(s["y"]) - s["radius"]))

        for p in sparks:
            p["y"] -= p["speed_y"]
            p["x"] += p["speed_x"]
            if p["y"] < 0:
                p["y"] = GAME_HEIGHT
                p["x"] = random.randint(0, GAME_WIDTH)
            canvas.set_at((int(p["x"]), int(p["y"])), p["color"])

        # UI del Menú
        title_surf = font_title.render("REQUIEM", True, (0, 0, 0))
        canvas.blit(title_surf, (12, 8))
        title_surf_red = font_title.render("REQUIEM", True, (120, 10, 10))
        canvas.blit(title_surf_red, (10, 6))

        sub_surf = font_sub.render('"EL JUICIO FINAL"', True, (220, 40, 0))
        canvas.blit(sub_surf, (20, 36))

        start_y = 58
        for i, option in enumerate(menu_options):
            btn_rect = pygame.Rect(26, start_y + (i * 18), 80, 13)
            
            if btn_rect.collidepoint(scaled_mouse_x, scaled_mouse_y):
                selected_option = i
                
            is_selected = (i == selected_option)
            
            if is_selected:
                pulse = abs(math.sin(time_counter * 4))
                glow_color = (255, int(40 + pulse * 60), 0)
                pygame.draw.rect(canvas, (40, 5, 5), btn_rect)
                pygame.draw.rect(canvas, glow_color, btn_rect, 1, border_radius=2)
                text_surf = font_menu.render(option, True, (255, 255, 255))
                draw_cool_indicator_demon(canvas, btn_rect.x - 18, btn_rect.y, time_counter)
            else:
                text_surf = font_menu.render(option, True, (180, 30, 30))
                
            text_x = btn_rect.x + (btn_rect.width - text_surf.get_width()) // 2
            canvas.blit(text_surf, (text_x, btn_rect.y + 1))

    elif game_state == "PROLOGUE":
        canvas.fill((5, 2, 2))
        
        prologue_surf = font_prologue.render("EL COMIENZO DEL FIN...", True, (200, 30, 30))
        px = (GAME_WIDTH - prologue_surf.get_width()) // 2
        py = (GAME_HEIGHT - prologue_surf.get_height()) // 2 - 10
        canvas.blit(prologue_surf, (px, py))

        if int(time_counter * 2) % 2 == 0:
            prompt_surf = font_sub.render("Presiona ENTER para continuar", True, (150, 150, 150))
            prompt_x = (GAME_WIDTH - prompt_surf.get_width()) // 2
            canvas.blit(prompt_surf, (prompt_x, py + 25))

    elif game_state == "GAMEPLAY":
        canvas.blit(school_bg, (0, 0))

    scaled_surface = pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
main()



def prologo():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    print("\n" + "=" * 50)
    print("ARCHIVOS DETECTADOS EN TU CARPETA:")
    print(os.listdir(BASE_DIR))
    print("=" * 50 + "\n")
    animacion_menu()
    ruta_imagen = os.path.join(BASE_DIR, "fondo_escuela.png")
    

    try:
        school_bg = pygame.image.load(ruta_imagen).convert_alpha()
        school_bg = pygame.transform.scale(school_bg, (configuracion))
        print("-> La imagen 'fondo_escuela.png' se cargó con éxito.")
    except FileNotFoundError:
        print("-> ADVERTENCIA: No se encontró 'fondo_escuela.png'. Se usará un fondo gris provisorio.")
        school_bg = pygame.Surface((configuracion))
        school_bg.fill((50, 50, 60))



