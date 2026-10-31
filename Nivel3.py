import os
import sys
import random
import math
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from enemigos import (
    Enemigo,
    cargar_spritesheet_jokai,
)

pygame.init()
pygame.font.init()

# 1. Configuración de pantalla y mundo
ANCHO, ALTO = 1350, 700
POSICION_SUELO = 638

# Recorrido lateral continuo hasta la entrada del jefe.
ANCHO_MUNDO = ANCHO * 10
PORTAL_X = ANCHO_MUNDO - 500
HUECO_INICIO = PORTAL_X - 150
HUECO_FIN = PORTAL_X + 150
TRAMO_FONDO_TUNELES = int(PORTAL_X * 0.7) // ANCHO + 1
PUERTA_TUNELES_X = TRAMO_FONDO_TUNELES * ANCHO
FIN_TRAMO_FONDO_TUNELES = PUERTA_TUNELES_X + ANCHO
LIMITE_POST_TUNELES_X = FIN_TRAMO_FONDO_TUNELES + 80

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 3 - Cueva y Batalla de Jefe")

# Tamaño del sprite ajustado a escala humana
ANCHO_HEROE, ALTO_HEROE = 300, 300

# Fuentes
fuente_lava_pixel = pygame.font.SysFont("Courier", 9, bold=True)
fuente_boss_title = pygame.font.SysFont("Georgia", 76, bold=True)
fuente_boss_subtitle = pygame.font.SysFont("Georgia", 32, italic=True)
fuente_jefe = pygame.font.SysFont("Georgia", 26, bold=True, italic=True)
fuente_ui = pygame.font.SysFont("Arial", 16, bold=True)
fuente_progreso = pygame.font.SysFont("Impact", 22)


def dibujar_luna_roja_batalla(screen, tiempo):
    x, y = 890, 140

    for radio, alpha in ((110, 12), (95, 18), (80, 25)):
        halo = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 0, 30, alpha), (radio, radio), radio)
        screen.blit(halo, (x - radio, y - radio))

    pygame.draw.circle(screen, (105, 0, 10), (x, y), 62)
    pygame.draw.circle(screen, (210, 18, 28), (x, y), 53)
    pygame.draw.circle(screen, (150, 5, 15), (x - 20, y - 12), 8)
    pygame.draw.circle(screen, (145, 5, 15), (x + 17, y + 18), 11)
    pygame.draw.circle(screen, (165, 8, 18), (x + 4, y - 25), 6)
    pygame.draw.circle(screen, (130, 3, 12), (x - 25, y + 25), 5)
    pygame.draw.circle(
        screen,
        (255, 50, 60),
        (x, y),
        63 + int(math.sin(tiempo * 4) * 4),
        2,
    )


# ==============================================================================
# CARGA DE IMÁGENES
# ==============================================================================
def cargar_imagen_comic_nivel3(nombre_archivo):
    rutas = (
        os.path.join(BASE_DIR, "imagenes", "Nivel3", nombre_archivo),
        os.path.join(BASE_DIR, "assets", "imagenes", "Nivel3", nombre_archivo),
    )
    for ruta in rutas:
        if os.path.isfile(ruta):
            imagen = pygame.image.load(ruta).convert()
            return pygame.transform.scale(imagen, (ANCHO, ALTO))
    raise FileNotFoundError(
        f"No se encontro el comic {nombre_archivo}: {rutas}"
    )


def mostrar_comic_inicio(screen):
    img_inicio = cargar_imagen_comic_nivel3("comic_inicio3.png")
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
        label = fuente_ui.render("PRESIONA ENTER PARA COMENZAR EL NIVEL 3", True, (255, 255, 255))
        rect = label.get_rect(center=(ANCHO // 2, ALTO - 35))
        sombra = pygame.Surface((rect.width + 20, rect.height + 10))
        sombra.fill((0, 0, 0))
        sombra.set_alpha(180)
        screen.blit(sombra, (rect.x - 10, rect.y - 5))
        screen.blit(label, rect)
        pygame.display.flip()
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
IMG_LEVIATHAN = buscar_y_cargar_barra("leviathan.png")

# 2. Carga de fondos

def cargar_fondo_nivel3(nombre_archivo):
    rutas = (
        os.path.join(BASE_DIR, "imagenes", "Nivel3", nombre_archivo),
        os.path.join(BASE_DIR, "assets", "imagenes", "Nivel3", nombre_archivo),
    )
    for ruta in rutas:
        if os.path.isfile(ruta):
            imagen = pygame.image.load(ruta).convert()
            return pygame.transform.scale(imagen, (ANCHO, ALTO))
    raise FileNotFoundError(f"No se encontro el fondo {nombre_archivo}: {rutas}")


fondos = [
    cargar_fondo_nivel3("Nivel3_imagen1.png.png"),
    cargar_fondo_nivel3("Nivel3_imagen2.png.png"),
]
fondo_tuneles = cargar_fondo_nivel3("Nivel3_imagen3.png.png")
fondo_entrada_jefe = cargar_fondo_nivel3("Nivel3_imagen4.png.png")
fondo_batalla = cargar_fondo_nivel3("Nivel3_imagen5.png.png")


def mostrar_comic_final(screen):
    img_final = cargar_imagen_comic_nivel3("comic_final3.png")
    reloj = pygame.time.Clock()
    opcion = None
    while opcion is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    opcion = 1
                elif event.key == pygame.K_2:
                    opcion = 2

        screen.blit(img_final, (0, 0))
        instrucciones = (
            "Presiona 1 para dejar que Escanor entre al portal.",
            "Presiona 2 para impedir que Escanor entre al portal.",
        )
        for indice, instruccion in enumerate(instrucciones):
            texto = fuente_ui.render(instruccion, True, (255, 255, 255))
            rect_texto = texto.get_rect(
                center=(ANCHO // 2, ALTO - 54 + indice * 24)
            )
            sombra = pygame.Surface((rect_texto.width + 20, rect_texto.height + 8))
            sombra.fill((0, 0, 0))
            sombra.set_alpha(180)
            screen.blit(sombra, (rect_texto.x - 10, rect_texto.y - 4))
            screen.blit(texto, rect_texto)
        pygame.display.flip()
        reloj.tick(60)

    nombre_final = "comic_final2_3.png" if opcion == 1 else "comic_final1_3.png"
    imagen_final = cargar_imagen_comic_nivel3(nombre_final)
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                esperando = False
        screen.blit(imagen_final, (0, 0))
        pygame.display.flip()
        reloj.tick(60)


# 3. Clase para el Jugador (P_viento)
class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animaciones = {
            'idle': [], 'run': [], 'roll': [], 'j_up': [],
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
        self.enemigos_golpeados = set()

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
                self.enemigos_golpeados.clear()
                self.estado = 'sp_atk'
                self.frame_index = 0

            elif evento.key == pygame.K_f:
                if not self.en_suelo and not self.atacando:
                    self.atacando = True
                    self.has_hit = False
                    self.enemigos_golpeados.clear()
                    self.estado = 'air_atk'
                    self.frame_index = 0

                elif self.en_suelo and not (self.rodando or self.defendiendo):
                    if not self.atacando:
                        self.atacando = True
                        self.has_hit = False
                        self.enemigos_golpeados.clear()
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
            self.estado = 'j_up'
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
                    self.enemigos_golpeados.clear()
                    self.combo_siguiente = False
                else:
                    self.atacando = False
            elif self.estado == '2_atk':
                if self.combo_siguiente:
                    self.estado = '3_atk'
                    self.has_hit = False
                    self.enemigos_golpeados.clear()
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
        if self.rodando:
            return
        self.health = max(0, self.health - damage)

    def update(
        self,
        scroll_x,
        transicion_realizada,
        limite_max_x=HUECO_FIN,
        limite_min_x=None,
    ):
        self.scroll_x_actual = scroll_x
        self.manejar_movimiento_continuo()

        if self.rodando:
            self.velocidad_x = (self.velocidad_movimiento + 3) * (1 if self.mirando_derecha else -1)

        self.pos_x += self.velocidad_x

        limite_izquierdo = scroll_x + 80

        if transicion_realizada and scroll_x == 0:
            limite_izquierdo = 80
            limite_derecho = ANCHO - 80
        elif transicion_realizada:
            limite_derecho = ANCHO_MUNDO - 80
        else:
            limite_derecho = limite_max_x

        if limite_min_x is not None:
            limite_izquierdo = max(limite_izquierdo, limite_min_x)

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

    def take_damage(self, damage):
        self.jugador.take_damage(damage)


# 4. UI e Interactivos
def dibujar_boton_demoniaco(pantalla):
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

    txt_str = "PRESS C TO INTERACT"
    txt_sombra = fuente_lava_pixel.render(txt_str, False, (12, 55, 150))
    txt_fuego = fuente_lava_pixel.render(txt_str, False, (105, 225, 255))

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


# 5. Escena de Batalla contra el Jefe
def ejecutar_batalla_carnicero(screen, player, fondo_img):
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
        jefe.update(player, dt, width=ANCHO, suelo_y=POSICION_SUELO)

        target_player_rect = player.hurtbox

        for proj in jefe.proyectiles[:]:
            if proj.rect.colliderect(target_player_rect):
                player.take_damage(8)
                if proj in jefe.proyectiles:
                    jefe.proyectiles.remove(proj)

        jefe_atacando = (
            getattr(jefe, 'attacking', False) or
            getattr(jefe, 'atacando', False) or
            getattr(jefe, 'estado', '') in ['attack', 'atk', '1_atk', 'attacking']
        )

        if jefe_atacando:
            if hasattr(jefe, 'hitbox') and jefe.hitbox and jefe.hitbox.width > 0:
                espada_hitbox = jefe.hitbox
            else:
                mirando_der = getattr(jefe, 'mirando_derecha', getattr(jefe, 'facing_right', jefe.rect.centerx < player.rect.centerx))
                ancho_espada = 130
                alto_espada = 120
                y_espada = jefe.rect.bottom - alto_espada - 10

                if mirando_der:
                    espada_hitbox = pygame.Rect(jefe.rect.centerx + 25, y_espada, ancho_espada, alto_espada)
                else:
                    espada_hitbox = pygame.Rect(jefe.rect.centerx - 25 - ancho_espada, y_espada, ancho_espada, alto_espada)

            if espada_hitbox.colliderect(target_player_rect):
                tiempo_en_hitbox_jefe += dt

                if tiempo_en_hitbox_jefe >= 1.0 and not getattr(jefe, 'has_hit', False):
                    player.take_damage(20)
                    setattr(jefe, 'has_hit', True)
            else:
                tiempo_en_hitbox_jefe = 0.0
        else:
            tiempo_en_hitbox_jefe = 0.0
            setattr(jefe, 'has_hit', False)

        if not getattr(jefe, 'muerto_definitivo', False) and player.atacando:
            if player.estado == 'sp_atk':
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
                        if player.estado == '2_atk':
                            dano_basico = 12
                        elif player.estado == '3_atk':
                            dano_basico = 16
                        elif player.estado == 'air_atk':
                            dano_basico = 12

                        jefe.take_damage(dano_basico)
                        player.has_hit = True

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
                lbl_sombra = fuente_jefe.render("Abbadon", True, (0, 0, 20))
                lbl_fuego_brillo = fuente_jefe.render("Abbadon", True, (8, 24, 65))
                lbl_jefe = fuente_jefe.render("Abbadon", True, (12, 35, 82))

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
                lbl_sombra = fuente_jefe.render("Abbadon", True, (0, 0, 20))
                lbl_jefe = fuente_jefe.render("Abbadon", True, (12, 35, 82))
                rect_lbl = lbl_jefe.get_rect(center=(ANCHO // 2, y_titulo))
                screen.blit(lbl_sombra, (rect_lbl.x + 2, rect_lbl.y + 2))
                screen.blit(lbl_jefe, rect_lbl)

        dibujar_barra_jugador(screen, player)

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

            if timer_muerte_jefe >= (TIEMPO_FADE_LETRERO + TIEMPO_ESPERA_POST):
                mostrar_comic_final(screen)
                en_batalla = False

        pygame.display.flip()


def ejecutar_batalla_werewolf(screen, player, fondo_img):
    from Jefes_enemigos import WerewolfBoss

    clock = pygame.time.Clock()
    jefe = WerewolfBoss(x=920, y=POSICION_SUELO - 100)
    jefe.max_health = 300
    jefe.health = jefe.max_health
    jefe.rect.bottom = POSICION_SUELO
    jefe.hurtbox = jefe.rect.copy()

    player.health = player.max_health
    player.pos_x = 180.0
    player.rect.centerx = 180
    player.rect.bottom = POSICION_SUELO
    player.scroll_x_actual = 0
    player.plataformas = []
    player.plataforma_actual = None
    player.plataforma_ignorada = None
    player.velocidad_x = 0
    player.velocidad_y = 0
    player.en_suelo = True
    player.atacando = False
    player.rodando = False
    player.defendiendo = False
    player.combo_siguiente = False
    player.has_hit = False
    player.enemigos_golpeados.clear()
    player.estado = "idle"
    player.frame_index = 0
    player.actualizar_hitboxes()
    player.animar()

    fase = 1
    fase2_activada = False
    transicion_fase = False
    transicion_timer = 0.0
    tiempo_congelado_transicion = None
    demonios_activos = False
    demonios_timer = 0.0
    demonios_cooldown = 7.8
    demonios = []
    proyectiles_demonio = []
    proyectiles_demonio_timer = 0.0
    bolas_fuego = []
    bola_fuego_timer = 0.0
    timer_muerte_jefe = 0.0
    en_batalla = True
    fuente_legend = pygame.font.SysFont("Georgia", 64, bold=True)
    fuente_nombre_jefe = pygame.font.SysFont("Georgia", 18, bold=True)

    def crear_demonios():
        return [
            {"x": 250, "y": 210, "fase": 0},
            {"x": ANCHO // 2, "y": 150, "fase": 2},
            {"x": 1100, "y": 210, "fase": 4},
        ]

    def dibujar_demonio(demonio, tiempo):
        x = int(demonio["x"])
        y = int(demonio["y"] + math.sin(tiempo * 3 + demonio["fase"]) * 8)
        aura = pygame.Surface((110, 110), pygame.SRCALPHA)
        pygame.draw.circle(aura, (150, 30, 255, 35), (55, 55), 50)
        pygame.draw.circle(aura, (210, 60, 255, 25), (55, 55), 40)
        screen.blit(aura, (x - 55, y - 55))
        pygame.draw.polygon(screen, (70, 20, 100), [(x - 18, y - 5), (x - 48, y - 25), (x - 38, y + 18), (x - 12, y + 12)])
        pygame.draw.polygon(screen, (70, 20, 100), [(x + 18, y - 5), (x + 48, y - 25), (x + 38, y + 18), (x + 12, y + 12)])
        pygame.draw.polygon(screen, (75, 15, 110), [(x, y - 30), (x - 25, y - 5), (x - 18, y + 30), (x, y + 42), (x + 18, y + 30), (x + 25, y - 5)])
        pygame.draw.circle(screen, (105, 20, 145), (x, y - 12), 20)
        pygame.draw.polygon(screen, (45, 10, 70), [(x - 13, y - 25), (x - 25, y - 45), (x - 8, y - 32)])
        pygame.draw.polygon(screen, (45, 10, 70), [(x + 13, y - 25), (x + 25, y - 45), (x + 8, y - 32)])
        pygame.draw.circle(screen, (255, 40, 70), (x - 8, y - 14), 4)
        pygame.draw.circle(screen, (255, 40, 70), (x + 8, y - 14), 4)
        pulso = int(math.sin(tiempo * 6) * 3)
        pygame.draw.circle(screen, (190, 40, 255), (x, y + 10), 9 + pulso)
        pygame.draw.circle(screen, (240, 150, 255), (x, y + 10), 4)

    def dibujar_escudo(tiempo):
        cx, cy = jefe.rect.center
        radio_base = max(jefe.rect.width, jefe.rect.height) // 2 + 30
        radio = int(radio_base + math.sin(tiempo * 6) * 6)
        halo = pygame.Surface((radio_base * 4, radio_base * 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, (140, 20, 255, 45), (radio_base * 2, radio_base * 2), radio + 20)
        pygame.draw.circle(halo, (200, 60, 255, 35), (radio_base * 2, radio_base * 2), radio + 10)
        screen.blit(halo, (cx - radio_base * 2, cy - radio_base * 2))
        for i in range(6):
            angulo = tiempo * 2 + i * (2 * math.pi / 6)
            punto = (int(cx + math.cos(angulo) * (radio + 5)), int(cy + math.sin(angulo) * (radio + 5)))
            pygame.draw.circle(screen, (220, 130, 255), punto, 6)
            pygame.draw.circle(screen, (255, 255, 255), punto, 3)
        escudo = pygame.Surface((radio * 2 + 10, radio * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(escudo, (150, 30, 240, 80), (radio + 5, radio + 5), radio)
        pygame.draw.circle(escudo, (220, 160, 255, 230), (radio + 5, radio + 5), radio, 3)
        pygame.draw.circle(escudo, (255, 255, 255, 255), (radio + 5, radio + 5), radio - 4, 1)
        screen.blit(escudo, (cx - radio - 5, cy - radio - 5))

    def cancelar_fase_al_morir():
        nonlocal fase2_activada, transicion_fase, transicion_timer
        nonlocal demonios_activos, demonios_timer, demonios_cooldown
        nonlocal demonios, proyectiles_demonio, proyectiles_demonio_timer
        nonlocal bolas_fuego, bola_fuego_timer

        fase2_activada = True
        transicion_fase = False
        transicion_timer = 0.0
        demonios_activos = False
        demonios_timer = 0.0
        demonios_cooldown = 7.8
        demonios.clear()
        proyectiles_demonio.clear()
        proyectiles_demonio_timer = 0.0
        bolas_fuego.clear()
        bola_fuego_timer = 0.0

    while en_batalla:
        dt = clock.tick(60) / 1000.0
        tiempo = pygame.time.get_ticks() / 1000.0
        if transicion_fase and tiempo_congelado_transicion is not None:
            tiempo = tiempo_congelado_transicion

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not transicion_fase:
                player.procesar_evento(event)

        if not transicion_fase:
            player.update(0, transicion_realizada=True, limite_max_x=ANCHO - 80)

        if jefe.health <= 0:
            cancelar_fase_al_morir()

        if not transicion_fase and not jefe.muerto_definitivo:
            if demonios_activos:
                jefe.cambiar_estado("idle")
                jefe.attacking = False
                jefe.has_hit = False
                jefe.hitbox = pygame.Rect(0, 0, 0, 0)
                jefe.actualizar_animacion()
                jefe.velocity_y = 0
                jefe.on_ground = True
                jefe.rect.bottom = POSICION_SUELO
                jefe.hurtbox = jefe.rect.copy()
            else:
                jefe.update(player, dt, width=ANCHO)
                jefe.rect.bottom = POSICION_SUELO
                jefe.hurtbox = jefe.rect.copy()
                jefe.rect.x = max(0, min(ANCHO - jefe.rect.width, jefe.rect.x))

        if (
            fase == 1
            and jefe.health > 0
            and jefe.health <= jefe.max_health * 0.5
            and not fase2_activada
        ):
            fase = 2
            fase2_activada = True
            transicion_fase = True
            transicion_timer = 3.0
            tiempo_congelado_transicion = tiempo

        if transicion_fase:
            transicion_timer -= dt
            if transicion_timer <= 0:
                transicion_fase = False
                tiempo_congelado_transicion = None

        if (
            fase == 2
            and not transicion_fase
            and not jefe.muerto_definitivo
            and jefe.health > 0
        ):
            bola_fuego_timer -= dt
            if bola_fuego_timer <= 0:
                bola_fuego_timer = random.uniform(1.0, 1.7)
                for _ in range(random.randint(4, 6)):
                    bolas_fuego.append({
                        "x": random.randint(80, ANCHO - 80),
                        "y": -50,
                        "speed": random.randint(380, 520),
                        "aviso_timer": 0.7,
                        "radio": random.randint(14, 20),
                    })

            for bola in bolas_fuego[:]:
                if bola["aviso_timer"] > 0:
                    bola["aviso_timer"] -= dt
                    continue
                bola["y"] += bola["speed"] * dt
                bola_rect = pygame.Rect(
                    bola["x"] - bola["radio"],
                    bola["y"] - bola["radio"],
                    bola["radio"] * 2,
                    bola["radio"] * 2,
                )
                if bola_rect.colliderect(player.hurtbox):
                    player.take_damage(12)
                    bolas_fuego.remove(bola)
                elif bola["y"] >= POSICION_SUELO:
                    bolas_fuego.remove(bola)

            if demonios_activos:
                demonios_timer -= dt
                proyectiles_demonio_timer -= dt
                if proyectiles_demonio_timer <= 0:
                    for demonio in demonios:
                        dx = player.rect.centerx - demonio["x"]
                        dy = player.rect.centery - demonio["y"]
                        distancia = max(1, math.hypot(dx, dy))
                        proyectiles_demonio.append({
                            "x": demonio["x"],
                            "y": demonio["y"],
                            "vx": dx / distancia * 360,
                            "vy": dy / distancia * 360,
                            "rect": pygame.Rect(demonio["x"] - 8, demonio["y"] - 8, 16, 16),
                        })
                    proyectiles_demonio_timer = 1.6

                for proyectil in proyectiles_demonio[:]:
                    proyectil["x"] += proyectil["vx"] * dt
                    proyectil["y"] += proyectil["vy"] * dt
                    proyectil["rect"].center = (int(proyectil["x"]), int(proyectil["y"]))
                    if proyectil["rect"].colliderect(player.hurtbox):
                        player.take_damage(10)
                        proyectiles_demonio.remove(proyectil)
                    elif not screen.get_rect().inflate(100, 100).collidepoint(
                        proyectil["rect"].center
                    ):
                        proyectiles_demonio.remove(proyectil)

                if demonios_timer <= 0:
                    demonios.clear()
                    proyectiles_demonio.clear()
                    demonios_activos = False
                    demonios_cooldown = 7.8
            else:
                demonios_cooldown -= dt
                if demonios_cooldown <= 0:
                    demonios_activos = True
                    demonios_timer = 6
                    proyectiles_demonio_timer = 0.5
                    demonios = crear_demonios()
                    jefe.velocity_y = 0
                    jefe.on_ground = True
                    jefe.rect.bottom = POSICION_SUELO
                    jefe.hurtbox = jefe.rect.copy()

        if (
            not transicion_fase
            and jefe.health > 0
            and player.atacando
            and not demonios_activos
        ):
            if player.estado == "sp_atk":
                num_imagen = int(player.frame_index) + 1
                if num_imagen in (12, 18, 20) and not player.has_hit:
                    if player.hitbox.colliderect(jefe.hurtbox):
                        jefe.take_damage(18)
                        player.has_hit = True
                elif num_imagen not in (12, 18, 20):
                    player.has_hit = False
            elif not player.has_hit and player.hitbox.colliderect(jefe.hurtbox):
                dano = 10
                if player.estado == "2_atk":
                    dano = 12
                elif player.estado == "3_atk":
                    dano = 16
                elif player.estado == "air_atk":
                    dano = 12
                jefe.take_damage(dano)
                player.has_hit = True

        if jefe.health <= 0:
            cancelar_fase_al_morir()

        screen.blit(fondo_img, (0, 0))
        if fase == 2:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((35, 0, 20, 90))
            screen.blit(overlay, (0, 0))
            dibujar_luna_roja_batalla(screen, tiempo)

        jefe.draw(screen)
        if demonios_activos and not jefe.muerto_definitivo:
            dibujar_escudo(tiempo)
            for demonio in demonios:
                dibujar_demonio(demonio, tiempo)

        for proyectil in proyectiles_demonio:
            x, y = proyectil["rect"].center
            pygame.draw.line(screen, (110, 20, 180), (x, y - 30), (x, y + 8), 8)
            pygame.draw.circle(screen, (150, 30, 230), (x, y), 14)
            pygame.draw.circle(screen, (210, 80, 255), (x, y), 8)
            pygame.draw.circle(screen, (255, 190, 255), (x, y), 3)

        for bola in bolas_fuego:
            if bola["aviso_timer"] > 0:
                aviso = pygame.Surface((50, 12), pygame.SRCALPHA)
                aviso.fill((180, 40, 255, 140))
                screen.blit(aviso, (bola["x"] - 25, POSICION_SUELO - 6))
                pygame.draw.rect(
                    screen,
                    (230, 130, 255),
                    (bola["x"] - 25, POSICION_SUELO - 6, 50, 12),
                    2,
                )
            else:
                for i in range(3):
                    offset_y = (i + 1) * 12
                    radio_estela = max(2, bola["radio"] - i * 4)
                    pygame.draw.circle(
                        screen,
                        (140, 20, 220),
                        (int(bola["x"]), int(bola["y"] - offset_y)),
                        radio_estela,
                    )
                pygame.draw.circle(screen, (160, 30, 240), (int(bola["x"]), int(bola["y"])), bola["radio"])
                pygame.draw.circle(screen, (220, 110, 255), (int(bola["x"]), int(bola["y"])), int(bola["radio"] * 0.65))
                pygame.draw.circle(screen, (255, 230, 255), (int(bola["x"]), int(bola["y"])), int(bola["radio"] * 0.3))

        screen.blit(player.image, player.rect)

        if not jefe.muerto_definitivo:
            porcentaje_vida = max(0.0, min(1.0, jefe.health / jefe.max_health))
            if IMG_LEVIATHAN is not None:
                ancho_barra = 650
                alto_barra = int(IMG_LEVIATHAN.get_height() * ancho_barra / IMG_LEVIATHAN.get_width())
                barra_sin_nombre = IMG_LEVIATHAN.copy()
                barra_sin_nombre.fill(
                    (0, 0, 0, 0),
                    pygame.Rect(
                        0,
                        int(barra_sin_nombre.get_height() * 0.75),
                        barra_sin_nombre.get_width(),
                        barra_sin_nombre.get_height(),
                    ),
                )
                barra = pygame.transform.scale(
                    barra_sin_nombre,
                    (ancho_barra, alto_barra),
                )
                x_barra = (ANCHO - ancho_barra) // 2
                y_barra = 16
                escala_barra = ancho_barra / IMG_LEVIATHAN.get_width()
                x_relleno = x_barra + int(24 * escala_barra)
                y_relleno = y_barra + int(12 * escala_barra)
                ancho_relleno = int(179 * escala_barra)
                alto_relleno = max(1, int(6 * escala_barra))
                pygame.draw.rect(screen, (20, 5, 12), (x_relleno, y_relleno, ancho_relleno, alto_relleno))
                if porcentaje_vida > 0:
                    color_vida = (255, 210, 0) if porcentaje_vida <= 0.5 else (170, 20, 35)
                    pygame.draw.rect(screen, color_vida, (x_relleno, y_relleno, int(ancho_relleno * porcentaje_vida), alto_relleno))
                screen.blit(barra, (x_barra, y_barra))
                nombre_jefe = fuente_nombre_jefe.render(
                    "Abbadon: The Guardian of the Red Eclipse",
                    True,
                    (190, 100, 255),
                )
                nombre_sombra = fuente_nombre_jefe.render(
                    "Abbadon: The Guardian of the Red Eclipse",
                    True,
                    (35, 10, 55),
                )
                rect_nombre = nombre_jefe.get_rect(
                    center=(ANCHO // 2, y_barra + int(alto_barra * 0.85))
                )
                screen.blit(nombre_sombra, (rect_nombre.x + 1, rect_nombre.y + 1))
                screen.blit(nombre_jefe, rect_nombre)

        dibujar_barra_jugador(screen, player)
        if transicion_fase:
            texto = fuente_boss_title.render("FURIA NOCTURNA", True, (255, 50, 60))
            screen.blit(texto, texto.get_rect(center=(ANCHO // 2, ALTO // 2)))

        if jefe.muerto_definitivo:
            timer_muerte_jefe += dt
            progreso = min(1.0, timer_muerte_jefe / 1.8)
            alpha_val = int(progreso * 255)
            banda = pygame.Surface((ANCHO, 120), pygame.SRCALPHA)
            banda.fill((0, 0, 0, int(progreso * 135)))
            screen.blit(banda, (0, ALTO // 2 - 60))
            texto = fuente_legend.render(
                "LEGEND FALLEN", True, (235, 195, 75)
            )
            sombra = fuente_legend.render(
                "LEGEND FALLEN", True, (25, 10, 5)
            )
            texto.set_alpha(alpha_val)
            sombra.set_alpha(alpha_val)
            rect_texto = texto.get_rect(center=(ANCHO // 2, ALTO // 2))
            screen.blit(sombra, (rect_texto.x + 3, rect_texto.y + 3))
            screen.blit(texto, rect_texto)
            if timer_muerte_jefe >= 4.8:
                mostrar_comic_final(screen)
                en_batalla = False

        pygame.display.flip()


# ==============================================================================
class Murcielago(Enemigo):
    def __init__(self, x=550, y=500):
        super().__init__("Murcielago", 3, x, y)
        self.animaciones = {
            "idle": self._cargar("fly.png", 11),
            "ataque": self._cargar("attack.png", 11),
            "dano": self._cargar("hurt.png", 3),
            "muerte": self._cargar("death.png", 4),
        }
        self.image = self.animaciones["idle"][0]
        self.estado_animacion = "idle"
        self.frame_animacion = 0.0
        self.gravity = 0
        self.jump_force = 0
        self.can_jump = False
        self.muerto_definitivo = False
        self.desaparecer_timer = None
        self.dano_timer = 0.0

    @staticmethod
    def _cargar(nombre, cuadros):
        frames = cargar_spritesheet_jokai(f"assets/enemigos/Bat/{nombre}", 1, cuadros)
        return [pygame.transform.scale(frame, (105, 105)) for frame in frames]

    def take_damage(self, damage):
        if self.health <= 0:
            return
        super().take_damage(damage)
        self.dano_timer = 0.18
        self.attacking = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        if self.health <= 0:
            self.gravity = 0.5
            self.velocity_y = 0
            self.on_ground = False
            self.plataformas = []

    def update(self, player, dt, width=ANCHO_MUNDO):
        if self.muerto_definitivo:
            return
        if self.health <= 0:
            self.aplicar_gravedad_y_suelo()
            if self.on_ground:
                if self.desaparecer_timer is None:
                    self.desaparecer_timer = 1.2
                else:
                    self.desaparecer_timer -= dt
                    if self.desaparecer_timer <= 0:
                        self.muerto_definitivo = True
            estado = "muerte"
        else:
            super().update(player, dt, width)
            self.dano_timer = max(0, self.dano_timer - dt)
            estado = "dano" if self.dano_timer > 0 else "ataque" if self.attacking else "idle"
        if estado != self.estado_animacion:
            self.estado_animacion = estado
            self.frame_animacion = 0.0
        frames = self.animaciones[estado]
        self.frame_animacion += dt * 12
        self.frame_animacion = min(self.frame_animacion, len(frames) - 1) if estado == "muerte" else self.frame_animacion % len(frames)
        self.image = pygame.transform.flip(frames[int(self.frame_animacion)], self.direction == "left", False)
        if self.dano_timer > 0 and self.health > 0:
            self.image = self.image.copy()
            self.image.fill((255, 45, 45), special_flags=pygame.BLEND_RGB_MULT)

    def draw(self, screen):
        if not self.muerto_definitivo:
            screen.blit(self.image, (self.rect.centerx - self.image.get_width() // 2, self.rect.bottom - self.image.get_height()))


class EsqueletoCueva(Enemigo):
    COLUMNAS_HOJA = 13
    TAMANO_CUADRO = 64

    def __init__(self, x=550, y=500):
        super().__init__("Esqueleto de la cueva", 2, x, y)
        hoja = pygame.image.load(
            os.path.join(BASE_DIR, "assets", "enemigos", "Skeleton enemy.png")
        ).convert_alpha()
        self.animaciones = {
            "correr": self._cargar_fila(hoja, 2, 12),
            "idle": self._cargar_fila(hoja, 3, 4),
            "golpear": self._cargar_fila(hoja, 0, 13),
            "dano": self._cargar_fila(hoja, 1, 2),
            "muerte": self._cargar_fila(hoja, 1, 12),
        }
        self.animaciones = {
            estado: [
                pygame.transform.scale(frame, (105, 105))
                for frame in frames
            ]
            for estado, frames in self.animaciones.items()
        }
        self.image = self.animaciones["idle"][0]
        self.estado_animacion = "idle"
        self.frame_animacion = 0.0
        self.velocidad_animacion = 15
        self.dano_timer = 0.0
        self.desaparecer_timer = 1.2
        self.muerto_definitivo = False

    @classmethod
    def _cargar_fila(cls, hoja, fila, cantidad):
        return [
            hoja.subsurface(
                pygame.Rect(
                    columna * cls.TAMANO_CUADRO,
                    fila * cls.TAMANO_CUADRO,
                    cls.TAMANO_CUADRO,
                    cls.TAMANO_CUADRO,
                )
            )
            for columna in range(cantidad)
        ]

    def take_damage(self, damage):
        if self.health <= 0:
            return
        super().take_damage(damage)
        self.dano_timer = 0.18
        self.attacking = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def update(self, player, dt, width=ANCHO_MUNDO):
        if self.muerto_definitivo:
            return
        if self.health <= 0:
            self.aplicar_gravedad_y_suelo()
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True
            estado = "muerte"
        else:
            super().update(player, dt, width)
            self.dano_timer = max(0, self.dano_timer - dt)
            estado = (
                "dano" if self.dano_timer > 0
                else "golpear" if self.attacking
                else "correr"
            )

        if estado != self.estado_animacion:
            self.estado_animacion = estado
            self.frame_animacion = 0.0
        frames = self.animaciones[estado]
        self.frame_animacion += dt * self.velocidad_animacion
        if estado == "muerte":
            self.frame_animacion = min(self.frame_animacion, len(frames) - 1)
        else:
            self.frame_animacion %= len(frames)
        frame = frames[int(self.frame_animacion)]
        if self.direction == "left":
            frame = pygame.transform.flip(frame, True, False)
        if self.dano_timer > 0 and self.health > 0:
            frame = frame.copy()
            frame.fill((255, 45, 45), special_flags=pygame.BLEND_RGB_MULT)
        self.image = frame

    def draw(self, screen):
        if not self.muerto_definitivo:
            bounds = self.image.get_bounding_rect()
            screen.blit(
                self.image,
                (
                    self.rect.centerx - self.image.get_width() // 2,
                    self.rect.bottom - bounds.bottom,
                ),
            )


class MimicoCueva(Enemigo):
    TAMANO_FRAME = 438

    def __init__(self, x=550, y=500, transformado=False):
        super().__init__("Mimic", 2, x, y)
        self.animaciones = {
            "opening": self._cargar_fila("opening.png", 6),
            "transform": self._cargar_fila("transform.png", 7),
            "idle": self._cargar_fila("idle_transformed.png", 9),
            "walk": self._cargar_fila("walk.png", 6),
            "attack_1": self._cargar_fila("attack_1.png", 14),
            "attack_2": self._cargar_fila("attack_2.png", 13),
            "hurt": self._cargar_fila("hurt.png", 3),
            "death": self._cargar_fila("death.png", 6),
        }
        imagen_cofre = pygame.image.load(
            os.path.join(BASE_DIR, "assets", "enemigos", "Mimic", "Idle_closed.png")
        ).convert_alpha()
        self.animaciones["closed"] = [
            pygame.transform.flip(
                pygame.transform.scale(
                    imagen_cofre, (self.TAMANO_FRAME,) * 2
                ),
                True,
                False,
            )
        ]
        self.rect = pygame.Rect(0, 0, 120, 65)
        self.rect.centerx = x
        self.rect.bottom = y
        self.direction = "left"
        self.hurtbox = self.rect.copy()
        self.health = 90
        self.max_health = 90
        self.attack_range = 155
        self.attack_cooldown_time = 1.2
        self.gravity = 0.5
        self.jump_force = 0
        self.can_jump = False
        self.on_ground = True
        self.muerto_definitivo = False
        self.desaparecer_timer = 0.8
        self.dano_timer = 0.0
        self.transformado = transformado
        self.es_cofre_cerrado = not transformado
        self.estado_animacion = "idle" if transformado else "closed"
        self.frame_animacion = 0.0
        self.velocidad_animacion = 10
        self.attack_variant = 1
        self.image = self.animaciones[self.estado_animacion][0]
        self.esperando_jugador = False
        self.ataque_coordinado = False

    @classmethod
    def _cargar_fila(cls, nombre, cantidad):
        frames = cargar_spritesheet_jokai(
            f"assets/enemigos/Mimic/{nombre}", 1, cantidad
        )
        return [
            pygame.transform.scale(frame, (cls.TAMANO_FRAME,) * 2)
            for frame in frames
        ]

    def abrir_cofre(self):
        if self.es_cofre_cerrado:
            self.es_cofre_cerrado = False
            self.estado_animacion = "opening"
            self.frame_animacion = 0.0

    def attack(self):
        estaba_atacando = self.attacking
        super().attack()
        if not estaba_atacando and self.attacking:
            self.attack_variant = 2 if self.attack_variant == 1 else 1

    def take_damage(self, damage):
        if self.health <= 0 or self.es_cofre_cerrado or not self.transformado:
            return
        super().take_damage(damage)
        self.dano_timer = 0.18
        self.attacking = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def _avanzar_animacion(self, estado, dt, repetir=False):
        if estado != self.estado_animacion:
            self.estado_animacion = estado
            self.frame_animacion = 0.0
        frames = self.animaciones[estado]
        self.frame_animacion += dt * self.velocidad_animacion
        if repetir:
            self.frame_animacion %= len(frames)
        elif self.frame_animacion >= len(frames):
            if estado == "opening":
                self.estado_animacion = "transform"
                self.frame_animacion = 0.0
                return
            if estado == "transform":
                self.transformado = True
                self.estado_animacion = "idle"
                self.frame_animacion = 0.0
                return
            if estado == "death":
                self.muerto_definitivo = True
                self.frame_animacion = len(frames) - 1
            else:
                self.frame_animacion %= len(frames)
        frame = frames[int(self.frame_animacion)]
        if self.direction == "left":
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def update(self, player, dt, width=ANCHO_MUNDO):
        if self.muerto_definitivo:
            return
        if self.health <= 0:
            self.aplicar_gravedad_y_suelo()
            self._avanzar_animacion("death", dt)
            return
        if self.es_cofre_cerrado:
            self.image = self.animaciones["closed"][0]
            self.hurtbox.topleft = self.rect.topleft
            return
        if not self.transformado:
            self._avanzar_animacion(self.estado_animacion, dt)
            return

        x_anterior = self.rect.x
        super().update(player, dt, width)
        self.dano_timer = max(0.0, self.dano_timer - dt)
        if self.dano_timer > 0:
            estado = "hurt"
        elif self.attacking:
            estado = f"attack_{self.attack_variant}"
        elif self.rect.x != x_anterior:
            estado = "walk"
        else:
            estado = "idle"
        self._avanzar_animacion(
            estado, dt, repetir=estado != "hurt"
        )

    def draw(self, screen):
        if self.muerto_definitivo:
            return
        screen.blit(
            self.image,
            (
                self.rect.centerx - self.image.get_width() // 2,
                self.rect.bottom - self.image.get_bounding_rect().bottom,
            ),
        )


TIPOS_ENEMIGO = (Murcielago, EsqueletoCueva)
DISTANCIA_ENTRE_GRUPOS = 850
PRIMER_GRUPO_X = 800
ULTIMO_GRUPO_X = HUECO_INICIO - 1100
PUNTOS_GRUPO = list(range(PRIMER_GRUPO_X, ULTIMO_GRUPO_X + 1, DISTANCIA_ENTRE_GRUPOS))
GRUPOS_PREVIOS_TUNELES = sum(
    posicion <= PUERTA_TUNELES_X for posicion in PUNTOS_GRUPO
)
DISTANCIA_VISION_ENEMIGO = 270
ANTICIPACION_APARICION_ENEMIGOS = 600


def generar_plataformas_nivel():
    plataformas = []
    x, y, indice = 350, 485, 0
    escaleras = {4, 13, 22}
    while x < HUECO_INICIO - 100:
        if indice in escaleras:
            altura = random.randint(34, 42)
            for direccion in (-1, 1):
                for _ in range(3):
                    if x >= HUECO_INICIO - 100:
                        break
                    ancho = random.randint(195, 235)
                    y = max(365, min(500, y + direccion * altura))
                    plataformas.append(pygame.Rect(x, y, ancho, 18))
                    x += ancho + random.randint(35, 65)
                    indice += 1
            continue
        ancho = random.randint(190, 280)
        plataformas.append(pygame.Rect(x, y, ancho, 18))
        x += ancho + random.randint(35, 105)
        y = max(430, min(505, y + random.randint(-32, 32)))
        indice += 1
    return plataformas


def generar_diseno_plataforma():
    return {
        "roca": random.choice([(13, 14, 17), (16, 17, 20), (11, 12, 15)]),
        "borde": random.choice([(21, 22, 25), (24, 25, 28), (18, 19, 22)]),
        "sombra": (8, 9, 12),
    }


def dibujar_plataformas(screen, scroll_x, plataformas, disenos):
    for plataforma, diseno in zip(plataformas, disenos):
        rect = plataforma.move(-scroll_x, 0)
        if rect.right < 0 or rect.left > ANCHO:
            continue
        x, y, ancho = rect.x, rect.y, rect.width
        roca = [
            (x, y + 5), (x + 16, y + 1), (x + 31, y - 2),
            (x + 54, y), (x + ancho // 3, y - 3),
            (x + ancho // 2, y - 1), (x + ancho * 2 // 3, y - 4),
            (x + ancho - 29, y), (x + ancho - 12, y + 2),
            (x + ancho, y + 7), (x + ancho - 9, y + 20),
            (x + ancho - 26, y + 29), (x + ancho - 49, y + 35),
            (x + 38, y + 36), (x + 18, y + 28), (x + 6, y + 17),
        ]
        pygame.draw.polygon(
            screen, diseno["sombra"], [(px, py + 6) for px, py in roca]
        )
        pygame.draw.polygon(screen, diseno["roca"], roca)
        pygame.draw.lines(
            screen,
            diseno["borde"],
            False,
            [(x + 8, y + 4), (x + 31, y - 2), (x + 54, y), (x + ancho // 3, y - 3)],
            2,
        )


def crear_enemigo(clase, x):
    enemigo = clase(x=x, y=POSICION_SUELO)
    enemigo.health = enemigo.max_health = 60
    enemigo.dano_ataque = 7
    enemigo.suelo_y = POSICION_SUELO
    enemigo.rect.bottom = POSICION_SUELO
    enemigo.velocity_y = 0
    enemigo.on_ground = True
    enemigo.hurtbox.topleft = enemigo.rect.topleft
    enemigo.jump_force = 0 if isinstance(enemigo, Murcielago) else -15
    if isinstance(enemigo, Murcielago):
        enemigo.rect.bottom -= 115
        enemigo.hurtbox.topleft = enemigo.rect.topleft
    return enemigo


def obtener_animacion_idle(enemigo):
    if isinstance(enemigo, Murcielago):
        return enemigo.animaciones["idle"]
    if isinstance(enemigo, EsqueletoCueva):
        return enemigo.animaciones["idle"]
    return enemigo.animaciones["idle"]


def actualizar_animacion_idle(enemigo, dt):
    frames = obtener_animacion_idle(enemigo)
    enemigo.frame_idle = (enemigo.frame_idle + dt * 6) % len(frames)
    imagen = frames[int(enemigo.frame_idle)]
    enemigo.image = pygame.transform.flip(imagen, enemigo.direction == "left", False)


def generar_grupo_enemigos(posicion, indice_grupo=0):
    clases = [TIPOS_ENEMIGO[indice_grupo % 2], TIPOS_ENEMIGO[(indice_grupo + 1) % 2]]
    plataforma_candidata = [p for p in plataformas_nivel if posicion+360 <= p.centerx <= posicion+700]
    plataforma = min(plataforma_candidata or plataformas_nivel, key=lambda p: abs(p.centerx-(posicion+520)))
    enemigos = []
    for indice, clase in enumerate(clases):
        x = posicion + 360 if indice == 0 else plataforma.centerx
        enemigo = crear_enemigo(clase, x)
        enemigo.flank_side = -1 if indice % 2 == 0 else 1
        enemigo.preferred_distance = 70
        enemigo.attack_range = DISTANCIA_VISION_ENEMIGO
        enemigo.ataque_coordinado = True
        enemigo.rect.centerx = x
        if isinstance(enemigo, Murcielago):
            enemigo.gravity = 0
            enemigo.plataformas = []
            enemigo.on_ground = False
        else:
            enemigo.plataformas = plataformas_nivel
        if indice == 1 and not isinstance(enemigo, Murcielago):
            enemigo.rect.bottom = plataforma.top
        enemigo.velocity_y = 0
        enemigo.on_ground = True
        if isinstance(enemigo, Murcielago):
            enemigo.on_ground = False
            plataformas_vuelo = [
                p for p in plataformas_nivel
                if abs(p.centerx - enemigo.rect.centerx) <= 500
            ] or plataformas_nivel
            plataforma_vuelo = min(
                plataformas_vuelo,
                key=lambda p: abs(p.centerx - enemigo.rect.centerx),
            )
            alturas_vuelo = []
            if plataforma_vuelo.top >= 170:
                alturas_vuelo.append(("arriba", plataforma_vuelo.top - 50))
            if POSICION_SUELO - plataforma_vuelo.bottom >= 160:
                alturas_vuelo.append(("abajo", plataforma_vuelo.bottom + 50))
            if alturas_vuelo:
                modo_vuelo, altura = random.choice(alturas_vuelo)
                if modo_vuelo == "arriba":
                    enemigo.rect.bottom = altura
                else:
                    enemigo.rect.top = altura
        enemigo.hurtbox.topleft = enemigo.rect.topleft
        enemigo.strafe_timer = enemigo.strafe_direction = 0
        enemigo.jump_cooldown = random.uniform(0.4, 1.4)
        enemigo.speed = random.randint(3, 5)
        enemigo.esperando_jugador = True
        enemigo.distancia_vision = DISTANCIA_VISION_ENEMIGO
        enemigo.frame_idle = 0.0
        enemigo.direction = "left"
        enemigos.append(enemigo)
    for enemigo in enemigos:
        enemigo.allies = enemigos
    return enemigos


def enemigo_derrotado(enemigo):
    return enemigo.health <= 0 or getattr(enemigo, "muerto_definitivo", False)


def separar_enemigos(enemigos, ancho_mundo):
    activos = [e for e in enemigos if e.health > 0 and not getattr(e, "muerto_definitivo", False)]
    for _ in range(3):
        for indice, primero in enumerate(activos):
            for segundo in activos[indice+1:]:
                if abs(primero.rect.centery-segundo.rect.centery) >= (primero.rect.height+segundo.rect.height)//2+20:
                    continue
                signo = 1 if primero.rect.centerx <= segundo.rect.centerx else -1
                minimo = (primero.rect.width+segundo.rect.width)//2+18
                empuje = minimo - abs(segundo.rect.centerx-primero.rect.centerx)
                if empuje <= 0:
                    continue
                x1, x2 = primero.rect.x, segundo.rect.x
                primero.rect.centerx -= signo*((empuje+1)//2)
                segundo.rect.centerx += signo*(empuje//2)
                primero.rect.x = max(0,min(ancho_mundo-primero.rect.width,primero.rect.x))
                segundo.rect.x = max(0,min(ancho_mundo-segundo.rect.width,segundo.rect.x))
                primero.hitbox.x += primero.rect.x-x1
                segundo.hitbox.x += segundo.rect.x-x2
                primero.hurtbox.topleft = primero.rect.topleft
                segundo.hurtbox.topleft = segundo.rect.topleft


def ejecutar_prueba_tuneles(screen, player):
    global POSICION_SUELO

    suelo_original = POSICION_SUELO
    POSICION_SUELO = 590
    player_world_x = player.pos_x
    player_scroll = player.scroll_x_actual
    player_platforms = player.plataformas
    player.plataformas = []
    player.pos_x = 100
    player.rect.midbottom = (int(player.pos_x), POSICION_SUELO)
    player.velocidad_x = 0
    player.velocidad_y = 0
    player.en_suelo = True
    player.plataforma_actual = None
    player.plataforma_ignorada = None

    puerta_x = 1290
    orden_tuneles = [
        ("roja", 1110, (235, 65, 65)),
        ("amarilla", 670, (255, 205, 65)),
        ("azul", 185, (75, 145, 255)),
    ]
    pista = (
        "Tres magos se sentaron a la mesa. El mago del Fuego se sentó primero. "
        "El mago del Agua se sentó al final porque se atraganto tomando agua. "
        "El mago de la rayo se sentó justo en medio de los dos.\n"
        "Solo entrando a cada sala en este orden podras avanzar"
    )
    indice_tunel = 0
    pista_abierta = False
    pista_leida = False
    escena = "pasillo"
    enemigos_sala = []
    enemigos_generados = 0
    mensaje = "Acércate a la puerta y presiona C."
    mensaje_timer = 0.0
    reloj = pygame.time.Clock()
    vista_jugador = VistaJugadorMundo(player)
    fuente_pista = pygame.font.SysFont("Georgia", 26, bold=True)
    fuente_estado = pygame.font.SysFont("Arial", 24, bold=True)
    colores_tunel = {
        "roja": (235, 65, 65),
        "azul": (75, 145, 255),
        "amarilla": (255, 205, 65),
    }

    def dibujar_mensaje(texto, color=(255, 255, 255), y=ALTO - 38):
        etiqueta = fuente_estado.render(texto, True, color)
        rect = etiqueta.get_rect(center=(ANCHO // 2, y))
        sombra = pygame.Surface((rect.width + 24, rect.height + 12), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 190))
        screen.blit(sombra, (rect.x - 12, rect.y - 6))
        screen.blit(etiqueta, rect)

    def entrar_a_sala(nombre):
        nonlocal escena, enemigos_sala, enemigos_generados
        nonlocal mensaje

        escena = "sala"
        enemigos_sala = [
            preparar_enemigo_sala(indice) for indice in range(2)
        ]
        for enemigo in enemigos_sala:
            enemigo.allies = enemigos_sala
        enemigos_generados = 2
        mensaje = f"TUNEL {nombre.upper()}"
        player.pos_x = ANCHO - 100
        player.rect.midbottom = (int(player.pos_x), POSICION_SUELO)
        player.velocidad_x = 0
        player.velocidad_y = 0
        player.en_suelo = True
        player.atacando = False
        player.rodando = False
        player.defendiendo = False
        player.actualizar_hitboxes()

    def preparar_enemigo_sala(indice):
        clase = (Murcielago, EsqueletoCueva)[indice % 2]
        x = 450 if indice == 0 else 850
        enemigo = crear_enemigo(clase, x)
        enemigo.suelo_y = POSICION_SUELO
        enemigo.speed = random.randint(3, 5)
        enemigo.attack_range = 165
        enemigo.attack_cooldown_time = 1.35
        enemigo.ataque_coordinado = False
        enemigo.esperando_jugador = True
        enemigo.distancia_vision = 260
        enemigo.plataformas = []
        if isinstance(enemigo, Murcielago):
            enemigo.gravity = 0
            enemigo.rect.bottom = POSICION_SUELO - 150
            enemigo.on_ground = False
        else:
            enemigo.rect.bottom = POSICION_SUELO
            enemigo.on_ground = True
        enemigo.hurtbox.topleft = enemigo.rect.topleft
        return enemigo

    ejecutando_prueba = True
    try:
        while ejecutando_prueba:
            dt = reloj.tick(60) / 1000.0
            mensaje_timer = max(0.0, mensaje_timer - dt)
            interactuando = False

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_c:
                    if pista_abierta:
                        pista_abierta = False
                        pista_leida = True
                    elif escena == "sala":
                        sala_completada = (
                            enemigos_generados == 2
                            and all(enemigo_derrotado(e) for e in enemigos_sala)
                        )
                        if sala_completada and player.pos_x <= 155:
                            nombre, _, _ = orden_tuneles[indice_tunel]
                            escena = "pasillo"
                            indice_tunel += 1
                            player.pos_x = next(
                                (x for nombre_tunel, x, _ in orden_tuneles
                                 if nombre_tunel == nombre),
                                180,
                            )
                            player.rect.midbottom = (
                                int(player.pos_x), POSICION_SUELO
                            )
                            player.velocidad_x = 0
                            mensaje = f"Regresaste del tunel {nombre}."
                            mensaje_timer = 2.0
                        elif not sala_completada:
                            mensaje = "Derrota a todos los enemigos primero."
                            mensaje_timer = 2.0
                        else:
                            mensaje = "Ve hacia la izquierda y presiona C para salir."
                            mensaje_timer = 2.0
                    else:
                        interactuando = True

                if not pista_abierta and not (
                    evento.type == pygame.KEYDOWN and evento.key == pygame.K_c
                ):
                    player.procesar_evento(evento)

            if not ejecutando_prueba:
                break

            if escena == "pasillo" and interactuando:
                if abs(player.pos_x - puerta_x) <= 115:
                    if not pista_leida:
                        pista_abierta = True
                        mensaje = ""
                    elif indice_tunel == len(orden_tuneles):
                        player.pos_x = player_world_x
                        player.scroll_x_actual = player_scroll
                        player.plataformas = player_platforms
                        POSICION_SUELO = suelo_original
                        player.rect.midbottom = (
                            int(player.pos_x - player_scroll),
                            suelo_original,
                        )
                        player.actualizar_hitboxes()
                        return True
                    else:
                        mensaje = "Primero completa los tres tuneles."
                        mensaje_timer = 2.0
                elif not pista_leida:
                    mensaje = "Primero lee la pista junto a la puerta."
                    mensaje_timer = 2.0
                elif indice_tunel >= len(orden_tuneles):
                    mensaje = "Ya completaste los tuneles. Regresa a la puerta."
                    mensaje_timer = 2.0
                else:
                    tunel_cercano = min(
                        orden_tuneles,
                        key=lambda tunel: abs(player.pos_x - tunel[1]),
                    )
                    nombre, x_tunel, _ = tunel_cercano
                    if abs(player.pos_x - x_tunel) > 115:
                        mensaje = "Acercate a la puerta o a una entrada."
                        mensaje_timer = 1.5
                    elif nombre != orden_tuneles[indice_tunel][0]:
                        mensaje = "Este no es el camino."
                        mensaje_timer = 2.0
                    else:
                        entrar_a_sala(nombre)

            if not pista_abierta:
                player.update(
                    0, True, limite_max_x=ANCHO - 80
                )
                vista_jugador.sync(0)

            if escena == "sala":
                for enemigo in enemigos_sala:
                    if enemigo.health <= 0 and not getattr(
                        enemigo, "muerto_definitivo", False
                    ):
                        enemigo.update(vista_jugador, dt, width=ANCHO)
                for enemigo in enemigos_sala:
                    if enemigo_derrotado(enemigo):
                        continue
                    enemigo.allies = enemigos_sala
                    enemigo.update(vista_jugador, dt, width=ANCHO)
                    if (
                        enemigo.health > 0
                        and player.atacando
                        and enemigo not in player.enemigos_golpeados
                        and vista_jugador.hitbox.width > 0
                        and vista_jugador.hitbox.colliderect(enemigo.hurtbox)
                    ):
                        enemigo.take_damage(20)
                        player.enemigos_golpeados.add(enemigo)
                        player.has_hit = True
                    hitbox_enemigo = getattr(enemigo, "hitbox", None)
                    if (
                        enemigo.health > 0
                        and hitbox_enemigo is not None
                        and hitbox_enemigo.width > 0
                        and not getattr(enemigo, "has_hit", False)
                        and hitbox_enemigo.colliderect(vista_jugador.hurtbox)
                    ):
                        player.take_damage(
                            getattr(enemigo, "dano_ataque", 10)
                        )
                        enemigo.has_hit = True

            fondo = fondo_tuneles if escena == "pasillo" else fondos[0]
            screen.blit(fondo, (0, 0))
            screen.blit(player.image, player.rect)

            if escena == "pasillo":
                if pista_abierta:
                    panel = pygame.Surface((ANCHO - 220, 280), pygame.SRCALPHA)
                    panel.fill((4, 7, 12, 225))
                    panel_rect = panel.get_rect(center=(ANCHO // 2, ALTO // 2))
                    screen.blit(panel, panel_rect)
                    lineas = []
                    for parrafo in pista.splitlines():
                        linea = ""
                        for palabra in parrafo.split():
                            prueba = f"{linea} {palabra}".strip()
                            if fuente_pista.size(prueba)[0] > panel.get_width() - 70:
                                lineas.append(linea)
                                linea = palabra
                            else:
                                linea = prueba
                        if linea:
                            lineas.append(linea)
                    for indice, texto_linea in enumerate(lineas):
                        texto = fuente_pista.render(
                            texto_linea, True, (245, 240, 225)
                        )
                        screen.blit(
                            texto,
                            texto.get_rect(
                                center=(
                                    ANCHO // 2,
                                    panel_rect.y + 55 + indice * 38,
                                )
                            ),
                        )
                    dibujar_mensaje("Presiona C para cerrar la pista.")
                else:
                    dibujar_barra_jugador(screen, player)
                    tunel_cercano = min(
                        orden_tuneles,
                        key=lambda tunel: abs(player.pos_x - tunel[1]),
                    )
                    en_puerta = abs(player.pos_x - puerta_x) <= 115
                    en_tunel = abs(player.pos_x - tunel_cercano[1]) <= 115
                    if mensaje_timer > 0:
                        dibujar_mensaje(mensaje, (255, 220, 120))
                    elif en_puerta and pista_leida and indice_tunel == len(orden_tuneles):
                        dibujar_mensaje("Presiona C en la puerta para continuar.")
                    elif en_puerta and not pista_leida:
                        dibujar_mensaje("Presiona C para leer la pista.")
                    elif en_tunel and pista_leida and indice_tunel < len(orden_tuneles):
                        nombre = tunel_cercano[0]
                        if nombre == orden_tuneles[indice_tunel][0]:
                            dibujar_mensaje(
                                f"Presiona C para entrar al tunel {nombre}.",
                                colores_tunel[nombre],
                            )
                        else:
                            dibujar_mensaje("Este no es el camino.", (255, 220, 120))
                    else:
                        dibujar_mensaje(
                            "Explora las entradas de la cueva.",
                            (220, 220, 220),
                        )
            else:
                dibujar_barra_jugador(screen, player)
                for enemigo in enemigos_sala:
                    if not getattr(enemigo, "muerto_definitivo", False):
                        enemigo.draw(screen)
                if all(enemigo_derrotado(e) for e in enemigos_sala):
                    if player.pos_x <= 155:
                        dibujar_mensaje(
                            "Presiona C para volver a los tuneles.",
                            (150, 235, 175),
                        )
                    else:
                        dibujar_mensaje(
                            "Sala despejada: ve a la izquierda para salir.",
                            (150, 235, 175),
                        )
                else:
                    dibujar_mensaje(
                        f"ENEMIGOS RESTANTES: "
                        f"{sum(not enemigo_derrotado(e) for e in enemigos_sala)}",
                        (235, 205, 175),
                    )
            pygame.display.flip()

    finally:
        POSICION_SUELO = suelo_original
        player.plataformas = player_platforms


mostrar_comic_inicio(pantalla)
heroe = Jugador(200, POSICION_SUELO)
todos_los_sprites = pygame.sprite.Group(heroe)
vista_heroe = VistaJugadorMundo(heroe)
plataformas_nivel = generar_plataformas_nivel()
plataformas_nivel = [
    plataforma
    for plataforma in plataformas_nivel
    if plataforma.right <= PUERTA_TUNELES_X
    or plataforma.left >= FIN_TRAMO_FONDO_TUNELES
]
disenos_plataformas = [generar_diseno_plataforma() for _ in plataformas_nivel]
heroe.plataformas = plataformas_nivel
enemigos_nivel = []
proximo_grupo = 0
scroll_x = 0
transicion_realizada = False
puzzle_completado = False
mimicos_cofres = []
enemigos_post_cofre_generados = False
ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    dt = reloj.tick(60) / 1000.0

    while (
        proximo_grupo < len(PUNTOS_GRUPO)
        and heroe.pos_x
        >= PUNTOS_GRUPO[proximo_grupo] - ANTICIPACION_APARICION_ENEMIGOS
        and (
            puzzle_completado
            or PUNTOS_GRUPO[proximo_grupo] <= PUERTA_TUNELES_X
        )
    ):
        nuevo_grupo = generar_grupo_enemigos(
            PUNTOS_GRUPO[proximo_grupo], proximo_grupo
        )
        enemigos_nivel.extend(nuevo_grupo)
        proximo_grupo += 1
    todos_los_grupos_generados = proximo_grupo == len(PUNTOS_GRUPO)
    enemigos_pendientes = [e for e in enemigos_nivel if not enemigo_derrotado(e)]
    entrada_tuneles_desbloqueada = (
        proximo_grupo >= GRUPOS_PREVIOS_TUNELES
        and not enemigos_pendientes
    )
    portal_liberado = todos_los_grupos_generados and not enemigos_pendientes
    limite_max_x = HUECO_FIN if portal_liberado else HUECO_INICIO-40
    en_puerta_tuneles = (
        not puzzle_completado
        and abs(heroe.pos_x - PUERTA_TUNELES_X) <= 115
    )
    mimico_cercano = next(
        (
            enemigo
            for enemigo in enemigos_nivel
            if isinstance(enemigo, MimicoCueva)
            and enemigo.es_cofre_cerrado
            and abs(heroe.pos_x - enemigo.rect.centerx) <= 145
        ),
        None,
    )
    if not puzzle_completado:
        limite_max_x = min(limite_max_x, PUERTA_TUNELES_X)
    en_zona_hueco = portal_liberado and HUECO_INICIO <= heroe.pos_x <= HUECO_FIN and not transicion_realizada

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and en_puerta_tuneles
            and entrada_tuneles_desbloqueada
        ):
            puzzle_completado = ejecutar_prueba_tuneles(pantalla, heroe)
            if puzzle_completado:
                enemigos_nivel.clear()
                plataformas_restantes = [
                    (plataforma, diseno)
                    for plataforma, diseno in zip(
                        plataformas_nivel, disenos_plataformas
                    )
                    if plataforma.left >= FIN_TRAMO_FONDO_TUNELES
                ]
                plataformas_nivel[:] = [
                    plataforma for plataforma, _ in plataformas_restantes
                ]
                disenos_plataformas[:] = [
                    diseno for _, diseno in plataformas_restantes
                ]
                heroe.plataformas = plataformas_nivel
                proximo_grupo = len(PUNTOS_GRUPO)
                mimicos_cofres = [
                    MimicoCueva(LIMITE_POST_TUNELES_X + 650, POSICION_SUELO)
                ]
                enemigos_post_cofre_generados = False
                enemigos_nivel.extend(mimicos_cofres)
                heroe.pos_x = LIMITE_POST_TUNELES_X
                heroe.velocidad_x = 0
                limite_max_x = (
                    HUECO_FIN if portal_liberado else HUECO_INICIO - 40
                )
                en_puerta_tuneles = False
                heroe.rect.centerx = int(heroe.pos_x - scroll_x)
                heroe.actualizar_hitboxes()
            else:
                ejecutando = False
                break
        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_c
            and mimico_cercano is not None
        ):
            for cofre in mimicos_cofres:
                cofre.abrir_cofre()
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_c and en_zona_hueco:
            heroe.health = heroe.max_health
            pantalla.blit(fondo_entrada_jefe, (0,0))
            titulo = fuente_boss_title.render("Abbadon", True, (230,225,220))
            subtitulo = fuente_boss_subtitle.render("El Senor Oscuro", True, (205,190,175))
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2,ALTO//2-25)))
            pantalla.blit(subtitulo, subtitulo.get_rect(center=(ANCHO//2,ALTO//2+45)))
            pygame.display.flip()
            pygame.time.wait(2000)
            transicion_realizada = True
            ejecutar_batalla_werewolf(pantalla, heroe, fondo_batalla)
            ejecutando = False
            break
        else:
            heroe.procesar_evento(evento)
    if not ejecutando:
        break

    todos_los_sprites.update(
        scroll_x,
        transicion_realizada,
        limite_max_x=limite_max_x,
        limite_min_x=LIMITE_POST_TUNELES_X if puzzle_completado else None,
    )
    scroll_x = max(0,min(heroe.pos_x-ANCHO*0.4,ANCHO_MUNDO-ANCHO))
    heroe.rect.centerx = int(heroe.pos_x-scroll_x)
    heroe.actualizar_hitboxes()
    vista_heroe.sync(scroll_x)

    for enemigo in enemigos_nivel:
        if enemigo.health <= 0 and not getattr(enemigo,"muerto_definitivo",False):
            enemigo.update(vista_heroe,dt,width=ANCHO_MUNDO)
    for enemigo in enemigos_nivel:
        if enemigo_derrotado(enemigo):
            continue
        if getattr(enemigo,"esperando_jugador",False):
            dx = abs(vista_heroe.pos_x-enemigo.rect.centerx)
            dy = abs(vista_heroe.hurtbox.centery-enemigo.rect.centery)
            if dx <= enemigo.distancia_vision and dy <= 300:
                enemigo.esperando_jugador = False
            else:
                actualizar_animacion_idle(enemigo,dt)
                continue
        enemigo.allies = enemigos_nivel
        enemigo.suelo_y = POSICION_SUELO
        enemigo.plataformas = plataformas_nivel
        enemigo.update(vista_heroe,dt,width=ANCHO_MUNDO)
        if enemigo.health > 0:
            if (
                heroe.atacando
                and not getattr(enemigo, "es_cofre_cerrado", False)
                and enemigo not in heroe.enemigos_golpeados
                and vista_heroe.hitbox.width > 0
                and vista_heroe.hitbox.colliderect(enemigo.hurtbox)
            ):
                enemigo.take_damage(20)
                heroe.enemigos_golpeados.add(enemigo)
                heroe.has_hit = True
            hb = getattr(enemigo,"hitbox",None)
            if hb is not None and hb.width > 0 and not getattr(enemigo,"has_hit",False) and hb.colliderect(vista_heroe.hurtbox):
                heroe.take_damage(getattr(enemigo,"dano_ataque",10))
                enemigo.has_hit = True

    if (
        puzzle_completado
        and mimicos_cofres
        and mimicos_cofres[0].health <= 0
        and not enemigos_post_cofre_generados
    ):
        enemigos_post_cofre = generar_grupo_enemigos(
            mimicos_cofres[0].rect.centerx + 450
        )
        enemigos_nivel.extend(enemigos_post_cofre)
        enemigos_post_cofre_generados = True

    cercanos = [
        e for e in enemigos_nivel
        if e.health > 0
        and not getattr(e, "es_cofre_cerrado", False)
        and not getattr(e, "esperando_jugador", False)
        and not getattr(e, "muerto_definitivo", False)
        and abs(e.rect.centerx - vista_heroe.pos_x) <= 175
        and abs(e.rect.centery - vista_heroe.hurtbox.centery) <= 120
    ]
    if cercanos and all(not e.attacking and e.attack_cooldown<=0 for e in cercanos):
        for enemigo in cercanos:
            enemigo.attack()
    separar_enemigos(enemigos_nivel,ANCHO_MUNDO)
    if not puzzle_completado:
        for enemigo in enemigos_nivel:
            if enemigo.rect.right > PUERTA_TUNELES_X:
                desplazamiento = PUERTA_TUNELES_X - enemigo.rect.right
                enemigo.rect.x += desplazamiento
                enemigo.hitbox.x += desplazamiento
                enemigo.hurtbox.x += desplazamiento

    for tramo in range(ANCHO_MUNDO//ANCHO):
        x = tramo*ANCHO-scroll_x
        if -ANCHO < x < ANCHO:
            if tramo == ANCHO_MUNDO // ANCHO - 1:
                fondo = fondo_entrada_jefe
            elif tramo == TRAMO_FONDO_TUNELES and not puzzle_completado:
                fondo = fondo_tuneles
            else:
                fondo = fondos[tramo % len(fondos)]
            pantalla.blit(fondo,(x,0))
    dibujar_plataformas(pantalla,scroll_x,plataformas_nivel,disenos_plataformas)
    todos_los_sprites.draw(pantalla)
    for enemigo in enemigos_nivel:
        if not getattr(enemigo,"muerto_definitivo",False):
            x_original = enemigo.rect.x
            enemigo.rect.x -= scroll_x
            enemigo.draw(pantalla)
            enemigo.rect.x = x_original

    dibujar_barra_jugador(pantalla,heroe)
    progreso = min(100,int(heroe.pos_x*100/PORTAL_X))
    if portal_liberado:
        mensaje, color = "CAMINO DESPEJADO: ACERCATE A LA ENTRADA", (160,205,220)
    elif enemigos_pendientes:
        mensaje, color = f"RUMBO A ABBADON: {progreso}%  |  ENEMIGOS: {len(enemigos_pendientes)}", (215,205,190)
    else:
        mensaje, color = f"RUMBO A ABBADON: {progreso}%", (215,205,190)
    sombra = fuente_progreso.render(mensaje,True,(0,0,0))
    texto = fuente_progreso.render(mensaje,True,color)
    rect = texto.get_rect(topright=(ANCHO-30,20))
    pantalla.blit(sombra,(rect.x+2,rect.y+2))
    pantalla.blit(texto,rect)
    if en_puerta_tuneles:
        texto_puerta = fuente_ui.render(
            (
                "PRESIONA C PARA ENTRAR A LA SALA"
                if entrada_tuneles_desbloqueada
                else "DERROTA A TODOS LOS ENEMIGOS PARA ENTRAR"
            ),
            True,
            (255, 235, 190),
        )
        rect_puerta = texto_puerta.get_rect(
            center=(ANCHO // 2, ALTO - 45)
        )
        pantalla.blit(texto_puerta, rect_puerta)
    if mimico_cercano is not None:
        texto_cofre = fuente_ui.render(
            "PRESIONA C PARA ABRIR EL COFRE",
            True,
            (255, 235, 190),
        )
        rect_cofre = texto_cofre.get_rect(
            center=(ANCHO // 2, ALTO - 75)
        )
        pantalla.blit(texto_cofre, rect_cofre)
    if en_zona_hueco:
        dibujar_boton_demoniaco(pantalla)
    pygame.display.flip()

pygame.quit()
sys.exit()
