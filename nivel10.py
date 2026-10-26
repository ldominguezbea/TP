import os
import sys
import random
import pygame
from jugador2 import p_tierra
from jugador1 import p_viento
from enemigos import OrcoRojo, OjoVolador, Karasu_tengu

pygame.init()
pygame.font.init()

# 1. Configuración de pantalla y mundo
ANCHO, ALTO = 1350, 700
POSICION_SUELO = 620

CANTIDAD_FONDOS = 3
ANCHO_MUNDO = ANCHO * 7
PORTAL_X = ANCHO_MUNDO - 500
HUECO_INICIO = PORTAL_X - 150
HUECO_FIN = PORTAL_X + 150

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 1 - Batalla de Jefe")

ANCHO_HEROE, ALTO_HEROE = 300, 300

fuente_lava_pixel = pygame.font.SysFont("Courier", 9, bold=True)
fuente_boss_title = pygame.font.SysFont("Georgia", 76, bold=True)
fuente_boss_subtitle = pygame.font.SysFont("Georgia", 32, italic=True)
fuente_jefe = pygame.font.SysFont("Georgia", 26, bold=True, italic=True)
fuente_ui = pygame.font.SysFont("Arial", 16, bold=True)
fuente_progreso = pygame.font.SysFont("Impact", 22)


# =========================================================
# CARGA DE IMÁGENES Y CÓMICS
# =========================================================

def cargar_imagen_comic(nombre_archivo):
    rutas = [
        os.path.join("imagenes", "Nivel1", nombre_archivo),
        os.path.join("assets", "imagenes", "Nivel1", nombre_archivo)
    ]

    for ruta in rutas:
        if os.path.exists(ruta):
            try:
                img = pygame.image.load(ruta).convert()
                return pygame.transform.scale(img, (ANCHO, ALTO))
            except Exception as e:
                print(f"Error al cargar {ruta}: {e}")

    surf = pygame.Surface((ANCHO, ALTO))
    surf.fill((15, 15, 20))

    txt = fuente_boss_subtitle.render(
        f"[{nombre_archivo} no encontrado]",
        True,
        (255, 255, 255)
    )

    surf.blit(
        txt,
        txt.get_rect(center=(ANCHO // 2, ALTO // 2))
    )

    return surf


def mostrar_comic_inicio(screen):
    img_inicio = cargar_imagen_comic("comic_inicio.png")
    reloj = pygame.time.Clock()
    esperando = True

    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                esperando = False

        screen.blit(img_inicio, (0, 0))

        lbl_enter = fuente_ui.render(
            "PRESIONA ENTER PARA COMENZAR EL NIVEL 1",
            True,
            (255, 255, 255)
        )

        rect_txt = lbl_enter.get_rect(
            center=(ANCHO // 2, ALTO - 35)
        )

        sombra_bg = pygame.Surface(
            (rect_txt.width + 20, rect_txt.height + 10)
        )

        sombra_bg.fill((0, 0, 0))
        sombra_bg.set_alpha(180)

        screen.blit(
            sombra_bg,
            (rect_txt.x - 10, rect_txt.y - 5)
        )

        screen.blit(lbl_enter, rect_txt)

        pygame.display.flip()
        reloj.tick(60)


def mostrar_comic_final(screen):
    img_final = cargar_imagen_comic("comic_final.png")
    reloj = pygame.time.Clock()
    esperando = True

    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                esperando = False

        screen.blit(img_final, (0, 0))

        lbl_fin = fuente_ui.render(
            "FIN DEL NIVEL 1 - Presiona cualquier tecla para continuar",
            True,
            (255, 255, 255)
        )

        rect_txt = lbl_fin.get_rect(
            center=(ANCHO // 2, ALTO - 35)
        )

        sombra_bg = pygame.Surface(
            (rect_txt.width + 20, rect_txt.height + 10)
        )

        sombra_bg.fill((0, 0, 0))
        sombra_bg.set_alpha(180)

        screen.blit(
            sombra_bg,
            (rect_txt.x - 10, rect_txt.y - 5)
        )

        screen.blit(lbl_fin, rect_txt)

        pygame.display.flip()
        reloj.tick(60)


def buscar_y_cargar_barra(nombre_archivo):
    dir_actual = os.path.dirname(os.path.abspath(__file__))

    for _ in range(4):
        posible_ruta = os.path.join(
            dir_actual,
            "assets",
            "barras de vida",
            nombre_archivo
        )

        if os.path.exists(posible_ruta):
            try:
                img = pygame.image.load(posible_ruta).convert_alpha()
                return img
            except Exception as e:
                print(f"Error al cargar {posible_ruta}: {e}")

        dir_actual = os.path.dirname(dir_actual)

    ruta_relativa = os.path.join(
        "assets",
        "barras de vida",
        nombre_archivo
    )

    if os.path.exists(ruta_relativa):
        try:
            img = pygame.image.load(ruta_relativa).convert_alpha()
            return img
        except Exception as e:
            print(f"Error al cargar {ruta_relativa}: {e}")

    return None


IMG_SUN_SPIRIT = buscar_y_cargar_barra("sun_spirit.png")
IMG_BARRA_JUGADOR = buscar_y_cargar_barra("Barra_de_vida_jugador.png")


# =========================================================
# CARGA DE FONDOS
# =========================================================

fondos = []

for i in range(1, CANTIDAD_FONDOS + 1):
    ruta_imagen = os.path.join(
        "imagenes",
        "Nivel1",
        f"Nivel1_imagen{i}.png"
    )

    if not os.path.exists(ruta_imagen):
        ruta_imagen = os.path.join(
            "assets",
            "imagenes",
            "Nivel1",
            f"Nivel1_imagen{i}.png"
        )

    if os.path.exists(ruta_imagen):
        img = pygame.image.load(ruta_imagen).convert()
        fondos.append(
            pygame.transform.scale(img, (ANCHO, ALTO))
        )
    else:
        surf = pygame.Surface((ANCHO, ALTO))
        surf.fill((20, 15, 25))
        fondos.append(surf)


# =========================================================
# ADAPTADOR DEL JUGADOR AL MUNDO
# La clase del personaje ahora está en jugador.py
# =========================================================

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

    def take_damage(self, damage):
        self.jugador.take_damage(damage)


# =========================================================
# UI E INTERACTIVOS
# =========================================================

def dibujar_boton_demoniaco(pantalla):
    ANCHO_LOW, ALTO_LOW = 150, 38

    surf_pixel = pygame.Surface((ANCHO_LOW, ALTO_LOW))
    surf_pixel.fill((0, 0, 0))
    surf_pixel.set_colorkey((0, 0, 0))

    cuerno_izq = [
        (1, 7), (3, 7), (3, 5), (5, 5),
        (5, 3), (7, 1), (9, 1), (9, 9), (1, 9)
    ]

    cuerno_der = [
        (ANCHO_LOW - 2, 7),
        (ANCHO_LOW - 4, 7),
        (ANCHO_LOW - 4, 5),
        (ANCHO_LOW - 6, 5),
        (ANCHO_LOW - 6, 3),
        (ANCHO_LOW - 8, 1),
        (ANCHO_LOW - 10, 1),
        (ANCHO_LOW - 10, 9),
        (ANCHO_LOW - 2, 9)
    ]

    pygame.draw.polygon(surf_pixel, (170, 30, 20), cuerno_izq)
    pygame.draw.polygon(surf_pixel, (170, 30, 20), cuerno_der)
    pygame.draw.polygon(surf_pixel, (70, 10, 10), cuerno_izq, 1)
    pygame.draw.polygon(surf_pixel, (70, 10, 10), cuerno_der, 1)

    rect_piedra = pygame.Rect(
        7,
        7,
        ANCHO_LOW - 14,
        ALTO_LOW - 7
    )

    pygame.draw.rect(surf_pixel, (25, 22, 22), rect_piedra)
    pygame.draw.rect(surf_pixel, (75, 75, 80), rect_piedra, 1)

    detalles_piedra = [
        (9, 9, 4, 2, (95, 95, 100)),
        (18, 8, 3, 2, (45, 45, 50)),
        (28, 9, 5, 1, (105, 105, 110)),
        (42, 8, 2, 2, (55, 55, 60)),
        (65, 8, 4, 1, (90, 90, 95)),
        (95, 9, 3, 2, (50, 50, 55)),
        (120, 8, 4, 1, (100, 100, 105)),
        (135, 9, 2, 2, (45, 45, 50)),
        (14, 12, 1, 3, (190, 40, 10)),
        (15, 15, 3, 1, (230, 90, 10)),
        (128, 28, 4, 1, (210, 60, 10)),
        (132, 29, 1, 3, (170, 30, 0)),
        (75, 32, 6, 1, (180, 40, 10)),
        (11, 29, 3, 2, (85, 85, 90))
    ]

    for x, y, w, h, color in detalles_piedra:
        pygame.draw.rect(surf_pixel, color, (x, y, w, h))

    pygame.draw.rect(
        surf_pixel,
        (40, 40, 45),
        rect_piedra.inflate(-4, -4),
        1
    )

    txt_str = "PRESS C TO INTERACT"

    txt_sombra = fuente_lava_pixel.render(
        txt_str,
        False,
        (180, 30, 0)
    )

    txt_fuego = fuente_lava_pixel.render(
        txt_str,
        False,
        (255, 170, 0)
    )

    rect_txt = txt_fuego.get_rect(
        center=(ANCHO_LOW // 2, ALTO_LOW // 2 + 1)
    )

    surf_pixel.blit(
        txt_sombra,
        (rect_txt.x + 1, rect_txt.y + 1)
    )

    surf_pixel.blit(txt_fuego, rect_txt)

    ESCALA = 2.5
    ancho_final = int(ANCHO_LOW * ESCALA)
    alto_final = int(ALTO_LOW * ESCALA)

    surf_escalada = pygame.transform.scale(
        surf_pixel,
        (ancho_final, alto_final)
    )

    pantalla.blit(
        surf_escalada,
        (ANCHO - ancho_final - 25, ALTO - alto_final - 20)
    )


def dibujar_barra_jugador(screen, player):
    pct_player = max(
        0.0,
        min(
            1.0,
            player.health / player.max_health
            if player.max_health > 0 else 0
        )
    )

    if IMG_BARRA_JUGADOR is not None:
        ancho_b_p = 280

        escala_p = ancho_b_p / IMG_BARRA_JUGADOR.get_width()

        alto_b_p = int(
            IMG_BARRA_JUGADOR.get_height() * escala_p
        )

        bar_p_scaled = pygame.transform.scale(
            IMG_BARRA_JUGADOR,
            (ancho_b_p, alto_b_p)
        )

        x_p_ui, y_p_ui = 25, 20

        x_fill_p = x_p_ui + int(ancho_b_p * 0.08)
        y_fill_p = y_p_ui + int(alto_b_p * 0.44)

        w_max_fill_p = int(ancho_b_p * 0.84)
        h_fill_p = int(alto_b_p * 0.40)

        w_restante_p = int(w_max_fill_p * pct_player)

        pygame.draw.rect(
            screen,
            (20, 5, 5),
            (x_fill_p, y_fill_p, w_max_fill_p, h_fill_p)
        )

        if w_restante_p > 0:
            pygame.draw.rect(
                screen,
                (190, 30, 30),
                (x_fill_p, y_fill_p, w_restante_p, h_fill_p)
            )

            pygame.draw.rect(
                screen,
                (240, 90, 90),
                (
                    x_fill_p,
                    y_fill_p,
                    w_restante_p,
                    max(1, h_fill_p // 3)
                )
            )

        screen.blit(bar_p_scaled, (x_p_ui, y_p_ui))

        lbl_player = fuente_ui.render(
            f"JUGADOR: {int(player.health)} / {player.max_health}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            lbl_player,
            (x_p_ui + 5, y_p_ui + alto_b_p + 4)
        )

    else:
        ancho_b_player, alto_b_player = 200, 18
        x_player, y_player = 30, 30

        pygame.draw.rect(
            screen,
            (10, 10, 10),
            (
                x_player - 2,
                y_player - 2,
                ancho_b_player + 4,
                alto_b_player + 4
            )
        )

        if pct_player > 0:
            pygame.draw.rect(
                screen,
                (190, 30, 30),
                (
                    x_player,
                    y_player,
                    int(ancho_b_player * pct_player),
                    alto_b_player
                )
            )

        pygame.draw.rect(
            screen,
            (200, 200, 200),
            (
                x_player - 2,
                y_player - 2,
                ancho_b_player + 4,
                alto_b_player + 4
            ),
            2
        )

        lbl_player = fuente_ui.render(
            f"JUGADOR: {int(player.health)} / {player.max_health}",
            True,
            (255, 255, 255)
        )

        screen.blit(lbl_player, (x_player, 8))


# =========================================================
# BATALLA CONTRA EL JEFE
# =========================================================

def ejecutar_batalla_carnicero(screen, player, fondo_img):
    from Jefes_enemigos import CarniceroBoss

    clock = pygame.time.Clock()
    FPS = 60

    jefe = CarniceroBoss(
        x=920,
        y=POSICION_SUELO - 300
    )

    jefe.max_health = 300
    jefe.health = 300

    player.health = player.max_health
    player.pos_x = 180.0
    player.rect.centerx = 180
    player.rect.bottom = POSICION_SUELO

    en_batalla = True
    timer_muerte_jefe = 0.0
    tiempo_en_hitbox_jefe = 0.0

    TIEMPO_FADE_LETRERO = 1.8
    TIEMPO_ESPERA_POST = 3.0

    while en_batalla:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            player.procesar_evento(event)

        player.update(0, transicion_realizada=True)

        jefe.update(
            player,
            dt,
            width=ANCHO,
            suelo_y=POSICION_SUELO
        )

        target_player_rect = player.hurtbox

        for proj in jefe.proyectiles[:]:
            if proj.rect.colliderect(target_player_rect):
                player.take_damage(8)

                if proj in jefe.proyectiles:
                    jefe.proyectiles.remove(proj)

        jefe_atacando = (
            getattr(jefe, "attacking", False)
            or getattr(jefe, "atacando", False)
            or getattr(jefe, "estado", "") in [
                "attack",
                "atk",
                "1_atk",
                "attacking"
            ]
        )

        if jefe_atacando:
            if (
                hasattr(jefe, "hitbox")
                and jefe.hitbox
                and jefe.hitbox.width > 0
            ):
                espada_hitbox = jefe.hitbox

            else:
                mirando_der = getattr(
                    jefe,
                    "mirando_derecha",
                    getattr(
                        jefe,
                        "facing_right",
                        jefe.rect.centerx < player.rect.centerx
                    )
                )

                ancho_espada = 130
                alto_espada = 120
                y_espada = jefe.rect.bottom - alto_espada - 10

                if mirando_der:
                    espada_hitbox = pygame.Rect(
                        jefe.rect.centerx + 25,
                        y_espada,
                        ancho_espada,
                        alto_espada
                    )
                else:
                    espada_hitbox = pygame.Rect(
                        jefe.rect.centerx - 25 - ancho_espada,
                        y_espada,
                        ancho_espada,
                        alto_espada
                    )

            if espada_hitbox.colliderect(target_player_rect):
                tiempo_en_hitbox_jefe += dt

                if (
                    tiempo_en_hitbox_jefe >= 1.0
                    and not getattr(jefe, "has_hit", False)
                ):
                    player.take_damage(20)
                    setattr(jefe, "has_hit", True)
            else:
                tiempo_en_hitbox_jefe = 0.0

        else:
            tiempo_en_hitbox_jefe = 0.0
            setattr(jefe, "has_hit", False)

        if not getattr(jefe, "muerto_definitivo", False) and player.atacando:
            if player.estado == "sp_atk":
                num_imagen = int(player.frame_index) + 1

                if num_imagen in (12, 18, 20):
                    if not player.has_hit:
                        if player.hitbox.colliderect(jefe.hurtbox):
                            jefe.take_damage(18)
                            player.has_hit = True
                else:
                    player.has_hit = False

            else:
                if not player.has_hit:
                    if player.hitbox.colliderect(jefe.hurtbox):
                        dano_basico = 10

                        if player.estado == "2_atk":
                            dano_basico = 12
                        elif player.estado == "3_atk":
                            dano_basico = 16
                        elif player.estado == "air_atk":
                            dano_basico = 12

                        jefe.take_damage(dano_basico)
                        player.has_hit = True

        screen.blit(fondo_img, (0, 0))
        screen.blit(player.image, player.rect)
        jefe.draw(screen)

        if not getattr(jefe, "muerto_definitivo", False):
            max_v_jefe = getattr(jefe, "max_health", 300)

            pct_jefe = max(
                0.0,
                min(
                    1.0,
                    jefe.health / max_v_jefe
                    if max_v_jefe > 0 else 0
                )
            )

            if IMG_SUN_SPIRIT is not None:
                ancho_b_jefe = 650

                escala = ancho_b_jefe / IMG_SUN_SPIRIT.get_width()

                alto_b_jefe = int(
                    IMG_SUN_SPIRIT.get_height() * escala
                )

                bar_scaled = pygame.transform.scale(
                    IMG_SUN_SPIRIT,
                    (ancho_b_jefe, alto_b_jefe)
                )

                x_jefe_ui = (ANCHO - ancho_b_jefe) // 2
                y_jefe_ui = 18

                x_fill = x_jefe_ui + int(ancho_b_jefe * 0.11)
                y_fill = y_jefe_ui + int(alto_b_jefe * 0.38)

                w_max_fill = int(ancho_b_jefe * 0.78)
                h_fill = int(alto_b_jefe * 0.22)

                w_restante = int(w_max_fill * pct_jefe)

                pygame.draw.rect(
                    screen,
                    (20, 5, 5),
                    (x_fill, y_fill, w_max_fill, h_fill)
                )

                if w_restante > 0:
                    fase = getattr(jefe, "fase_actual", 1)

                    color_fase = (
                        (180, 30, 10)
                        if fase == 1
                        else (
                            (255, 100, 0)
                            if fase == 2
                            else (255, 200, 0)
                        )
                    )

                    pygame.draw.rect(
                        screen,
                        color_fase,
                        (x_fill, y_fill, w_restante, h_fill)
                    )

                    pygame.draw.rect(
                        screen,
                        (255, 220, 100),
                        (
                            x_fill,
                            y_fill,
                            w_restante,
                            max(1, h_fill // 3)
                        )
                    )

                screen.blit(bar_scaled, (x_jefe_ui, y_jefe_ui))

                y_titulo = y_jefe_ui + alto_b_jefe + 6

                lbl_sombra = fuente_jefe.render(
                    "Athros : The bloodred",
                    True,
                    (100, 10, 0)
                )

                lbl_fuego_brillo = fuente_jefe.render(
                    "Athros : The bloodred",
                    True,
                    (255, 80, 0)
                )

                lbl_jefe = fuente_jefe.render(
                    "Athros : The bloodred",
                    True,
                    (255, 190, 30)
                )

                rect_lbl = lbl_jefe.get_rect(
                    center=(ANCHO // 2, y_titulo)
                )

                screen.blit(
                    lbl_sombra,
                    (rect_lbl.x + 2, rect_lbl.y + 2)
                )

                screen.blit(
                    lbl_fuego_brillo,
                    (rect_lbl.x + 1, rect_lbl.y + 1)
                )

                screen.blit(lbl_jefe, rect_lbl)

            else:
                ancho_b_jefe, alto_b_jefe = 500, 20

                x_jefe, y_jefe = (
                    (ANCHO - ancho_b_jefe) // 2,
                    45
                )

                pygame.draw.rect(
                    screen,
                    (20, 5, 5),
                    (
                        x_jefe - 2,
                        y_jefe - 2,
                        ancho_b_jefe + 4,
                        alto_b_jefe + 4
                    )
                )

                w_restante = int(ancho_b_jefe * pct_jefe)

                if w_restante > 0:
                    fase = getattr(jefe, "fase_actual", 1)

                    color_fase = (
                        (180, 30, 10)
                        if fase == 1
                        else (
                            (255, 100, 0)
                            if fase == 2
                            else (255, 200, 0)
                        )
                    )

                    pygame.draw.rect(
                        screen,
                        color_fase,
                        (x_jefe, y_jefe, w_restante, alto_b_jefe)
                    )

                    pygame.draw.rect(
                        screen,
                        (255, 220, 100),
                        (
                            x_jefe,
                            y_jefe,
                            w_restante,
                            alto_b_jefe // 2
                        )
                    )

                pygame.draw.rect(
                    screen,
                    (255, 215, 0),
                    (
                        x_jefe - 2,
                        y_jefe - 2,
                        ancho_b_jefe + 4,
                        alto_b_jefe + 4
                    ),
                    2
                )

                y_titulo = y_jefe + alto_b_jefe + 10

                lbl_sombra = fuente_jefe.render(
                    "Athros : The bloodred",
                    True,
                    (100, 10, 0)
                )

                lbl_jefe = fuente_jefe.render(
                    "Athros : The bloodred",
                    True,
                    (255, 190, 30)
                )

                rect_lbl = lbl_jefe.get_rect(
                    center=(ANCHO // 2, y_titulo)
                )

                screen.blit(
                    lbl_sombra,
                    (rect_lbl.x + 2, rect_lbl.y + 2)
                )

                screen.blit(lbl_jefe, rect_lbl)

        dibujar_barra_jugador(screen, player)

        if getattr(jefe, "muerto_definitivo", False):
            timer_muerte_jefe += dt

            progreso = min(
                1.0,
                timer_muerte_jefe / TIEMPO_FADE_LETRERO
            )

            alpha_val = int(progreso * 255)
            banda_alto = 120

            banda_surf = pygame.Surface(
                (ANCHO, banda_alto),
                pygame.SRCALPHA
            )

            banda_surf.fill((0, 0, 0, int(progreso * 135)))

            y_banda = (ALTO // 2) - (banda_alto // 2)

            screen.blit(banda_surf, (0, y_banda))

            fuente_elden = pygame.font.SysFont(
                "Georgia",
                64,
                bold=True
            )

            surf_sombra = fuente_elden.render(
                "LEGEND FALLEN",
                True,
                (25, 10, 5)
            )

            surf_texto = fuente_elden.render(
                "LEGEND FALLEN",
                True,
                (235, 195, 75)
            )

            surf_sombra.set_alpha(alpha_val)
            surf_texto.set_alpha(alpha_val)

            rect_txt = surf_texto.get_rect(
                center=(ANCHO // 2, ALTO // 2)
            )

            screen.blit(
                surf_sombra,
                (rect_txt.x + 3, rect_txt.y + 3)
            )

            screen.blit(surf_texto, rect_txt)

            if timer_muerte_jefe >= (
                TIEMPO_FADE_LETRERO + TIEMPO_ESPERA_POST
            ):
                mostrar_comic_final(screen)
                en_batalla = False

        pygame.display.flip()


# =========================================================
# GRUPOS DE ENEMIGOS ACTIVADOS POR DISTANCIA
# =========================================================

TIPOS_ENEMIGO = [OrcoRojo, OjoVolador, Karasu_tengu]
DISTANCIA_ENTRE_GRUPOS = 850
PRIMER_GRUPO_X = 800
ULTIMO_GRUPO_X = HUECO_INICIO - 1100

PUNTOS_GRUPO = list(
    range(
        PRIMER_GRUPO_X,
        ULTIMO_GRUPO_X + 1,
        DISTANCIA_ENTRE_GRUPOS
    )
)


def generar_plataformas_nivel():
    plataformas = []

    x = 350
    y = 520

    while x < HUECO_INICIO - 100:
        ancho = random.randint(190, 280)
        plataformas.append(
            pygame.Rect(x, y, ancho, 18)
        )

        x += ancho + random.randint(35, 105)
        y = max(
            325,
            min(560, y + random.randint(-75, 75))
        )

    return plataformas


def generar_diseno_plataforma():
    return {
        "estilo": random.randrange(5),
        "color": random.choice([
            (111, 76, 48),
            (80, 91, 77),
            (91, 80, 65),
            (105, 91, 67),
            (72, 78, 79),
        ]),
        "detalles": [
            (
                random.random(),
                random.randint(3, 13),
                random.randint(3, 8)
            )
            for _ in range(7)
        ],
        "libros": [
            (
                random.randint(9, 20),
                random.choice([
                    (121, 43, 36),
                    (49, 76, 84),
                    (163, 125, 55),
                    (71, 99, 64),
                    (97, 65, 104),
                ])
            )
            for _ in range(5)
        ],
        "ladrillos": [
            random.choice([
                (119, 91, 72),
                (91, 83, 73),
                (132, 112, 91)
            ])
            for _ in range(7)
        ],
        "manchas": [
            (
                random.random(),
                random.randint(6, 16),
                random.randint(3, 7)
            )
            for _ in range(4)
        ],
        "runa": random.choice([
            (210, 48, 25),
            (178, 50, 32),
            (125, 39, 35)
        ]),
    }


def dibujar_plataformas(screen, scroll_x, plataformas, disenos):
    for plataforma, diseno in zip(plataformas, disenos):
        rect = plataforma.move(-scroll_x, 0)

        if rect.right < 0 or rect.left > ANCHO:
            continue

        estilo = diseno["estilo"]
        base = diseno["color"]

        pygame.draw.rect(
            screen,
            (27, 24, 23),
            rect.move(0, 7)
        )

        if estilo == 0:
            pygame.draw.rect(screen, (68, 47, 34), rect)

            pygame.draw.rect(
                screen,
                base,
                (rect.x, rect.y, rect.width, 7)
            )

            pygame.draw.line(
                screen,
                (166, 133, 91),
                (rect.x + 4, rect.y + 2),
                (rect.right - 5, rect.y + 2),
                2
            )

            pygame.draw.polygon(
                screen,
                (47, 37, 30),
                [
                    (rect.x + rect.width // 2, rect.y + 8),
                    (
                        rect.x + rect.width // 2 + 18,
                        rect.bottom - 2
                    ),
                    (
                        rect.x + rect.width // 2 + 7,
                        rect.bottom - 2
                    )
                ]
            )

        elif estilo == 1:
            pygame.draw.rect(screen, (36, 35, 39), rect)

            book_x = rect.x + 8

            for book_width, book_color in diseno["libros"]:
                if book_x + book_width > rect.right - 5:
                    break

                book = pygame.Rect(
                    book_x,
                    rect.y - 12,
                    book_width,
                    20
                )

                pygame.draw.rect(screen, book_color, book)

                pygame.draw.rect(
                    screen,
                    (197, 174, 128),
                    (
                        book.x + 3,
                        book.y + 4,
                        2,
                        12
                    )
                )

                book_x += book_width + 5

            pygame.draw.line(
                screen,
                (91, 69, 60),
                (rect.x, rect.y + 8),
                (rect.right, rect.y + 8),
                3
            )

        elif estilo == 2:
            pygame.draw.rect(screen, (27, 45, 48), rect)
            pygame.draw.rect(screen, (75, 53, 42), rect, 5)

            for fraccion, largo, inclinacion in diseno["detalles"][:5]:
                chalk_x = rect.x + int(
                    fraccion * max(1, rect.width - largo)
                )

                pygame.draw.line(
                    screen,
                    (134, 133, 105),
                    (chalk_x, rect.y + 5),
                    (
                        chalk_x + largo,
                        rect.y + 5 + inclinacion // 2
                    ),
                    2
                )

            pygame.draw.circle(
                screen,
                diseno["runa"],
                (rect.right - 18, rect.y + 5),
                5,
                1
            )

            pygame.draw.line(
                screen,
                diseno["runa"],
                (rect.right - 22, rect.y + 5),
                (rect.right - 14, rect.y + 5),
                1
            )

        elif estilo == 3:
            pygame.draw.rect(screen, (43, 39, 42), rect)

            ladrillo_x = rect.x

            for indice, (fraccion, alto, _) in enumerate(
                diseno["detalles"]
            ):
                ladrillo_x = rect.x + int(
                    fraccion * max(1, rect.width - 24)
                )

                pygame.draw.rect(
                    screen,
                    diseno["ladrillos"][indice],
                    (
                        ladrillo_x,
                        rect.y + 2,
                        min(25, rect.right - ladrillo_x),
                        max(4, alto - 2)
                    )
                )

            pygame.draw.line(
                screen,
                (113, 83, 67),
                (rect.x + 3, rect.y + 1),
                (rect.right - 4, rect.y + 1),
                2
            )

        else:
            pygame.draw.rect(screen, (38, 39, 43), rect)

            pygame.draw.rect(
                screen,
                (75, 67, 58),
                (rect.x, rect.y + 4, rect.width, 9),
                border_radius=4
            )

            for fraccion, _, _ in diseno["detalles"][:4]:
                banda_x = rect.x + int(
                    fraccion * max(1, rect.width - 9)
                )

                pygame.draw.rect(
                    screen,
                    (144, 130, 105),
                    (banda_x, rect.y + 2, 5, 14)
                )

            pygame.draw.circle(
                screen,
                (84, 101, 101),
                (rect.x + 9, rect.y + 9),
                5,
                2
            )

            pygame.draw.circle(
                screen,
                (84, 101, 101),
                (rect.right - 9, rect.y + 9),
                5,
                2
            )

        # Sangre seca y runas pintadas en restos de mobiliario escolar.
        for fraccion, largo, alto in diseno["manchas"]:
            mancha_x = rect.x + int(
                fraccion * max(1, rect.width - largo)
            )

            pygame.draw.ellipse(
                screen,
                (83, 25, 29),
                (
                    mancha_x,
                    rect.y + 2,
                    largo,
                    max(3, alto // 2)
                )
            )

            pygame.draw.line(
                screen,
                (109, 31, 32),
                (mancha_x + largo // 2, rect.y + 4),
                (
                    mancha_x + largo // 2 - 2,
                    rect.y + min(16, alto)
                ),
                1
            )

        if estilo in (0, 3):
            # Silueta discreta de un estudiante caído entre los escombros.
            cuerpo_x = rect.x + rect.width // 2
            cuerpo_y = rect.y - 5

            pygame.draw.ellipse(
                screen,
                (24, 21, 25),
                (cuerpo_x - 12, cuerpo_y - 5, 10, 9)
            )

            pygame.draw.line(
                screen,
                (24, 21, 25),
                (cuerpo_x - 2, cuerpo_y),
                (cuerpo_x + 18, cuerpo_y + 4),
                5
            )

            pygame.draw.line(
                screen,
                (24, 21, 25),
                (cuerpo_x + 10, cuerpo_y + 2),
                (cuerpo_x + 20, cuerpo_y - 4),
                3
            )

        for fraccion, alto, largo in diseno["detalles"]:
            detalle_x = rect.x + int(
                fraccion * max(1, rect.width - 8)
            )

            pygame.draw.line(
                screen,
                (39, 34, 30),
                (detalle_x, rect.y + 8),
                (
                    min(rect.right - 2, detalle_x + largo),
                    min(rect.bottom - 2, rect.y + alto)
                ),
                1
            )


# =========================================================
# CREACIÓN Y ORGANIZACIÓN DE ENEMIGOS
# =========================================================

def crear_enemigo(clase, x):
    """Crea un enemigo y ajusta sus propiedades iniciales."""

    if clase is OrcoRojo:
        enemigo = OrcoRojo(
            x=x,
            y=POSICION_SUELO,
            escala=2.0
        )
        enemigo.dano_ataque = 10

    elif clase is Karasu_tengu:
        enemigo = Karasu_tengu(
            x=x,
            y=POSICION_SUELO
        )
        enemigo.dano_ataque = 5

    else:
        enemigo = OjoVolador(
            x=x,
            y=POSICION_SUELO,
            suelo_y=POSICION_SUELO
        )
        enemigo.DANO_PROYECTIL = 10

    enemigo.suelo_y = POSICION_SUELO

    if isinstance(enemigo, (OrcoRojo, Karasu_tengu)):
        enemigo.rect.bottom = POSICION_SUELO
        enemigo.jump_force = -15

    return enemigo


def generar_grupo_enemigos(posicion):
    """Genera un grupo de enemigos al alcanzar una distancia."""

    cantidad = random.randint(2, 3)
    enemigos = []

    indice_grupo = round(
        (posicion - PRIMER_GRUPO_X) / DISTANCIA_ENTRE_GRUPOS
    )

    for i in range(cantidad):
        x = posicion + random.randint(100, 220) + i * 65

        enemigo = crear_enemigo(
            random.choice(TIPOS_ENEMIGO),
            x
        )

        enemigo.plataformas = plataformas_nivel

        enemigo.flank_side = (
            (-1 if i % 2 == 0 else 1)
            * (1 if indice_grupo % 2 == 0 else -1)
        )

        enemigo.preferred_distance = random.randint(55, 115)
        enemigo.strafe_timer = random.uniform(0.6, 1.8)
        enemigo.strafe_direction = random.choice((-1, 1))
        enemigo.jump_cooldown = random.uniform(0.4, 1.4)
        enemigo.speed = random.randint(3, 5)

        enemigos.append(enemigo)

    for enemigo in enemigos:
        enemigo.allies = enemigos

    return enemigos


def enemigo_derrotado(enemigo):
    return (
        enemigo.health <= 0
        or getattr(enemigo, "muerto_definitivo", False)
    )


def separar_enemigos(enemigos, ancho_mundo):
    enemigos_activos = [
        enemigo for enemigo in enemigos
        if enemigo.health > 0
        and not getattr(enemigo, "muerto_definitivo", False)
    ]

    for _ in range(3):
        for indice, primero in enumerate(enemigos_activos):
            for segundo in enemigos_activos[indice + 1:]:
                if not primero.rect.inflate(0, 20).colliderect(
                    segundo.rect.inflate(0, 20)
                ):
                    continue

                signo = (
                    1
                    if primero.rect.centerx <= segundo.rect.centerx
                    else -1
                )

                distancia_minima = (
                    primero.rect.width + segundo.rect.width
                ) // 2 + 18

                distancia_actual = abs(
                    segundo.rect.centerx - primero.rect.centerx
                )

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
                    0,
                    min(
                        ancho_mundo - primero.rect.width,
                        primero.rect.x
                    )
                )

                segundo.rect.x = max(
                    0,
                    min(
                        ancho_mundo - segundo.rect.width,
                        segundo.rect.x
                    )
                )

                primero.hitbox.x += (
                    primero.rect.x - primero_x_anterior
                )

                segundo.hitbox.x += (
                    segundo.rect.x - segundo_x_anterior
                )

                if hasattr(primero, "actualizar_hurtbox"):
                    primero.actualizar_hurtbox()
                else:
                    primero.hurtbox.topleft = primero.rect.topleft

                if hasattr(segundo, "actualizar_hurtbox"):
                    segundo.actualizar_hurtbox()
                else:
                    segundo.hurtbox.topleft = segundo.rect.topleft


# =========================================================
# INICIALIZACIÓN Y FLUJO PRINCIPAL DEL JUEGO
# =========================================================

mostrar_comic_inicio(pantalla)

# Se crea el personaje desde jugador.py.
heroe = p_viento(200, POSICION_SUELO, POSICION_SUELO)

todos_los_sprites = pygame.sprite.Group(heroe)
vista_heroe = VistaJugadorMundo(heroe)

plataformas_nivel = generar_plataformas_nivel()

disenos_plataformas = [
    generar_diseno_plataforma()
    for _ in plataformas_nivel
]

heroe.plataformas = plataformas_nivel

enemigos_nivel = []
proximo_grupo = 0

scroll_x = 0
transicion_realizada = False

ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    dt = reloj.tick(60) / 1000.0

    while (
        proximo_grupo < len(PUNTOS_GRUPO)
        and heroe.pos_x >= PUNTOS_GRUPO[proximo_grupo]
    ):
        enemigos_nivel.extend(
            generar_grupo_enemigos(
                PUNTOS_GRUPO[proximo_grupo]
            )
        )

        proximo_grupo += 1

    todos_los_grupos_generados = (
        proximo_grupo == len(PUNTOS_GRUPO)
    )

    enemigos_pendientes = [
        enemigo
        for enemigo in enemigos_nivel
        if not enemigo_derrotado(enemigo)
    ]

    portal_liberado = (
        todos_los_grupos_generados
        and not enemigos_pendientes
    )

    limite_max_x = (
        HUECO_FIN
        if portal_liberado
        else HUECO_INICIO - 40
    )

    en_zona_hueco = (
        portal_liberado
        and HUECO_INICIO <= heroe.pos_x <= HUECO_FIN
        and not transicion_realizada
    )

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and en_zona_hueco
        ):
            heroe.health = heroe.max_health

            pantalla.fill((0, 0, 0))

            txt_title = fuente_boss_title.render(
                "Athros",
                True,
                (180, 20, 20)
            )

            txt_subtitle = fuente_boss_subtitle.render(
                "the bloodred",
                True,
                (140, 15, 15)
            )

            pantalla.blit(
                txt_title,
                txt_title.get_rect(
                    center=(ANCHO // 2, ALTO // 2 - 25)
                )
            )

            pantalla.blit(
                txt_subtitle,
                txt_subtitle.get_rect(
                    center=(ANCHO // 2, ALTO // 2 + 45)
                )
            )

            pygame.display.flip()
            pygame.time.wait(2000)

            transicion_realizada = True

            ejecutar_batalla_carnicero(
                pantalla,
                heroe,
                fondos[2]
            )

            ejecutando = False
            break

        heroe.procesar_evento(evento)

    if not ejecutando:
        break

    todos_los_sprites.update(
        scroll_x,
        transicion_realizada,
        limite_max_x=limite_max_x
    )

    scroll_x = max(
        0,
        min(
            heroe.pos_x - ANCHO * 0.4,
            ANCHO_MUNDO - ANCHO
        )
    )

    heroe.rect.centerx = int(heroe.pos_x - scroll_x)
    heroe.actualizar_hitboxes()

    vista_heroe.sync(scroll_x)

    # Enemigos y combate en el mundo.
    for enemigo in enemigos_nivel:
        enemigo.allies = enemigos_nivel

    for enemigo in enemigos_nivel:
        if (
            enemigo_derrotado(enemigo)
            and getattr(enemigo, "muerto_definitivo", False)
        ):
            if isinstance(enemigo, OjoVolador):
                enemigo.update(
                    vista_heroe,
                    dt,
                    width=ANCHO_MUNDO
                )
            continue

        enemigo.suelo_y = POSICION_SUELO
        enemigo.plataformas = plataformas_nivel

        enemigo.update(
            vista_heroe,
            dt,
            width=ANCHO_MUNDO
        )

        if enemigo.health <= 0:
            continue

        # Ataque del héroe al enemigo.
        if (
            heroe.atacando
            and not heroe.has_hit
            and vista_heroe.hitbox.width > 0
            and vista_heroe.hitbox.colliderect(enemigo.hurtbox)
        ):
            enemigo.take_damage(20)
            heroe.has_hit = True

        # Ataque del enemigo al héroe.
        hb = getattr(enemigo, "hitbox", None)

        if (
            hb is not None
            and hb.width > 0
            and not getattr(enemigo, "has_hit", False)
        ):
            if hb.colliderect(vista_heroe.hurtbox):
                heroe.take_damage(
                    getattr(enemigo, "dano_ataque", 10)
                )
                enemigo.has_hit = True

    separar_enemigos(enemigos_nivel, ANCHO_MUNDO)

    # Fondo continuo.
    for i in range(ANCHO_MUNDO // ANCHO):
        pos_x_fondo = i * ANCHO - scroll_x

        if -ANCHO < pos_x_fondo < ANCHO:
            pantalla.blit(
                fondos[i % len(fondos)],
                (pos_x_fondo, 0)
            )

    dibujar_plataformas(
        pantalla,
        scroll_x,
        plataformas_nivel,
        disenos_plataformas
    )

    # Renderizado del héroe y los enemigos.
    todos_los_sprites.draw(pantalla)

    for enemigo in enemigos_nivel:
        if isinstance(enemigo, OjoVolador):
            enemigo.draw(pantalla, scroll_x)

        elif not getattr(enemigo, "muerto_definitivo", False):
            pos_x_orig = enemigo.rect.x
            enemigo.rect.x -= scroll_x

            enemigo.draw(pantalla)

            enemigo.rect.x = pos_x_orig

    # Progreso del recorrido y acceso al jefe.
    dibujar_barra_jugador(pantalla, heroe)

    progreso = min(
        100,
        int(heroe.pos_x * 100 / PORTAL_X)
    )

    if portal_liberado:
        str_progreso = "CAMINO DESPEJADO: ACÉRCATE AL PORTAL"
        color_progreso = (90, 230, 130)

    elif enemigos_pendientes:
        str_progreso = (
            f"RUMBO A ATHROS: {progreso}%  |  "
            f"ENEMIGOS: {len(enemigos_pendientes)}"
        )
        color_progreso = (255, 190, 90)

    else:
        str_progreso = f"RUMBO A ATHROS: {progreso}%"
        color_progreso = (230, 210, 160)

    txt_progreso_sombra = fuente_progreso.render(
        str_progreso,
        True,
        (0, 0, 0)
    )

    txt_progreso = fuente_progreso.render(
        str_progreso,
        True,
        color_progreso
    )

    rect_progreso = txt_progreso.get_rect(
        topright=(ANCHO - 30, 20)
    )

    pantalla.blit(
        txt_progreso_sombra,
        (rect_progreso.x + 2, rect_progreso.y + 2)
    )

    pantalla.blit(txt_progreso, rect_progreso)

    if en_zona_hueco:
        dibujar_boton_demoniaco(pantalla)

    pygame.display.flip()

pygame.quit()
sys.exit()