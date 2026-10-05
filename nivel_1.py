import pygame
import enemigos
import os
import sys
import random
import math

pygame.init()
pygame.font.init()

# 1. Configuración de la pantalla
ANCHO, ALTO = 1350, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 1")

# --- AJUSTES DEL PERSONAJE Y ESCENARIO ---
ANCHO_HEROE, ALTO_HEROE = 600,240
POSICION_SUELO = 620 
CANTIDAD_FONDOS = 3
ANCHO_MUNDO = ANCHO * CANTIDAD_FONDOS  # Ancho total del nivel (3 pantallas)

# Zona del hueco en la Imagen 2
HUECO_INICIO = ANCHO + 600   # 1950 px
HUECO_FIN = ANCHO + 800      # 2150 px
HUECO_CENTRO_X = (HUECO_INICIO + HUECO_FIN) // 2

# Fuentes
fuente_pixel = pygame.font.SysFont("Courier", 20, bold=True)
fuente_boss_title = pygame.font.SysFont("Georgia", 76, bold=True)
fuente_boss_subtitle = pygame.font.SysFont("Georgia", 32, italic=True)
# ------------------------------------------

# 2. Carga de los 3 fondos del Nivel 1
fondos = []
for i in range(1, CANTIDAD_FONDOS + 1):
    ruta_imagen = os.path.join("imagenes", "Nivel1", f"Nivel1_imagen{i}.png")
    img = pygame.image.load(ruta_imagen).convert()
    fondos.append(pygame.transform.scale(img, (ANCHO, ALTO)))


# 3. Clase para el Héroe (P_viento)
class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animaciones = {
            'idle': [], 'run': [], 'roll': [], 'j_up': [],
            'defend': [], '1_atk': [], '2_atk': [], '3_atk': [],
            'air_atk': [], 'sp_atk': []
        }
        self.cargar_animaciones()

        # Estado inicial y animación
        self.estado = 'idle'
        self.frame_index = 0
        self.velocidad_animacion = 0.22

        self.image = self.animaciones[self.estado][self.frame_index]
        self.rect = self.image.get_rect(midbottom=(x, y))

        # Posición real global dentro del mundo
        self.pos_x = float(x)

        # Física y movimiento
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.velocidad_movimiento = 7
        self.fuerza_salto = -16
        self.gravedad = 0.8

        # Banderas de estado
        self.mirando_derecha = True
        self.en_suelo = True
        self.rodando = False
        self.defendiendo = False
        self.atacando = False
        self.combo_siguiente = False

    def cargar_animaciones(self):
        ESCALA = (ANCHO_HEROE, ALTO_HEROE)
        base_path = os.path.join("assets", "Heroes", "P_viento")

        for i in range(1, 9):  # idle (1-8)
            img = pygame.image.load(os.path.join(base_path, "idle", f"idle_{i}.png")).convert_alpha()
            self.animaciones['idle'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 9):  # run (1-8)
            img = pygame.image.load(os.path.join(base_path, "run", f"run_{i}.png")).convert_alpha()
            self.animaciones['run'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 7):  # roll (1-6)
            img = pygame.image.load(os.path.join(base_path, "roll", f"roll_{i}.png")).convert_alpha()
            self.animaciones['roll'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 4):  # j_up (1-3)
            img = pygame.image.load(os.path.join(base_path, "j_up", f"j_up_{i}.png")).convert_alpha()
            self.animaciones['j_up'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 9):  # defend (1-8)
            img = pygame.image.load(os.path.join(base_path, "defend", f"defend_{i}.png")).convert_alpha()
            self.animaciones['defend'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 9):  # 1_atk (1-8)
            img = pygame.image.load(os.path.join(base_path, "1_atk", f"1_atk_{i}.png")).convert_alpha()
            self.animaciones['1_atk'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 19):  # 2_atk (1-18)
            img = pygame.image.load(os.path.join(base_path, "2_atk", f"2_atk_{i}.png")).convert_alpha()
            self.animaciones['2_atk'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 8):  # air_atk (1-7)
            img = pygame.image.load(os.path.join(base_path, "air_atk", f"air_atk_{i}.png")).convert_alpha()
            self.animaciones['air_atk'].append(pygame.transform.scale(img, ESCALA))

        for i in range(1, 31):  # sp_atk (1-30)
            img = pygame.image.load(os.path.join(base_path, "sp_atk", f"sp_atk_{i}.png")).convert_alpha()
            self.animaciones['sp_atk'].append(pygame.transform.scale(img, ESCALA))

        for i in range(12, 27):  # 3_atk (12-26)
            img = pygame.image.load(os.path.join(base_path, "3_atk", f"3_atk_{i}.png")).convert_alpha()
            self.animaciones['3_atk'].append(pygame.transform.scale(img, ESCALA))

    def procesar_evento(self, evento):
        """Maneja las pulsaciones únicas de teclas."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_w and self.en_suelo and not (self.atacando or self.rodando or self.defendiendo):
                self.velocidad_y = self.fuerza_salto
                self.en_suelo = False

            elif evento.key == pygame.K_q and self.en_suelo and not (self.rodando or self.atacando or self.defendiendo):
                self.rodando = True
                self.frame_index = 0

            elif evento.key == pygame.K_r and self.en_suelo and not (self.rodando or self.atacando or self.defendiendo):
                self.defendiendo = True
                self.frame_index = 0

            elif evento.key == pygame.K_e and self.en_suelo and not (self.rodando or self.atacando or self.defendiendo):
                self.atacando = True
                self.estado = 'sp_atk'
                self.frame_index = 0

            elif evento.key == pygame.K_f:
                if not self.en_suelo and not self.atacando:
                    self.atacando = True
                    self.estado = 'air_atk'
                    self.frame_index = 0

                elif self.en_suelo and not (self.rodando or self.defendiendo):
                    if not self.atacando:
                        self.atacando = True
                        self.estado = '1_atk'
                        self.frame_index = 0
                        self.combo_siguiente = False
                    elif self.estado in ['1_atk', '2_atk']:
                        self.combo_siguiente = True

    def manejar_movimiento_continuo(self):
        teclas = pygame.key.get_pressed()

        if self.rodando or self.defendiendo or (self.atacando and self.en_suelo):
            self.velocidad_x = 0
            return

        self.velocidad_x = 0

        if teclas[pygame.K_a]:
            self.velocidad_x = -self.velocidad_movimiento
            self.mirando_derecha = False
        if teclas[pygame.K_d]:
            self.velocidad_x = self.velocidad_movimiento
            self.mirando_derecha = True

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
                    self.combo_siguiente = False
                else:
                    self.atacando = False
            elif self.estado == '2_atk':
                if self.combo_siguiente:
                    self.estado = '3_atk'
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

    def update(self, scroll_x):
        self.manejar_movimiento_continuo()

        if self.rodando:
            self.velocidad_x = (self.velocidad_movimiento + 3) * (1 if self.mirando_derecha else -1)

        self.pos_x += self.velocidad_x

        # Bloqueo de marcha atrás
        limite_izquierdo = scroll_x + 80
        self.pos_x = max(limite_izquierdo, min(self.pos_x, ANCHO_MUNDO - 80))

        self.rect.centerx = int(self.pos_x - scroll_x)

        self.aplicar_gravedad()
        self.actualizar_estado()
        self.animar()


def dibujar_boton_pixel_art(pantalla, centro_x, centro_y):
    """Renderiza un cuadro pixel art animado (flotante) con el texto PRESS C TO INTERACT."""
    # Movimiento flotante sinusoidal
    offset_y = math.sin(pygame.time.get_ticks() * 0.006) * 8
    pos_y = int(centro_y + offset_y)

    texto = fuente_pixel.render("[ PRESS C TO INTERACT ]", False, (255, 230, 150))
    rect_txt = texto.get_rect(center=(centro_x, pos_y))

    # Dimensiones del contenedor Pixel Art
    ancho_box = rect_txt.width + 24
    alto_box = rect_txt.height + 16
    rect_box = pygame.Rect(0, 0, ancho_box, alto_box)
    rect_box.center = (centro_x, pos_y)

    # Renderizado con bordes pixelados
    pygame.draw.rect(pantalla, (20, 20, 25), rect_box)  # Fondo oscuro
    pygame.draw.rect(pantalla, (220, 180, 60), rect_box, 4)  # Borde dorado grueso
    pygame.draw.rect(pantalla, (100, 75, 20), rect_box.inflate(-8, -8), 2)  # Borde interno

    pantalla.blit(texto, rect_txt)


# Instancia del héroe
heroe = Jugador(200, POSICION_SUELO)
todos_los_sprites = pygame.sprite.Group(heroe)

scroll_x = 0

# 4. Bucle principal
ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    en_zona_hueco = HUECO_INICIO <= heroe.pos_x <= HUECO_FIN

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_c and en_zona_hueco:
            # --- PANTALLA DE CARGA TIPO DARK SOULS ---
            pantalla.fill((0, 0, 0))

            # Renderizado de texto rojo estilo Dark Souls
            txt_title = fuente_boss_title.render("Athros", True, (180, 20, 20))
            txt_subtitle = fuente_boss_subtitle.render("the bloodred", True, (140, 15, 15))

            rect_title = txt_title.get_rect(center=(ANCHO // 2, ALTO // 2 - 25))
            rect_subtitle = txt_subtitle.get_rect(center=(ANCHO // 2, ALTO // 2 + 45))

            pantalla.blit(txt_title, rect_title)
            pantalla.blit(txt_subtitle, rect_subtitle)

            pygame.display.flip()
            pygame.time.wait(2000)

            # Teletransporte al inicio de la Imagen 3
            heroe.pos_x = ANCHO * 2 + 150
            scroll_x = ANCHO * 2

            pygame.event.clear()
            break

        heroe.procesar_evento(evento)

    # Restricción de cámara (solo avanza hacia adelante)
    target_scroll = int(heroe.pos_x - ANCHO // 2)
    scroll_x = max(scroll_x, min(target_scroll, ANCHO_MUNDO - ANCHO))

    todos_los_sprites.update(scroll_x)

    # Dibujar fondos
    for i, fondo_img in enumerate(fondos):
        pos_x_fondo = i * ANCHO - scroll_x
        if -ANCHO < pos_x_fondo < ANCHO:
            pantalla.blit(fondo_img, (pos_x_fondo, 0))

    # Dibujar el botón flotante en la posición del hueco en el mapa
    screen_hueco_x = HUECO_CENTRO_X - scroll_x
    if -150 < screen_hueco_x < ANCHO + 150:
        dibujar_boton_pixel_art(pantalla, screen_hueco_x, POSICION_SUELO - 110)

    todos_los_sprites.draw(pantalla)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()