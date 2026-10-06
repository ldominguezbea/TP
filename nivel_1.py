import pygame
import os
import sys
import random

try:
    import enemigos
except ImportError:
    enemigos = None

pygame.init()
pygame.font.init()

# 1. Configuración de pantalla y mundo
ANCHO, ALTO = 1350, 700
POSICION_SUELO = 620
CANTIDAD_FONDOS = 3
ANCHO_MUNDO = ANCHO * CANTIDAD_FONDOS

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 1 - Batalla de Jefe")

# Tamaño del sprite ajustado a escala humana
ANCHO_HEROE, ALTO_HEROE = 300, 300

HUECO_INICIO = ANCHO + 600   # 1950 px
HUECO_FIN = ANCHO + 800      # 2150 px

# Fuentes
fuente_lava_pixel = pygame.font.SysFont("Courier", 9, bold=True)
fuente_boss_title = pygame.font.SysFont("Georgia", 76, bold=True)
fuente_boss_subtitle = pygame.font.SysFont("Georgia", 32, italic=True)
fuente_jefe = pygame.font.SysFont("Impact", 24)
fuente_ui = pygame.font.SysFont("Arial", 16, bold=True)

# 2. Carga de fondos
fondos = []
for i in range(1, CANTIDAD_FONDOS + 1):
    ruta_imagen = os.path.join("imagenes", "Nivel1", f"Nivel1_imagen{i}.png")
    if not os.path.exists(ruta_imagen):
        ruta_imagen = os.path.join("assets", "imagenes", "Nivel1", f"Nivel1_imagen{i}.png")

    if os.path.exists(ruta_imagen):
        img = pygame.image.load(ruta_imagen).convert()
        fondos.append(pygame.transform.scale(img, (ANCHO, ALTO)))
    else:
        surf = pygame.Surface((ANCHO, ALTO))
        surf.fill((20, 15, 25))
        fondos.append(surf)


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
                if self.atacando:
                    self.atacando = False
                self.velocidad_y = self.fuerza_salto
                self.en_suelo = False

            elif evento.key == pygame.K_q and self.en_suelo and not (self.rodando or self.defendiendo):
                if self.atacando:
                    self.atacando = False
                self.rodando = True
                self.frame_index = 0

            elif evento.key == pygame.K_r and self.en_suelo and not (self.rodando or self.defendiendo):
                if self.atacando:
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
            if self.atacando:
                self.atacando = False

        if teclas[pygame.K_d]:
            self.velocidad_x = self.velocidad_movimiento
            self.mirando_derecha = True
            if self.atacando:
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
        # 1. Hurtbox (Cuerpo del jugador para recibir daño):
        # Ajustada exactamente al cuerpo visible (60px ancho, 150px alto)
        ancho_cuerpo, alto_cuerpo = 60, 150
        self.hurtbox = pygame.Rect(0, 0, ancho_cuerpo, alto_cuerpo)
        self.hurtbox.midbottom = self.rect.midbottom

        # 2. Hitbox (Ataque del jugador para dañar al enemigo):
        if self.atacando:
            ancho_hb, alto_hb = 110, 130
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
        self.velocidad_y += self.gravedad
        self.rect.y += self.velocidad_y

        if self.rect.bottom >= POSICION_SUELO:
            self.rect.bottom = POSICION_SUELO
            self.velocidad_y = 0
            self.en_suelo = True

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def update(self, scroll_x, transicion_realizada):
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
            limite_derecho = HUECO_FIN

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
def ejecutar_batalla_carnicero(screen, player, fondo_img, img_cierre=None):
    from Jefes_enemigos import CarniceroBoss

    clock = pygame.time.Clock()
    FPS = 60

    jefe = CarniceroBoss(x=920, y=POSICION_SUELO - 300)

    player.pos_x = 180.0
    player.rect.centerx = 180
    player.rect.bottom = POSICION_SUELO

    en_batalla = True
    timer_muerte_jefe = 0.0
    mostrar_cierre = False

    while en_batalla:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            player.procesar_evento(event)

        player.update(0, transicion_realizada=True)
        jefe.update(player, dt, width=ANCHO, suelo_y=POSICION_SUELO)

        # Usar la hurtbox precisa del jugador para recibir daño
        target_player_rect = player.hurtbox

        # Daños y Colisiones
        for proj in jefe.proyectiles[:]:
            if proj.rect.colliderect(target_player_rect):
                player.take_damage(6)
                if proj in jefe.proyectiles:
                    jefe.proyectiles.remove(proj)

        if getattr(jefe, 'attacking', False) and not getattr(jefe, 'has_hit', False):
            if jefe.hitbox.width > 0 and jefe.hitbox.colliderect(target_player_rect):
                player.take_damage(18)
                jefe.has_hit = True

        if not getattr(jefe, 'muerto_definitivo', False) and player.atacando and not player.has_hit:
            if player.hitbox.colliderect(jefe.hurtbox):
                jefe.take_damage(8)
                player.has_hit = True

        if getattr(jefe, 'muerto_definitivo', False):
            timer_muerte_jefe += dt
            if timer_muerte_jefe >= 5.0:
                mostrar_cierre = True

        # Renderizado
        screen.blit(fondo_img, (0, 0))
        screen.blit(player.image, player.rect)
        jefe.draw(screen)

        # UI del Jefe
        if not getattr(jefe, 'muerto_definitivo', False):
            ancho_b_jefe, alto_b_jefe = 500, 20
            x_jefe, y_jefe = (ANCHO - ancho_b_jefe) // 2, 45

            pygame.draw.rect(screen, (20, 5, 5), (x_jefe - 2, y_jefe - 2, ancho_b_jefe + 4, alto_b_jefe + 4))
            max_v_jefe = getattr(jefe, 'max_health', 100)
            pct_jefe = max(0.0, min(1.0, jefe.health / max_v_jefe if max_v_jefe > 0 else 0))
            w_restante = int(ancho_b_jefe * pct_jefe)

            if w_restante > 0:
                fase = getattr(jefe, 'fase_actual', 1)
                color_fase = (180, 30, 10) if fase == 1 else ((255, 100, 0) if fase == 2 else (255, 200, 0))
                pygame.draw.rect(screen, color_fase, (x_jefe, y_jefe, w_restante, alto_b_jefe))
                pygame.draw.rect(screen, (255, 220, 100), (x_jefe, y_jefe, w_restante, alto_b_jefe // 2))

            pygame.draw.rect(screen, (255, 215, 0), (x_jefe - 2, y_jefe - 2, ancho_b_jefe + 4, alto_b_jefe + 4), 2)
            lbl_jefe = fuente_jefe.render("Athros : The bloodred", True, (255, 200, 50))
            screen.blit(lbl_jefe, (ANCHO // 2 - lbl_jefe.get_width() // 2, 15))

        # UI del Jugador
        ancho_b_player, alto_b_player = 180, 18
        x_player, y_player = 30, 30

        pygame.draw.rect(screen, (10, 10, 10), (x_player - 2, y_player - 2, ancho_b_player + 4, alto_b_player + 4))
        pct_player = max(0.0, min(1.0, player.health / player.max_health))

        if pct_player > 0:
            pygame.draw.rect(screen, (40, 180, 70), (x_player, y_player, int(ancho_b_player * pct_player), alto_b_player))

        pygame.draw.rect(screen, (200, 200, 200), (x_player - 2, y_player - 2, ancho_b_player + 4, alto_b_player + 4), 2)
        lbl_player = fuente_ui.render("JUGADOR", True, (255, 255, 255))
        screen.blit(lbl_player, (x_player, 8))

        # Pantalla final
        if mostrar_cierre:
            if img_cierre:
                screen.blit(img_cierre, (0, 0))
            else:
                overlay = pygame.Surface((ANCHO, ALTO))
                overlay.set_alpha(220)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))

                fuente_cierre = pygame.font.SysFont("Impact", 48)
                lbl_cierre = fuente_cierre.render("NIVEL 1 COMPLETADO", True, (255, 215, 0))
                screen.blit(lbl_cierre, (ANCHO // 2 - lbl_cierre.get_width() // 2, ALTO // 2 - 24))

        pygame.display.flip()


# 6. Inicialización del juego principal
heroe = Jugador(200, POSICION_SUELO)
todos_los_sprites = pygame.sprite.Group(heroe)

scroll_x = 0
transicion_realizada = False

ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
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

            transicion_realizada = True
            ejecutar_batalla_carnicero(pantalla, heroe, fondos[2])
            ejecutando = False
            break

        heroe.procesar_evento(evento)

    if not ejecutando:
        break

    target_scroll = int(heroe.pos_x - ANCHO // 2)
    max_scroll = ANCHO_MUNDO - ANCHO if transicion_realizada else ANCHO
    scroll_x = max(scroll_x, min(target_scroll, max_scroll))

    todos_los_sprites.update(scroll_x, transicion_realizada)

    for i, fondo_img in enumerate(fondos):
        if i == 2 and not transicion_realizada:
            continue
        pos_x_fondo = i * ANCHO - scroll_x
        if -ANCHO < pos_x_fondo < ANCHO:
            pantalla.blit(fondo_img, (pos_x_fondo, 0))

    todos_los_sprites.draw(pantalla)

    if en_zona_hueco:
        dibujar_boton_demoniaco(pantalla)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()
