import pygame
import sys

pygame.init()
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, GAME_HEIGHT, BASE_DIR, abrir_archivo

# Configuración del motor de video de Pygame
canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("REQUIEM: El juicio final")
clock = pygame.time.Clock()

import random
import math
import animacion_menu
from prologo import prologue

# Fuentes tipográficas vectoriales
font_title = pygame.font.SysFont("Impact", 64)
font_menu = pygame.font.SysFont("Arial", 22, bold=True)
font_char_name = pygame.font.SysFont("Impact", 42)
font_desc = pygame.font.SysFont("Arial", 16, bold=False)
font_ui_help = pygame.font.SysFont("Arial", 18, bold=True)

menu_options = ["NEW GAME", "CONTINUE", "CONTROLS", "TROPHIES", "EXIT"]
selected_option = 0
game_state = "MENU"

assets_chars = BASE_DIR / "assets" / "sprites" / "seleccion_personajes"

characters = [
    {
        "name": "Fei Liang",
        "file": assets_chars / "Fei_liang.png",
        "color": (225, 220, 205),
        "desc": "Un héroe capaz de manipular el viento y moverse a una velocidad extraordinaria. Su origen está rodeado de misterio, pero su aparición suele coincidir con grandes amenazas.\n\nÁgil, impredecible y veloz. Utiliza corrientes de aire para aumentar sus movimientos, esquivar ataques y lanzar poderosas ráfagas."
    },
    {
        "name": "Korg",
        "file": assets_chars / "Korg.png",
        "color": (240, 150, 50),
        "desc": "Un guerrero elegido por el poder de la tierra. Su cuerpo y su espíritu se volvieron tan resistentes como la roca, convirtiéndolo en uno de los protectores más fuertes del grupo.\n\nSerio, resistente y protector. Puede crear roca, levantar barreras y potenciar sus golpes con energía terrestre."
    },
    {
        "name": "Diana",
        "file": assets_chars / "Diana.png",
        "color": (50, 155, 90),
        "desc": "Una heroína conectada con la naturaleza desde su nacimiento. Puede controlar plantas y utilizar su energía para proteger la vida y combatir a quienes amenazan el equilibrio del mundo.\n\nInteligente, tranquila y estratégica. Utiliza su arco junto con enredaderas, raíces y ataques de energía vegetal."
    },
    {
        "name": "Escanor",
        "file": assets_chars / "Escanor.png",
        "color": (195, 35, 35),
        "desc": "Un héroe nacido con el poder de controlar las llamas. Desde pequeño aprendió a dominar su temperamento junto con su poder y ahora lucha para proteger a quienes no pueden defenderse.\n\nValiente, impulsivo y decidido. Combate con una espada enorme y concentra fuego en sus ataques para aumentar su fuerza."
    }
]
selected_char_index = 0
chosen_char_name = None

archivos_imagenes = {
    "Fei Liang": "Fei_liang.png",
    "Korg": "Korg.png",
    "Diana": "Diana.png",
    "Escanor": "Escanor.png",
}
imagenes_chars = {}
archivos_ya_abiertos = set()

prologue_bg_surface = None


def buscar_imagen(nombre_archivo):
    carpetas = [
        assets_chars,
        BASE_DIR / "assets" / "sprites",
        BASE_DIR / "assets",
        BASE_DIR / "imagenes",
        BASE_DIR,
    ]
    for carpeta in carpetas:
        if carpeta.is_dir():
            for archivo in carpeta.iterdir():
                if archivo.name.lower() == nombre_archivo.lower():
                    return archivo
    return None


def obtener_imagen_personaje(char, caja=(314, 314)):
    nombre = char["name"]
    if nombre not in imagenes_chars:
        img = None
        ruta = buscar_imagen(archivos_imagenes[nombre])
        if ruta is None:
            print(f"[IMAGEN] No se encontró {archivos_imagenes[nombre]}.")
        else:
            try:
                img = pygame.image.load(str(ruta)).convert_alpha()
                w, h = img.get_size()
                esc = min(caja[0] / w, caja[1] / h)
                img = pygame.transform.scale(img, (int(w * esc), int(h * esc)))
            except pygame.error as e:
                print(f"[IMAGEN] Error cargando {ruta}: {e}")
                img = None
        imagenes_chars[nombre] = img
    return imagenes_chars[nombre]


def draw_text_wrapped(surface, text, x, y, max_width, font, color):
    lines = text.split('\n')
    current_y = y
    for line in lines:
        words = line.split(' ')
        if not words or words == ['']:
            current_y += 12
            continue
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                text_surf = font.render(current_line, True, color)
                surface.blit(text_surf, (x, current_y))
                current_y += font.get_linesize()
                current_line = word + " "
        if current_line:
            text_surf = font.render(current_line, True, color)
            surface.blit(text_surf, (x, current_y))
            current_y += font.get_linesize()


def draw_character_artwork(surface, name, cx, cy):
    if name == "Fei Liang":
        pygame.draw.rect(surface, (45, 40, 42), (cx - 40, cy - 10, 80, 70), border_radius=5)
        pygame.draw.circle(surface, (235, 225, 215), (cx, cy - 25), 32)
    elif name == "Korg":
        pygame.draw.rect(surface, (70, 50, 45), (cx - 40, cy - 10, 80, 70), border_radius=5)
        pygame.draw.circle(surface, (240, 185, 145), (cx, cy - 25), 28)
    elif name == "Diana":
        pygame.draw.rect(surface, (25, 65, 40), (cx - 45, cy - 15, 90, 75), border_radius=8)
        pygame.draw.circle(surface, (245, 245, 250), (cx, cy - 22), 30)
    elif name == "Escanor":
        pygame.draw.rect(surface, (165, 25, 25), (cx - 50, cy - 5, 100, 65), border_radius=10)
        pygame.draw.circle(surface, (240, 190, 145), (cx, cy - 28), 26)


def render_menu(time_counter):
    animacion_menu.draw_scenery(canvas, time_counter)
    pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)

    title_surf = font_title.render("REQUIEM", True, (230, 40, 40))
    screen.blit(title_surf, (80, 60))
    sub_surf = font_menu.render("EL JUICIO FINAL", True, (235, 185, 40))
    screen.blit(sub_surf, (84, 135))

    for i, option in enumerate(menu_options):
        activa = i == selected_option
        color = (255, 255, 255) if activa else (150, 130, 130)
        texto = ("> " if activa else "  ") + option
        surf = font_menu.render(texto, True, color)
        screen.blit(surf, (84, 230 + i * 42))

    if chosen_char_name:
        info = font_ui_help.render(f"Héroe elegido: {chosen_char_name}", True, (235, 185, 40))
        screen.blit(info, (84, SCREEN_HEIGHT - 60))


def render_prologue():
    global prologue_bg_surface
    screen.fill((10, 10, 15))

    if prologue_bg_surface is None:
        prologue_bg_surface = prologue()

    canvas.blit(prologue_bg_surface, (0, 0))
    scaled_surface = pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    title_surf = font_title.render("PRÓLOGO", True, (255, 255, 255))
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 80))

    help_surf = font_ui_help.render("Presiona [ENTER] o [ESPACIO] para continuar...", True, (235, 185, 40))
    screen.blit(help_surf, (SCREEN_WIDTH // 2 - help_surf.get_width() // 2, SCREEN_HEIGHT - 80))


def render_character_select_high_res(time_counter):
    """Función de renderizado de la selección de personaje."""
    screen.fill((14, 11, 18))

    char = characters[selected_char_index]
    if char["file"] not in archivos_ya_abiertos:
        archivos_ya_abiertos.add(char["file"])

    title_surf = font_title.render("SELECCIONA TU HÉROE", True, (230, 40, 40))
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 40))

    box_width, box_height = 320, 320
    box_x = 180
    box_y = 180
    preview_box = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, (24, 19, 28), preview_box)
    pygame.draw.rect(screen, char["color"], preview_box, 3, border_radius=8)

    center_x = box_x + box_width // 2
    center_y = box_y + box_height // 2

    img = obtener_imagen_personaje(char)
    if img:
        screen.blit(img, img.get_rect(center=(center_x, center_y)))
    else:
        draw_character_artwork(screen, char["name"], center_x, center_y)

    name_surf = font_char_name.render(char["name"], True, (255, 255, 255))
    screen.blit(name_surf, (box_x + box_width // 2 - name_surf.get_width() // 2, box_y + box_height + 20))

    arrow_pulse = int(math.sin(time_counter * 5) * 6)
    arrow_l = font_title.render("<", True, (235, 185, 40))
    arrow_r = font_title.render(">", True, (235, 185, 40))
    screen.blit(arrow_l, (box_x - 70 - arrow_pulse, box_y + box_height // 2 - 40))
    screen.blit(arrow_r, (box_x + box_width + 45 + arrow_pulse, box_y + box_height // 2 - 40))

    desc_x = 590
    desc_y = 185
    desc_width = 600

    header_desc = font_menu.render("BIOGRAFÍA Y ESTILO DE COMBATE", True, char["color"])
    screen.blit(header_desc, (desc_x, desc_y))
    pygame.draw.line(screen, (60, 50, 70), (desc_x, desc_y + 35), (desc_x + desc_width, desc_y + 35), 2)

    draw_text_wrapped(screen, char["desc"], desc_x, desc_y + 55, desc_width, font_desc, (220, 220, 225))

    help_surf = font_ui_help.render("[ENTER] CONFIRMAR HÉROE   |   [ESC] VOLVER AL MENÚ", True, (130, 130, 140))
    screen.blit(help_surf, (SCREEN_WIDTH // 2 - help_surf.get_width() // 2, SCREEN_HEIGHT - 65))


def main():
    global selected_option, game_state, selected_char_index, chosen_char_name
    time_counter = 0
    running = True

    while running:
        clock.tick(60)
        time_counter += 0.05

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
                        option = menu_options[selected_option]
                        if option == "NEW GAME":
                            game_state = "PROLOGUE"
                        elif option == "EXIT":
                            running = False

                elif game_state == "PROLOGUE":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state = "CHARACTER_SELECT"
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

                elif game_state == "CHARACTER_SELECT":
                    if event.key == pygame.K_LEFT:
                        selected_char_index = (selected_char_index - 1) % len(characters)
                    elif event.key == pygame.K_RIGHT:
                        selected_char_index = (selected_char_index + 1) % len(characters)
                    elif event.key == pygame.K_RETURN:
                        chosen_char_name = characters[selected_char_index]["name"]
                        game_state = "MENU"
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

        # --- DIBUJO ---
        if game_state == "MENU":
            render_menu(time_counter)
        elif game_state == "PROLOGUE":
            render_prologue()
        elif game_state == "CHARACTER_SELECT":
            render_character_select_high_res(time_counter)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()