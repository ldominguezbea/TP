import pygame
import os
import sys
import math

pygame.init()
pygame.font.init()

# ============================================================
# CONFIGURACIÓN DEL JUEGO
# ============================================================

ANCHO, ALTO = 1350, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 1")

RELOJ = pygame.time.Clock()
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

# Hueco ubicado en la Imagen 2
HUECO_INICIO = ANCHO + 600
HUECO_FIN = ANCHO + 800
HUECO_CENTRO_X = (HUECO_INICIO + HUECO_FIN) // 2

# ============================================================
# CONFIGURACIÓN DEL JUGADOR
# ============================================================

ANCHO_HEROE = 600
ALTO_HEROE = 240

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
# CARGAR ESCENARIO
# ============================================================

fondos = []

for i in range(1, CANTIDAD_FONDOS + 1):

    ruta_imagen = os.path.join(
        "imagenes",
        "Nivel1",
        f"Nivel1_imagen{i}.png"
    )

    img = pygame.image.load(ruta_imagen).convert()

    img = pygame.transform.scale(
        img,
        (ANCHO, ALTO)
    )

    fondos.append(img)


# ============================================================
# CLASE DEL JUGADOR
# ============================================================

class Jugador(pygame.sprite.Sprite):

    def __init__(self, x, y):

        super().__init__()

        # ----------------------------------------------------
        # Animaciones
        # ----------------------------------------------------

        self.animaciones = {
            "idle": [],
            "run": [],
            "roll": [],
            "j_up": [],
            "defend": [],
            "1_atk": [],
            "2_atk": [],
            "3_atk": [],
            "air_atk": [],
            "sp_atk": []
        }

        self.cargar_animaciones()

        # ----------------------------------------------------
        # Estado
        # ----------------------------------------------------

        self.estado = "idle"
        self.frame_index = 0
        self.velocidad_animacion = 0.22

        self.image = self.animaciones[
            self.estado
        ][0]

        self.rect = self.image.get_rect(
            midbottom=(x, y)
        )

        # Posición real dentro del mundo
        self.pos_x = float(x)

        # ----------------------------------------------------
        # Física
        # ----------------------------------------------------

        self.velocidad_x = 0
        self.velocidad_y = 0

        self.velocidad_movimiento = 7
        self.fuerza_salto = -16
        self.gravedad = 0.8

        # ----------------------------------------------------
        # Estados del jugador
        # ----------------------------------------------------

        self.mirando_derecha = True

        self.en_suelo = True

        self.rodando = False
        self.defendiendo = False
        self.atacando = False

        self.combo_siguiente = False

    # ========================================================
    # CARGAR ANIMACIONES
    # ========================================================

    def cargar_animaciones(self):

        ESCALA = (
            ANCHO_HEROE,
            ALTO_HEROE
        )

        base_path = os.path.join(
            "assets",
            "Heroes",
            "P_viento"
        )

        # ----------------------------------------------------
        # Idle
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "idle",
                    f"idle_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["idle"].append(img)

        # ----------------------------------------------------
        # Run
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "run",
                    f"run_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["run"].append(img)

        # ----------------------------------------------------
        # Roll
        # ----------------------------------------------------

        for i in range(1, 7):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "roll",
                    f"roll_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["roll"].append(img)

        # ----------------------------------------------------
        # Salto
        # ----------------------------------------------------

        for i in range(1, 4):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "j_up",
                    f"j_up_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["j_up"].append(img)

        # ----------------------------------------------------
        # Defensa
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "defend",
                    f"defend_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["defend"].append(img)

        # ----------------------------------------------------
        # Ataque 1
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "1_atk",
                    f"1_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["1_atk"].append(img)

        # ----------------------------------------------------
        # Ataque 2
        # ----------------------------------------------------

        for i in range(1, 19):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "2_atk",
                    f"2_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["2_atk"].append(img)

        # ----------------------------------------------------
        # Ataque aéreo
        # ----------------------------------------------------

        for i in range(1, 8):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "air_atk",
                    f"air_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["air_atk"].append(img)

        # ----------------------------------------------------
        # Ataque especial
        # ----------------------------------------------------

        for i in range(1, 31):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "sp_atk",
                    f"sp_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["sp_atk"].append(img)

        # ----------------------------------------------------
        # Ataque 3
        # ----------------------------------------------------

        for i in range(12, 27):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "3_atk",
                    f"3_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                ESCALA
            )

            self.animaciones["3_atk"].append(img)

    # ========================================================
    # EVENTOS DEL JUGADOR
    # ========================================================

    def procesar_evento(self, evento):

        if evento.type != pygame.KEYDOWN:
            return

        # ----------------------------------------------------
        # SALTO
        # ----------------------------------------------------

        if (
            evento.key == pygame.K_w
            and self.en_suelo
            and not (
                self.atacando
                or self.rodando
                or self.defendiendo
            )
        ):

            self.velocidad_y = self.fuerza_salto
            self.en_suelo = False

        # ----------------------------------------------------
        # RODAR
        # ----------------------------------------------------

        elif (
            evento.key == pygame.K_q
            and self.en_suelo
            and not (
                self.rodando
                or self.atacando
                or self.defendiendo
            )
        ):

            self.rodando = True
            self.frame_index = 0

        # ----------------------------------------------------
        # DEFENDER
        # ----------------------------------------------------

        elif (
            evento.key == pygame.K_r
            and self.en_suelo
            and not (
                self.rodando
                or self.atacando
                or self.defendiendo
            )
        ):

            self.defendiendo = True
            self.frame_index = 0

        # ----------------------------------------------------
        # ATAQUE ESPECIAL
        # ----------------------------------------------------

        elif (
            evento.key == pygame.K_e
            and self.en_suelo
            and not (
                self.rodando
                or self.atacando
                or self.defendiendo
            )
        ):

            self.atacando = True
            self.estado = "sp_atk"
            self.frame_index = 0

        # ----------------------------------------------------
        # ATAQUE NORMAL / COMBO
        # ----------------------------------------------------

        elif evento.key == pygame.K_f:

            # Ataque aéreo
            if not self.en_suelo and not self.atacando:

                self.atacando = True
                self.estado = "air_atk"
                self.frame_index = 0

            # Ataque terrestre
            elif (
                self.en_suelo
                and not (
                    self.rodando
                    or self.defendiendo
                )
            ):

                if not self.atacando:

                    self.atacando = True
                    self.estado = "1_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False

                elif self.estado in [
                    "1_atk",
                    "2_atk"
                ]:

                    self.combo_siguiente = True

    # ========================================================
    # MOVIMIENTO
    # ========================================================

    def manejar_movimiento_continuo(self):

        teclas = pygame.key.get_pressed()

        # No moverse durante estas acciones
        if (
            self.rodando
            or self.defendiendo
            or (
                self.atacando
                and self.en_suelo
            )
        ):

            self.velocidad_x = 0
            return

        self.velocidad_x = 0

        # Izquierda
        if teclas[pygame.K_a]:

            self.velocidad_x = -self.velocidad_movimiento
            self.mirando_derecha = False

        # Derecha
        if teclas[pygame.K_d]:

            self.velocidad_x = self.velocidad_movimiento
            self.mirando_derecha = True

    # ========================================================
    # ACTUALIZAR ESTADO
    # ========================================================

    def actualizar_estado(self):

        if self.rodando:

            self.estado = "roll"

        elif self.defendiendo:

            self.estado = "defend"

        elif self.atacando:

            pass

        elif not self.en_suelo:

            self.estado = "j_up"

        elif self.velocidad_x != 0:

            self.estado = "run"

        else:

            self.estado = "idle"

    # ========================================================
    # ANIMACIONES
    # ========================================================

    def animar(self):

        anim = self.animaciones[self.estado]

        self.frame_index += self.velocidad_animacion

        # Terminó la animación
        if self.frame_index >= len(anim):

            self.frame_index = 0

            # Roll
            if self.rodando:

                self.rodando = False

            # Defensa
            elif self.defendiendo:

                self.defendiendo = False

            # Ataques que terminan directamente
            elif self.estado in [
                "air_atk",
                "sp_atk",
                "3_atk"
            ]:

                self.atacando = False

            # Ataque 1
            elif self.estado == "1_atk":

                if self.combo_siguiente:

                    self.estado = "2_atk"
                    self.combo_siguiente = False

                else:

                    self.atacando = False

            # Ataque 2
            elif self.estado == "2_atk":

                if self.combo_siguiente:

                    self.estado = "3_atk"
                    self.combo_siguiente = False

                else:

                    self.atacando = False

        frame_actual = anim[
            int(self.frame_index)
        ]

        # Girar personaje
        if not self.mirando_derecha:

            self.image = pygame.transform.flip(
                frame_actual,
                True,
                False
            )

        else:

            self.image = frame_actual

    # ========================================================
    # GRAVEDAD
    # ========================================================

    def aplicar_gravedad(self):

        self.velocidad_y += self.gravedad

        self.rect.y += self.velocidad_y

        # Suelo
        if self.rect.bottom >= POSICION_SUELO:

            self.rect.bottom = POSICION_SUELO

            self.velocidad_y = 0
            self.en_suelo = True

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, scroll_x):

        self.manejar_movimiento_continuo()

        # Velocidad extra al rodar
        if self.rodando:

            self.velocidad_x = (
                self.velocidad_movimiento + 3
            ) * (
                1 if self.mirando_derecha else -1
            )

        # Actualizar posición global
        self.pos_x += self.velocidad_x

        # ----------------------------------------------------
        # LÍMITES DEL MUNDO
        # ----------------------------------------------------

        limite_izquierdo = scroll_x + 80

        self.pos_x = max(
            limite_izquierdo,
            min(
                self.pos_x,
                ANCHO_MUNDO - 80
            )
        )

        # Convertir posición del mundo a pantalla
        self.rect.centerx = int(
            self.pos_x - scroll_x
        )

        # Física
        self.aplicar_gravedad()

        # Estado
        self.actualizar_estado()

        # Animación
        self.animar()


# ============================================================
# BOTÓN DE INTERACCIÓN
# ============================================================

def dibujar_boton_pixel_art(
    pantalla,
    centro_x,
    centro_y
):

    # Animación flotante
    offset_y = math.sin(
        pygame.time.get_ticks() * 0.006
    ) * 8

    pos_y = int(
        centro_y + offset_y
    )

    # Texto
    texto = fuente_pixel.render(
        "[ PRESS C TO INTERACT ]",
        False,
        (255, 230, 150)
    )

    rect_txt = texto.get_rect(
        center=(centro_x, pos_y)
    )

    # Tamaño del cuadro
    ancho_box = rect_txt.width + 24
    alto_box = rect_txt.height + 16

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
        pantalla,
        (20, 20, 25),
        rect_box
    )

    # Borde exterior
    pygame.draw.rect(
        pantalla,
        (220, 180, 60),
        rect_box,
        4
    )

    # Borde interior
    pygame.draw.rect(
        pantalla,
        (100, 75, 20),
        rect_box.inflate(-8, -8),
        2
    )

    # Texto
    pantalla.blit(
        texto,
        rect_txt
    )


# ============================================================
# PANTALLA DE INTERACCIÓN
# ============================================================

def pantalla_athros():

    pantalla.fill(
        (0, 0, 0)
    )

    # Título
    txt_title = fuente_boss_title.render(
        "Athros",
        True,
        (180, 20, 20)
    )

    # Subtítulo
    txt_subtitle = fuente_boss_subtitle.render(
        "the bloodred",
        True,
        (140, 15, 15)
    )

    # Posiciones
    rect_title = txt_title.get_rect(
        center=(
            ANCHO // 2,
            ALTO // 2 - 25
        )
    )

    rect_subtitle = txt_subtitle.get_rect(
        center=(
            ANCHO // 2,
            ALTO // 2 + 45
        )
    )

    # Dibujar
    pantalla.blit(
        txt_title,
        rect_title
    )

    pantalla.blit(
        txt_subtitle,
        rect_subtitle
    )

    pygame.display.flip()

    # Esperar 2 segundos
    pygame.time.wait(2000)


# ============================================================
# CREAR JUGADOR
# ============================================================

heroe = Jugador(
    200,
    POSICION_SUELO
)

todos_los_sprites = pygame.sprite.Group()

todos_los_sprites.add(
    heroe
)


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
    # COMPROBAR SI ESTÁ EN LA ZONA DE INTERACCIÓN
    # --------------------------------------------------------

    en_zona_hueco = (
        HUECO_INICIO
        <= heroe.pos_x
        <= HUECO_FIN
    )

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    for evento in pygame.event.get():

        # Cerrar juego
        if evento.type == pygame.QUIT:

            ejecutando = False

        # ----------------------------------------------------
        # INTERACCIÓN CON C
        # ----------------------------------------------------

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and en_zona_hueco
        ):

            # Mostrar pantalla de Athros
            pantalla_athros()

            # ------------------------------------------------
            # TELETRANSPORTE AL INICIO DE LA IMAGEN 3
            # ------------------------------------------------

            heroe.pos_x = (
                ANCHO * 2 + 150
            )

            scroll_x = (
                ANCHO * 2
            )

            # Limpiar eventos pendientes
            pygame.event.clear()

            break

        # Eventos del jugador
        heroe.procesar_evento(
            evento
        )

    # --------------------------------------------------------
    # CÁMARA
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ACTUALIZAR JUGADOR
    # --------------------------------------------------------

    todos_los_sprites.update(
        scroll_x
    )

    # --------------------------------------------------------
    # DIBUJAR ESCENARIO
    # --------------------------------------------------------

    for i, fondo_img in enumerate(fondos):

        pos_x_fondo = (
            i * ANCHO
            - scroll_x
        )

        if (
            -ANCHO
            < pos_x_fondo
            < ANCHO
        ):

            pantalla.blit(
                fondo_img,
                (
                    pos_x_fondo,
                    0
                )
            )

    # --------------------------------------------------------
    # DIBUJAR INTERACCIÓN
    # --------------------------------------------------------

    screen_hueco_x = (
        HUECO_CENTRO_X
        - scroll_x
    )

    if (
        -150
        < screen_hueco_x
        < ANCHO + 150
    ):

        dibujar_boton_pixel_art(
            pantalla,
            screen_hueco_x,
            POSICION_SUELO - 110
        )

    # --------------------------------------------------------
    # DIBUJAR JUGADOR
    # --------------------------------------------------------

    todos_los_sprites.draw(
        pantalla
    )

    # --------------------------------------------------------
    # ACTUALIZAR PANTALLA
    # --------------------------------------------------------

    pygame.display.flip()

    RELOJ.tick(FPS)


# ============================================================
# CERRAR PYGAME
# ============================================================

pygame.quit()
sys.exit()