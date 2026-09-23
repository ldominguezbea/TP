import pygame
import random
import math
import sys
import os
import animacion_menu

pygame.init()

# Dimensiones generales
SCREEN_WIDTH = animacion_menu.SCREEN_WIDTH
SCREEN_HEIGHT = animacion_menu.SCREEN_HEIGHT
GAME_WIDTH = animacion_menu.GAME_WIDTH
GAME_HEIGHT = animacion_menu.GAME_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("REQUIEM: El juicio final")
clock = pygame.time.Clock()

# Canvas Pixel Art interno
canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

# Rutas e imágenes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(BASE_DIR, "fondo_escuela.jpg")

try:
    school_bg = pygame.image.load(ruta_imagen).convert_alpha()
    school_bg = pygame.transform.scale(school_bg, (GAME_WIDTH, GAME_HEIGHT))
    print("-> La imagen 'fondo_escuela.jpg' se cargó con éxito.")
except FileNotFoundError:
    print("-> ADVERTENCIA: No se encontró la imagen. Se usará un fondo provisorio.")
    school_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    school_bg.fill((50, 50, 60))

# Fuentes
font_title = pygame.font.SysFont("Impact", 28)
font_sub = pygame.font.SysFont("Arial", 8, bold=True)
font_menu = pygame.font.SysFont("Arial", 8, bold=True)
font_prologue = pygame.font.SysFont("Arial", 12, bold=True)

menu_options = ["NEW GAME", "CONTINUE", "CONTROLS", "TROPHIES", "EXIT"]
selected_option = 0
game_state = "MENU"

# Partículas de Humo
smoke_particles = [
    {
        "x": random.randint(0, GAME_WIDTH),
        "y": random.randint(0, GAME_HEIGHT),
        "radius": random.randint(8, 20),
        "alpha": random.randint(30, 80),
        "speed_y": random.uniform(0.1, 0.25),
        "speed_x": random.uniform(0.05, 0.2)
    } for _ in range(30)
]

# Partículas de Chispas
sparks = [
    {
        "x": random.randint(0, GAME_WIDTH),
        "y": random.randint(0, GAME_HEIGHT),
        "speed_y": random.uniform(0.2, 0.6),
        "speed_x": random.uniform(-0.15, 0.15),
        "color": random.choice([(255, 100, 0), (255, 200, 0), (200, 30, 0)])
    } for _ in range(40)
]

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

def main():
    global selected_option, game_state
    time_counter = 0
    running = True

    while running:
        time_counter += 0.05
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scaled_mouse_x = mouse_x * (GAME_WIDTH / SCREEN_WIDTH)
        scaled_mouse_y = mouse_y * (GAME_HEIGHT / SCREEN_HEIGHT)

        # 1. EVENTOS
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
                
            elif event.type == pygame.MOUSEBUTTOMDOWN:
                if mouse_x == and mouse_y == 


        if game_state == "MENU":
            animacion_menu.draw_scenery(canvas, time_counter)

            for fd in flying_demons:
                fd["x"] += fd["speed"] * fd["dir"]
                if fd["dir"] == -1 and fd["x"] < -30:
                    fd["x"] = GAME_WIDTH + 30
                    fd["y"] = random.randint(15, 65)
                elif fd["dir"] == 1 and fd["x"] > GAME_WIDTH + 30:
                    fd["x"] = -30
                    fd["y"] = random.randint(15, 65)
                animacion_menu.draw_flying_demon(canvas, fd["x"], fd["y"], fd["dir"], time_counter, fd["wing_offset"])

            for d in demons:
                d["x"] += d["speed"] * d["dir"]
                if d["x"] < -30:
                    d["x"] = GAME_WIDTH + random.randint(30, 80)
                animacion_menu.draw_cool_demon(canvas, d["x"], d["y"], d["dir"], time_counter)

            for c in civilians:
                c["x"] += c["speed"] * c["dir"]
                if c["x"] < -20:
                    c["x"] = GAME_WIDTH + random.randint(10, 50)
                animacion_menu.draw_detailed_civilian(canvas, c["x"], c["y"], c["dir"], time_counter)

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

            # UI Menú
            title_surf = font_title.render("REQUIEM", True, (0, 0, 0))
            canvas.blit(title_surf, (12, 8))
            title_surf_red = font_title.render("REQUIEM", True, (120, 10, 10))
            canvas.blit(title_surf_red, (10, 6))

            sub_surf = font_sub.render('"EL JUICIO FINAL"', True, (220, 40, 0))
            canvas.blit(sub_surf, (20, 36))

            start_y = 58
            from prologo import prologue
            for i, option in enumerate(menu_options):
                btn_rect = pygame.Rect(26, start_y + (i * 18), 80, 13)
                pos_NEWGAME = 
                
                if btn_rect.collidepoint(scaled_mouse_x, scaled_mouse_y):
                    selected_option = i
                    
                is_selected = (i == selected_option)
                
                if is_selected:
                    pulse = abs(math.sin(time_counter * 4))
                    glow_color = (255, int(40 + pulse * 60), 0)
                    pygame.draw.rect(canvas, (40, 5, 5), btn_rect)
                    pygame.draw.rect(canvas, glow_color, btn_rect, 1, border_radius=2)
                    text_surf = font_menu.render(option, True, (255, 255, 255))
                    animacion_menu.draw_cool_indicator_demon(canvas, btn_rect.x - 18, btn_rect.y, time_counter)
                else:
                    text_surf = font_menu.render(option, True, (180, 30, 30))
                    
                text_x = btn_rect.x + (btn_rect.width - text_surf.get_width()) // 2
                canvas.blit(text_surf, (text_x, btn_rect.y + 1))

        elif game_state == "PROLOGUE":
            from prologo import prologue
            prologue()

        elif game_state == "GAMEPLAY":
            Player()

        scaled_surface = pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_surface, (0, 0))


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

main()