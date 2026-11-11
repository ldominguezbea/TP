import pygame
import sys
import os
import array
import random
import math
import json

pygame.init()

# ============================================================
# INICIALIZACIÓN SEGURA DEL AUDIO
# ============================================================

try:
    pygame.mixer.init()
    audio_disponible = True
    print("[AUDIO] Audio inicializado correctamente.")

except pygame.error as e:
    audio_disponible = False
    print(f"[AUDIO] Sin audio. El juego continuará normalmente: {e}")


from config import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, GAME_HEIGHT, BASE_DIR, abrir_archivo

import animacion_menu
from prologo import prologue
from selector_niveles import LevelSelector
from sonidos_selector_niveles import Audio
from personajes import PERSONAJE_SELECCIONADO_ENV
from pergamino_controles import ControlsScroll


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("REQUIEM: El juicio final")

clock = pygame.time.Clock()

class _Nivel1Finalizado(Exception):
    pass


# ============================================================
# SISTEMA DE AUDIO
# ============================================================

MENU_AUDIO_VOLUME = 0.45

MENU_CUE_FILES = {
    "NEW GAME": ("New_game.mp3", 0, 3500),
    "CONTINUE": ("continue.mp3", 0, 6000),
    "CONTROLS": ("Controls.mp3", 3000, 3000),
    "EXIT": ("Exit.mp3", 0, 3000),
}


# Audio alternativo por si la clase Audio no puede inicializarse.
class AudioSilencioso:

    def update_ambient(self, *args, **kwargs):
        pass


try:
    audio = Audio() if audio_disponible else AudioSilencioso()

except (pygame.error, OSError) as e:
    print(f"[AUDIO] No se pudo iniciar el sistema de audio: {e}")
    audio_disponible = False
    audio = AudioSilencioso()


navigation_sound = None


def create_navigation_sound():

    mixer_settings = pygame.mixer.get_init()

    if mixer_settings is None:
        raise RuntimeError("El mezclador de pygame no está inicializado.")

    sample_rate, sample_format, channels = mixer_settings

    if sample_format != -16:
        raise RuntimeError(
            "El sonido de navegación requiere audio PCM firmado de 16 bits."
        )

    samples = array.array("h")
    noise = random.Random(501)
    previous_sample = 0.0

    sample_count = round(sample_rate * 0.18)

    for index in range(sample_count):

        progress = index / sample_count
        cutoff = 7200 - 6100 * progress

        filter_amount = 1 - math.exp(
            -math.tau * cutoff / sample_rate
        )

        previous_sample += filter_amount * (
            noise.uniform(-1, 1) - previous_sample
        )

        attack = min(1.0, index / (sample_rate * 0.004))
        envelope = attack * (1 - progress) ** 2.4

        value = round(15000 * previous_sample * envelope)

        samples.extend([value] * channels)

    return pygame.mixer.Sound(buffer=samples.tobytes())


# Crear el sonido de navegación solamente si hay audio.
if audio_disponible:

    try:
        navigation_sound = create_navigation_sound()
        navigation_sound.set_volume(MENU_AUDIO_VOLUME)

    except (pygame.error, RuntimeError) as e:
        print(f"[AUDIO] Error creando sonido de navegación: {e}")
        audio_disponible = False
        navigation_sound = None


def make_sound_segment(sound, start_ms, duration_ms):

    mixer_settings = pygame.mixer.get_init()

    if mixer_settings is None:
        raise RuntimeError("El mezclador no está inicializado.")

    sample_rate, sample_format, channels = mixer_settings

    frame_size = (abs(sample_format) // 8) * channels

    raw = sound.get_raw()

    start_frame = round(sample_rate * start_ms / 1000)
    end_frame = round(
        sample_rate * (start_ms + duration_ms) / 1000
    )

    segment = raw[
        start_frame * frame_size:end_frame * frame_size
    ]

    if len(segment) != (end_frame - start_frame) * frame_size:
        raise ValueError("El audio no contiene la duración solicitada.")

    return pygame.mixer.Sound(buffer=segment)


def play_menu_cue(option):

    if not audio_disponible:
        return pygame.time.get_ticks(), None

    try:

        filename, offset_ms, duration_ms = MENU_CUE_FILES[option]

        sound = pygame.mixer.Sound(
            str(BASE_DIR / "musica" / filename)
        )

        if offset_ms:
            sound = make_sound_segment(
                sound,
                offset_ms,
                duration_ms
            )

        sound.set_volume(MENU_AUDIO_VOLUME)
        sound.play(maxtime=duration_ms)

        return pygame.time.get_ticks() + duration_ms, sound

    except (pygame.error, OSError, ValueError, RuntimeError) as e:

        print(f"[AUDIO] Error reproduciendo sonido del menú: {e}")

        return pygame.time.get_ticks(), None


# ============================================================
# GUARDADO DE PARTIDAS
# ============================================================

SAVE_FILE = BASE_DIR / "savegame.json"


def save_game(character_name, level_number):

    data = {
        "character": character_name,
        "level": level_number
    }

    SAVE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def load_game():

    try:
        data = json.loads(
            SAVE_FILE.read_text(encoding="utf-8")
        )

    except FileNotFoundError:
        print(f"[PARTIDA] No existe una partida guardada en {SAVE_FILE}.")
        return None

    except json.JSONDecodeError as error:
        print(f"[PARTIDA] El archivo guardado no es válido: {error}")
        return None

    valid_characters = {
        character["name"] for character in characters
    }

    if not isinstance(data, dict):
        print(f"[PARTIDA] Datos inválidos en {SAVE_FILE}.")
        return None

    character_name = data.get("character")
    level_number = data.get("level")

    if (
        not isinstance(character_name, str)
        or character_name not in valid_characters
        or type(level_number) is not int
        or level_number not in (1, 2, 3, 4, 5)
    ):

        print(f"[PARTIDA] Datos inválidos en {SAVE_FILE}.")
        return None

    return data


# ============================================================
# VARIABLES DEL JUEGO
# ============================================================

level_selector = None
chosen_level = None

level_select_overlay = pygame.Surface(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.SRCALPHA
)

level_select_overlay.fill((0, 0, 0, 155))

controls_overlay = pygame.Surface(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.SRCALPHA
)

controls_overlay.fill((0, 0, 0, 110))

controls_scroll = ControlsScroll(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    BASE_DIR / "assets" / "pergamino_controles"
)


# ============================================================
# FUENTES
# ============================================================

font_title = pygame.font.SysFont("Impact", 64)
font_menu = pygame.font.SysFont("Arial", 22, bold=True)
font_char_name = pygame.font.SysFont("Impact", 42)
font_desc = pygame.font.SysFont("Arial", 16, bold=False)
font_ui_help = pygame.font.SysFont("Arial", 18, bold=True)


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

menu_options = [
    "NEW GAME",
    "CONTINUE",
    "CONTROLS",
    "EXIT"
]

selected_option = 0
game_state = "MENU"

MENU_AUDIO_VOLUME = 0.45

assets_chars = BASE_DIR / "assets" / "sprites" / "seleccion_personajes"


# ============================================================
# PERSONAJES
# ============================================================

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

prologue_images = []
prologue_image_index = 0

menu_notice = ""
# ============================================================
# ATMÓSFERA DEL MENÚ
# ============================================================

class MenuAtmosphere:

    PARTICLE_COUNT = 180

    def __init__(self, size):

        self.width, self.height = size

        self.particle_layer = pygame.Surface(
            size,
            pygame.SRCALPHA
        )

        rng = random.Random(1604)

        self.particles = tuple(
            (
                rng.randrange(self.width),
                rng.randrange(self.height),
                rng.uniform(8.0, 28.0),
                rng.random() * math.tau,
                rng.choice((1, 1, 1, 2)),
            )
            for _ in range(self.PARTICLE_COUNT)
        )

        self.elapsed_ms = 0

    def update(self, elapsed_ms):

        self.elapsed_ms += max(0, elapsed_ms)

    def draw(self, target):

        self.particle_layer.fill((0, 0, 0, 0))

        elapsed_seconds = self.elapsed_ms / 1000

        for start_x, start_y, speed, phase, size in self.particles:

            y = round(
                (start_y - elapsed_seconds * speed)
                % (self.height + size)
            ) - size

            x = round(
                start_x
                + math.sin(elapsed_seconds * 0.35 + phase) * 5
            )

            flicker = (
                0.65
                + 0.35 * math.sin(elapsed_seconds * 1.6 + phase)
            )

            color = (
                255,
                75 + round(110 * flicker),
                18 + round(35 * flicker)
            )

            alpha = round(95 + 140 * flicker)

            pygame.draw.circle(
                self.particle_layer,
                (*color, alpha),
                (x % self.width, y),
                size,
            )

        target.blit(
            self.particle_layer,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_ADD,
        )


menu_atmosphere = MenuAtmosphere(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)


# ============================================================
# LANZAMIENTO DE NIVELES
# ============================================================

def launch_level(level_number):

    global screen, level_selector

    if level_selector is None:
        level_selector = LevelSelector(screen, audio)

    level_path = level_selector.get_level_path(level_number)

    audio.update_ambient(0.0, active=False)

    if level_path is None:

        print(
            f"[NIVEL] No se encontró el archivo del nivel {level_number}."
        )

        return False

    if level_number == 1:

        previous_cwd = os.getcwd()

        try:

            os.chdir(BASE_DIR)

            try:

                runpy.run_path(
                    str(level_path),
                    run_name="_nivel1_integrado",
                    init_globals={
                        "_Nivel1Finalizado": _Nivel1Finalizado
                    },
                )

            except _Nivel1Finalizado:
                pass

        finally:

            os.chdir(previous_cwd)

            screen = pygame.display.get_surface()

            pygame.display.set_caption(
                "REQUIEM: El juicio final"
            )

    else:

        subprocess.run(
            [sys.executable, level_path],
            cwd=BASE_DIR,
            check=False,
        )

    return True


# ============================================================
# BÚSQUEDA DE IMÁGENES
# ============================================================

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

        ruta = buscar_imagen(
            archivos_imagenes[nombre]
        )

        if ruta is None:

            print(
                f"[IMAGEN] No se encontró {archivos_imagenes[nombre]}."
            )

        else:

            try:

                img = pygame.image.load(
                    str(ruta)
                ).convert_alpha()

                w, h = img.get_size()

                esc = min(
                    caja[0] / w,
                    caja[1] / h
                )

                img = pygame.transform.scale(
                    img,
                    (int(w * esc), int(h * esc))
                )

            except pygame.error as e:

                print(
                    f"[IMAGEN] Error cargando {ruta}: {e}"
                )

                img = None

        imagenes_chars[nombre] = img

    return imagenes_chars[nombre]


# ============================================================
# TEXTO
# ============================================================

def draw_text_wrapped(
    surface,
    text,
    x,
    y,
    max_width,
    font,
    color
):

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

                text_surf = font.render(
                    current_line,
                    True,
                    color
                )

                surface.blit(
                    text_surf,
                    (x, current_y)
                )

                current_y += font.get_linesize()

                current_line = word + " "

        if current_line:

            text_surf = font.render(
                current_line,
                True,
                color
            )

            surface.blit(
                text_surf,
                (x, current_y)
            )

            current_y += font.get_linesize()


# ============================================================
# DIBUJO ALTERNATIVO DE PERSONAJES
# ============================================================

def draw_character_artwork(surface, name, cx, cy):

    if name == "Fei Liang":

        pygame.draw.rect(
            surface,
            (45, 40, 42),
            (cx - 40, cy - 10, 80, 70),
            border_radius=5
        )

        pygame.draw.circle(
            surface,
            (235, 225, 215),
            (cx, cy - 25),
            32
        )

    elif name == "Korg":

        pygame.draw.rect(
            surface,
            (70, 50, 45),
            (cx - 40, cy - 10, 80, 70),
            border_radius=5
        )

        pygame.draw.circle(
            surface,
            (240, 185, 145),
            (cx, cy - 25),
            28
        )

    elif name == "Diana":

        pygame.draw.rect(
            surface,
            (25, 65, 40),
            (cx - 45, cy - 15, 90, 75),
            border_radius=8
        )

        pygame.draw.circle(
            surface,
            (245, 245, 250),
            (cx, cy - 22),
            30
        )

    elif name == "Escanor":

        pygame.draw.rect(
            surface,
            (165, 25, 25),
            (cx - 50, cy - 5, 100, 65),
            border_radius=10
        )

        pygame.draw.circle(
            surface,
            (240, 190, 145),
            (cx, cy - 28),
            26
        )


# ============================================================
# DIBUJO DEL MENÚ
# ============================================================

def render_menu(time_counter):

    mouse_x, mouse_y = pygame.mouse.get_pos()

    parallax_x = (
        mouse_x / SCREEN_WIDTH - 0.5
    ) * 2

    parallax_y = (
        mouse_y / SCREEN_HEIGHT - 0.5
    ) * 2

    animacion_menu.draw_scenery(
        canvas,
        time_counter,
        (parallax_x, parallax_y)
    )

    pygame.transform.scale(
        canvas,
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        screen
    )

    menu_atmosphere.draw(screen)

    title_surf = font_title.render(
        "REQUIEM",
        True,
        (230, 40, 40)
    )

    screen.blit(
        title_surf,
        (80, 60)
    )

    sub_surf = font_menu.render(
        "EL JUICIO FINAL",
        True,
        (235, 185, 40)
    )

    screen.blit(
        sub_surf,
        (84, 135)
    )

    for i, option in enumerate(menu_options):

        activa = i == selected_option

        color = (
            (255, 255, 255)
            if activa
            else (150, 130, 130)
        )

        texto = (
            "> " if activa else "  "
        ) + option

        position = (
            84,
            230 + i * 42
        )

        if activa:

            flicker = (
                0.65
                + 0.35 * math.sin(time_counter * 31)
            )

            glow = font_menu.render(
                texto,
                True,
                (255, 0, 0)
            )

            glow.set_alpha(
                round(120 + 100 * flicker)
            )

            jitter = (
                2
                if math.sin(time_counter * 47) > 0.94
                else 0
            )

            for dx, dy in (
                (-2, 0),
                (2, 0),
                (0, -2),
                (0, 2)
            ):

                screen.blit(
                    glow,
                    (
                        position[0] + dx + jitter,
                        position[1] + dy
                    )
                )

            color = (
                255,
                round(80 + 120 * flicker),
                round(60 + 100 * flicker)
            )

        surf = font_menu.render(
            texto,
            True,
            color
        )

        screen.blit(
            surf,
            position
        )

    if chosen_char_name:

        info = font_ui_help.render(
            f"Héroe elegido: {chosen_char_name}",
            True,
            (235, 185, 40)
        )

        screen.blit(
            info,
            (84, SCREEN_HEIGHT - 60)
        )

    if menu_notice:

        notice_surf = font_ui_help.render(
            menu_notice,
            True,
            (255, 125, 90)
        )

        screen.blit(
            notice_surf,
            (84, SCREEN_HEIGHT - 32)
        )


# ============================================================
# PANTALLA DE CONTROLES
# ============================================================

def render_controls(time_counter):

    render_menu(time_counter)

    screen.blit(
        controls_overlay,
        (0, 0)
    )

    controls_scroll.draw(screen)


# ============================================================
# PRÓLOGO
# ============================================================

def render_prologue():

    screen.blit(
        prologue_images[prologue_image_index],
        (0, 0)
    )


# ============================================================
# SELECCIÓN DE NIVELES
# ============================================================

def render_level_select(time_counter):

    animacion_menu.draw_scenery(
        canvas,
        time_counter
    )

    pygame.transform.scale(
        canvas,
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        screen
    )

    screen.blit(
        level_select_overlay,
        (0, 0)
    )

    level_selector.draw(
        pygame.time.get_ticks()
    )


# ============================================================
# SELECCIÓN DE PERSONAJES
# ============================================================

def render_character_select_high_res(time_counter):

    """Función de renderizado de la selección de personaje."""

    screen.fill((14, 11, 18))

    char = characters[selected_char_index]

    if char["file"] not in archivos_ya_abiertos:
        archivos_ya_abiertos.add(char["file"])

    title_surf = font_title.render(
        "SELECCIONA TU HÉROE",
        True,
        (230, 40, 40)
    )

    screen.blit(
        title_surf,
        (
            SCREEN_WIDTH // 2 - title_surf.get_width() // 2,
            40
        )
    )

    box_width, box_height = 320, 320

    box_x = 180
    box_y = 180

    preview_box = pygame.Rect(
        box_x,
        box_y,
        box_width,
        box_height
    )

    pygame.draw.rect(
        screen,
        (24, 19, 28),
        preview_box
    )

    pygame.draw.rect(
        screen,
        char["color"],
        preview_box,
        3,
        border_radius=8
    )

    center_x = box_x + box_width // 2
    center_y = box_y + box_height // 2

    img = obtener_imagen_personaje(char)

    if img:

        screen.blit(
            img,
            img.get_rect(
                center=(center_x, center_y)
            )
        )

    else:

        draw_character_artwork(
            screen,
            char["name"],
            center_x,
            center_y
        )

    name_surf = font_char_name.render(
        char["name"],
        True,
        (255, 255, 255)
    )

    screen.blit(
        name_surf,
        (
            box_x + box_width // 2 - name_surf.get_width() // 2,
            box_y + box_height + 20
        )
    )

    arrow_pulse = int(
        math.sin(time_counter * 5) * 6
    )

    arrow_l = font_title.render(
        "<",
        True,
        (235, 185, 40)
    )

    arrow_r = font_title.render(
        ">",
        True,
        (235, 185, 40)
    )

    screen.blit(
        arrow_l,
        (
            box_x - 70 - arrow_pulse,
            box_y + box_height // 2 - 40
        )
    )

    screen.blit(
        arrow_r,
        (
            box_x + box_width + 45 + arrow_pulse,
            box_y + box_height // 2 - 40
        )
    )

    desc_x = 590
    desc_y = 185
    desc_width = 600

    header_desc = font_menu.render(
        "BIOGRAFÍA Y ESTILO DE COMBATE",
        True,
        char["color"]
    )

    screen.blit(
        header_desc,
        (desc_x, desc_y)
    )

    pygame.draw.line(
        screen,
        (60, 50, 70),
        (desc_x, desc_y + 35),
        (desc_x + desc_width, desc_y + 35),
        2
    )

    draw_text_wrapped(
        screen,
        char["desc"],
        desc_x,
        desc_y + 55,
        desc_width,
        font_desc,
        (220, 220, 225)
    )

    help_surf = font_ui_help.render(
        "[ENTER] CONFIRMAR HÉROE   |   [ESC] VOLVER AL MENÚ",
        True,
        (130, 130, 140)
    )

    screen.blit(
        help_surf,
        (
            SCREEN_WIDTH // 2 - help_surf.get_width() // 2,
            SCREEN_HEIGHT - 65
        )
    )
# ============================================================
# BUCLE PRINCIPAL DEL JUEGO
# ============================================================

def main():

    global screen
    global selected_option
    global game_state
    global selected_char_index
    global chosen_char_name
    global prologue_images
    global prologue_image_index
    global level_selector
    global chosen_level
    global menu_notice
    global audio_disponible

    time_counter = 0

    running = True
    enter_held = False

    menu_music_playing = False
    pending_menu_action = None

    game_state = "MENU"

    while running:

        elapsed_ms = clock.tick(60)

        time_counter += 0.05

        # ====================================================
        # EVENTOS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYUP:

                if event.key == pygame.K_RETURN:
                    enter_held = False

            elif event.type == pygame.KEYDOWN:

                fresh_enter = (
                    event.key == pygame.K_RETURN
                    and not enter_held
                )

                if event.key == pygame.K_RETURN:
                    enter_held = True

                # ============================================
                # MENÚ PRINCIPAL
                # ============================================

                if game_state == "MENU" and pending_menu_action is None:

                    if event.key == pygame.K_UP:

                        selected_option = (
                            selected_option - 1
                        ) % len(menu_options)

                        if audio_disponible and navigation_sound is not None:
                            navigation_sound.play()

                    elif event.key == pygame.K_DOWN:

                        selected_option = (
                            selected_option + 1
                        ) % len(menu_options)

                        if audio_disponible and navigation_sound is not None:
                            navigation_sound.play()

                    elif event.key == pygame.K_RETURN and fresh_enter:

                        option = menu_options[selected_option]

                        deadline, cue_sound = play_menu_cue(option)

                        pending_menu_action = (
                            option,
                            deadline,
                            cue_sound
                        )

                # ============================================
                # CONTROLES
                # ============================================

                elif game_state == "CONTROLS":

                    if event.key == pygame.K_RETURN and fresh_enter:
                        controls_scroll.handle_enter()

                # ============================================
                # PRÓLOGO
                # ============================================

                elif game_state == "PROLOGUE":

                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE
                    ):

                        if prologue_image_index < len(prologue_images) - 1:

                            prologue_image_index += 1

                        else:

                            game_state = "CHARACTER_SELECT"

                    elif event.key == pygame.K_ESCAPE:

                        game_state = "MENU"

                # ============================================
                # SELECCIÓN DE PERSONAJES
                # ============================================

                elif game_state == "CHARACTER_SELECT":

                    if event.key == pygame.K_LEFT:

                        selected_char_index = (
                            selected_char_index - 1
                        ) % len(characters)

                    elif event.key == pygame.K_RIGHT:

                        selected_char_index = (
                            selected_char_index + 1
                        ) % len(characters)

                    elif event.key == pygame.K_RETURN:

                        chosen_char_name = characters[
                            selected_char_index
                        ]["name"]

                        os.environ[
                            PERSONAJE_SELECCIONADO_ENV
                        ] = chosen_char_name

                        chosen_level = None

                        level_selector = LevelSelector(
                            screen,
                            audio
                        )

                        game_state = "LEVEL_SELECT"

                    elif event.key == pygame.K_ESCAPE:

                        game_state = "MENU"

                # ============================================
                # SELECCIÓN DE NIVELES
                # ============================================

                elif game_state == "LEVEL_SELECT":

                    result = level_selector.handle_event(event)

                    if result == "back":

                        audio.update_ambient(
                            0.0,
                            active=False
                        )

                        game_state = "CHARACTER_SELECT"

                    elif isinstance(result, int):

                        chosen_level = result

                        save_game(
                            chosen_char_name,
                            chosen_level
                        )

                        launch_level(chosen_level)

                        chosen_level = None

        # ====================================================
        # EJECUTAR ACCIONES DEL MENÚ
        # ====================================================

        if (
            pending_menu_action is not None
            and pygame.time.get_ticks() >= pending_menu_action[1]
        ):

            option, _, _cue_sound = pending_menu_action

            pending_menu_action = None

            # ================================================
            # NEW GAME
            # ================================================

            if option == "NEW GAME":

                prologue_images = prologue()

                prologue_image_index = 0

                game_state = "PROLOGUE"

                menu_notice = ""

            # ================================================
            # CONTINUE
            # ================================================

            elif option == "CONTINUE":

                saved_game = load_game()

                if saved_game is None:

                    menu_notice = "No hay una partida guardada válida."

                else:

                    chosen_char_name = saved_game["character"]

                    selected_char_index = next(
                        index
                        for index, character in enumerate(characters)
                        if character["name"] == chosen_char_name
                    )

                    os.environ[
                        PERSONAJE_SELECCIONADO_ENV
                    ] = chosen_char_name

                    chosen_level = saved_game["level"]

                    level_selector = LevelSelector(
                        screen,
                        audio
                    )

                    if level_selector.get_level_path(chosen_level) is None:

                        menu_notice = (
                            "El nivel guardado ya no está disponible."
                        )

                    else:

                        if menu_music_playing:

                            if audio_disponible:
                                try:
                                    pygame.mixer.music.stop()
                                except pygame.error:
                                    audio_disponible = False

                            menu_music_playing = False

                        game_state = "LEVEL_SELECT"

                        launch_level(chosen_level)

                        chosen_level = None

                        menu_notice = ""

            # ================================================
            # CONTROLS
            # ================================================

            elif option == "CONTROLS":

                controls_scroll.reset()

                game_state = "CONTROLS"

                menu_notice = ""

            # ================================================
            # EXIT
            # ================================================

            elif option == "EXIT":

                running = False

        # ====================================================
        # ACTUALIZACIÓN DE ESTADOS
        # ====================================================

        if game_state == "LEVEL_SELECT":

            level_selector.update(elapsed_ms)

        elif game_state == "CONTROLS":

            if controls_scroll.update(elapsed_ms / 1000):
                game_state = "MENU"

        # ====================================================
        # ACTUALIZACIÓN DE PARTÍCULAS
        # ====================================================

        if game_state in ("MENU", "CONTROLS"):

            menu_atmosphere.update(elapsed_ms)

        # ====================================================
        # MÚSICA DEL MENÚ
        # ====================================================

        if game_state == "MENU" and not menu_music_playing:

            if audio_disponible:

                try:

                    pygame.mixer.music.load(
                        str(BASE_DIR / "musica" / "Menu_theme.mp3")
                    )

                    pygame.mixer.music.set_volume(
                        MENU_AUDIO_VOLUME
                    )

                    pygame.mixer.music.play(-1)

                    menu_music_playing = True

                except (pygame.error, OSError) as e:

                    print(
                        f"[AUDIO] No se pudo reproducir la música: {e}"
                    )

                    audio_disponible = False

                    menu_music_playing = False

        elif game_state != "MENU" and menu_music_playing:

            if audio_disponible:

                try:
                    pygame.mixer.music.stop()

                except pygame.error as e:

                    print(f"[AUDIO] Error deteniendo la música: {e}")

                    audio_disponible = False

            menu_music_playing = False

        # ====================================================
        # DIBUJO
        # ====================================================

        if game_state == "MENU":

            render_menu(time_counter)

        elif game_state == "CONTROLS":

            render_controls(time_counter)

        elif game_state == "PROLOGUE":

            render_prologue()

        elif game_state == "CHARACTER_SELECT":

            render_character_select_high_res(time_counter)

        elif game_state == "LEVEL_SELECT":

            render_level_select(time_counter)

        pygame.display.flip()

    # ========================================================
    # CIERRE DEL JUEGO
    # ========================================================

    pygame.quit()
    sys.exit()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()