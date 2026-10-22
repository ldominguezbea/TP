import os
import sys
import random
import math
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from enemigos import HombreLoboNegro, HombreLoboRojo, Mushroom

pygame.init()
pygame.font.init()

# 1. Configuración de pantalla y mundo
ANCHO, ALTO = 1350, 700
POSICION_SUELO = 620

# Recorrido lateral continuo hasta la entrada del jefe.
ANCHO_MUNDO = ANCHO * 7
PORTAL_X = ANCHO_MUNDO - 500
HUECO_INICIO = PORTAL_X - 150
HUECO_FIN = PORTAL_X + 150

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 2 - Batalla de Jefe")

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
def cargar_imagen_comic(nombre_archivo):
    nombres_archivo = [nombre_archivo]
    if nombre_archivo.lower().endswith(".png"):
        nombres_archivo.append(f"{nombre_archivo}.png")

    carpetas = (
        ("imagenes", "Nivel2"),
        ("assets", "imagenes", "Nivel2"),
    )
    rutas = [
        os.path.join(BASE_DIR, *carpeta, nombre)
        for nombre in nombres_archivo
        for carpeta in carpetas
    ]
    for ruta in rutas:
        if os.path.isfile(ruta):
            img = pygame.image.load(ruta).convert()
            return pygame.transform.scale(img, (ANCHO, ALTO))

    raise FileNotFoundError(
        f"No se encontró el cómic {nombre_archivo}. Rutas revisadas: {rutas}"
    )


def mostrar_comic_inicio(screen):
    img_inicio = cargar_imagen_comic("comic_inicio2.png")
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

        lbl_enter = fuente_ui.render("PRESIONA ENTER PARA COMENZAR EL NIVEL 2", True, (255, 255, 255))
        rect_txt = lbl_enter.get_rect(center=(ANCHO // 2, ALTO - 35))
        sombra_bg = pygame.Surface((rect_txt.width + 20, rect_txt.height + 10))
        sombra_bg.fill((0, 0, 0))
        sombra_bg.set_alpha(180)

        screen.blit(sombra_bg, (rect_txt.x - 10, rect_txt.y - 5))
        screen.blit(lbl_enter, rect_txt)

        pygame.display.flip()
        reloj.tick(60)


def mostrar_comic_final(screen):
    img_final = cargar_imagen_comic("comic_final2.png")
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

        lbl_fin = fuente_ui.render("FIN DEL NIVEL 2 - Presiona cualquier tecla para continuar", True, (255, 255, 255))
        rect_txt = lbl_fin.get_rect(center=(ANCHO // 2, ALTO - 35))
        sombra_bg = pygame.Surface((rect_txt.width + 20, rect_txt.height + 10))
        sombra_bg.fill((0, 0, 0))
        sombra_bg.set_alpha(180)

        screen.blit(sombra_bg, (rect_txt.x - 10, rect_txt.y - 5))
        screen.blit(lbl_fin, rect_txt)

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
def cargar_fondo_nivel2(nombre_archivo):
    rutas = (
        os.path.join(BASE_DIR, "imagenes", "Nivel2", nombre_archivo),
        os.path.join(BASE_DIR, "assets", "imagenes", "Nivel2", nombre_archivo),
    )
    for ruta_imagen in rutas:
        if os.path.exists(ruta_imagen):
            img = pygame.image.load(ruta_imagen).convert()
            return pygame.transform.scale(img, (ANCHO, ALTO))

    surf = pygame.Surface((ANCHO, ALTO))
    surf.fill((20, 15, 25))
    return surf


fondos = [
    cargar_fondo_nivel2("Nivel2_imagen2.png"),
    cargar_fondo_nivel2("Nivel2_imagen4.png"),
]
fondo_batalla = cargar_fondo_nivel2("Nivel2_imagen1.png")
fondo_jefe = cargar_fondo_nivel2("Nivel2_imagen3.png")


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
            if evento.key == pygame.K_w and self.en_suelo and not (self.rodando or self.defendiendo):
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
        self.velocidad_y += self.gravedad
        self.rect.y += self.velocidad_y

        if self.velocidad_y >= 0:
            for plataforma in self.plataformas:
                plataforma_pantalla = plataforma.move(-self.scroll_x_actual, 0)
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
                    break

        if not self.en_suelo and self.rect.bottom >= POSICION_SUELO:
            self.rect.bottom = POSICION_SUELO
            self.velocidad_y = 0
            self.en_suelo = True

    def take_damage(self, damage):
        if self.rodando:
            return
        self.health = max(0, self.health - damage)

    def update(self, scroll_x, transicion_realizada, limite_max_x=HUECO_FIN):
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
    txt_sombra = fuente_lava_pixel.render(txt_str, False, (180, 30, 0))
    txt_fuego = fuente_lava_pixel.render(txt_str, False, (255, 170, 0))

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

    while en_batalla:
        dt = clock.tick(60) / 1000.0
        tiempo = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            player.procesar_evento(event)

        player.update(0, transicion_realizada=True, limite_max_x=ANCHO - 80)

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
            and jefe.health <= jefe.max_health * 0.5
            and not fase2_activada
        ):
            fase = 2
            fase2_activada = True
            transicion_fase = True
            transicion_timer = 3.0

        if transicion_fase:
            transicion_timer -= dt
            if transicion_timer <= 0:
                transicion_fase = False

        if fase == 2 and not transicion_fase and not jefe.muerto_definitivo:
            bola_fuego_timer -= dt
            if bola_fuego_timer <= 0:
                bola_fuego_timer = random.uniform(1.8, 3.0)
                for _ in range(random.randint(2, 4)):
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

        if jefe.health > 0 and player.atacando and not demonios_activos:
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
# GRUPOS DE ENEMIGOS ACTIVADOS POR DISTANCIA
# ==============================================================================
TIPOS_ENEMIGO = [HombreLoboRojo, HombreLoboNegro, Mushroom]
DISTANCIA_ENTRE_GRUPOS = 850
PRIMER_GRUPO_X = 800
ULTIMO_GRUPO_X = HUECO_INICIO - 1100
PUNTOS_GRUPO = list(range(PRIMER_GRUPO_X, ULTIMO_GRUPO_X + 1, DISTANCIA_ENTRE_GRUPOS))

def generar_plataformas_nivel():
    plataformas = []
    x = 350
    y = 520

    while x < HUECO_INICIO - 100:
        ancho = random.randint(190, 280)
        plataformas.append(pygame.Rect(x, y, ancho, 18))

        # El hueco y el cambio de altura quedan dentro del alcance de un salto.
        x += ancho + random.randint(35, 105)
        y = max(325, min(560, y + random.randint(-75, 75)))

    return plataformas


def generar_diseno_plataforma():
    return {
        "madera": random.choice([
            (91, 59, 37), (108, 72, 43), (78, 57, 40),
        ]),
        "musgo": random.choice([
            (30, 58, 25), (39, 68, 29), (26, 50, 22),
        ]),
        "hojas": [
            (random.random(), random.randint(5, 13), random.choice([
                (37, 68, 29), (54, 79, 31), (28, 56, 29),
            ]))
            for _ in range(6)
        ],
        "nudos": [
            (random.random(), random.randint(3, 6))
            for _ in range(2)
        ],
    }


def dibujar_plataformas(screen, scroll_x, plataformas, disenos):
    for plataforma, diseno in zip(plataformas, disenos):
        rect = plataforma.move(-scroll_x, 0)
        if rect.right < 0 or rect.left > ANCHO:
            continue

        sombra = rect.move(0, 7)
        pygame.draw.rect(screen, (32, 29, 22), sombra, border_radius=7)
        pygame.draw.rect(screen, diseno["madera"], rect, border_radius=6)
        pygame.draw.rect(
            screen,
            (121, 85, 54),
            (rect.x + 3, rect.y + 7, max(1, rect.width - 6), rect.height - 9),
            border_radius=4,
        )

        copa_musgo = pygame.Rect(rect.x, rect.y - 2, rect.width, 9)
        pygame.draw.rect(screen, diseno["musgo"], copa_musgo, border_radius=5)
        pygame.draw.line(
            screen, (66, 83, 42),
            (rect.x + 8, rect.y + 2), (rect.right - 8, rect.y + 2), 2,
        )

        for fraccion, radio, color in diseno["hojas"]:
            hoja_x = rect.x + int(fraccion * max(1, rect.width - radio * 2))
            pygame.draw.ellipse(
                screen, color,
                (hoja_x, rect.y - radio // 2, radio * 2, radio),
            )

        for fraccion, radio in diseno["nudos"]:
            nudo_x = rect.x + int(fraccion * max(1, rect.width - radio * 2))
            nudo_y = rect.y + rect.height // 2
            pygame.draw.ellipse(
                screen, (78, 51, 34),
                (nudo_x, nudo_y, radio * 2, radio),
            )
            pygame.draw.ellipse(
                screen, (155, 112, 67),
                (nudo_x + 2, nudo_y + 1, max(1, radio - 1), max(1, radio - 2)),
                1,
            )

        for raiz_x in (rect.x + 12, rect.right - 12):
            pygame.draw.line(
                screen, (79, 52, 35),
                (raiz_x, rect.bottom - 2), (raiz_x - 4, rect.bottom + 7), 3,
            )


def crear_enemigo(clase, x):
    """Instancia un enemigo y lo alinea con el suelo."""
    if clase in (HombreLoboRojo, HombreLoboNegro, Mushroom):
        enemigo = clase(x=x, y=POSICION_SUELO)
        enemigo.health = 60
        enemigo.max_health = 60
        enemigo.dano_ataque = 5

    enemigo.suelo_y = POSICION_SUELO
    enemigo.rect.bottom = POSICION_SUELO
    enemigo.velocity_y = 0
    enemigo.on_ground = True
    enemigo.hurtbox.topleft = enemigo.rect.topleft
    enemigo.jump_force = -15
    return enemigo


def generar_grupo_enemigos(posicion, indice_grupo=0):
    """Genera una tanda de dos enemigos y alterna los tipos entre tandas."""
    enemigos = []
    clases_grupo = [
        TIPOS_ENEMIGO[indice_grupo % len(TIPOS_ENEMIGO)],
        TIPOS_ENEMIGO[(indice_grupo + 1) % len(TIPOS_ENEMIGO)],
    ]
    for i, clase in enumerate(clases_grupo):
        enemigo = crear_enemigo(clase, posicion)
        enemigo.plataformas = plataformas_nivel
        enemigo.flank_side = -1 if i % 2 == 0 else 1
        enemigo.preferred_distance = 65
        enemigo.attack_range = 215
        enemigo.ataque_coordinado = True
        enemigo.rect.centerx = posicion + enemigo.flank_side * enemigo.preferred_distance
        enemigo.hurtbox.topleft = enemigo.rect.topleft
        enemigo.strafe_timer = 0
        enemigo.strafe_direction = 0
        enemigo.jump_cooldown = random.uniform(0.4, 1.4)
        enemigo.speed = random.randint(3, 5)
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

mostrar_comic_inicio(pantalla)

heroe = Jugador(200, POSICION_SUELO)
todos_los_sprites = pygame.sprite.Group(heroe)
vista_heroe = VistaJugadorMundo(heroe)
plataformas_nivel = generar_plataformas_nivel()
disenos_plataformas = [
    generar_diseno_plataforma() for _ in plataformas_nivel
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
                PUNTOS_GRUPO[proximo_grupo], proximo_grupo
            )
        )
        proximo_grupo += 1

    todos_los_grupos_generados = proximo_grupo == len(PUNTOS_GRUPO)
    enemigos_pendientes = [
        enemigo for enemigo in enemigos_nivel if not enemigo_derrotado(enemigo)
    ]
    portal_liberado = todos_los_grupos_generados and not enemigos_pendientes
    limite_max_x = HUECO_FIN if portal_liberado else HUECO_INICIO - 40

    en_zona_hueco = (
        portal_liberado
        and HUECO_INICIO <= heroe.pos_x <= HUECO_FIN
        and not transicion_realizada
    )

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_c and en_zona_hueco:
            heroe.health = heroe.max_health

            pantalla.fill((0, 0, 0))

            txt_title = fuente_boss_title.render("Abbadon", True, (12, 35, 82))
            txt_subtitle = fuente_boss_subtitle.render(
                "El Señor Oscuro", True, (18, 42, 105)
            )

            pantalla.blit(txt_title, txt_title.get_rect(center=(ANCHO // 2, ALTO // 2 - 25)))
            pantalla.blit(txt_subtitle, txt_subtitle.get_rect(center=(ANCHO // 2, ALTO // 2 + 45)))

            pygame.display.flip()
            pygame.time.wait(2000)

            transicion_realizada = True
            ejecutar_batalla_werewolf(pantalla, heroe, fondo_batalla)
            ejecutando = False
            break

        heroe.procesar_evento(evento)

    if not ejecutando:
        break

    todos_los_sprites.update(scroll_x, transicion_realizada, limite_max_x=limite_max_x)
    scroll_x = max(0, min(heroe.pos_x - ANCHO * 0.4, ANCHO_MUNDO - ANCHO))
    heroe.rect.centerx = int(heroe.pos_x - scroll_x)
    heroe.actualizar_hitboxes()
    vista_heroe.sync(scroll_x)

    # --- Enemigos y combate en mundo ---
    for enemigo in enemigos_nivel:
        if enemigo.health <= 0 and not getattr(enemigo, "muerto_definitivo", False):
            enemigo.update(vista_heroe, dt, width=ANCHO_MUNDO)

    for enemigo in enemigos_nivel:
        if enemigo_derrotado(enemigo):
            continue

        enemigo.allies = enemigos_nivel
        enemigo.suelo_y = POSICION_SUELO
        enemigo.plataformas = plataformas_nivel
        enemigo.update(vista_heroe, dt, width=ANCHO_MUNDO)

        if enemigo.health > 0:
            if (heroe.atacando and enemigo not in heroe.enemigos_golpeados
                    and vista_heroe.hitbox.width > 0
                    and vista_heroe.hitbox.colliderect(enemigo.hurtbox)):
                enemigo.take_damage(20)
                heroe.enemigos_golpeados.add(enemigo)
                heroe.has_hit = True

            hb = getattr(enemigo, 'hitbox', None)
            if hb is not None and hb.width > 0 and not getattr(enemigo, 'has_hit', False):
                if hb.colliderect(vista_heroe.hurtbox):
                    heroe.take_damage(getattr(enemigo, 'dano_ataque', 10))
                    enemigo.has_hit = True

    enemigos_cercanos = [
        enemigo for enemigo in enemigos_nivel
        if enemigo.health > 0
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

    # --- Fondo continuo: cada tramo da paso al siguiente escenario ---
    for i in range(ANCHO_MUNDO // ANCHO):
        pos_x_fondo = i * ANCHO - scroll_x
        if -ANCHO < pos_x_fondo < ANCHO:
            fondo_tramo = (
                fondo_jefe if i == ANCHO_MUNDO // ANCHO - 1
                else fondos[i % len(fondos)]
            )
            pantalla.blit(fondo_tramo, (pos_x_fondo, 0))

    dibujar_plataformas(
        pantalla, scroll_x, plataformas_nivel, disenos_plataformas
    )
    # Renderizado de héroe y enemigos
    todos_los_sprites.draw(pantalla)

    for enemigo in enemigos_nivel:
        if not getattr(enemigo, 'muerto_definitivo', False):
            pos_x_orig = enemigo.rect.x
            enemigo.rect.x -= scroll_x
            enemigo.draw(pantalla)
            enemigo.rect.x = pos_x_orig

    # --- Progreso del recorrido y acceso al jefe ---
    dibujar_barra_jugador(pantalla, heroe)

    progreso = min(100, int(heroe.pos_x * 100 / PORTAL_X))
    if portal_liberado:
        str_progreso = "CAMINO DESPEJADO: ACÉRCATE AL PORTAL"
        color_progreso = (90, 230, 130)
    elif enemigos_pendientes:
        str_progreso = f"RUMBO HACIA ABBADON: {progreso}%  |  ENEMIGOS: {len(enemigos_pendientes)}"
        color_progreso = (18, 42, 105)
    else:
        str_progreso = f"RUMBO HACIA ABBADON: {progreso}%"
        color_progreso = (18, 42, 105)

    txt_progreso_sombra = fuente_progreso.render(str_progreso, True, (0, 0, 0))
    txt_progreso = fuente_progreso.render(str_progreso, True, color_progreso)
    rect_progreso = txt_progreso.get_rect(topright=(ANCHO - 30, 20))

    pantalla.blit(txt_progreso_sombra, (rect_progreso.x + 2, rect_progreso.y + 2))
    pantalla.blit(txt_progreso, rect_progreso)

    if en_zona_hueco:
        dibujar_boton_demoniaco(pantalla)

    pygame.display.flip()

pygame.quit()
sys.exit()