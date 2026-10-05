import pygame
import sys

# 1. INICIALIZACIÓN ABSOLUTA: Esto previene cierres inesperados por orden de carga
pygame.init()
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, GAME_HEIGHT, BASE_DIR, abrir_archivo

# Configuración del motor de video de Pygame
canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("REQUIEM: El juicio final")
clock = pygame.time.Clock()

# Importaciones seguras una vez que la pantalla de video está inicializada
import random
import math
import animacion_menu

# Fuentes tipográficas vectoriales escaladas para alta definición
font_title = pygame.font.SysFont("Impact", 64)
font_menu = pygame.font.SysFont("Arial", 22, bold=True)
font_char_name = pygame.font.SysFont("Impact", 42)
font_desc = pygame.font.SysFont("Arial", 16, bold=False)
font_ui_help = pygame.font.SysFont("Arial", 18, bold=True)

menu_options = ["NEW GAME", "SELECT CHARACTER", "CONTINUE", "CONTROLS", "TROPHIES", "EXIT"]
selected_option = 0
game_state = "MENU"

assets_chars = BASE_DIR / "assets" / "sprites" / "seleccion_personajes"

# --- LISTA DE HÉROES ACTUALIZADA (Tus personajes, nombres y biografías) ---
characters = [
    {
        "name": "Fei Liang",
        "file": assets_chars / "image_nu4OJY.txt",
        "color": (225, 220, 205),
        "desc": "Un héroe capaz de manipular el viento y moverse a una velocidad extraordinaria. Su origen está rodeado de misterio, pero su aparición suele coincidir con grandes amenazas.\n\nÁgil, impredecible y veloz. Utiliza corrientes de aire para aumentar sus movimientos, esquivar ataques y lanzar poderosas ráfagas."
    },
    {
        "name": "Korg",
        "file": assets_chars / "image_zUzvZd.txt",
        "color": (240, 150, 50),
        "desc": "Un guerrero elegido por el poder de la tierra. Su cuerpo y su espíritu se volvieron tan resistentes como la roca, convirtiéndolo en uno de los protectores más fuertes del grupo.\n\nSerio, resistente y protector. Puede crear roca, levantar barreras y potenciar sus golpes con energía terrestre."
    },
    {
        "name": "Diana",
        "file": assets_chars / "image_rOhLRq.txt",
        "color": (50, 155, 90),
        "desc": "Una heroína conectada con la naturaleza desde su nacimiento. Puede controlar plantas y utilizar su energía para proteger la vida y combatir a quienes amenazan el equilibrio del mundo.\n\nInteligente, tranquila y estratégica. Utiliza su arco junto con enredaderas, raíces y ataques de energía vegetal."
    },
    {
        "name": "Escanor",
        "file": assets_chars / "image_F6W_Wb.txt",
        "color": (195, 35, 35),
        "desc": "Un héroe nacido con el poder de controlar las llamas. Desde pequeño aprendió a dominar su temperamento junto con su poder y ahora lucha para proteger a quienes no pueden defenderse.\n\nValiente, impulsivo y decidido. Combate con una espada enorme y concentra fuego en sus ataques para aumentar su fuerza."
    }
]
selected_char_index = 0

def draw_text_wrapped(surface, text, x, y, max_width, font, color):
    """Procesador dinámico para el ajuste de líneas de texto en HD"""
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
    """Renderiza vectorialmente las características físicas de tus personajes en el recuadro central"""
    if name == "Fei Liang":
        pygame.draw.rect(surface, (45, 40, 42), (cx - 40, cy - 10, 80, 70), border_radius=5)
        pygame.draw.circle(surface, (235, 225, 215), (cx, cy - 25), 32)
        pygame.draw.rect(surface, (30, 25, 25), (cx - 20, cy - 32, 40, 16))
        pygame.draw.circle(surface, (245, 190, 150), (cx, cy - 24), 8)
        pygame.draw.line(surface, (20, 20, 20), (cx - 45, cy - 45), (cx - 15, cy - 10), 8)
        pygame.draw.line(surface, (20, 20, 20), (cx + 45, cy - 45), (cx + 15, cy - 10), 8)
    
    elif name == "Korg":
        pygame.draw.rect(surface, (70, 50, 45), (cx - 40, cy - 10, 80, 70), border_radius=5)
        pygame.draw.circle(surface, (240, 185, 145), (cx, cy - 25), 28)
        for i in range(7):
            angle = math.pi * (i / 6)
            bx = cx + int(math.cos(angle) * 38)
            by = cy - 5 + int(math.sin(angle) * 15)
            pygame.draw.circle(surface, (245, 130, 30), (bx, by), 9)
            pygame.draw.circle(surface, (20, 15, 10), (bx, by), 9, 1)

    elif name == "Diana":
        pygame.draw.rect(surface, (25, 65, 40), (cx - 45, cy - 15, 90, 75), border_radius=8)
        pygame.draw.circle(surface, (245, 245, 250), (cx, cy - 22), 30)
        pygame.draw.circle(surface, (245, 195, 155), (cx, cy - 22), 22)
        pygame.draw.polygon(surface, (245, 195, 155), [(cx - 20, cy - 25), (cx - 42, cy - 35), (cx - 20, cy - 15)])
        pygame.draw.polygon(surface, (245, 195, 155), [(cx + 20, cy - 25), (cx + 42, cy - 35), (cx + 20, cy - 15)])
        pygame.draw.rect(surface, (20, 100, 50), (cx - 15, cy - 44, 30, 8))
        
    elif name == "Escanor":
        pygame.draw.rect(surface, (165, 25, 25), (cx - 50, cy - 5, 100, 65), border_radius=10)
        pygame.draw.rect(surface, (220, 170, 45), (cx - 50, cy - 5, 100, 65), 3, border_radius=10)
        pygame.draw.circle(surface, (240, 190, 145), (cx, cy - 28), 26)
        pygame.draw.rect(surface, (95, 55, 40), (cx - 24, cy - 56, 48, 28), border_radius=4)

def render_character_select_high_res(time_counter):
    """Estructura de la escena de selección en alta fidelidad nativa"""
    screen.fill((14, 11, 18))
    
    char = characters[selected_char_index]
    abrir_archivo(char["file"]) # Lectura mediante tu función personalizada

    # Cabecera de escena
    title_surf = font_title.render("SELECCIONA TU HÉROE", True, (230, 40, 40))
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 40))

    # Caja central de previsualización del personaje
    box_width, box_height = 320, 320
    box_x = 180
    box_y = 180
    preview_box = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, (24, 19, 28), preview_box)
    pygame.draw.rect(screen, char["color"], preview_box, 3, border_radius=8)

    center_x = box_x + box_width // 2
    center_y = box_y + box_height // 2
    draw_character_artwork(screen, char["name"], center_x, center_y)

    # Nombre debajo de la caja
    name_surf = font_char_name.render(char["name"], True, (255, 255, 255))
    screen.blit(name_surf, (box_x + box_width // 2 - name_surf.get_width() // 2, box_y + box_height + 20))

    # Flechas místicas animadas por hilos de tiempo
    arrow_pulse = int(math.sin(time_counter * 5) * 6)
    arrow_l = font_title.render("<", True, (235, 185, 40))
    arrow_r = font_title.render(">", True, (235, 185, 40))
    screen.blit(arrow_l, (box_x - 70 - arrow_pulse, box_y + box_height // 2 - 40))
    screen.blit(arrow_r, (box_x + box_width + 45 + arrow_pulse, box_y + box_height // 2 - 40))

    # Panel lateral de descripción detallada
    desc_x = 590
    desc_y = 185
    desc_width = 600
    
    header_desc = font_menu.render("BIOGRAFÍA Y ESTILO DE COMBATE", True, char["color"])
    screen.blit(header_desc, (desc_x, desc_y))
    pygame.draw.line(screen, (60, 50, 70), (desc_x, desc_y + 35), (desc_x + desc_width, desc_y + 35), 2)
    
    # Renderizado ajustado de la descripción en HD
    draw_text_wrapped(screen, char["desc"], desc_x, desc_y + 55, desc_width, font_desc, (220, 220, 225))

    # Ayuda contextual inferior
    help_surf = font_ui_help.render("[ENTER] CONFIRMAR HÉROE   |   [ESC] VOLVER AL MENÚ", True, (130, 130, 140))
    screen.blit(help_surf, (SCREEN_WIDTH // 2 - help_surf.get_width() // 2, SCREEN_HEIGHT - 65))

def main():
    global selected_option, game_state, selected_char_index
    time_counter = 0
    running = True

    while running:
        clock.tick(60)
        time_counter += 0.05
        mouse_x, mouse_y = pygame.mouse.get_pos()

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
                        if option == "SELECT CHARACTER": 
                            game_state = "CHARACTER_SELECT"
                        elif option == "EXIT": 
                            running = False

                elif game_state == "CHARACTER_SELECT":
                    if event.key == pygame.K_LEFT:
                        selected_char_index = (selected_char_index - 1) % len(characters)
                    elif event.key == pygame.K_RIGHT:
                        selected_char_index = (selected_char_index + 1) % len(characters)
                    elif event.key == pygame.K_ESCAPE: 
                        game_state = "MENU"


