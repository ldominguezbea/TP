import os
import sys
import random
import pygame

# 0. Importación de las clases de enemigos desde enemigos.py
try:
    from enemigos import OrcoRojo, OjoVolador, Karasu_tengu
except ImportError:
    OrcoRojo = None
    OjoVolador = None
    Karasu_tengu = None

pygame.init()
pygame.font.init()

# 1. Configuración de pantalla y mundo
ANCHO, ALTO = 1350, 700
POSICION_SUELO = 620

# 5 pantallas para las 5 oleadas + 1 pantalla final para el Jefe (Total 6 pantallas)
PANTALLAS_TOTALES = 6
ANCHO_MUNDO = ANCHO * PANTALLAS_TOTALES

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 1 - Batalla de Jefe")

# Tamaño del sprite ajustado a escala humana
ANCHO_HEROE, ALTO_HEROE = 300, 300

# Zona de transición al jefe (en la pantalla final)
HUECO_INICIO = (PANTALLAS_TOTALES - 1) * ANCHO + 300   # 7050 px
HUECO_FIN = (PANTALLAS_TOTALES - 1) * ANCHO + 800      # 7550 px

# Fuentes
fuente_lava_pixel = pygame.font.SysFont("Courier", 9, bold=True)
fuente_boss_title = pygame.font.SysFont("Georgia", 76, bold=True)
fuente_boss_subtitle = pygame.font.SysFont("Georgia", 32, italic=True)
fuente_jefe = pygame.font.SysFont("Georgia", 26, bold=True, italic=True)
fuente_ui = pygame.font.SysFont("Arial", 16, bold=True)


# ==============================================================================
# CARGA DE IMÁGENES Y CÓMICS
# ==============================================================================
def cargar_imagen_comic(nombre_archivo):
    """Busca y carga las imágenes de los cómics desde las rutas del proyecto."""
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
    txt = fuente_boss_subtitle.render(f"[{nombre_archivo} no encontrado]", True, (255, 255, 255))
    surf.blit(txt, txt.get_rect(center=(ANCHO // 2, ALTO // 2)))
    return surf


def mostrar_comic_inicio(screen):
    """Muestra la imagen comic_inicio.png hasta que el jugador presiona ENTER."""
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

        lbl_enter = fuente_ui.render("PRESIONA ENTER PARA COMENZAR EL NIVEL 1", True, (255, 255, 255))
        rect_txt = lbl_enter.get_rect(center=(ANCHO // 2, ALTO - 35))
        sombra_bg = pygame.Surface((rect_txt.width + 20, rect_txt.height + 10))
        sombra_bg.fill((0, 0, 0))
        sombra_bg.set_alpha(180)
        
        screen.blit(sombra_bg, (rect_txt.x - 10, rect_txt.y - 5))
        screen.blit(lbl_enter, rect_txt)

        pygame.display.flip()
        reloj.tick(60)


def mostrar_comic_final(screen):
    """Muestra la imagen comic_final.png al concluir el nivel."""
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

        lbl_fin = fuente_ui.render("FIN DEL NIVEL 1 - Presiona cualquier tecla para continuar", True, (255, 255, 255))
        rect_txt = lbl_fin.get_rect(center=(ANCHO // 2, ALTO - 35))
        sombra_bg = pygame.Surface((rect_txt.width + 20, rect_txt.height + 10))
        sombra_bg.fill((0, 0, 0))
        sombra_bg.set_alpha(180)

        screen.blit(sombra_bg, (rect_txt.x - 10, rect_txt.y - 5))
        screen.blit(lbl_fin, rect_txt)

        pygame.display.flip()
        reloj.tick(60)


def buscar_y_cargar_barra(nombre_archivo):
    """Busca la textura de la barra subiendo niveles en el directorio si es necesario."""
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


# 2. Carga de fondos
fondos_base = []
for i in range(1, 4):
    ruta_imagen = os.path.join("imagenes", "Nivel1", f"Nivel1_imagen{i}.png")
    if not os.path.exists(ruta_imagen):
        ruta_imagen = os.path.join("assets", "imagenes", "Nivel1", f"Nivel1_imagen{i}.png")

    if os.path.exists(ruta_imagen):
        img = pygame.image.load(ruta_imagen).convert()
        fondos_base.append(pygame.transform.scale(img, (ANCHO, ALTO)))
    else:
        surf = pygame.Surface((ANCHO, ALTO))
        surf.fill((20, 15, 25))
        fondos_base.append(surf)


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

        # Física y movimiento
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.velocidad_movimiento = 7
        self.fuerza_salto = -16
        self.gravedad = 0.8

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
                ancho_hb, alto_hb = 180, 120
            elif self.estado == 'air_atk':
                ancho_hb, alto_hb = 150, 100
            else:
                ancho_hb, alto_hb = 140, 80

            y_hb = self.rect.bottom - alto_hb - 10

            if self.mirando_derecha:
                self.hitbox = pygame.Rect(self.rect.centerx + 5, y_hb, ancho_hb, alto_hb)
            else:
                self.hitbox = pygame.Rect(self.rect.centerx - 5 - ancho_hb, y_hb, ancho_hb, alto_hb)
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
        self.velocidad_y += self.gravedad
        self.rect.y += self.velocidad_y

        if self.rect.bottom >= POSICION_SUELO:
            self.rect.bottom = POSICION_SUELO
            self.velocidad_y = 0
            self.en_suelo = True

    def take_damage(self, damage):
        if self.rodando or (self.atacando and self.estado == 'sp_atk'):
            return
        self.health = max(0, self.health - damage)

    def update(self, scroll_x, transicion_realizada, limite_izquierdo_min=0, limite_derecho_max=None):
        self.manejar_movimiento_continuo()

        if self.rodando:
            self.velocidad_x = (self.velocidad_movimiento + 3) * (1 if self.mirando_derecha else -1)

        self.pos_x += self.velocidad_x

        limite_izquierdo = max(scroll_x + 80, limite_izquierdo_min + 80)

        if transicion_realizada and scroll_x == 0:
            limite_izquierdo = 80
            limite_derecho = ANCHO - 80
        elif transicion_realizada:
            limite_derecho = ANCHO_MUNDO - 80
        else:
            limite_derecho = HUECO_FIN

        if limite_derecho_max is not None:
            limite_derecho = min(limite_derecho, limite_derecho_max)

        self.pos_x = max(limite_izquierdo, min(self.pos_x, limite_derecho))
        self.rect.centerx = int(self.pos_x - scroll_x)

        self.aplicar_gravedad()
        self.actualizar_estado()
        self.actualizar_hitboxes()
        self.animar()


# 4. Botón Demoníaco Interactivo
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


# 5. Escena de Batalla contra el Jefe
def ejecutar_batalla_carnicero(screen, player, fondo_img):
    from Jefes_enemigos import CarniceroBoss

    clock = pygame.time.Clock()
    FPS = 60

    jefe = CarniceroBoss(x=920, y=POSICION_SUELO - 300)

    jefe.max_health = 300
    jefe.health = 300

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

        # Proyectiles del jefe
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

        # UI DEL JEFE
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

        # UI DEL JUGADOR
        pct_player = max(0.0, min(1.0, player.health / player.max_health if player.max_health > 0 else 0))

        if IMG_BARRA_JUGADOR is not None:
            ancho_b_p = 280
            escala_p = ancho_b_p / IMG_BARRA_JUGADOR.get_width()
            alto_b_p = int(IMG_BARRA_JUGADOR.get_height() * escala_p)
            bar_p_scaled = pygame.transform.scale(IMG_BARRA_JUGADOR, (ancho_b_p, alto_b_p))

            x_p_ui = 25
            y_p_ui = 20

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


# ==============================================================================
# INICIALIZACIÓN Y FLUJO PRINCIPAL DEL JUEGO
# ==============================================================================

# 1. MOSTRAR CÓMIC DE INICIO (Requiere presionar ENTER)
mostrar_comic_inicio(pantalla)

# 2. COMIENZO DEL NIVEL 1
heroe = Jugador(200, POSICION_SUELO)
todos_los_sprites = pygame.sprite.Group(heroe)

# Lista de clases de enemigos disponibles
CLASES_ENEMIGOS = [c for c in [OrcoRojo, OjoVolador, Karasu_tengu] if c is not None]

# Configuración de las 5 Oleadas (1 por pantalla completa de 1350px)
CANTIDADES_OLEADAS = [2, 4, 5, 6, 6]

# Posiciones donde arranca cada pantalla
POSICIONES_ACTIVACION = [i * ANCHO + 500 for i in range(5)]

indice_oleada_actual = 0
oleada_activa = False
enemigos_lista = []

scroll_x = 0
transicion_realizada = False

ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    dt = reloj.tick(60) / 1000.0
    en_zona_hueco = HUECO_INICIO <= heroe.pos_x <= HUECO_FIN and not transicion_realizada

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_c and en_zona_hueco:
            pantalla.fill((0, 0, 0))

            txt_title = fuente_boss_title.render("Athros", True, (180, 20, 20))
            txt_subtitle = fuente_boss_subtitle.render("the bloodred", True, (140, 15, 15))

            pantalla.blit(txt_title, txt_title.get_rect(center=(ANCHO // 2, ALTO // 2 - 25)))
            pantalla.blit(txt_subtitle, txt_subtitle.get_rect(center=(ANCHO // 2, ALTO // 2 + 45)))

            pygame.display.flip()
            pygame.time.wait(2000)

            enemigos_lista.clear()
            transicion_realizada = True
            ejecutar_batalla_carnicero(pantalla, heroe, fondos_base[2])
            ejecutando = False
            break

        heroe.procesar_evento(evento)

    if not ejecutando:
        break

    # --------------------------------------------------------------------------
    # GESTIÓN Y BLOQUEO POR PANTALLA
    # --------------------------------------------------------------------------
    if not transicion_realizada and indice_oleada_actual < len(POSICIONES_ACTIVACION) and CLASES_ENEMIGOS:
        pos_disparo = POSICIONES_ACTIVACION[indice_oleada_actual]
        
        if not oleada_activa and heroe.pos_x >= pos_disparo:
            oleada_activa = True
            cant_enemigos = CANTIDADES_OLEADAS[indice_oleada_actual]
            
            inicio_pantalla_x = indice_oleada_actual * ANCHO
            fin_pantalla_x = (indice_oleada_actual + 1) * ANCHO
            
            for _ in range(cant_enemigos):
                ClaseE = random.choice(CLASES_ENEMIGOS)
                
                spawn_x = random.randint(inicio_pantalla_x + 350, fin_pantalla_x - 150)
                
                nombre_clase = ClaseE.__name__ if hasattr(ClaseE, '__name__') else ''
                
                # Ajustar la altura del OjoVolador para que sea golpeable por el jugador
                if 'Ojo' in nombre_clase or 'Volador' in nombre_clase:
                    spawn_y = POSICION_SUELO - random.randint(30, 70)
                elif 'Karasu' in nombre_clase:
                    spawn_y = POSICION_SUELO - random.randint(60, 100)
                else:
                    spawn_y = POSICION_SUELO
                
                try:
                    e = ClaseE(spawn_x, spawn_y)
                except TypeError:
                    try:
                        e = ClaseE(spawn_x, spawn_y, POSICION_SUELO)
                    except TypeError:
                        e = ClaseE()
                        if hasattr(e, 'rect'):
                            e.rect.x = spawn_x
                            e.rect.bottom = spawn_y
                
                # Garantizar inicialización correcta de salud
                if not hasattr(e, 'health') and not hasattr(e, 'salud') and not hasattr(e, 'hp'):
                    setattr(e, 'health', 40)
                
                enemigos_lista.append(e)

    if oleada_activa and len(enemigos_lista) == 0:
        oleada_activa = False
        indice_oleada_actual += 1

    min_x_permitido = indice_oleada_actual * ANCHO if oleada_activa else 0
    max_x_permitido = ((indice_oleada_actual + 1) * ANCHO) if oleada_activa else (ANCHO_MUNDO - 100)

    todos_los_sprites.update(
        scroll_x, 
        transicion_realizada, 
        limite_izquierdo_min=min_x_permitido, 
        limite_derecho_max=max_x_permitido
    )

    target_scroll = int(heroe.pos_x - ANCHO // 2)
    max_scroll_pantalla = (indice_oleada_actual * ANCHO) if oleada_activa else (ANCHO_MUNDO - ANCHO)
    min_scroll_pantalla = (indice_oleada_actual * ANCHO) if oleada_activa else 0

    scroll_x = max(min_scroll_pantalla, min(target_scroll, max_scroll_pantalla))

    # --------------------------------------------------------------------------
    # SEPARACIÓN FÍSICA PARA EVITAR SOBREPOSICIÓN
    # --------------------------------------------------------------------------
    for i in range(len(enemigos_lista)):
        for j in range(i + 1, len(enemigos_lista)):
            e1 = enemigos_lista[i]
            e2 = enemigos_lista[j]
            
            r1 = getattr(e1, 'hurtbox', getattr(e1, 'rect', None))
            r2 = getattr(e2, 'hurtbox', getattr(e2, 'rect', None))
            
            if r1 and r2 and r1.colliderect(r2):
                solapamiento = r1.clip(r2)
                if solapamiento.width > 0:
                    empuje = solapamiento.width // 2 + 1
                    if r1.centerx < r2.centerx:
                        if hasattr(e1, 'rect'): e1.rect.x -= empuje
                        if hasattr(e2, 'rect'): e2.rect.x += empuje
                    else:
                        if hasattr(e1, 'rect'): e1.rect.x += empuje
                        if hasattr(e2, 'rect'): e2.rect.x -= empuje

    # --------------------------------------------------------------------------
    # PROCESAMIENTO Y COMBATE CON ENEMIGOS
    # --------------------------------------------------------------------------
    for enemigo in list(enemigos_lista):
        # Actualizar lógica interna del enemigo
        if hasattr(enemigo, 'update'):
            try:
                enemigo.update(heroe, dt)
            except TypeError:
                try:
                    enemigo.update(heroe, scroll_x)
                except TypeError:
                    try:
                        enemigo.update(heroe)
                    except TypeError:
                        enemigo.update()

        salud_e = getattr(enemigo, 'health', getattr(enemigo, 'salud', getattr(enemigo, 'hp', getattr(enemigo, 'vida', 100))))
        esta_muriendo = getattr(enemigo, 'muriendo', False) or getattr(enemigo, 'esta_muerto', False) or (salud_e <= 0)

        # SI LA VIDA LLEGA A 0: REPRODUCIR LA ANIMACIÓN DE MUERTE
        if esta_muriendo:
            if not getattr(enemigo, 'muriendo', False):
                setattr(enemigo, 'muriendo', True)
                setattr(enemigo, 'timer_muerte', 0.0)
                
                if hasattr(enemigo, 'morir'):
                    enemigo.morir()
                elif hasattr(enemigo, 'estado'):
                    enemigo.estado = 'die'
                    enemigo.frame_index = 0

            timer_m = getattr(enemigo, 'timer_muerte', 0.0) + dt
            setattr(enemigo, 'timer_muerte', timer_m)

            anim_concluida = False
            if hasattr(enemigo, 'muerto') and enemigo.muerto:
                anim_concluida = True
            elif hasattr(enemigo, 'animacion_terminada') and enemigo.animacion_terminada:
                anim_concluida = True
            elif timer_m >= 1.0:  # Permite 1 segundo para ver la animación de muerte
                anim_concluida = True

            if anim_concluida:
                if enemigo in enemigos_lista:
                    enemigos_lista.remove(enemigo)
                continue

        # DAÑO DEL JUGADOR AL ENEMIGO (OJO VOLADOR Y OTROS)
        if heroe.atacando and heroe.hitbox.width > 0 and not esta_muriendo:
            e_hurt_raw = getattr(enemigo, 'hurtbox', getattr(enemigo, 'rect', None))
            if e_hurt_raw:
                # Conversión de coordenadas de mundo a pantalla para la colisión
                e_hurt_screen = e_hurt_raw.copy()
                e_hurt_screen.x -= scroll_x
                
                if heroe.hitbox.colliderect(e_hurt_screen) or heroe.hitbox.colliderect(e_hurt_raw):
                    if not getattr(enemigo, 'recibio_dano_golpe', False):
                        dano = 25
                        
                        if hasattr(enemigo, 'recibir_dano'):
                            enemigo.recibir_dano(dano)
                        elif hasattr(enemigo, 'take_damage'):
                            enemigo.take_damage(dano)

                        if hasattr(enemigo, 'health'): enemigo.health -= dano
                        if hasattr(enemigo, 'salud'): enemigo.salud -= dano
                        if hasattr(enemigo, 'hp'): enemigo.hp -= dano
                        if hasattr(enemigo, 'vida'): enemigo.vida -= dano

                        setattr(enemigo, 'recibio_dano_golpe', True)
        else:
            setattr(enemigo, 'recibio_dano_golpe', False)

        # ATAQUE DEL ENEMIGO AL JUGADOR
        if not esta_muriendo:
            e_hitbox_raw = getattr(enemigo, 'hitbox', getattr(enemigo, 'rect', None))
            if e_hitbox_raw:
                e_hitbox_screen = e_hitbox_raw.copy()
                e_hitbox_screen.x -= scroll_x
                
                if e_hitbox_screen.colliderect(heroe.hurtbox) or e_hitbox_raw.colliderect(heroe.hurtbox):
                    if not getattr(enemigo, 'ha_dado_golpe', False):
                        heroe.take_damage(8)
                        setattr(enemigo, 'ha_dado_golpe', True)
                else:
                    setattr(enemigo, 'ha_dado_golpe', False)

    # --------------------------------------------------------------------------
    # RENDERIZADO DEL ESCENARIO Y SPRITES
    # --------------------------------------------------------------------------
    for i in range(PANTALLAS_TOTALES):
        fondo_img = fondos_base[i % len(fondos_base)]
        pos_x_fondo = i * ANCHO - scroll_x
        if -ANCHO < pos_x_fondo < ANCHO:
            pantalla.blit(fondo_img, (pos_x_fondo, 0))

    todos_los_sprites.draw(pantalla)

    for e in enemigos_lista:
        if hasattr(e, 'draw'):
            try:
                e.draw(pantalla, scroll_x)
            except TypeError:
                e.draw(pantalla)
        elif hasattr(e, 'image') and hasattr(e, 'rect'):
            rect_pantalla = e.rect.copy()
            rect_pantalla.x -= scroll_x
            pantalla.blit(e.image, rect_pantalla)

    if en_zona_hueco:
        dibujar_boton_demoniaco(pantalla)

    # UI del Jugador
    pct_player = max(0.0, min(1.0, heroe.health / heroe.max_health if heroe.max_health > 0 else 0))

    if IMG_BARRA_JUGADOR is not None:
        ancho_b_p = 280
        escala_p = ancho_b_p / IMG_BARRA_JUGADOR.get_width()
        alto_b_p = int(IMG_BARRA_JUGADOR.get_height() * escala_p)
        bar_p_scaled = pygame.transform.scale(IMG_BARRA_JUGADOR, (ancho_b_p, alto_b_p))

        x_p_ui = 25
        y_p_ui = 20

        x_fill_p = x_p_ui + int(ancho_b_p * 0.08)
        y_fill_p = y_p_ui + int(alto_b_p * 0.44)
        w_max_fill_p = int(ancho_b_p * 0.84)
        h_fill_p = int(alto_b_p * 0.40)

        w_restante_p = int(w_max_fill_p * pct_player)

        pygame.draw.rect(pantalla, (20, 5, 5), (x_fill_p, y_fill_p, w_max_fill_p, h_fill_p))

        if w_restante_p > 0:
            pygame.draw.rect(pantalla, (190, 30, 30), (x_fill_p, y_fill_p, w_restante_p, h_fill_p))
            pygame.draw.rect(pantalla, (240, 90, 90), (x_fill_p, y_fill_p, w_restante_p, max(1, h_fill_p // 3)))

        pantalla.blit(bar_p_scaled, (x_p_ui, y_p_ui))
        lbl_p = fuente_ui.render(f"JUGADOR: {int(heroe.health)} / {heroe.max_health}", True, (255, 255, 255))
        pantalla.blit(lbl_p, (x_p_ui + 5, y_p_ui + alto_b_p + 4))

    if oleada_activa:
        txt_oleada = fuente_ui.render(f"OLEADA {indice_oleada_actual + 1} / {len(CANTIDADES_OLEADAS)} - ¡Derrota a los enemigos de la zona!", True, (255, 200, 50))
        rect_o = txt_oleada.get_rect(center=(ANCHO // 2, 30))
        bg_o = pygame.Surface((rect_o.width + 20, rect_o.height + 10))
        bg_o.fill((0, 0, 0))
        bg_o.set_alpha(180)
        pantalla.blit(bg_o, (rect_o.x - 10, rect_o.y - 5))
        pantalla.blit(txt_oleada, rect_o)

    pygame.display.flip()

pygame.quit()
sys.exit()