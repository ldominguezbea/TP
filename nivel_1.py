import os
import sys
import random
import pygame

from enemigos import (
    OrcoRojo,
    OjoVolador,
    Karasu_tengu,
    cargar_spritesheet_jokai,
)
from personajes import crear_jugador
from menu_pausa import (
    RETURN_TO_MENU_EXIT_CODE,
    NivelIntegradoFinalizado,
    menu_muerte_juego,
    pausar_juego,
)

pygame.init()
pygame.font.init()

NIVEL_INTEGRADO = __name__ == "_nivel1_integrado"
accion_cierre_nivel = None
nivel_completado = False
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_MUSICA_PERSECUCION = os.path.join(
    BASE_DIR,
    "musica",
    "when_the_shadows_first_lengthened.ogg",
)
musica_persecucion_activa = False

# 1. Configuración de pantalla y mundo
ANCHO, ALTO = 1350, 700
POSICION_SUELO = 620
ORDEN_FONDOS_NIVEL = (1, 4, 5, 6, 7, 8, 9, 10)

# Recorrido lateral inicial hasta la entrada de la biblioteca.
CANTIDAD_FONDOS = len(ORDEN_FONDOS_NIVEL)
ANCHO_MUNDO = ANCHO * CANTIDAD_FONDOS + 500
PORTAL_X = ANCHO_MUNDO - 500
HUECO_INICIO = PORTAL_X - 150
HUECO_FIN = PORTAL_X + 150
ZONA_BIBLIOTECA_X = ANCHO * 3 + int(ANCHO * 0.75)
RADIO_INTERACCION_FONDO = 100
PUERTA_ESCENA_X = ANCHO - 130
VENTILACION_X = int(ANCHO * 0.48)
HUECO_FINAL_X = ANCHO - 130
ESCALA_ORCO_NIVEL = 1.5
VELOCIDAD_PERSEGUIDOR = 420
VELOCIDAD_ANIM_MONSTRUO = 8
DISTANCIA_CONTACTO_MONSTRUO = 80

FASE_RECORRIDO = "RECORRIDO"
FASE_BIBLIOTECA_7 = "BIBLIOTECA_7"
FASE_BIBLIOTECA_9 = "BIBLIOTECA_9"
FASE_PASILLO_HOSPITAL = "PASILLO_HOSPITAL"
FASE_HOSPITAL_11 = "HOSPITAL_11"
FASE_CONDUCTO_1 = "CONDUCTO_1"
FASE_CONDUCTO_2 = "CONDUCTO_2"
FASE_CONDUCTO_3 = "CONDUCTO_3"
FASE_HUECO_FINAL = "HUECO_FINAL"
FASES_CONDUCTO = (
    FASE_CONDUCTO_1,
    FASE_CONDUCTO_2,
    FASE_CONDUCTO_3,
)
PLATAFORMAS_ESCENA = {
    FASE_BIBLIOTECA_7: [
        pygame.Rect(300, 505, 230, 18),
        pygame.Rect(760, 455, 230, 18),
        pygame.Rect(1080, 515, 190, 18),
    ],
    FASE_BIBLIOTECA_9: [
        pygame.Rect(250, 510, 220, 18),
        pygame.Rect(650, 455, 230, 18),
        pygame.Rect(1010, 500, 220, 18),
    ],
    FASE_PASILLO_HOSPITAL: [
        pygame.Rect(330, 510, 230, 18),
        pygame.Rect(800, 465, 230, 18),
    ],
}

TRAZADOS_CONDUCTOS = {
    FASE_CONDUCTO_1: (
        (0.0, 0.688),
        (0.20, 0.688),
        (0.25, 0.667),
        (0.30, 0.486),
        (0.35, 0.378),
        (0.50, 0.378),
        (0.55, 0.395),
        (0.60, 0.582),
        (0.65, 0.755),
        (1.0, 0.755),
    ),
    FASE_CONDUCTO_2: (
        (0.0, 0.706),
        (0.40, 0.706),
        (0.45, 0.592),
        (0.50, 0.431),
        (0.55, 0.369),
        (1.0, 0.369),
    ),
    FASE_CONDUCTO_3: (
        (0.0, 0.296),
        (0.35, 0.296),
        (0.40, 0.425),
        (0.45, 0.620),
        (0.50, 0.806),
        (1.0, 0.806),
    ),
}

pantalla = pygame.display.get_surface()
if pantalla is None:
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 1 - Batalla de Jefe")


def iniciar_musica_persecucion():
    global musica_persecucion_activa

    if musica_persecucion_activa or pygame.mixer.get_init() is None:
        return
    try:
        pygame.mixer.music.load(RUTA_MUSICA_PERSECUCION)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1, fade_ms=800)
        musica_persecucion_activa = True
    except (pygame.error, OSError) as error:
        print(f"[AUDIO] No se pudo iniciar la música de persecución: {error}")


def detener_musica_persecucion():
    global musica_persecucion_activa

    if not musica_persecucion_activa:
        return
    if pygame.mixer.get_init() is not None:
        pygame.mixer.music.fadeout(800)
    musica_persecucion_activa = False


def cerrar_nivel(action=None):
    detener_musica_persecucion()
    if NIVEL_INTEGRADO:
        if action is not None:
            raise NivelIntegradoFinalizado(nivel_completado, action)
        raise NivelIntegradoFinalizado(nivel_completado)
    if action == "retry":
        pygame.quit()
        os.execv(
            sys.executable,
            [sys.executable, os.path.abspath(__file__), *sys.argv[1:]],
        )
    if action == "menu":
        raise SystemExit(RETURN_TO_MENU_EXIT_CODE)
    if action == "exit":
        pygame.quit()
        raise SystemExit(0)
    pygame.quit()
    sys.exit()


def solicitar_cierre_nivel(action):
    if NIVEL_INTEGRADO:
        global accion_cierre_nivel
        accion_cierre_nivel = action
        return
    cerrar_nivel(action)


def muerte_terminada(jugador):
    return getattr(jugador, "muerto", False) and (
        getattr(jugador, "muerte_terminada", False)
        or not jugador.alive()
    )


def mostrar_menu_muerte(screen):
    accion = menu_muerte_juego(screen, devolver_accion=True)
    solicitar_cierre_nivel(accion)
    return accion


# Tamaño del sprite ajustado a escala humana
ANCHO_HEROE, ALTO_HEROE = 300, 300

# Fuentes
fuente_lava_pixel = pygame.font.SysFont("Courier", 9, bold=True)
fuente_boss_title = pygame.font.SysFont("Georgia", 76, bold=True)
fuente_boss_subtitle = pygame.font.SysFont("Georgia", 32, italic=True)
fuente_jefe = pygame.font.SysFont("Georgia", 26, bold=True, italic=True)
fuente_ui = pygame.font.SysFont("Arial", 16, bold=True)
fuente_progreso = pygame.font.SysFont("Impact", 22)


# ==============================================================================
# CARGA DE IMÁGENES Y CÓMICS
# ==============================================================================
def ajustar_imagen_a_pantalla(imagen, tamano_pantalla):
    ancho, alto = tamano_pantalla
    ancho_imagen, alto_imagen = imagen.get_size()
    escala_imagen = min(ancho / ancho_imagen, alto / alto_imagen)
    tamano_ajustado = (
        max(1, round(ancho_imagen * escala_imagen)),
        max(1, round(alto_imagen * escala_imagen)),
    )
    imagen_ajustada = pygame.transform.smoothscale(imagen, tamano_ajustado)
    fondo = pygame.transform.smoothscale(imagen_ajustada, tamano_pantalla)
    tamano_desenfoque = (max(1, ancho // 18), max(1, alto // 18))
    fondo = pygame.transform.smoothscale(
        pygame.transform.smoothscale(fondo, tamano_desenfoque),
        tamano_pantalla,
    )
    velo = pygame.Surface(tamano_pantalla, pygame.SRCALPHA)
    velo.fill((0, 0, 0, 90))
    fondo.blit(velo, (0, 0))

    fondo.blit(
        imagen_ajustada,
        imagen_ajustada.get_rect(center=(ancho // 2, alto // 2)),
    )
    return fondo


def ajustar_fondo_a_pantalla(imagen, tamano_pantalla):
    return pygame.transform.scale(imagen, tamano_pantalla)


def cargar_imagen_comic(nombre_archivo, tamano_pantalla=None):
    if tamano_pantalla is None:
        tamano_pantalla = pantalla.get_size()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rutas = [
        os.path.join(base_dir, "imagenes", "Nivel1", nombre_archivo),
        os.path.join("imagenes", "Nivel1", nombre_archivo),
        os.path.join(base_dir, "assets", "imagenes", "Nivel1", nombre_archivo),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            try:
                img = pygame.image.load(ruta).convert_alpha()
                return ajustar_imagen_a_pantalla(img, tamano_pantalla)
            except (OSError, pygame.error) as e:
                print(f"Error al cargar {ruta}: {e}")

    surf = pygame.Surface(tamano_pantalla)
    surf.fill((15, 15, 20))
    txt = fuente_boss_subtitle.render(f"[{nombre_archivo} no encontrado]", True, (255, 255, 255))
    surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
    return surf


def mostrar_comic_inicio(screen):
    imagen = cargar_imagen_comic("comic_inicio.png", screen.get_size())
    instruccion = fuente_ui.render(
        "PRESIONA ENTER PARA COMENZAR", True, (255, 255, 255)
    )
    reloj = pygame.time.Clock()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cerrar_nivel("exit")

    while True:
        screen.blit(imagen, (0, 0))
        rect_instruccion = instruccion.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 30)
        )
        sombra = pygame.Surface(
            (rect_instruccion.width + 24, rect_instruccion.height + 12),
            pygame.SRCALPHA,
        )
        sombra.fill((0, 0, 0, 175))
        screen.blit(sombra, sombra.get_rect(center=rect_instruccion.center))
        screen.blit(instruccion, rect_instruccion)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cerrar_nivel("exit")
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
            ):
                return
        reloj.tick(60)


def mostrar_comic_final(screen):
    img_final = cargar_imagen_comic("comic_final.png", screen.get_size())
    reloj = pygame.time.Clock()
    esperando = True

    while esperando:
        screen.blit(img_final, (0, 0))

        lbl_fin = fuente_ui.render(
            "FIN DEL NIVEL 1 - Presiona cualquier tecla para continuar",
            True,
            (255, 255, 255),
        )
        rect_txt = lbl_fin.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 35)
        )
        sombra_bg = pygame.Surface((rect_txt.width + 20, rect_txt.height + 10))
        sombra_bg.fill((0, 0, 0))
        sombra_bg.set_alpha(180)

        screen.blit(sombra_bg, (rect_txt.x - 10, rect_txt.y - 5))
        screen.blit(lbl_fin, rect_txt)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cerrar_nivel("exit")
            if event.type == pygame.KEYDOWN:
                esperando = False
        reloj.tick(60)


def buscar_y_cargar_barra(nombre_archivo):
    dir_actual = os.path.dirname(os.path.abspath(__file__))

    for _ in range(4):
        posible_ruta = os.path.join(dir_actual, "assets", "barras de vida", nombre_archivo)
        if os.path.exists(posible_ruta):
            try:
                img = pygame.image.load(posible_ruta).convert_alpha()
                return img
            except Exception as e:
                print(f"Error al cargar {posible_ruta}: {e}")
        dir_actual = os.path.dirname(dir_actual)

    ruta_relativa = os.path.join("assets", "barras de vida", nombre_archivo)
    if os.path.exists(ruta_relativa):
        try:
            img = pygame.image.load(ruta_relativa).convert_alpha()
            return img
        except Exception as e:
            print(f"Error al cargar {ruta_relativa}: {e}")

    return None


IMG_SUN_SPIRIT = buscar_y_cargar_barra("sun_spirit.png")
IMG_BARRA_JUGADOR = buscar_y_cargar_barra("Barra_de_vida_jugador.png")

def cargar_fondo_nivel1(numero):
    nombres = [f"Nivel1_imagen{numero}.png"]
    if numero == 10:
        nombres.append("Nivel_1imagen10.png")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    carpetas = (
        os.path.join(base_dir, "imagenes", "Nivel1"),
        os.path.join(base_dir, "assets", "imagenes", "Nivel1"),
    )
    for carpeta in carpetas:
        for nombre in nombres:
            ruta = os.path.join(carpeta, nombre)
            if os.path.exists(ruta):
                img = pygame.image.load(ruta).convert()
                return ajustar_fondo_a_pantalla(img, pantalla.get_size())

    surf = pygame.Surface(pantalla.get_size())
    surf.fill((20, 15, 25))
    return surf


def cargar_fondo_archivo(nombre_archivo):
    ruta = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "imagenes",
        "Nivel1",
        nombre_archivo,
    )
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró el fondo del nivel: {ruta}")
    img = pygame.image.load(ruta).convert()
    return ajustar_fondo_a_pantalla(img, pantalla.get_size())


def cargar_frames_monstruo_carne(altura, nombres):
    carpeta = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "assets",
        "enemigos",
        "Monstruo_carne",
    )
    if not os.path.isdir(carpeta):
        raise FileNotFoundError(f"No se encontraron los sprites del monstruo: {carpeta}")

    frames = []
    for nombre in nombres:
        ruta = os.path.join(carpeta, nombre)
        if not os.path.isfile(ruta):
            raise FileNotFoundError(f"No se encontró un frame del monstruo: {ruta}")
        imagen = pygame.image.load(ruta).convert_alpha()
        bounds = imagen.get_bounding_rect()
        if bounds.width and bounds.height:
            imagen = imagen.subsurface(bounds).copy()
        factor = altura / imagen.get_height()
        frames.append(
            pygame.transform.scale(
                imagen,
                (max(1, round(imagen.get_width() * factor)), altura),
            )
        )
    return frames


def colocar_jugador_en_escena(jugador, x, fase):
    jugador.pos_x = float(x)
    jugador.posicion_suelo = POSICION_SUELO
    jugador.velocidad_x = 0
    jugador.velocidad_y = 0
    jugador.scroll_x_actual = 0
    jugador.plataformas = PLATAFORMAS_ESCENA.get(fase, [])
    jugador.plataforma_actual = None
    jugador.plataforma_ignorada = None
    jugador.rect.centerx = round(x)
    jugador.rect.bottom = POSICION_SUELO
    jugador.en_suelo = True
    jugador.actualizar_hitboxes()


def obtener_suelo_conducto(fase, x):
    progreso = max(0.0, min(1.0, x / ANCHO))
    puntos = TRAZADOS_CONDUCTOS[fase]
    for (x1, y1), (x2, y2) in zip(puntos, puntos[1:]):
        if progreso <= x2:
            tramo = (progreso - x1) / (x2 - x1)
            return round((y1 + (y2 - y1) * tramo) * ALTO)
    return round(puntos[-1][1] * ALTO)


def obtener_limite_derecho(fase):
    limites = {
        FASE_RECORRIDO: ZONA_BIBLIOTECA_X,
        FASE_BIBLIOTECA_7: ANCHO - 80,
        FASE_BIBLIOTECA_9: PUERTA_ESCENA_X,
        FASE_PASILLO_HOSPITAL: int(ANCHO * 0.79),
        FASE_HOSPITAL_11: VENTILACION_X,
        FASE_CONDUCTO_1: ANCHO - 80,
        FASE_CONDUCTO_2: ANCHO - 80,
        FASE_CONDUCTO_3: ANCHO - 80,
        FASE_HUECO_FINAL: HUECO_FINAL_X,
    }
    return limites[fase]


PROGRESO_POR_FASE = {
    FASE_RECORRIDO: (0, 40, 100),
    FASE_BIBLIOTECA_7: (40, 48, 180),
    FASE_BIBLIOTECA_9: (48, 56, 100),
    FASE_PASILLO_HOSPITAL: (56, 63, 180),
    FASE_HOSPITAL_11: (63, 67, 180),
    FASE_CONDUCTO_1: (67, 75, 110),
    FASE_CONDUCTO_2: (75, 83, 100),
    FASE_CONDUCTO_3: (83, 91, 100),
    FASE_HUECO_FINAL: (91, 99, 180),
}


def calcular_progreso_nivel(fase, x):
    inicio_porcentaje, fin_porcentaje, inicio_x = PROGRESO_POR_FASE[fase]
    limite_x = obtener_limite_derecho(fase)
    distancia = max(1, limite_x - inicio_x)
    avance = max(0.0, min(1.0, (x - inicio_x) / distancia))
    porcentaje_fase = inicio_porcentaje + int(
        avance * (fin_porcentaje - inicio_porcentaje)
    )
    return min(99, porcentaje_fase)


def requiere_interaccion(fase, x):
    if fase == FASE_RECORRIDO:
        return abs(x - ZONA_BIBLIOTECA_X) <= RADIO_INTERACCION_FONDO
    if fase == FASE_HOSPITAL_11:
        return abs(x - VENTILACION_X) <= 90
    if fase in (
        FASE_BIBLIOTECA_9,
        FASE_PASILLO_HOSPITAL,
        FASE_CONDUCTO_3,
        FASE_HUECO_FINAL,
    ):
        return x >= obtener_limite_derecho(fase) - 90
    return False


# 2. Carga de fondos
fondos = [cargar_fondo_nivel1(numero) for numero in ORDEN_FONDOS_NIVEL]
fondo_batalla = cargar_fondo_nivel1(3)
fondos_escena = {
    FASE_BIBLIOTECA_7: fondos[4],
    FASE_BIBLIOTECA_9: fondos[6],
    FASE_PASILLO_HOSPITAL: cargar_fondo_archivo(
        "Pasillo de hospital en llamas.png"
    ),
    FASE_HOSPITAL_11: cargar_fondo_nivel1(11),
    FASE_CONDUCTO_1: cargar_fondo_archivo("Conducto1.png"),
    FASE_CONDUCTO_2: cargar_fondo_archivo("Conducto2.png"),
    FASE_CONDUCTO_3: cargar_fondo_archivo("Conducto3.png"),
    FASE_HUECO_FINAL: cargar_fondo_nivel1(2),
}
frames_monstruo_carne = cargar_frames_monstruo_carne(
    70,
    (
        "Monstruo de carne.png",
        "Monstruo de carne2.png",
        "Monstruo de carne3.png",
    ),
)
mostrar_comic_inicio(pantalla)


# 3. Clase para el Jugador (P_viento)
class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animaciones = {
            'idle': [], 'run': [], 'roll': [], 'j_up': [], 'j_down': [],
            'defend': [], '1_atk': [], '2_atk': [], '3_atk': [],
            'air_atk': [], 'sp_atk': []
        }
        self.cargar_animaciones()

        self.estado = 'idle'
        self.frame_index = 0
        self.velocidad_animacion = 0.22

        self.image = self.animaciones[self.estado][self.frame_index]
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.pos_x = float(x)

        # Atributos de combate y vida
        self.health = 100
        self.max_health = 100
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.hurtbox = pygame.Rect(0, 0, 0, 0)
        self.has_hit = False

        # Física y movimiento
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.velocidad_movimiento = 7
        self.fuerza_salto = -16
        self.gravedad = 0.8
        self.plataformas = []
        self.scroll_x_actual = 0
        self.plataforma_actual = None
        self.plataforma_ignorada = None

        # Estados de acción
        self.mirando_derecha = True
        self.en_suelo = True
        self.rodando = False
        self.defendiendo = False
        self.atacando = False
        self.combo_siguiente = False

    def cargar_animaciones(self):
        ESCALA = (ANCHO_HEROE, ALTO_HEROE)
        base_path = os.path.join("assets", "Heroes", "P_viento")

        def cargar_secuencia(carpeta, total, omitir=None):
            if omitir is None:
                omitir = []
            imgs = []
            for i in range(1, total + 1):
                if i in omitir:
                    continue
                ruta = os.path.join(base_path, carpeta, f"{carpeta}_{i}.png")
                if os.path.exists(ruta):
                    img = pygame.image.load(ruta).convert_alpha()
                    imgs.append(pygame.transform.scale(img, ESCALA))
            if not imgs:
                s = pygame.Surface(ESCALA, pygame.SRCALPHA)
                s.fill((0, 150, 255, 180))
                imgs.append(s)
            return imgs

        self.animaciones['idle'] = cargar_secuencia("idle", 8)
        self.animaciones['run'] = cargar_secuencia("run", 8)
        self.animaciones['roll'] = cargar_secuencia("roll", 6)
        self.animaciones['j_up'] = cargar_secuencia("j_up", 3)
        self.animaciones['j_down'] = cargar_secuencia("j_down", 3)
        self.animaciones['defend'] = cargar_secuencia("defend", 8)
        self.animaciones['1_atk'] = cargar_secuencia("1_atk", 8, omitir=[6, 7, 8])
        self.animaciones['2_atk'] = cargar_secuencia("2_atk", 18, omitir=[14, 15, 16, 17, 18])
        self.animaciones['3_atk'] = cargar_secuencia("3_atk", 27)
        self.animaciones['air_atk'] = cargar_secuencia("air_atk", 7)
        self.animaciones['sp_atk'] = cargar_secuencia("sp_atk", 30)

    def procesar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_s and self.plataforma_actual is not None:
                self.plataforma_ignorada = self.plataforma_actual
                self.plataforma_actual = None
                self.en_suelo = False
                self.velocidad_y = max(2, self.gravedad)

            elif evento.key == pygame.K_w and self.en_suelo and not (self.rodando or self.defendiendo):
                if self.atacando and self.estado != 'sp_atk':
                    self.atacando = False
                self.velocidad_y = self.fuerza_salto
                self.en_suelo = False

            elif evento.key == pygame.K_q and self.en_suelo and not (self.rodando or self.defendiendo):
                if self.atacando and self.estado != 'sp_atk':
                    self.atacando = False
                self.rodando = True
                self.frame_index = 0

            elif evento.key == pygame.K_r and self.en_suelo and not (self.rodando or self.defendiendo):
                if self.atacando and self.estado != 'sp_atk':
                    self.atacando = False
                self.defendiendo = True
                self.frame_index = 0

            elif evento.key == pygame.K_e and self.en_suelo and not (self.rodando or self.defendiendo):
                self.atacando = True
                self.has_hit = False
                self.estado = 'sp_atk'
                self.frame_index = 0

            elif evento.key == pygame.K_f:
                if not self.en_suelo and not self.atacando:
                    self.atacando = True
                    self.has_hit = False
                    self.estado = 'air_atk'
                    self.frame_index = 0

                elif self.en_suelo and not (self.rodando or self.defendiendo):
                    if not self.atacando:
                        self.atacando = True
                        self.has_hit = False
                        self.estado = '1_atk'
                        self.frame_index = 0
                        self.combo_siguiente = False
                    elif self.estado in ['1_atk', '2_atk']:
                        self.combo_siguiente = True

    def manejar_movimiento_continuo(self):
        teclas = pygame.key.get_pressed()

        if self.rodando or self.defendiendo:
            self.velocidad_x = 0
            return

        self.velocidad_x = 0

        if teclas[pygame.K_a]:
            self.velocidad_x = -self.velocidad_movimiento
            self.mirando_derecha = False
            if self.atacando and self.estado != 'sp_atk':
                self.atacando = False

        if teclas[pygame.K_d]:
            self.velocidad_x = self.velocidad_movimiento
            self.mirando_derecha = True
            if self.atacando and self.estado != 'sp_atk':
                self.atacando = False

    def actualizar_estado(self):
        if self.rodando:
            self.estado = 'roll'
        elif self.defendiendo:
            self.estado = 'defend'
        elif self.atacando:
            pass
        elif not self.en_suelo:
            self.estado = 'j_up' if self.velocidad_y < 0 else 'j_down'
        elif self.velocidad_x != 0:
            self.estado = 'run'
        else:
            self.estado = 'idle'

    def actualizar_hitboxes(self):
        ancho_cuerpo, alto_cuerpo = 60, 100
        self.hurtbox = pygame.Rect(0, 0, ancho_cuerpo, alto_cuerpo)
        self.hurtbox.midbottom = self.rect.midbottom

        if self.atacando:
            if self.estado == 'sp_atk':
                ancho_hb, alto_hb = 140, 60
            else:
                ancho_hb, alto_hb = 110, 45

            y_hb = self.rect.bottom - alto_hb - 10

            if self.mirando_derecha:
                self.hitbox = pygame.Rect(self.rect.centerx + 10, y_hb, ancho_hb, alto_hb)
            else:
                self.hitbox = pygame.Rect(self.rect.centerx - 10 - ancho_hb, y_hb, ancho_hb, alto_hb)
        else:
            self.hitbox = pygame.Rect(0, 0, 0, 0)

    def animar(self):
        anim = self.animaciones[self.estado]
        self.frame_index += self.velocidad_animacion

        if self.frame_index >= len(anim):
            self.frame_index = 0

            if self.rodando:
                self.rodando = False
            elif self.defendiendo:
                self.defendiendo = False
            elif self.estado in ['air_atk', 'sp_atk', '3_atk']:
                self.atacando = False
            elif self.estado == '1_atk':
                if self.combo_siguiente:
                    self.estado = '2_atk'
                    self.has_hit = False
                    self.combo_siguiente = False
                else:
                    self.atacando = False
            elif self.estado == '2_atk':
                if self.combo_siguiente:
                    self.estado = '3_atk'
                    self.has_hit = False
                    self.combo_siguiente = False
                else:
                    self.atacando = False

        frame_actual = anim[int(self.frame_index)]
        if not self.mirando_derecha:
            self.image = pygame.transform.flip(frame_actual, True, False)
        else:
            self.image = frame_actual

    def aplicar_gravedad(self):
        bottom_anterior = self.rect.bottom
        self.en_suelo = False
        self.plataforma_actual = None
        self.velocidad_y += self.gravedad
        self.rect.y += self.velocidad_y

        if self.velocidad_y >= 0:
            for plataforma in self.plataformas:
                plataforma_pantalla = plataforma.move(-self.scroll_x_actual, 0)
                if self.plataforma_ignorada is plataforma:
                    if self.rect.bottom >= plataforma_pantalla.bottom:
                        self.plataforma_ignorada = None
                    else:
                        continue
                zona_suelo = plataforma_pantalla.inflate(-20, 0)
                pisa_plataforma = (
                    bottom_anterior <= zona_suelo.top
                    and self.rect.bottom >= zona_suelo.top
                    and self.rect.centerx + 30 > zona_suelo.left
                    and self.rect.centerx - 30 < zona_suelo.right
                )
                if pisa_plataforma:
                    self.rect.bottom = zona_suelo.top
                    self.velocidad_y = 0
                    self.en_suelo = True
                    self.plataforma_actual = plataforma
                    break

        if not self.en_suelo and self.rect.bottom >= POSICION_SUELO:
            self.rect.bottom = POSICION_SUELO
            self.velocidad_y = 0
            self.en_suelo = True
            self.plataforma_actual = None

    def take_damage(self, damage):
        if self.rodando or (self.atacando and self.estado == 'sp_atk'):
            return
        self.health = max(0, self.health - damage)

    def update(
        self,
        scroll_x,
        transicion_realizada,
        limite_max_x=HUECO_FIN,
        limite_min_x=80,
    ):
        self.scroll_x_actual = scroll_x
        self.manejar_movimiento_continuo()

        if self.rodando:
            self.velocidad_x = (self.velocidad_movimiento + 3) * (1 if self.mirando_derecha else -1)

        self.pos_x += self.velocidad_x

        limite_izquierdo = max(scroll_x + 80, limite_min_x)

        if transicion_realizada and scroll_x == 0:
            limite_izquierdo = 80
            limite_derecho = ANCHO - 80
        elif transicion_realizada:
            limite_derecho = ANCHO_MUNDO - 80
        else:
            limite_derecho = limite_max_x

        self.pos_x = max(limite_izquierdo, min(self.pos_x, limite_derecho))
        self.rect.centerx = int(self.pos_x - scroll_x)

        self.aplicar_gravedad()
        self.actualizar_estado()
        self.actualizar_hitboxes()
        self.animar()


class VistaJugadorMundo:
    def __init__(self, jugador):
        self.jugador = jugador
        self.sync(0)

    def sync(self, scroll_x):
        j = self.jugador
        self.rect = j.rect.move(scroll_x, 0)
        self.hurtbox = j.hurtbox.move(scroll_x, 0)
        self.hitbox = j.hitbox.move(scroll_x, 0)
        self.pos_x = j.pos_x

    def take_damage(self, damage, attacker=None):
        self.jugador.take_damage(damage, attacker=attacker)


# 4. UI e Interactivos
def dibujar_boton_demoniaco(pantalla, texto="PRESS C TO INTERACT"):
    ANCHO_LOW, ALTO_LOW = 150, 38
    surf_pixel = pygame.Surface((ANCHO_LOW, ALTO_LOW))
    surf_pixel.fill((0, 0, 0))
    surf_pixel.set_colorkey((0, 0, 0))

    cuerno_izq = [(1, 7), (3, 7), (3, 5), (5, 5), (5, 3), (7, 1), (9, 1), (9, 9), (1, 9)]
    cuerno_der = [(ANCHO_LOW - 2, 7), (ANCHO_LOW - 4, 7), (ANCHO_LOW - 4, 5), (ANCHO_LOW - 6, 5),
                  (ANCHO_LOW - 6, 3), (ANCHO_LOW - 8, 1), (ANCHO_LOW - 10, 1), (ANCHO_LOW - 10, 9), (ANCHO_LOW - 2, 9)]

    pygame.draw.polygon(surf_pixel, (170, 30, 20), cuerno_izq)
    pygame.draw.polygon(surf_pixel, (170, 30, 20), cuerno_der)
    pygame.draw.polygon(surf_pixel, (70, 10, 10), cuerno_izq, 1)
    pygame.draw.polygon(surf_pixel, (70, 10, 10), cuerno_der, 1)

    rect_piedra = pygame.Rect(7, 7, ANCHO_LOW - 14, ALTO_LOW - 7)
    pygame.draw.rect(surf_pixel, (25, 22, 22), rect_piedra)
    pygame.draw.rect(surf_pixel, (75, 75, 80), rect_piedra, 1)

    detalles_piedra = [
        (9, 9, 4, 2, (95, 95, 100)), (18, 8, 3, 2, (45, 45, 50)),
        (28, 9, 5, 1, (105, 105, 110)), (42, 8, 2, 2, (55, 55, 60)),
        (65, 8, 4, 1, (90, 90, 95)), (95, 9, 3, 2, (50, 50, 55)),
        (120, 8, 4, 1, (100, 100, 105)), (135, 9, 2, 2, (45, 45, 50)),
        (14, 12, 1, 3, (190, 40, 10)), (15, 15, 3, 1, (230, 90, 10)),
        (128, 28, 4, 1, (210, 60, 10)), (132, 29, 1, 3, (170, 30, 0)),
        (75, 32, 6, 1, (180, 40, 10)), (11, 29, 3, 2, (85, 85, 90))
    ]
    for x, y, w, h, color in detalles_piedra:
        pygame.draw.rect(surf_pixel, color, (x, y, w, h))

    pygame.draw.rect(surf_pixel, (40, 40, 45), rect_piedra.inflate(-4, -4), 1)

    txt_sombra = fuente_lava_pixel.render(texto, False, (180, 30, 0))
    txt_fuego = fuente_lava_pixel.render(texto, False, (255, 170, 0))

    rect_txt = txt_fuego.get_rect(center=(ANCHO_LOW // 2, ALTO_LOW // 2 + 1))
    surf_pixel.blit(txt_sombra, (rect_txt.x + 1, rect_txt.y + 1))
    surf_pixel.blit(txt_fuego, rect_txt)

    ESCALA = 2.5
    ancho_final = int(ANCHO_LOW * ESCALA)
    alto_final = int(ALTO_LOW * ESCALA)

    surf_escalada = pygame.transform.scale(surf_pixel, (ancho_final, alto_final))
    pantalla.blit(surf_escalada, (ANCHO - ancho_final - 25, ALTO - alto_final - 20))


def dibujar_barra_jugador(screen, player):
    pct_player = max(0.0, min(1.0, player.health / player.max_health if player.max_health > 0 else 0))

    if IMG_BARRA_JUGADOR is not None:
        ancho_b_p = 280
        escala_p = ancho_b_p / IMG_BARRA_JUGADOR.get_width()
        alto_b_p = int(IMG_BARRA_JUGADOR.get_height() * escala_p)
        bar_p_scaled = pygame.transform.scale(IMG_BARRA_JUGADOR, (ancho_b_p, alto_b_p))

        x_p_ui, y_p_ui = 25, 20

        x_fill_p = x_p_ui + int(ancho_b_p * 0.08)
        y_fill_p = y_p_ui + int(alto_b_p * 0.44)
        w_max_fill_p = int(ancho_b_p * 0.84)
        h_fill_p = int(alto_b_p * 0.40)
        w_restante_p = int(w_max_fill_p * pct_player)

        pygame.draw.rect(screen, (20, 5, 5), (x_fill_p, y_fill_p, w_max_fill_p, h_fill_p))
        if w_restante_p > 0:
            pygame.draw.rect(screen, (190, 30, 30), (x_fill_p, y_fill_p, w_restante_p, h_fill_p))
            pygame.draw.rect(screen, (240, 90, 90), (x_fill_p, y_fill_p, w_restante_p, max(1, h_fill_p // 3)))

        screen.blit(bar_p_scaled, (x_p_ui, y_p_ui))

        lbl_player = fuente_ui.render(f"JUGADOR: {int(player.health)} / {player.max_health}", True, (255, 255, 255))
        screen.blit(lbl_player, (x_p_ui + 5, y_p_ui + alto_b_p + 4))
    else:
        ancho_b_player, alto_b_player = 200, 18
        x_player, y_player = 30, 30

        pygame.draw.rect(screen, (10, 10, 10), (x_player - 2, y_player - 2, ancho_b_player + 4, alto_b_player + 4))
        if pct_player > 0:
            pygame.draw.rect(screen, (190, 30, 30), (x_player, y_player, int(ancho_b_player * pct_player), alto_b_player))
        pygame.draw.rect(screen, (200, 200, 200), (x_player - 2, y_player - 2, ancho_b_player + 4, alto_b_player + 4), 2)
        lbl_player = fuente_ui.render(f"JUGADOR: {int(player.health)} / {player.max_health}", True, (255, 255, 255))
        screen.blit(lbl_player, (x_player, 8))

    player.dibujar_barra_energia(screen)


# 5. Escena de Batalla contra el Jefe
def obtener_hitbox_ataque_jefe_nivel1(jefe):
    frames = jefe.animaciones.get(jefe.estado_actual, [])
    if not jefe.attacking or not jefe.estado_actual.startswith("attack") or not frames:
        return None

    progreso_ataque = jefe.frame_actual / max(1, len(frames) - 1)
    if not 0.55 <= progreso_ataque <= 0.82:
        return None

    ancho, alto = 175, 55
    y = jefe.rect.y + 225
    if jefe.direction == "left":
        x = jefe.rect.left - ancho
    else:
        x = jefe.rect.right
    return pygame.Rect(x, y, ancho, alto)


def mostrar_intro_batalla_jefe(screen, fondo):
    ancho, alto = screen.get_size()
    reloj_intro = pygame.time.Clock()
    inicio = pygame.time.get_ticks()
    duracion_ms = 3000

    fuente_etiqueta = pygame.font.SysFont("Arial", 18, bold=True)
    fuente_titulo = pygame.font.SysFont("Georgia", 92, bold=True)
    fuente_epiteto = pygame.font.SysFont("Georgia", 34, bold=True, italic=True)
    fuente_cierre = pygame.font.SysFont("Arial", 18, bold=True)

    ancho_panel = int(ancho * 0.76)
    alto_panel = int(alto * 0.56)
    panel_rect = pygame.Rect(0, 0, ancho_panel, alto_panel)
    panel_rect.center = (ancho // 2, alto // 2)
    panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    oscurecer = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    oscurecer.fill((8, 2, 5, 170))

    particulas = [
        [
            random.uniform(0, ancho),
            random.uniform(0, alto),
            random.uniform(20, 75),
            random.randint(1, 3),
        ]
        for _ in range(30)
    ]

    while True:
        dt = reloj_intro.tick(60) / 1000.0
        transcurrido = pygame.time.get_ticks() - inicio
        if transcurrido >= duracion_ms:
            break

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                cerrar_nivel("exit")
            if evento.type == pygame.KEYDOWN and evento.key in (
                pygame.K_RETURN,
                pygame.K_SPACE,
            ):
                return

        entrada = min(1.0, transcurrido / 550.0)
        screen.blit(fondo, (0, 0))
        screen.blit(oscurecer, (0, 0))

        for particula in particulas:
            particula[1] -= particula[2] * dt
            if particula[1] < 0:
                particula[0] = random.uniform(0, ancho)
                particula[1] = alto
            color = (150 + particula[3] * 25, 38 + particula[3] * 8, 16)
            pygame.draw.circle(
                screen,
                color,
                (round(particula[0]), round(particula[1])),
                particula[3],
            )

        panel.fill((7, 5, 8, int(220 * entrada)))
        screen.blit(panel, panel_rect)
        intensidad = int(120 * entrada)
        pygame.draw.rect(
            screen, (intensidad, 28, 20), panel_rect, 2, border_radius=8
        )

        margen = 34
        largo_esquina = 58
        color_marco = (185, 104, 55)
        pygame.draw.line(
            screen, color_marco,
            (panel_rect.left + margen, panel_rect.top + margen),
            (panel_rect.left + margen + largo_esquina, panel_rect.top + margen),
            2,
        )
        pygame.draw.line(
            screen, color_marco,
            (panel_rect.right - margen, panel_rect.top + margen),
            (panel_rect.right - margen - largo_esquina, panel_rect.top + margen),
            2,
        )
        pygame.draw.line(
            screen, color_marco,
            (panel_rect.left + margen, panel_rect.bottom - margen),
            (panel_rect.left + margen + largo_esquina, panel_rect.bottom - margen),
            2,
        )
        pygame.draw.line(
            screen, color_marco,
            (panel_rect.right - margen, panel_rect.bottom - margen),
            (panel_rect.right - margen - largo_esquina, panel_rect.bottom - margen),
            2,
        )

        etiqueta = fuente_etiqueta.render(
            "JEFE FINAL  |  NIVEL 1", True, (225, 175, 112)
        )
        etiqueta.set_alpha(int(255 * entrada))
        screen.blit(
            etiqueta,
            etiqueta.get_rect(center=(ancho // 2, panel_rect.top + 72)),
        )

        titulo_sombra = fuente_titulo.render("ATHROS", True, (110, 12, 12))
        titulo = fuente_titulo.render("ATHROS", True, (238, 221, 198))
        epiteto = fuente_epiteto.render(
            "THE BLOODRED", True, (196, 55, 39)
        )
        for superficie in (titulo_sombra, titulo, epiteto):
            superficie.set_alpha(int(255 * entrada))

        centro_titulo = (ancho // 2, panel_rect.top + 166 + int((1 - entrada) * 18))
        rect_titulo = titulo.get_rect(center=centro_titulo)
        screen.blit(titulo_sombra, rect_titulo.move(3, 5))
        screen.blit(titulo, rect_titulo)
        screen.blit(
            epiteto,
            epiteto.get_rect(center=(ancho // 2, panel_rect.top + 245)),
        )

        separador_y = panel_rect.top + 290
        pygame.draw.line(
            screen, (115, 39, 27),
            (panel_rect.left + 130, separador_y),
            (panel_rect.right - 130, separador_y),
            1,
        )
        pygame.draw.polygon(
            screen,
            (208, 155, 94),
            [
                (ancho // 2, separador_y - 6),
                (ancho // 2 + 6, separador_y),
                (ancho // 2, separador_y + 6),
                (ancho // 2 - 6, separador_y),
            ],
        )

        cierre = fuente_cierre.render(
            "EL CARNICERO HA DESPERTADO", True, (225, 202, 158)
        )
        cierre.set_alpha(int(255 * entrada))
        screen.blit(
            cierre,
            cierre.get_rect(center=(ancho // 2, panel_rect.top + 337)),
        )
        continuar = fuente_etiqueta.render(
            "ENTER / ESPACIO  |  CONTINUAR", True, (190, 145, 105)
        )
        continuar.set_alpha(int(220 * entrada))
        screen.blit(
            continuar,
            continuar.get_rect(center=(ancho // 2, panel_rect.bottom + 32)),
        )
        pygame.display.flip()


def ejecutar_batalla_carnicero(screen, player, fondo_img):
    global nivel_completado

    from Jefes_enemigos import CarniceroBoss

    clock = pygame.time.Clock()
    FPS = 60

    jefe = CarniceroBoss(x=920, y=POSICION_SUELO - 300)

    jefe.max_health = 300
    jefe.health = 300

    player.health = player.max_health

    player.pos_x = 180.0
    player.rect.centerx = 180
    player.rect.bottom = POSICION_SUELO
    player.plataformas = []
    player.plataforma_actual = None
    player.plataforma_ignorada = None
    player.scroll_x_actual = 0
    player.velocidad_y = 0
    player.en_suelo = True

    en_batalla = True
    timer_muerte_jefe = 0.0
    momento_derrota_jefe_ms = None

    TIEMPO_FADE_LETRERO = 1.8
    DURACION_COMIC_FINAL_SEGUNDOS = 6.0

    while en_batalla:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cerrar_nivel("exit")
                en_batalla = False
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                accion = pausar_juego(screen, devolver_accion=True)
                if accion in ("menu", "exit"):
                    solicitar_cierre_nivel(accion)
                    en_batalla = False
                    break
                continue

            player.procesar_evento(event)

        if not en_batalla:
            break

        player.update(0, transicion_realizada=True)
        if muerte_terminada(player):
            mostrar_menu_muerte(screen)
            en_batalla = False
            break
        jefe.update(player, dt, width=ANCHO, suelo_y=POSICION_SUELO)

        target_player_rect = player.hurtbox

        for proj in jefe.proyectiles[:]:
            if (
                proj.rect.colliderect(target_player_rect)
                and not getattr(proj, "esquivado", False)
            ):
                if player.rodando:
                    proj.esquivado = True
                else:
                    player.take_damage(7, attacker=proj)
                    if proj in jefe.proyectiles:
                        jefe.proyectiles.remove(proj)

        jefe_atacando = (
            getattr(jefe, 'attacking', False) or
            getattr(jefe, 'atacando', False) or
            getattr(jefe, 'estado', '') in ['attack', 'atk', '1_atk', 'attacking']
        )

        if jefe_atacando:
            espada_hitbox = obtener_hitbox_ataque_jefe_nivel1(jefe)
            if (
                espada_hitbox is not None
                and espada_hitbox.colliderect(target_player_rect)
                and not getattr(jefe, 'has_hit', False)
            ):
                player.take_damage(16, attacker=espada_hitbox)
                setattr(jefe, 'has_hit', True)
        else:
            setattr(jefe, 'has_hit', False)

        if not getattr(jefe, 'muerto_definitivo', False):
            player.comprobar_golpe(jefe)
            player.comprobar_golpes_proyectiles((jefe,))

        if jefe.health <= 0 and momento_derrota_jefe_ms is None:
            momento_derrota_jefe_ms = pygame.time.get_ticks()

        screen.blit(fondo_img, (0, 0))
        screen.blit(player.image, player.rect)
        jefe.draw(screen)

        if not getattr(jefe, 'muerto_definitivo', False):
            max_v_jefe = getattr(jefe, 'max_health', 300)
            pct_jefe = max(0.0, min(1.0, jefe.health / max_v_jefe if max_v_jefe > 0 else 0))

            if IMG_SUN_SPIRIT is not None:
                ancho_b_jefe = 650
                escala = ancho_b_jefe / IMG_SUN_SPIRIT.get_width()
                alto_b_jefe = int(IMG_SUN_SPIRIT.get_height() * escala)
                bar_scaled = pygame.transform.scale(IMG_SUN_SPIRIT, (ancho_b_jefe, alto_b_jefe))

                x_jefe_ui = (ANCHO - ancho_b_jefe) // 2
                y_jefe_ui = 18

                x_fill = x_jefe_ui + int(ancho_b_jefe * 0.11)
                y_fill = y_jefe_ui + int(alto_b_jefe * 0.38)
                w_max_fill = int(ancho_b_jefe * 0.78)
                h_fill = int(alto_b_jefe * 0.22)

                w_restante = int(w_max_fill * pct_jefe)

                pygame.draw.rect(screen, (20, 5, 5), (x_fill, y_fill, w_max_fill, h_fill))

                if w_restante > 0:
                    fase = getattr(jefe, 'fase_actual', 1)
                    color_fase = (180, 30, 10) if fase == 1 else ((255, 100, 0) if fase == 2 else (255, 200, 0))
                    pygame.draw.rect(screen, color_fase, (x_fill, y_fill, w_restante, h_fill))
                    pygame.draw.rect(screen, (255, 220, 100), (x_fill, y_fill, w_restante, max(1, h_fill // 3)))

                screen.blit(bar_scaled, (x_jefe_ui, y_jefe_ui))

                y_titulo = y_jefe_ui + alto_b_jefe + 6
                lbl_sombra = fuente_jefe.render("Athros : The bloodred", True, (100, 10, 0))
                lbl_fuego_brillo = fuente_jefe.render("Athros : The bloodred", True, (255, 80, 0))
                lbl_jefe = fuente_jefe.render("Athros : The bloodred", True, (255, 190, 30))

                rect_lbl = lbl_jefe.get_rect(center=(ANCHO // 2, y_titulo))
                screen.blit(lbl_sombra, (rect_lbl.x + 2, rect_lbl.y + 2))
                screen.blit(lbl_fuego_brillo, (rect_lbl.x + 1, rect_lbl.y + 1))
                screen.blit(lbl_jefe, rect_lbl)

            else:
                ancho_b_jefe, alto_b_jefe = 500, 20
                x_jefe, y_jefe = (ANCHO - ancho_b_jefe) // 2, 45

                pygame.draw.rect(screen, (20, 5, 5), (x_jefe - 2, y_jefe - 2, ancho_b_jefe + 4, alto_b_jefe + 4))
                w_restante = int(ancho_b_jefe * pct_jefe)

                if w_restante > 0:
                    fase = getattr(jefe, 'fase_actual', 1)
                    color_fase = (180, 30, 10) if fase == 1 else ((255, 100, 0) if fase == 2 else (255, 200, 0))
                    pygame.draw.rect(screen, color_fase, (x_jefe, y_jefe, w_restante, alto_b_jefe))
                    pygame.draw.rect(screen, (255, 220, 100), (x_jefe, y_jefe, w_restante, alto_b_jefe // 2))

                pygame.draw.rect(screen, (255, 215, 0), (x_jefe - 2, y_jefe - 2, ancho_b_jefe + 4, alto_b_jefe + 4), 2)

                y_titulo = y_jefe + alto_b_jefe + 10
                lbl_sombra = fuente_jefe.render("Athros : The bloodred", True, (100, 10, 0))
                lbl_jefe = fuente_jefe.render("Athros : The bloodred", True, (255, 190, 30))
                rect_lbl = lbl_jefe.get_rect(center=(ANCHO // 2, y_titulo))
                screen.blit(lbl_sombra, (rect_lbl.x + 2, rect_lbl.y + 2))
                screen.blit(lbl_jefe, rect_lbl)

        dibujar_barra_jugador(screen, player)
        texto_progreso = fuente_progreso.render(
            "RUMBO AL PORTAL: 100%", True, (230, 210, 160)
        )
        screen.blit(
            texto_progreso,
            texto_progreso.get_rect(topright=(ANCHO - 30, 20)),
        )

        if getattr(jefe, 'muerto_definitivo', False):
            timer_muerte_jefe += dt

            progreso = min(1.0, timer_muerte_jefe / TIEMPO_FADE_LETRERO)
            alpha_val = int(progreso * 255)

            banda_alto = 120
            banda_surf = pygame.Surface((ANCHO, banda_alto), pygame.SRCALPHA)
            banda_surf.fill((0, 0, 0, int(progreso * 135)))

            y_banda = (ALTO // 2) - (banda_alto // 2)
            screen.blit(banda_surf, (0, y_banda))

            fuente_elden = pygame.font.SysFont("Georgia", 64, bold=True)

            surf_sombra = fuente_elden.render("LEGEND FALLEN", True, (25, 10, 5))
            surf_texto = fuente_elden.render("LEGEND FALLEN", True, (235, 195, 75))

            surf_sombra.set_alpha(alpha_val)
            surf_texto.set_alpha(alpha_val)

            rect_txt = surf_texto.get_rect(center=(ANCHO // 2, ALTO // 2))
            screen.blit(surf_sombra, (rect_txt.x + 3, rect_txt.y + 3))
            screen.blit(surf_texto, rect_txt)

            if (
                momento_derrota_jefe_ms is not None
                and pygame.time.get_ticks() - momento_derrota_jefe_ms
                >= DURACION_COMIC_FINAL_SEGUNDOS * 1000
            ):
                mostrar_comic_final(screen)
                nivel_completado = True
                en_batalla = False

        pygame.display.flip()


# ==============================================================================
# GRUPOS DE ENEMIGOS ACTIVADOS POR DISTANCIA
# ==============================================================================
TIPOS_ENEMIGO = [OrcoRojo, OjoVolador, Karasu_tengu]
DISTANCIA_ENTRE_GRUPOS = 850
PRIMER_GRUPO_X = 800
ULTIMO_GRUPO_X = ZONA_BIBLIOTECA_X - 1800
PUNTOS_GRUPO = list(range(PRIMER_GRUPO_X, ULTIMO_GRUPO_X + 1, DISTANCIA_ENTRE_GRUPOS))
DISTANCIA_VISION_ENEMIGO = 270
ANTICIPACION_APARICION_ENEMIGOS = 600
CONFIGURACION_ANIMACION_IDLE = {
    OrcoRojo: ("assets/enemigos/Orco_rojo/Idle.png", 5),
    Karasu_tengu: ("assets/enemigos/Karasu_tengu/Idle.png", 6),
}
ANIMACIONES_IDLE_ENEMIGOS = {}

def generar_plataformas_nivel():
    plataformas = []
    x = 350
    y = 520

    while x < HUECO_INICIO - 100:
        ancho = random.randint(190, 280)
        plataformas.append(pygame.Rect(x, y, ancho, 18))

        # Las primeras cuatro imágenes mantienen el piso plano; después varía.
        x += ancho + random.randint(35, 105)
        if x < ANCHO * 4:
            y = 520
        else:
            y = max(325, min(560, y + random.randint(-75, 75)))

    return plataformas


def generar_diseno_plataforma():
    return {
        "madera": random.choice([
            (117, 75, 43), (139, 91, 52), (101, 64, 39),
            (151, 105, 63),
        ]),
        "veta": random.choice([
            (173, 123, 72), (186, 137, 85), (130, 87, 52),
        ]),
        "metal": random.choice([
            (72, 78, 82), (91, 96, 98), (59, 65, 70),
        ]),
    }


def dibujar_plataformas(screen, scroll_x, plataformas, disenos):
    for plataforma, diseno in zip(plataformas, disenos):
        rect = plataforma.move(-scroll_x, 0)
        if rect.right < 0 or rect.left > ANCHO:
            continue

        x, y, ancho = rect.x, rect.y, rect.width
        madera = diseno["madera"]
        metal = diseno["metal"]
        pata_izquierda = x + 16
        pata_derecha = rect.right - 16
        base_patas_y = y + 58

        pygame.draw.line(
            screen, (35, 30, 25), (pata_izquierda, y + 14),
            (pata_izquierda - 5, base_patas_y), 5,
        )
        pygame.draw.line(
            screen, (35, 30, 25), (pata_derecha, y + 14),
            (pata_derecha + 5, base_patas_y), 5,
        )
        pygame.draw.line(
            screen, metal, (pata_izquierda, y + 14),
            (pata_izquierda - 5, base_patas_y), 3,
        )
        pygame.draw.line(
            screen, metal, (pata_derecha, y + 14),
            (pata_derecha + 5, base_patas_y), 3,
        )
        pygame.draw.line(
            screen, metal, (pata_izquierda - 3, y + 39),
            (pata_derecha + 3, y + 39), 3,
        )

        pygame.draw.rect(
            screen, (47, 34, 25), (x + 3, y + 6, ancho - 6, 13)
        )
        pygame.draw.rect(
            screen, madera, (x, y - 3, ancho, 10)
        )
        pygame.draw.rect(
            screen, diseno["veta"], (x + 2, y - 2, ancho - 4, 3)
        )
        pygame.draw.line(
            screen, (78, 49, 30), (x + 6, y + 2),
            (rect.right - 6, y + 2), 1,
        )
        pygame.draw.rect(
            screen, (58, 42, 31), (x + 9, y + 8, ancho - 18, 5), 1
        )
        pygame.draw.rect(screen, metal, (x + 12, y + 15, 8, 3))
        pygame.draw.rect(screen, metal, (rect.right - 20, y + 15, 8, 3))


def crear_enemigo(clase, x):
    """Instancia un enemigo. OrcoRojo y Karasu_tengu se alinean con el suelo; OjoVolador flota."""
    if clase is OrcoRojo:
        enemigo = OrcoRojo(
            x=x, y=POSICION_SUELO, escala=ESCALA_ORCO_NIVEL
        )
        enemigo.dano_ataque = 5
    elif clase is Karasu_tengu:
        enemigo = Karasu_tengu(x=x, y=POSICION_SUELO)
        enemigo.dano_ataque = 5
    else:
        # El OjoVolador conserva la altura flotante que tenías configurada
        enemigo = OjoVolador(x=x, y=POSICION_SUELO, suelo_y=POSICION_SUELO)
        enemigo.DANO_PROYECTIL = 5

    enemigo.health = 40
    enemigo.max_health = 40
    enemigo.suelo_y = POSICION_SUELO
    if isinstance(enemigo, (OrcoRojo, Karasu_tengu)):
        enemigo.rect.bottom = POSICION_SUELO
        enemigo.jump_force = -15
        enemigo.velocity_y = 0
        enemigo.on_ground = True
        enemigo.hurtbox.topleft = enemigo.rect.topleft
    return enemigo


def obtener_animacion_idle(enemigo):
    clase = type(enemigo)
    if clase is OjoVolador:
        return enemigo.animaciones["correr"]
    if clase not in ANIMACIONES_IDLE_ENEMIGOS:
        ruta, cantidad_frames = CONFIGURACION_ANIMACION_IDLE[clase]
        frames = cargar_spritesheet_jokai(ruta, 1, cantidad_frames)
        tamaño = enemigo.animaciones["correr"][0].get_size()
        ANIMACIONES_IDLE_ENEMIGOS[clase] = [
            pygame.transform.scale(frame, tamaño)
            if frame.get_size() != tamaño else frame
            for frame in frames
        ]
    return ANIMACIONES_IDLE_ENEMIGOS[clase]


def actualizar_animacion_idle(enemigo, dt):
    frames = enemigo.animaciones["idle"]
    enemigo.frame_idle = (
        enemigo.frame_idle + dt * 6
    ) % len(frames)
    imagen = frames[int(enemigo.frame_idle)]
    enemigo.image = (
        pygame.transform.flip(imagen, True, False)
        if enemigo.direction == "left"
        else imagen
    )


def generar_grupo_enemigos(posicion, indice_grupo=0):
    """Genera dos enemigos y alterna sus tipos entre grupos."""
    enemigos = []
    clases_grupo = [
        TIPOS_ENEMIGO[indice_grupo % len(TIPOS_ENEMIGO)],
        TIPOS_ENEMIGO[(indice_grupo + 1) % len(TIPOS_ENEMIGO)],
    ]
    posicion_suelo = posicion + 360
    plataformas_cercanas = [
        plataforma for plataforma in plataformas_nivel
        if posicion + 360 <= plataforma.centerx <= posicion + 700
    ]
    plataforma_enemigo = min(
        plataformas_cercanas or plataformas_nivel,
        key=lambda plataforma: abs(plataforma.centerx - (posicion + 520)),
        default=None,
    )

    for i, clase in enumerate(clases_grupo):
        usa_plataforma = (
            i == 1
            and clase is not OjoVolador
            and plataforma_enemigo is not None
        )
        x = (
            plataforma_enemigo.centerx
            if usa_plataforma
            else posicion_suelo + i * 160
        )
        enemigo = crear_enemigo(clase, x)
        enemigo.rect.centerx = x
        enemigo.hurtbox.topleft = enemigo.rect.topleft
        enemigo.plataformas = plataformas_nivel
        enemigo.flank_side = -1 if i % 2 == 0 else 1
        enemigo.attack_range = 270
        enemigo.ataque_coordinado = True
        enemigo.esperando_jugador = True
        enemigo.distancia_vision = DISTANCIA_VISION_ENEMIGO
        enemigo.animaciones["idle"] = obtener_animacion_idle(enemigo)
        enemigo.frame_idle = 0.0
        enemigo.direction = "left"
        if clase is not OjoVolador:
            enemigo.preferred_distance = 65
        if usa_plataforma:
            enemigo.rect.centerx = plataforma_enemigo.centerx
            enemigo.rect.bottom = plataforma_enemigo.top
        if clase is not OjoVolador:
            enemigo.velocity_y = 0
            enemigo.on_ground = True
            enemigo.hurtbox.topleft = enemigo.rect.topleft
        enemigo.jump_cooldown = random.uniform(0.4, 1.4)
        enemigo.speed = random.randint(3, 5)
        enemigos.append(enemigo)
    for enemigo in enemigos:
        enemigo.allies = enemigos
    return enemigos


ENEMIGOS_POR_ESCENA = {
    FASE_BIBLIOTECA_7: (
        (OrcoRojo, 650),
        (Karasu_tengu, 1050),
    ),
    FASE_BIBLIOTECA_9: (
        (OrcoRojo, 650),
        (Karasu_tengu, 1050),
    ),
    FASE_PASILLO_HOSPITAL: (
        (OrcoRojo, 650),
        (Karasu_tengu, 950),
    ),
    FASE_HOSPITAL_11: (
        (OrcoRojo, 350),
        (Karasu_tengu, 570),
    ),
}


def generar_enemigos_escena(fase):
    enemigos = []
    for clase, x in ENEMIGOS_POR_ESCENA.get(fase, ()):
        enemigo = crear_enemigo(clase, x)
        enemigo.rect.centerx = x
        enemigo.rect.bottom = POSICION_SUELO
        enemigo.hurtbox.topleft = enemigo.rect.topleft
        enemigo.plataformas = []
        enemigo.velocity_y = 0
        enemigo.on_ground = True
        enemigo.esperando_jugador = True
        enemigo.distancia_vision = DISTANCIA_VISION_ENEMIGO
        enemigo.attack_range = 240
        enemigo.ataque_coordinado = True
        enemigo.preferred_distance = 65
        enemigo.direction = "left"
        enemigo.animaciones["idle"] = obtener_animacion_idle(enemigo)
        enemigo.frame_idle = 0.0
        enemigos.append(enemigo)

    for enemigo in enemigos:
        enemigo.allies = enemigos
    return enemigos


def enemigo_derrotado(enemigo):
    return enemigo.health <= 0 or getattr(enemigo, 'muerto_definitivo', False)


def separar_enemigos(enemigos, ancho_mundo):
    enemigos_activos = [
        enemigo for enemigo in enemigos
        if enemigo.health > 0 and not getattr(enemigo, "muerto_definitivo", False)
    ]

    for _ in range(3):
        for indice, primero in enumerate(enemigos_activos):
            for segundo in enemigos_activos[indice + 1:]:
                distancia_vertical = abs(
                    primero.rect.centery - segundo.rect.centery
                )
                distancia_vertical_minima = (
                    primero.rect.height + segundo.rect.height
                ) // 2 + 20
                if distancia_vertical >= distancia_vertical_minima:
                    continue

                if not primero.rect.inflate(0, 20).colliderect(
                    segundo.rect.inflate(0, 20)
                ):
                    continue

                signo = 1 if primero.rect.centerx <= segundo.rect.centerx else -1
                distancia_minima = (primero.rect.width + segundo.rect.width) // 2 + 18
                distancia_actual = abs(segundo.rect.centerx - primero.rect.centerx)
                empuje = distancia_minima - distancia_actual
                if empuje <= 0:
                    continue

                primero_x_anterior = primero.rect.x
                segundo_x_anterior = segundo.rect.x
                empuje_primero = (empuje + 1) // 2
                empuje_segundo = empuje // 2
                primero.rect.centerx -= signo * empuje_primero
                segundo.rect.centerx += signo * empuje_segundo
                primero.rect.x = max(
                    0, min(ancho_mundo - primero.rect.width, primero.rect.x)
                )
                segundo.rect.x = max(
                    0, min(ancho_mundo - segundo.rect.width, segundo.rect.x)
                )
                primero.hitbox.x += primero.rect.x - primero_x_anterior
                segundo.hitbox.x += segundo.rect.x - segundo_x_anterior

                if hasattr(primero, "actualizar_hurtbox"):
                    primero.actualizar_hurtbox()
                else:
                    primero.hurtbox.topleft = primero.rect.topleft
                if hasattr(segundo, "actualizar_hurtbox"):
                    segundo.actualizar_hurtbox()
                else:
                    segundo.hurtbox.topleft = segundo.rect.topleft


# ==============================================================================
# INICIALIZACIÓN Y FLUJO PRINCIPAL DEL JUEGO
# ==============================================================================

heroe = crear_jugador(
    200,
    POSICION_SUELO,
    POSICION_SUELO,
    ANCHO_MUNDO,
    ANCHO,
)
todos_los_sprites = pygame.sprite.Group(heroe)
vista_heroe = VistaJugadorMundo(heroe)
plataformas_nivel = generar_plataformas_nivel()
disenos_plataformas = [
    generar_diseno_plataforma() for _ in plataformas_nivel
]
disenos_plataformas_escena = {
    fase: [generar_diseno_plataforma() for _ in plataformas]
    for fase, plataformas in PLATAFORMAS_ESCENA.items()
}
heroe.plataformas = plataformas_nivel

enemigos_nivel = []
enemigos_escena = []
proximo_grupo = 0

scroll_x = 0
transicion_realizada = False
biblioteca_ingresada = False
fase_nivel = FASE_RECORRIDO
perseguidor_activo = False
perseguidor_x = 0.0
monstruo_frame = 0.0

ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    dt = reloj.tick(60) / 1000.0

    if fase_nivel == FASE_RECORRIDO:
        while (
            proximo_grupo < len(PUNTOS_GRUPO)
            and heroe.pos_x
            >= PUNTOS_GRUPO[proximo_grupo] - ANTICIPACION_APARICION_ENEMIGOS
        ):
            enemigos_nivel.extend(
                generar_grupo_enemigos(
                    PUNTOS_GRUPO[proximo_grupo], proximo_grupo
                )
            )
            proximo_grupo += 1

        if heroe.pos_x >= ZONA_BIBLIOTECA_X - 500:
            enemigos_nivel.clear()

    enemigos_pendientes = [
        enemigo for enemigo in enemigos_nivel if not enemigo_derrotado(enemigo)
    ]
    limite_max_x = obtener_limite_derecho(fase_nivel)
    interaccion_disponible = requiere_interaccion(fase_nivel, heroe.pos_x)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            cerrar_nivel("exit")
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            accion = pausar_juego(pantalla, devolver_accion=True)
            if accion in ("menu", "exit"):
                detener_musica_persecucion()
                solicitar_cierre_nivel(accion)
                ejecutando = False
                break
            continue

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and interaccion_disponible
            and not heroe.muerto
        ):
            if fase_nivel == FASE_RECORRIDO:
                biblioteca_ingresada = True
                enemigos_nivel.clear()
                fase_nivel = FASE_BIBLIOTECA_7
                enemigos_escena = generar_enemigos_escena(fase_nivel)
                colocar_jugador_en_escena(heroe, 180, fase_nivel)
                scroll_x = 0

            elif fase_nivel == FASE_BIBLIOTECA_9:
                fase_nivel = FASE_PASILLO_HOSPITAL
                enemigos_escena = generar_enemigos_escena(fase_nivel)
                colocar_jugador_en_escena(heroe, 180, fase_nivel)
                scroll_x = 0

            elif fase_nivel == FASE_PASILLO_HOSPITAL:
                fase_nivel = FASE_HOSPITAL_11
                enemigos_escena = generar_enemigos_escena(fase_nivel)
                colocar_jugador_en_escena(heroe, 180, fase_nivel)
                scroll_x = 0

            elif fase_nivel == FASE_HOSPITAL_11:
                fase_nivel = FASE_CONDUCTO_1
                enemigos_escena.clear()
                colocar_jugador_en_escena(heroe, 110, fase_nivel)
                heroe.rect.bottom = obtener_suelo_conducto(
                    fase_nivel, heroe.pos_x
                )
                heroe.actualizar_hitboxes()
                perseguidor_activo = False
                perseguidor_x = 0.0
                monstruo_frame = 0.0
                scroll_x = 0

            elif fase_nivel == FASE_CONDUCTO_3:
                detener_musica_persecucion()
                fase_nivel = FASE_HUECO_FINAL
                enemigos_escena.clear()
                colocar_jugador_en_escena(heroe, 180, fase_nivel)
                perseguidor_activo = False
                scroll_x = 0

            elif fase_nivel == FASE_HUECO_FINAL:
                heroe.health = heroe.max_health
                mostrar_intro_batalla_jefe(pantalla, fondo_batalla)

                transicion_realizada = True
                ejecutar_batalla_carnicero(pantalla, heroe, fondo_batalla)
                ejecutando = False
                break

        if not heroe.muerto:
            heroe.procesar_evento(evento)

    if not ejecutando:
        break

    if fase_nivel in FASES_CONDUCTO:
        heroe.posicion_suelo = obtener_suelo_conducto(
            fase_nivel, heroe.pos_x
        )
    else:
        heroe.posicion_suelo = POSICION_SUELO

    todos_los_sprites.update(
        scroll_x,
        transicion_realizada,
        limite_max_x=limite_max_x,
        limite_min_x=80,
    )
    if muerte_terminada(heroe):
        detener_musica_persecucion()
        mostrar_menu_muerte(pantalla)
        break
    if fase_nivel == FASE_RECORRIDO:
        scroll_x = max(0, min(heroe.pos_x - ANCHO * 0.4, ANCHO_MUNDO - ANCHO))
    else:
        scroll_x = 0
    heroe.rect.centerx = int(heroe.pos_x - scroll_x)
    if fase_nivel in FASES_CONDUCTO:
        heroe.velocidad_y = 0
        heroe.rect.bottom = obtener_suelo_conducto(
            fase_nivel, heroe.pos_x
        )
        heroe.en_suelo = True
    heroe.actualizar_hitboxes()
    vista_heroe.sync(scroll_x)

    if (
        fase_nivel == FASE_BIBLIOTECA_7
        and heroe.pos_x >= obtener_limite_derecho(fase_nivel)
    ):
        fase_nivel = FASE_BIBLIOTECA_9
        enemigos_escena = generar_enemigos_escena(fase_nivel)
        colocar_jugador_en_escena(heroe, 100, fase_nivel)
        scroll_x = 0
        vista_heroe.sync(scroll_x)
    elif (
        fase_nivel in FASES_CONDUCTO[:2]
        and heroe.pos_x >= obtener_limite_derecho(fase_nivel)
    ):
        indice_conducto = FASES_CONDUCTO.index(fase_nivel) + 1
        fase_nivel = FASES_CONDUCTO[indice_conducto]
        colocar_jugador_en_escena(heroe, 100, fase_nivel)
        heroe.rect.bottom = obtener_suelo_conducto(
            fase_nivel, heroe.pos_x
        )
        heroe.actualizar_hitboxes()
        vista_heroe.sync(0)

    if fase_nivel == FASE_RECORRIDO:
        for enemigo in enemigos_nivel:
            enemigo.allies = enemigos_nivel

        for enemigo in enemigos_nivel:
            if enemigo_derrotado(enemigo) and getattr(enemigo, 'muerto_definitivo', False):
                if isinstance(enemigo, OjoVolador):
                    enemigo.update(vista_heroe, dt, width=ANCHO_MUNDO)
                continue

            if getattr(enemigo, "esperando_jugador", False):
                distancia_horizontal = abs(
                    vista_heroe.pos_x - enemigo.rect.centerx
                )
                distancia_vertical = abs(
                    vista_heroe.hurtbox.centery - enemigo.rect.centery
                )
                if (
                    distancia_horizontal <= enemigo.distancia_vision
                    and distancia_vertical <= 300
                ):
                    enemigo.esperando_jugador = False
                else:
                    actualizar_animacion_idle(enemigo, dt)
                    continue

            enemigo.suelo_y = POSICION_SUELO
            enemigo.plataformas = plataformas_nivel
            enemigo.update(vista_heroe, dt, width=ANCHO_MUNDO)

            if enemigo.health <= 0:
                continue

            if not getattr(enemigo, "es_cofre_cerrado", False):
                heroe.comprobar_golpe(enemigo)

            hb = getattr(enemigo, 'hitbox', None)
            if hb is not None and hb.width > 0 and not getattr(enemigo, 'has_hit', False):
                if hb.colliderect(vista_heroe.hurtbox):
                    heroe.take_damage(
                        getattr(enemigo, 'dano_ataque', 5),
                        attacker=enemigo,
                    )
                    enemigo.has_hit = True

        heroe.comprobar_golpes_proyectiles(enemigos_nivel)

        enemigos_cercanos = [
            enemigo for enemigo in enemigos_nivel
            if isinstance(enemigo, (OrcoRojo, Karasu_tengu))
            and enemigo.health > 0
            and not getattr(enemigo, "esperando_jugador", False)
            and not getattr(enemigo, "muerto_definitivo", False)
            and abs(enemigo.rect.centerx - vista_heroe.pos_x) <= 175
            and abs(enemigo.rect.centery - vista_heroe.hurtbox.centery) <= 95
        ]
        grupo_listo_para_atacar = bool(enemigos_cercanos) and all(
            not enemigo.attacking and enemigo.attack_cooldown <= 0
            for enemigo in enemigos_cercanos
        )
        if grupo_listo_para_atacar:
            for enemigo in enemigos_cercanos:
                enemigo.attack()

        separar_enemigos(enemigos_nivel, ANCHO_MUNDO)

    elif fase_nivel in ENEMIGOS_POR_ESCENA:
        for enemigo in enemigos_escena:
            enemigo.allies = enemigos_escena

        for enemigo in enemigos_escena:
            if enemigo_derrotado(enemigo) and getattr(
                enemigo, "muerto_definitivo", False
            ):
                continue

            if getattr(enemigo, "esperando_jugador", False):
                distancia_horizontal = abs(
                    vista_heroe.pos_x - enemigo.rect.centerx
                )
                distancia_vertical = abs(
                    vista_heroe.hurtbox.centery - enemigo.rect.centery
                )
                if (
                    distancia_horizontal <= enemigo.distancia_vision
                    and distancia_vertical <= 300
                ):
                    enemigo.esperando_jugador = False
                else:
                    actualizar_animacion_idle(enemigo, dt)
                    continue

            enemigo.suelo_y = POSICION_SUELO
            enemigo.plataformas = []
            enemigo.update(vista_heroe, dt, width=ANCHO)

            if enemigo.health <= 0:
                continue

            heroe.comprobar_golpe(enemigo)
            hb = getattr(enemigo, "hitbox", None)
            if (
                hb is not None
                and hb.width > 0
                and not getattr(enemigo, "has_hit", False)
                and hb.colliderect(vista_heroe.hurtbox)
            ):
                heroe.take_damage(
                    getattr(enemigo, "dano_ataque", 5),
                    attacker=enemigo,
                )
                enemigo.has_hit = True

        heroe.comprobar_golpes_proyectiles(enemigos_escena)

        enemigos_cercanos = [
            enemigo
            for enemigo in enemigos_escena
            if enemigo.health > 0
            and not getattr(enemigo, "esperando_jugador", False)
            and not getattr(enemigo, "muerto_definitivo", False)
            and abs(enemigo.rect.centerx - vista_heroe.pos_x) <= 175
            and abs(enemigo.rect.centery - vista_heroe.hurtbox.centery) <= 95
        ]
        for enemigo in enemigos_cercanos:
            if not enemigo.attacking and enemigo.attack_cooldown <= 0:
                enemigo.attack()

        separar_enemigos(enemigos_escena, ANCHO)

    elif fase_nivel in FASES_CONDUCTO:
        indice_conducto = FASES_CONDUCTO.index(fase_nivel)
        progreso_jugador_conducto = (
            indice_conducto * ANCHO + heroe.pos_x
        )
        if fase_nivel == FASE_CONDUCTO_1 and heroe.pos_x >= 350:
            if not perseguidor_activo:
                perseguidor_activo = True
                perseguidor_x = progreso_jugador_conducto - 500
                iniciar_musica_persecucion()

        if perseguidor_activo:
            if perseguidor_x < progreso_jugador_conducto:
                perseguidor_x = min(
                    perseguidor_x + VELOCIDAD_PERSEGUIDOR * dt,
                    progreso_jugador_conducto,
                )
            monstruo_frame = (
                monstruo_frame + dt * VELOCIDAD_ANIM_MONSTRUO
            ) % len(frames_monstruo_carne)

            distancia_contacto = DISTANCIA_CONTACTO_MONSTRUO
            if abs(progreso_jugador_conducto - perseguidor_x) <= distancia_contacto:
                detener_musica_persecucion()
                mostrar_menu_muerte(pantalla)
                ejecutando = False
                break

    if fase_nivel == FASE_RECORRIDO:
        for i in range((ANCHO_MUNDO + ANCHO - 1) // ANCHO):
            pos_x_fondo = i * ANCHO - scroll_x
            if -ANCHO < pos_x_fondo < ANCHO:
                indice_fondo = min(i, len(fondos) - 1)
                if not biblioteca_ingresada and i == 4:
                    indice_fondo = 3
                pantalla.blit(fondos[indice_fondo], (pos_x_fondo, 0))

        dibujar_plataformas(
            pantalla, scroll_x, plataformas_nivel, disenos_plataformas
        )
    else:
        pantalla.blit(fondos_escena[fase_nivel], (0, 0))
        if fase_nivel in PLATAFORMAS_ESCENA:
            dibujar_plataformas(
                pantalla,
                0,
                PLATAFORMAS_ESCENA[fase_nivel],
                disenos_plataformas_escena[fase_nivel],
            )

        if (
            fase_nivel in FASES_CONDUCTO
            and perseguidor_activo
        ):
            indice_conducto = FASES_CONDUCTO.index(fase_nivel)
            posicion_local_perseguidor = (
                perseguidor_x - indice_conducto * ANCHO
            )
            if -200 < posicion_local_perseguidor < ANCHO + 200:
                imagen_perseguidor = frames_monstruo_carne[
                    int(monstruo_frame)
                ]
                posicion_perseguidor_y = obtener_suelo_conducto(
                    fase_nivel,
                    max(0, min(ANCHO, posicion_local_perseguidor)),
                )
                rect_perseguidor = imagen_perseguidor.get_rect(
                    midbottom=(
                        round(posicion_local_perseguidor),
                        posicion_perseguidor_y,
                    )
                )
                pantalla.blit(imagen_perseguidor, rect_perseguidor)

        if fase_nivel in ENEMIGOS_POR_ESCENA:
            for enemigo in enemigos_escena:
                if not getattr(enemigo, "muerto_definitivo", False):
                    enemigo.draw(pantalla)

    if fase_nivel in FASES_CONDUCTO:
        imagen_heroe = heroe.image
        rect_heroe = imagen_heroe.get_rect(
            midbottom=(heroe.rect.centerx, heroe.rect.bottom)
        )
        pantalla.blit(imagen_heroe, rect_heroe)
    else:
        todos_los_sprites.draw(pantalla)
    if hasattr(heroe, "proyectiles"):
        heroe.proyectiles.draw(pantalla)

    if fase_nivel == FASE_RECORRIDO:
        for enemigo in enemigos_nivel:
            if isinstance(enemigo, OjoVolador):
                enemigo.draw(pantalla, scroll_x)
            elif not getattr(enemigo, 'muerto_definitivo', False):
                pos_x_orig = enemigo.rect.x
                enemigo.rect.x -= scroll_x
                enemigo.draw(pantalla)
                enemigo.rect.x = pos_x_orig

    progreso = calcular_progreso_nivel(fase_nivel, heroe.pos_x)
    if fase_nivel == FASE_RECORRIDO and enemigos_pendientes:
        str_progreso = (
            f"RUMBO AL PORTAL: {progreso}%"
            f"  |  ENEMIGOS: {len(enemigos_pendientes)}"
        )
        color_progreso = (255, 190, 90)
    else:
        str_progreso = f"RUMBO AL PORTAL: {progreso}%"
        color_progreso = (230, 210, 160)

    txt_progreso_sombra = fuente_progreso.render(str_progreso, True, (0, 0, 0))
    txt_progreso = fuente_progreso.render(str_progreso, True, color_progreso)
    rect_progreso = txt_progreso.get_rect(topright=(ANCHO - 30, 20))
    pantalla.blit(
        txt_progreso_sombra, (rect_progreso.x + 2, rect_progreso.y + 2)
    )
    pantalla.blit(txt_progreso, rect_progreso)

    dibujar_barra_jugador(pantalla, heroe)

    if requiere_interaccion(fase_nivel, heroe.pos_x):
        dibujar_boton_demoniaco(pantalla, "PRESIONA C PARA ENTRAR")

    pygame.display.flip()
if not NIVEL_INTEGRADO:
    pygame.quit()
    sys.exit()