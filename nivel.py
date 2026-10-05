import pygame
import os
import sys
import math

from jugadores import p_viento
from jugadores import p_tierra
from jugadores import p_fuego


# ============================================================
# INICIALIZAR PYGAME
# ============================================================

pygame.init()
pygame.font.init()


# ============================================================
# CONFIGURACIÓN DE PANTALLA
# ============================================================

ANCHO = 1350
ALTO = 700

pantalla = pygame.display.set_mode(
    (ANCHO, ALTO)
)

pygame.display.set_caption("Nivel 1")

reloj = pygame.time.Clock()

FPS = 60


# ============================================================
# CONFIGURACIÓN DEL ESCENARIO
# ============================================================

POSICION_SUELO = 620

CANTIDAD_FONDOS = 3

ANCHO_MUNDO = ANCHO * CANTIDAD_FONDOS


# ============================================================
# ZONA DE INTERACCIÓN
# ============================================================

HUECO_INICIO = ANCHO + 600
HUECO_FIN = ANCHO + 800

HUECO_CENTRO_X = (
    HUECO_INICIO + HUECO_FIN
) // 2


# ============================================================
# FUENTES
# ============================================================

fuente_pixel = pygame.font.SysFont(
    "Courier",
    20,
    bold=True
)

fuente_boss_title = pygame.font.SysFont(
    "Georgia",
    76,
    bold=True
)

fuente_boss_subtitle = pygame.font.SysFont(
    "Georgia",
    32,
    italic=True
)


# ============================================================
# CARGAR FONDOS
# ============================================================

fondos = []

for i in range(1, CANTIDAD_FONDOS + 1):

    ruta_imagen = os.path.join(
        "imagenes",
        "Nivel1",
        f"Nivel1_imagen{i}.png"
    )

    imagen = pygame.image.load(
        ruta_imagen
    ).convert()

    imagen = pygame.transform.scale(
        imagen,
        (ANCHO, ALTO)
    )

    fondos.append(imagen)


# ============================================================
# BOTÓN DE INTERACCIÓN
# ============================================================

def dibujar_boton_interaccion(
    superficie,
    centro_x,
    centro_y
):

    offset_y = math.sin(
        pygame.time.get_ticks() * 0.006
    ) * 8

    pos_y = int(
        centro_y + offset_y
    )

    texto = fuente_pixel.render(
        "[ PRESS C TO INTERACT ]",
        False,
        (255, 230, 150)
    )

    rect_texto = texto.get_rect(
        center=(
            centro_x,
            pos_y
        )
    )

    ancho_box = rect_texto.width + 24
    alto_box = rect_texto.height + 16

    rect_box = pygame.Rect(
        0,
        0,
        ancho_box,
        alto_box
    )

    rect_box.center = (
        centro_x,
        pos_y
    )

    pygame.draw.rect(
        superficie,
        (20, 20, 25),
        rect_box
    )

    pygame.draw.rect(
        superficie,
        (220, 180, 60),
        rect_box,
        4
    )

    pygame.draw.rect(
        superficie,
        (100, 75, 20),
        rect_box.inflate(-8, -8),
        2
    )

    superficie.blit(
        texto,
        rect_texto
    )


# ============================================================
# PANTALLA DE ATHROS
# ============================================================

def mostrar_athros():

    pantalla.fill(
        (0, 0, 0)
    )

    titulo = fuente_boss_title.render(
        "Athros",
        True,
        (180, 20, 20)
    )

    subtitulo = fuente_boss_subtitle.render(
        "the bloodred",
        True,
        (140, 15, 15)
    )

    rect_titulo = titulo.get_rect(
        center=(
            ANCHO // 2,
            ALTO // 2 - 25
        )
    )

    rect_subtitulo = subtitulo.get_rect(
        center=(
            ANCHO // 2,
            ALTO // 2 + 45
        )
    )

    pantalla.blit(
        titulo,
        rect_titulo
    )

    pantalla.blit(
        subtitulo,
        rect_subtitulo
    )

    pygame.display.flip()

    pygame.time.wait(2000)


# ============================================================
# CREAR JUGADORES
# ============================================================

heroe1 = p_viento(
    200,
    POSICION_SUELO,
    POSICION_SUELO
)

heroe2 = p_tierra(
    200,
    POSICION_SUELO,
    POSICION_SUELO
)

heroe3 = p_fuego(
    200,
    POSICION_SUELO,
    POSICION_SUELO
)


# ============================================================
# JUGADOR ACTUAL
# ============================================================
#
# None   = todavía no se eligió personaje
# heroe1 = P_viento
# heroe2 = P_tierra
# heroe3 = P_fuego
#

jugador_actual = None


# ============================================================
# GRUPO DE SPRITES
# ============================================================

todos_los_sprites = pygame.sprite.Group()


# ============================================================
# CÁMARA
# ============================================================

scroll_x = 0


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

ejecutando = True

while ejecutando:

    # ========================================================
    # COMPROBAR ZONA DE INTERACCIÓN
    # ========================================================

    if jugador_actual is not None:

        en_zona_hueco = (
            HUECO_INICIO
            <= jugador_actual.pos_x
            <= HUECO_FIN
        )

    else:

        en_zona_hueco = False


    # ========================================================
    # EVENTOS
    # ========================================================

    for evento in pygame.event.get():

        # ====================================================
        # CERRAR JUEGO
        # ====================================================

        if evento.type == pygame.QUIT:

            ejecutando = False


        # ====================================================
        # SELECCIONAR P_VIENTO - U
        # ====================================================

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_u
            and jugador_actual is None
        ):

            jugador_actual = heroe1

            todos_los_sprites.empty()

            todos_los_sprites.add(
                jugador_actual
            )


        # ====================================================
        # SELECCIONAR P_TIERRA - I
        # ====================================================

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_i
            and jugador_actual is None
        ):

            jugador_actual = heroe2

            todos_los_sprites.empty()

            todos_los_sprites.add(
                jugador_actual
            )


        # ====================================================
        # SELECCIONAR P_FUEGO - J
        # ====================================================

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_j
            and jugador_actual is None
        ):

            jugador_actual = heroe3

            todos_los_sprites.empty()

            todos_los_sprites.add(
                jugador_actual
            )


        # ====================================================
        # INTERACCIÓN CON C
        # ====================================================

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and en_zona_hueco
            and jugador_actual is not None
        ):

            # ------------------------------------------------
            # MOSTRAR PANTALLA DE ATHROS
            # ------------------------------------------------

            mostrar_athros()

            # ------------------------------------------------
            # TELETRANSPORTAR JUGADOR ACTUAL
            # ------------------------------------------------

            jugador_actual.pos_x = (
                ANCHO * 2 + 150
            )

            # ------------------------------------------------
            # ACTUALIZAR CÁMARA
            # ------------------------------------------------

            scroll_x = (
                ANCHO * 2
            )

            # ------------------------------------------------
            # LIMPIAR EVENTOS
            # ------------------------------------------------

            pygame.event.clear()

            break


        # ====================================================
        # EVENTOS DEL JUGADOR
        # ====================================================

        if jugador_actual is not None:

            jugador_actual.procesar_evento(
                evento
            )


    # ========================================================
    # CÁMARA
    # ========================================================

    if jugador_actual is not None:

        target_scroll = int(
            jugador_actual.pos_x
            - ANCHO // 2
        )

        # ----------------------------------------------------
        # LA CÁMARA SOLAMENTE AVANZA
        # ----------------------------------------------------

        scroll_x = max(
            scroll_x,
            min(
                target_scroll,
                ANCHO_MUNDO - ANCHO
            )
        )


    # ========================================================
    # ACTUALIZAR JUGADOR
    # ========================================================

    if jugador_actual is not None:

        todos_los_sprites.update(
            scroll_x,
            ANCHO_MUNDO
        )


    # ========================================================
    # DIBUJAR FONDOS
    # ========================================================

    for i, fondo in enumerate(fondos):

        posicion_x = (
            i * ANCHO
            - scroll_x
        )

        if (
            -ANCHO
            < posicion_x
            < ANCHO
        ):

            pantalla.blit(
                fondo,
                (
                    posicion_x,
                    0
                )
            )


    # ========================================================
    # DIBUJAR INTERACCIÓN
    # ========================================================

    posicion_hueco_pantalla = (
        HUECO_CENTRO_X
        - scroll_x
    )

    if (
        -150
        < posicion_hueco_pantalla
        < ANCHO + 150
    ):

        if jugador_actual is not None:

            dibujar_boton_interaccion(
                pantalla,
                posicion_hueco_pantalla,
                POSICION_SUELO - 110
            )


    # ========================================================
    # DIBUJAR JUGADOR
    # ========================================================

    if jugador_actual is not None:

        todos_los_sprites.draw(
            pantalla
        )


    # ========================================================
    # ACTUALIZAR PANTALLA
    # ========================================================

    pygame.display.flip()

    reloj.tick(FPS)


# ============================================================
# CERRAR
# ============================================================

pygame.quit()
sys.exit()
