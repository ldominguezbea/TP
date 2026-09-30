import sys
import random
import math
import pygame
import animacion_menu
from jugadores import Player

pygame.init()

SCREEN_WIDTH = animacion_menu.SCREEN_WIDTH
SCREEN_HEIGHT = animacion_menu.SCREEN_HEIGHT
GAME_WIDTH = animacion_menu.GAME_WIDTH
GAME_HEIGHT = animacion_menu.GAME_HEIGHT

canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("REQUIEM: El juicio final")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Impact", 28)
font_sub = pygame.font.SysFont("Arial", 8, bold=True)
font_menu = pygame.font.SysFont("Arial", 8, bold=True)
font_prologue = pygame.font.SysFont("Arial", 12, bold=True)
font_char_name = pygame.font.SysFont("Impact", 16)
font_stats = pygame.font.SysFont("Arial", 7, bold=True)

# Menú extendido con la selección de personaje
menu_options = ["NEW GAME", "SELECT CHARACTER", "CONTINUE", "CONTROLS", "TROPHIES", "EXIT"]
selected_option = 0
game_state = "MENU"


characters = [
    {
        "name": "GUERRERO",
        "description": "Fuerza bruta y alta resistencia.",
        "color": (200, 50, 50),
        "health": "████████░░",
        "speed": "████░░░░░░",
        "power": "████████░░"
    },
    {
        "name": "MAGO",
        "description": "Ataques de largo alcance y magia destructiva.",
        "color": (50, 100, 220),
        "health": "████░░░░░░",
        "speed": "██████░░░░",
        "power": "██████████"
    },
    {
        "name": "ASESINO",
        "description": "Gran velocidad y golpes críticos rápidos.",
        "color": (50, 200, 100),
        "health": "█████░░░░░",
        "speed": "██████████",
        "power": "███████░░░"
    }
]
selected_char_index = 0
active_player = None


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

def render_character_select(time_counter):
    """Renderiza el menú de selección de personajes en el canvas."""
    canvas.fill((15, 10, 15))
    
    # Título del menú
    title = font_title.render("SELECCIONA TU HÉROE", True, (200, 30, 30))
    canvas.blit(title, (GAME_WIDTH // 2 - title.get_width() // 2, 10))

    char = characters[selected_char_index]

    # Recadro de Previsualización del Personaje
    preview_box = pygame.Rect(GAME_WIDTH // 2 - 35, 45, 70, 75)
    pygame.draw.rect(canvas, (30, 20, 25), preview_box)
    pygame.draw.rect(canvas, char["color"], preview_box, 2, border_radius=4)

    # Silueta / Representación gráfica del personaje
    pygame.draw.circle(canvas, char["color"], (GAME_WIDTH // 2, 75), 18)

    # Nombre del Personaje
    name_surf = font_char_name.render(char["name"], True, (255, 255, 255))
    canvas.blit(name_surf, (GAME_WIDTH // 2 - name_surf.get_width() // 2, 125))

    # Indicadores de flecha (Pulsación visual)
    arrow_offset = int(math.sin(time_counter * 6) * 3)
    arrow_left = font_title.render("<", True, (220, 180, 0))
    arrow_right = font_title.render(">", True, (220, 180, 0))
    canvas.blit(arrow_left, (25 - arrow_offset, 65))
    canvas.blit(arrow_right, (GAME_WIDTH - 35 + arrow_offset, 65))

    # Estadísticas e Información
    desc_surf = font_stats.render(char["description"], True, (180, 180, 180))
    canvas.blit(desc_surf, (GAME_WIDTH // 2 - desc_surf.get_width() // 2, 142))

    hp_surf = font_stats.render(f"SALUD: {char['health']}", True, (255, 80, 80))
    spd_surf = font_stats.render(f"VEL:   {char['speed']}", True, (80, 255, 80))
    pow_surf = font_stats.render(f"PODER: {char['power']}", True, (80, 180, 255))

    canvas.blit(hp_surf, (40, 155))
    canvas.blit(spd_surf, (40, 165))
    canvas.blit(pow_surf, (40, 175))

    # Instrucciones de navegación
    info_surf = font_sub.render("[ENTER] CONFIRMAR   |   [ESC] VOLVER", True, (150, 150, 150))
    canvas.blit(info_surf, (GAME_WIDTH // 2 - info_surf.get_width() // 2, 192))


def main():
    global selected_option, game_state, selected_char_index, active_player
    time_counter = 0
    running = True

    while running:
        time_counter += 0.05
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scaled_mouse_x = mouse_x * (GAME_WIDTH / SCREEN_WIDTH)
        scaled_mouse_y = mouse_y * (GAME_HEIGHT / SCREEN_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # --- NAVEGACIÓN EN MENÚ PRINCIPAL ---
                if game_state == "MENU":
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        option = menu_options[selected_option]
                        if option == "NEW GAME":
                            game_state = "PROLOGUE"
                        elif option == "SELECT CHARACTER":
                            game_state = "CHARACTER_SELECT"
                        elif option == "EXIT":
                            running = False

                # --- NAVEGACIÓN EN SELECCIÓN DE PERSONAJE ---
                elif game_state == "CHARACTER_SELECT":
                    if event.key == pygame.K_LEFT:
                        selected_char_index = (selected_char_index - 1) % len(characters)
                    elif event.key == pygame.K_RIGHT:
                        selected_char_index = (selected_char_index + 1) % len(characters)
                    elif event.key == pygame.K_RETURN:
                        # Inicia el juego con el personaje seleccionado
                        game_state = "GAMEPLAY"
                        active_player = Player(200, 500)
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

        # --- DIBUJADO DE ESTADOS DE JUEGO ---
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

            start_y = 50
            for i, option in enumerate(menu_options):
                btn_rect = pygame.Rect(26, start_y + (i * 15), 90, 12)

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

        elif game_state == "CHARACTER_SELECT":
            render_character_select(time_counter)

        elif game_state == "PROLOGUE":
            from prologo import prologue
            prologue()

        elif game_state == "GAMEPLAY":
            from enemigos import Enemigo
            canvas.fill((20, 20, 20))
            if active_player:
                active_player.update(1 / 60)

        # Escalar lienzo a la pantalla principal
        scaled_surface = pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()