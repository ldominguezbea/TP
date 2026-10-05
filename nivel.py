import pygame
import os
import sys
import math

from jugadores import p_viento


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

    # Fondo
    pygame.draw.rect(
        superficie,
        (20, 20, 25),
        rect_box
    )

    # Borde exterior
    pygame.draw.rect(
        superficie,
        (220, 180, 60),
        rect_box,
        4
    )

    # Borde interior
    pygame.draw.rect(
        superficie,
        (100, 75, 20),
        rect_box.inflate(-8, -8),
        2
    )

    # Texto
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
# CREAR JUGADOR
# ============================================================

heroe = p_viento(
    200,
    POSICION_SUELO,
    POSICION_SUELO
)


# ============================================================
# ESTADO DEL JUGADOR
# ============================================================

# IMPORTANTE:
# El jugador existe, pero NO está visible al comenzar.

jugador_visible = False


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

    # --------------------------------------------------------
    # COMPROBAR ZONA DE INTERACCIÓN
    # --------------------------------------------------------

    en_zona_hueco = (
        jugador_visible
        and HUECO_INICIO
        <= heroe.pos_x
        <= HUECO_FIN
    )

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    for evento in pygame.event.get():

        # ====================================================
        # CERRAR JUEGO
        # ====================================================

        if evento.type == pygame.QUIT:

            ejecutando = False

        # ====================================================
        # TECLA U
        # ====================================================
        #
        # Al presionar U aparece el héroe.
        #

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_u
            and not jugador_visible
        ):

            jugador_visible = True

            todos_los_sprites.add(
                heroe
            )

        # ====================================================
        # INTERACCIÓN CON C
        # ====================================================

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and en_zona_hueco
        ):

            # Mostrar pantalla de Athros
            mostrar_athros()

            # ------------------------------------------------
            # TELETRANSPORTE
            # ------------------------------------------------

            heroe.pos_x = (
                ANCHO * 2 + 150
            )

            scroll_x = (
                ANCHO * 2
            )

            pygame.event.clear()

            break

        # ====================================================
        # EVENTOS DEL JUGADOR
        # ====================================================

        if jugador_visible:

            heroe.procesar_evento(
                evento
            )

    # ========================================================
    # CÁMARA
    # ========================================================

    if jugador_visible:

        target_scroll = int(
            heroe.pos_x
            - ANCHO // 2
        )

        # La cámara solamente avanza
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

    if jugador_visible:

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

        # Solo mostrar la interacción
        # cuando el jugador ya apareció.

        if jugador_visible:

            dibujar_boton_interaccion(
                pantalla,
                posicion_hueco_pantalla,
                POSICION_SUELO - 110
            )

    # ========================================================
    # DIBUJAR JUGADOR
    # ========================================================

    if jugador_visible:

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
