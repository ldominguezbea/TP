import pygame
import os
import sys
import math

from jugador1 import p_viento
from jugador2 import p_tierra
from jugador3 import p_fuego
from jugador4 import p_planta


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

pantalla = pygame.display.set_mode((ANCHO, ALTO))

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

fondos = []

for i in range(1, CANTIDAD_FONDOS + 1):

    ruta_imagen = os.path.join(
        BASE_DIR,
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
        center=(centro_x, pos_y)
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

    pantalla.fill((0, 0, 0))

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
# CLASE ENEMIGO
# ============================================================

class Enemigo(pygame.sprite.Sprite):

    def __init__(self, x, posicion_suelo):
        super().__init__()

        self.ancho = 40
        self.alto = 100
        self.velocidad = 2
        self.velocidad_salto = -12
        self.gravedad = 0.6

        self.posicion_suelo = posicion_suelo

        # Posición del enemigo en el mundo.
        self.pos_x = float(x)
        self.pos_y = float(posicion_suelo - self.alto)

        # Cuerpo rectangular azul.
        self.image = pygame.Surface(
            (self.ancho, self.alto)
        )
        self.image.fill((0, 0, 255))

        self.rect = self.image.get_rect()

        # Hurtbox invisible.
        self.hurtbox = pygame.Rect(
            0, 0, self.ancho, self.alto
        )

        # Hitbox roja que aparece durante el ataque.
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.hitbox_activa = False
        self.duracion_ataque = 250
        self.tiempo_ataque = 0
        self.cooldown_ataque = 1000
        self.ultimo_ataque = -self.cooldown_ataque

        self.direccion = -1
        self.atacando = False

        # Salto.
        self.velocidad_vertical = 0
        self.en_suelo = True
        self.proximo_salto = pygame.time.get_ticks() + 2000

    def actualizar_rectangulos(self, scroll_x):

        # Rectángulos en coordenadas de pantalla.
        self.rect.topleft = (
            int(self.pos_x - scroll_x),
            int(self.pos_y)
        )

        self.hurtbox.topleft = self.rect.topleft

        # Actualizar la hitbox roja según la dirección.
        if self.hitbox_activa:

            if self.direccion == 1:
                self.hitbox = pygame.Rect(
                    self.rect.right,
                    self.rect.top + 20,
                    45,
                    50
                )

            else:
                self.hitbox = pygame.Rect(
                    self.rect.left - 45,
                    self.rect.top + 20,
                    45,
                    50
                )

    def iniciar_ataque(self, ahora):

        self.atacando = True
        self.hitbox_activa = True
        self.tiempo_ataque = ahora
        self.ultimo_ataque = ahora

    def update(self, jugador, scroll_x, ancho_mundo):

        ahora = pygame.time.get_ticks()

        # Actualizar posición visual y hurtbox.
        self.actualizar_rectangulos(scroll_x)

        if jugador is None:
            self.hitbox_activa = False
            self.atacando = False
            return

        # Posición del jugador en el mundo.
        jugador_x = jugador.pos_x

        diferencia_x = jugador_x - self.pos_x

        # Determinar hacia dónde mira el enemigo.
        if diferencia_x > 0:
            self.direccion = 1

        elif diferencia_x < 0:
            self.direccion = -1

        # Terminar el ataque después de su duración.
        if self.atacando:

            if ahora - self.tiempo_ataque >= self.duracion_ataque:
                self.atacando = False
                self.hitbox_activa = False

        # Si está atacando, permanece quieto.
        if not self.atacando:

            # Atacar cuando el jugador está cerca.
            if (
                abs(diferencia_x) <= 100
                and ahora - self.ultimo_ataque
                >= self.cooldown_ataque
            ):
                self.iniciar_ataque(ahora)

            else:

                # Perseguir al jugador.
                if abs(diferencia_x) > 5:
                    self.pos_x += (
                        self.direccion * self.velocidad
                    )

                # Saltar ocasionalmente mientras persigue.
                if (
                    self.en_suelo
                    and ahora >= self.proximo_salto
                ):
                    self.velocidad_vertical = self.velocidad_salto
                    self.en_suelo = False

                    self.proximo_salto = (
                        ahora + 2000 + int(
                            pygame.time.get_ticks() % 2500
                        )
                    )

        # Aplicar gravedad.
        if not self.en_suelo:

            self.velocidad_vertical += self.gravedad
            self.pos_y += self.velocidad_vertical

            suelo_y = self.posicion_suelo - self.alto

            if self.pos_y >= suelo_y:
                self.pos_y = suelo_y
                self.velocidad_vertical = 0
                self.en_suelo = True

        # Mantener al enemigo dentro del mundo.
        self.pos_x = max(
            0,
            min(
                self.pos_x,
                ancho_mundo - self.ancho
            )
        )

        # Actualizar rectángulos con la posición nueva.
        self.actualizar_rectangulos(scroll_x)

    def draw(self, superficie, scroll_x):

        self.actualizar_rectangulos(scroll_x)

        # Dibujar el cuerpo azul.
        superficie.blit(
            self.image,
            self.rect
        )

        # Dibujar la hitbox roja durante el ataque.
        if self.hitbox_activa:

            pygame.draw.rect(
                superficie,
                (255, 0, 0),
                self.hitbox
            )
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

heroe4 = p_planta(
    200,
    POSICION_SUELO,
    POSICION_SUELO
)


# ============================================================
# JUGADOR ACTUAL
# ============================================================

jugador_actual = None
# ============================================================
# ENEMIGO
# ============================================================

enemigo = Enemigo(
    ANCHO + 400,
    POSICION_SUELO
)

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

        # CERRAR JUEGO
        if evento.type == pygame.QUIT:

            ejecutando = False
            continue

        # ----------------------------------------------------
        # SELECCIONAR P_VIENTO - U
        # ----------------------------------------------------

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_u
            and jugador_actual is None
        ):

            jugador_actual = heroe1

            todos_los_sprites.empty()
            todos_los_sprites.add(jugador_actual)

        # ----------------------------------------------------
        # SELECCIONAR P_TIERRA - I
        # ----------------------------------------------------

        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_i
            and jugador_actual is None
        ):

            jugador_actual = heroe2

            todos_los_sprites.empty()
            todos_los_sprites.add(jugador_actual)

        # ----------------------------------------------------
        # SELECCIONAR P_FUEGO - J
        # ----------------------------------------------------

        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_j
            and jugador_actual is None
        ):

            jugador_actual = heroe3

            todos_los_sprites.empty()
            todos_los_sprites.add(jugador_actual)

        # ----------------------------------------------------
        # SELECCIONAR P_PLANTA - K
        # ----------------------------------------------------

        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_k
            and jugador_actual is None
        ):

            jugador_actual = heroe4

            todos_los_sprites.empty()
            todos_los_sprites.add(jugador_actual)

        # ----------------------------------------------------
        # INTERACCIÓN CON C
        # ----------------------------------------------------

        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and en_zona_hueco
            and jugador_actual is not None
        ):

            mostrar_athros()

            # Teletransportar al jugador.
            jugador_actual.pos_x = ANCHO * 2 + 150

            # Actualizar la cámara.
            scroll_x = ANCHO * 2

            # Actualizar la posición visual.
            jugador_actual.rect.centerx = int(
                jugador_actual.pos_x - scroll_x
            )

            # Evitar procesar eventos antiguos después
            # de regresar de la pantalla de Athros.
            pygame.event.clear()
            break

        # ----------------------------------------------------
        # EVENTOS DEL JUGADOR
        # ----------------------------------------------------

        if jugador_actual is not None:

            jugador_actual.procesar_evento(evento)

    # ========================================================
    # CÁMARA
    # ========================================================

    if jugador_actual is not None:

        target_scroll = int(
            jugador_actual.pos_x - ANCHO // 2
        )

        # La cámara solamente avanza.
        scroll_x = max(
            scroll_x,
            min(
                target_scroll,
                ANCHO_MUNDO - ANCHO
            )
        )

    # ========================================================
    # ACTUALIZAR JUGADOR Y PROYECTILES
    # ========================================================

    if jugador_actual is not None:

        # El jugador actualiza sus proyectiles internamente.
        # No volver a llamar proyectiles.update() aquí.
        todos_los_sprites.update(
            scroll_x,
            ANCHO_MUNDO
        )
    # ========================================================
    # ACTUALIZAR ENEMIGO
    # ========================================================

    enemigo.update(
        jugador_actual,
        scroll_x,
        ANCHO_MUNDO
    )

    # ========================================================
    # DIBUJAR FONDOS
    # ========================================================

    for i, fondo in enumerate(fondos):

        posicion_x = i * ANCHO - scroll_x

        if -ANCHO < posicion_x < ANCHO:

            pantalla.blit(
                fondo,
                (posicion_x, 0)
            )

    # ========================================================
    # DIBUJAR INTERACCIÓN
    # ========================================================

    posicion_hueco_pantalla = (
        HUECO_CENTRO_X - scroll_x
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
    # DIBUJAR PROYECTILES
    # ========================================================

    if (
        jugador_actual is not None
        and hasattr(jugador_actual, "proyectiles")
    ):

        jugador_actual.proyectiles.draw(
            pantalla
        )
    # ========================================================
    # DIBUJAR ENEMIGO
    # ========================================================

    enemigo.draw(
        pantalla,
        scroll_x
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