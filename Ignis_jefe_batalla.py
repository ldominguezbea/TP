import os
import random
import math
import pygame
from Jefes_enemigos import ImpalerBoss
from personajes import crear_jugador
from barra_vida_jugador import dibujar_barra_vida_jugador
from cinematica_final import (
    DURACION_MINIMA_FIN_MS,
    PantallaFinalEpica,
    detener_musica_epica,
    iniciar_musica_epica,
)
from menu_pausa import (
    NivelIntegradoFinalizado,
    menu_muerte_juego,
    pausar_juego,
)


pygame.init()
NIVEL_INTEGRADO = __name__ in (
    "_nivel4_integrado",
    "_nivel4_boss_integrado",
)
nivel_completado = False
final_definitivo = False
accion_cierre_nivel = None

WIDTH = 1350
HEIGHT = 700
SUELO_Y = 590
FACTOR_DANO_JEFE = 0.7


def ajustar_dano_jefe(dano):
    return round(dano * FACTOR_DANO_JEFE)


def matar_jugador(jugador):
    if jugador.muerto:
        return

    jugador.inmune_dano = False
    jugador.recibiendo_dano = False
    jugador.rodando = False
    jugador.defendiendo = False
    jugador.atacando = False
    jugador.take_damage(jugador.health)


def muerte_terminada(jugador):
    return getattr(jugador, "muerto", False) and (
        getattr(jugador, "muerte_terminada", False)
        or not jugador.alive()
    )


def solicitar_cierre_nivel(action):
    global accion_cierre_nivel
    accion_cierre_nivel = action


def mostrar_menu_muerte():
    if NIVEL_INTEGRADO:
        action = menu_muerte_juego(screen, devolver_accion=True)
        solicitar_cierre_nivel(action)
        return
    menu_muerte_juego(screen)


screen = pygame.display.get_surface()
if screen is None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demon King: The Impaler")

clock = pygame.time.Clock()
fuente_aviso = pygame.font.SysFont("Arial", 24, bold=True)
fuente_fase = pygame.font.SysFont("Georgia", 26, bold=True)
fuente_cuenta_regresiva = pygame.font.SysFont("Arial", 54, bold=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_FONDOS_BATALLA = os.path.join(BASE_DIR, "imagenes", "Nivel4")
BARRA_IGNIS_ORIGINAL = pygame.image.load(
    os.path.join(BASE_DIR, "assets", "barras de vida", "ignis.png")
).convert_alpha()
ANCHO_BARRA_JEFE = 300
ALTO_BARRA_JEFE = round(
    BARRA_IGNIS_ORIGINAL.get_height()
    * ANCHO_BARRA_JEFE
    / BARRA_IGNIS_ORIGINAL.get_width()
)
BARRA_IGNIS = pygame.transform.smoothscale(
    BARRA_IGNIS_ORIGINAL,
    (ANCHO_BARRA_JEFE, ALTO_BARRA_JEFE),
)
fondo_primera_barra = pygame.transform.scale(
    pygame.image.load(
        os.path.join(
            CARPETA_FONDOS_BATALLA,
            "Trono Gótico en el Castillo Infernal.png",
        )
    ).convert(),
    (WIDTH, HEIGHT),
)
fondo_segunda_barra = pygame.transform.scale(
    pygame.image.load(
        os.path.join(
            CARPETA_FONDOS_BATALLA,
            "Salón del trono en llamas.png",
        )
    ).convert(),
    (WIDTH, HEIGHT),
)

def mostrar_comic_segunda_barra():
    ruta = os.path.join(
        CARPETA_FONDOS_BATALLA,
        "Batalla Carmesí en el Castillo Infernal.png",
    )
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró el cómic de la batalla: {ruta}")
    imagen = pygame.transform.scale(
        pygame.image.load(ruta).convert(),
        (WIDTH, HEIGHT),
    )
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if NIVEL_INTEGRADO:
                    raise NivelIntegradoFinalizado(nivel_completado, "exit")
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    esperando = False
                elif event.key == pygame.K_ESCAPE:
                    action = pausar_juego(
                        screen,
                        devolver_accion=NIVEL_INTEGRADO,
                    )
                    if NIVEL_INTEGRADO and action in ("menu", "exit"):
                        solicitar_cierre_nivel(action)
                        return

        screen.blit(imagen, (0, 0))
        texto = fuente_aviso.render(
            "PRESIONA ENTER PARA CONTINUAR",
            True,
            (255, 255, 255),
        )
        caja = texto.get_rect(center=(WIDTH // 2, HEIGHT - 32))
        fondo_texto = pygame.Surface((caja.width + 28, caja.height + 16))
        fondo_texto.fill((0, 0, 0))
        fondo_texto.set_alpha(190)
        screen.blit(fondo_texto, (caja.x - 14, caja.y - 8))
        screen.blit(texto, caja)
        pygame.display.flip()
        clock.tick(60)


def esperar_enter_cinematica(
    dibujar,
    enter_liberado=True,
    duracion_minima_ms=0,
):
    teclas_enter = (pygame.K_RETURN, pygame.K_KP_ENTER)
    inicio_ms = pygame.time.get_ticks()
    while True:
        enter_aceptado = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if NIVEL_INTEGRADO:
                    raise NivelIntegradoFinalizado(nivel_completado, "exit")
                raise SystemExit
            if event.type == pygame.KEYUP and event.key in teclas_enter:
                enter_liberado = True
            elif event.type == pygame.KEYDOWN and event.key in teclas_enter:
                if (
                    enter_liberado
                    and not enter_aceptado
                    and pygame.time.get_ticks() - inicio_ms >= duracion_minima_ms
                ):
                    enter_aceptado = True
                enter_liberado = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                action = pausar_juego(
                    screen,
                    devolver_accion=NIVEL_INTEGRADO,
                )
                if action in ("menu", "exit"):
                    if NIVEL_INTEGRADO:
                        solicitar_cierre_nivel(action)
                        return enter_liberado
                    raise SystemExit
        if enter_aceptado:
            return enter_liberado
        dibujar()
        pygame.display.flip()
        clock.tick(60)


def mostrar_intro_impaler():
    ancho, alto = screen.get_size()
    reloj_intro = pygame.time.Clock()
    inicio = pygame.time.get_ticks()
    duracion_ms = 3000
    fuente_etiqueta = pygame.font.SysFont("Arial", 18, bold=True)
    fuente_titulo = pygame.font.SysFont("Georgia", 88, bold=True)
    fuente_epiteto = pygame.font.SysFont("Georgia", 34, bold=True, italic=True)
    fuente_cierre = pygame.font.SysFont("Arial", 18, bold=True)

    panel_rect = pygame.Rect(0, 0, int(ancho * 0.76), int(alto * 0.56))
    panel_rect.center = (ancho // 2, alto // 2)
    panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    oscurecer = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    oscurecer.fill((15, 2, 2, 190))
    particulas = [
        [
            random.uniform(0, ancho),
            random.uniform(0, alto),
            random.uniform(22, 82),
            random.randint(1, 3),
            random.uniform(0, math.tau),
        ]
        for _ in range(34)
    ]

    while True:
        dt = reloj_intro.tick(60) / 1000.0
        transcurrido = pygame.time.get_ticks() - inicio
        if transcurrido >= duracion_ms:
            return

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                if NIVEL_INTEGRADO:
                    raise NivelIntegradoFinalizado(nivel_completado, "exit")
                raise SystemExit
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
                if evento.key == pygame.K_ESCAPE:
                    action = pausar_juego(
                        screen,
                        devolver_accion=NIVEL_INTEGRADO,
                    )
                    if action in ("menu", "exit"):
                        if NIVEL_INTEGRADO:
                            solicitar_cierre_nivel(action)
                            return
                        raise SystemExit

        entrada = min(1.0, transcurrido / 550.0)
        screen.blit(fondo_primera_barra, (0, 0))
        screen.blit(oscurecer, (0, 0))

        for particula in particulas:
            particula[1] -= particula[2] * dt
            particula[0] += math.sin(
                transcurrido / 260.0 + particula[4]
            ) * 12 * dt
            if particula[1] < 0:
                particula[0] = random.uniform(0, ancho)
                particula[1] = alto
            brillo = 0.5 + 0.5 * math.sin(
                transcurrido / 120.0 + particula[4]
            )
            pygame.draw.circle(
                screen,
                (255, int(75 + 115 * brillo), 28),
                (round(particula[0]), round(particula[1])),
                particula[3],
            )

        panel.fill((12, 3, 5, int(226 * entrada)))
        screen.blit(panel, panel_rect)
        pulso = 0.5 + 0.5 * math.sin(transcurrido / 230.0)
        color_marco = (int(145 + 90 * pulso), 43, 20)
        pygame.draw.rect(
            screen,
            (int(90 * entrada), 22, 12),
            panel_rect,
            2,
            border_radius=8,
        )

        margen = 34
        largo_esquina = 58
        esquinas = (
            ((panel_rect.left + margen, panel_rect.top + margen),
             (panel_rect.left + margen + largo_esquina, panel_rect.top + margen)),
            ((panel_rect.right - margen, panel_rect.top + margen),
             (panel_rect.right - margen - largo_esquina, panel_rect.top + margen)),
            ((panel_rect.left + margen, panel_rect.bottom - margen),
             (panel_rect.left + margen + largo_esquina, panel_rect.bottom - margen)),
            ((panel_rect.right - margen, panel_rect.bottom - margen),
             (panel_rect.right - margen - largo_esquina, panel_rect.bottom - margen)),
        )
        for inicio_linea, fin_linea in esquinas:
            pygame.draw.line(screen, color_marco, inicio_linea, fin_linea, 2)

        etiqueta = fuente_etiqueta.render(
            "JEFE FINAL  |  NIVEL 4", True, (245, 163, 105)
        )
        etiqueta.set_alpha(int(255 * entrada))
        screen.blit(
            etiqueta,
            etiqueta.get_rect(center=(ancho // 2, panel_rect.top + 70)),
        )

        titulo_sombra = fuente_titulo.render("DEMON KING", True, (75, 4, 8))
        titulo = fuente_titulo.render("DEMON KING", True, (255, 226, 190))
        epiteto = fuente_epiteto.render(
            "THE IMPALER", True, (255, 91, 48)
        )
        for superficie in (titulo_sombra, titulo, epiteto):
            superficie.set_alpha(int(255 * entrada))

        centro_titulo = (
            ancho // 2,
            panel_rect.top + 166 + int((1 - entrada) * 18),
        )
        rect_titulo = titulo.get_rect(center=centro_titulo)
        screen.blit(titulo_sombra, rect_titulo.move(3, 5))
        screen.blit(titulo, rect_titulo)
        screen.blit(
            epiteto,
            epiteto.get_rect(center=(ancho // 2, panel_rect.top + 245)),
        )

        separador_y = panel_rect.top + 294
        pygame.draw.line(
            screen,
            (145, 44, 24),
            (panel_rect.left + 130, separador_y),
            (panel_rect.right - 130, separador_y),
            1,
        )
        pygame.draw.polygon(
            screen,
            (255, 166, 93),
            [
                (ancho // 2, separador_y - 6),
                (ancho // 2 + 6, separador_y),
                (ancho // 2, separador_y + 6),
                (ancho // 2 - 6, separador_y),
            ],
        )

        cierre = fuente_cierre.render(
            "EL REY DEMONIO HA DESPERTADO", True, (238, 207, 165)
        )
        cierre.set_alpha(int(255 * entrada))
        screen.blit(
            cierre,
            cierre.get_rect(center=(ancho // 2, panel_rect.top + 337)),
        )
        continuar = fuente_etiqueta.render(
            "ENTER / ESPACIO  |  SALTAR INTRO",
            True,
            (230, 160, 115),
        )
        continuar.set_alpha(int(220 * entrada))
        screen.blit(
            continuar,
            continuar.get_rect(center=(ancho // 2, panel_rect.bottom + 32)),
        )
        pygame.display.flip()


def mostrar_cinematica_final_definitiva():
    def cargar_imagen_final(nombre):
        ruta = os.path.join(CARPETA_FONDOS_BATALLA, nombre)
        if not os.path.isfile(ruta):
            raise FileNotFoundError(f"No se encontró la imagen del final: {ruta}")
        imagen = pygame.image.load(ruta).convert_alpha()
        escala = min(WIDTH / imagen.get_width(), HEIGHT / imagen.get_height())
        return pygame.transform.smoothscale(
            imagen,
            (
                round(imagen.get_width() * escala),
                round(imagen.get_height() * escala),
            ),
        )

    imagen_batalla = cargar_imagen_final(
        "Captura de pantalla 2026-11-18 111126.png"
    )
    imagen = cargar_imagen_final("Héroes ante la ciudad en ruinas.png")

    fuente_final = pygame.font.SysFont("Georgia", 30, bold=True)
    fuente_prompt = pygame.font.SysFont("Arial", 18, bold=True)
    lineas_texto = (
        "Los héroes lograron vencer al rey demonio",
        "y volvieron a la ciudad.",
    )

    def dibujar_imagen_batalla():
        pantalla_imagen = pygame.Rect(0, 0, WIDTH, HEIGHT - 52)
        escala = min(
            pantalla_imagen.width / imagen_batalla.get_width(),
            pantalla_imagen.height / imagen_batalla.get_height(),
        )
        tamano = (
            round(imagen_batalla.get_width() * escala),
            round(imagen_batalla.get_height() * escala),
        )
        screen.fill((0, 0, 0))
        imagen_ajustada = pygame.transform.smoothscale(imagen_batalla, tamano)
        screen.blit(
            imagen_ajustada,
            imagen_ajustada.get_rect(center=pantalla_imagen.center),
        )

        texto = fuente_prompt.render(
            "PRESIONA ENTER PARA CONTINUAR",
            True,
            (255, 238, 205),
        )
        caja_texto = texto.get_rect(center=(WIDTH // 2, HEIGHT - 24))
        fondo_texto = pygame.Surface(
            (caja_texto.width + 24, caja_texto.height + 12),
            pygame.SRCALPHA,
        )
        fondo_texto.fill((8, 5, 8, 205))
        screen.blit(fondo_texto, fondo_texto.get_rect(center=caja_texto.center))
        screen.blit(texto, caja_texto)

    def dibujar_texto():
        screen.fill((0, 0, 0))
        alto_linea = fuente_final.get_linesize()
        y = HEIGHT // 2 - alto_linea // 2
        for linea in lineas_texto:
            texto = fuente_final.render(linea, True, (255, 255, 255))
            screen.blit(texto, texto.get_rect(center=(WIDTH // 2, y)))
            y += alto_linea

    enter_liberado = esperar_enter_cinematica(dibujar_imagen_batalla)
    if accion_cierre_nivel is not None:
        return

    enter_liberado = esperar_enter_cinematica(
        dibujar_texto,
        enter_liberado,
    )
    if accion_cierre_nivel is not None:
        return

    def dibujar_imagen():
        screen.fill((0, 0, 0))
        screen.blit(imagen, imagen.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    enter_liberado = esperar_enter_cinematica(
        dibujar_imagen,
        enter_liberado,
    )
    if accion_cierre_nivel is not None:
        return

    pantalla_fin = PantallaFinalEpica(
        screen,
        imagen,
        "Los heroes vencieron al rey demonio y salvaron la ciudad.",
    )
    iniciar_musica_epica()
    try:
        esperar_enter_cinematica(
            pantalla_fin.draw,
            enter_liberado,
            DURACION_MINIMA_FIN_MS,
        )
    finally:
        detener_musica_epica()


class ParticulaFuego:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.0, 2.0)
        self.vy = random.uniform(-6.0, -2.5)
        self.radio = random.uniform(4, 9)
        self.vida = 1.0

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.radio = max(0, self.radio - dt * 5)
        self.vida -= dt * 1.8

    def draw(self, screen, alpha_global=255):
        if self.vida > 0 and self.radio > 0:
            alpha = int(self.vida * alpha_global)
            if self.vida > 0.65:
                color = (255, 246, 190)
            elif self.vida > 0.35:
                color = (255, 115, 12)
            else:
                color = (190, 25, 5)

            center = (round(self.x), round(self.y))
            radius = max(1, round(self.radio))
            pygame.draw.circle(screen, (*color, alpha // 4), center, radius + 5)
            pygame.draw.circle(screen, (*color, alpha), center, radius)
            pygame.draw.circle(
                screen,
                (255, 238, 155, alpha),
                (center[0] - max(1, radius // 3), center[1] - max(1, radius // 3)),
                max(1, radius // 3),
            )


class ZonaFuego:
    def __init__(self, ancho_pantalla=WIDTH, alto_pantalla=HEIGHT, suelo_y=SUELO_Y):
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.suelo_y = suelo_y

        self.estado = "inactivo"
        self.cooldown_aparicion = 3.5
        self.timer = 0.8

        self.duracion_advertencia = 1.2
        self.duracion_fuego = 3.5
        self.duracion_desaparecer = 1.0

        self.lado_fuego = "izquierda"
        self.ancho_cobertura = 0.0
        self.max_ancho = self.ancho_pantalla * 0.45  
        self.alto_fuego_base = 280

        self.velocidad_expansion = self.max_ancho / 1.2
        self.alpha_opacidad = 255.0
        self.pos_y = self.suelo_y - self.alto_fuego_base
        self.fuego_surface = pygame.Surface(
            (int(self.max_ancho), self.alto_fuego_base),
            pygame.SRCALPHA,
        )
        self.particles_surface = pygame.Surface(
            (self.ancho_pantalla, self.alto_pantalla),
            pygame.SRCALPHA,
        )

        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.particulas = []
        self.tiempo_fuego = 0

        self.alerta_surf = pygame.Surface((int(self.max_ancho), self.alto_fuego_base), pygame.SRCALPHA)
        self.alerta_surf.fill((255, 30, 0, 70))

    def activar_evento(self):
        if self.estado == "inactivo":
            self.estado = "advertencia"
            self.timer = self.duracion_advertencia
            self.ancho_cobertura = 0.0
            self.alpha_opacidad = 255.0
            self.lado_fuego = random.choice(["izquierda", "derecha"])
            self.particulas.clear()

    def update(self, player, enemy, dt):
        self.tiempo_fuego += dt * 8

        if getattr(enemy, "health", 0) <= 0 or getattr(enemy, "muerto_definitivo", False):
            self.estado = "inactivo"
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            self.particulas.clear()
            return

        if self.estado == "inactivo":
            self.timer -= dt
            if self.timer <= 0:
                self.activar_evento()
            return

        elif self.estado == "advertencia":
            self.timer -= dt
            if self.timer <= 0:
                self.estado = "activo"
                self.timer = self.duracion_fuego

        elif self.estado in ["activo", "desapareciendo"]:
            if self.estado == "activo":
                self.timer -= dt
                if self.ancho_cobertura < self.max_ancho:
                    self.ancho_cobertura += self.velocidad_expansion * dt
                    if self.ancho_cobertura > self.max_ancho:
                        self.ancho_cobertura = self.max_ancho
                if self.timer <= 0:
                    self.estado = "desapareciendo"
                    self.timer = self.duracion_desaparecer

            elif self.estado == "desapareciendo":
                self.timer -= dt
                self.alpha_opacidad = max(0.0, (self.timer / self.duracion_desaparecer) * 255.0)
                if self.timer <= 0:
                    self.estado = "inactivo"
                    self.timer = self.cooldown_aparicion
                    self.hitbox = pygame.Rect(0, 0, 0, 0)
                    self.particulas.clear()
                    return

            w = int(self.ancho_cobertura)
            if self.lado_fuego == "izquierda":
                self.hitbox = pygame.Rect(0, self.pos_y, w, self.alto_fuego_base)
            else:
                self.hitbox = pygame.Rect(self.ancho_pantalla - w, self.pos_y, w, self.alto_fuego_base)

            if player.hurtbox.colliderect(self.hitbox):
                matar_jugador(player)

            # Generar partículas
            if w > 0:
                for _ in range(4):
                    if self.lado_fuego == "izquierda":
                        px = random.uniform(0, w)
                    else:
                        px = random.uniform(self.ancho_pantalla - w, self.ancho_pantalla)
                    py = self.suelo_y - random.uniform(5, 70)
                    self.particulas.append(ParticulaFuego(px, py))

        for p in self.particulas[:]:
            p.update(dt)
            if p.vida <= 0 or p.radio <= 0:
                self.particulas.remove(p)

    def draw(self, screen):
        if self.estado == "inactivo":
            return

        if self.estado == "advertencia":
            if int(pygame.time.get_ticks() / 200) % 2 == 0:
                pos_x = 0 if self.lado_fuego == "izquierda" else self.ancho_pantalla - self.max_ancho
                screen.blit(self.alerta_surf, (pos_x, self.pos_y))

        elif self.estado in ["activo", "desapareciendo"]:
            if self.ancho_cobertura > 0:
                w = min(int(self.ancho_cobertura), self.fuego_surface.get_width())
                alpha = int(self.alpha_opacidad)
                fuego_surf = self.fuego_surface
                fuego_surf.fill((0, 0, 0, 0))
                pygame.draw.rect(
                    fuego_surf,
                    (125, 12, 2, int(alpha * 0.8)),
                    (0, 35, w, self.alto_fuego_base - 35),
                )
                pygame.draw.rect(
                    fuego_surf,
                    (235, 44, 2, int(alpha * 0.86)),
                    (0, 95, w, self.alto_fuego_base - 95),
                )
                pygame.draw.rect(
                    fuego_surf,
                    (255, 150, 12, alpha),
                    (0, 165, w, self.alto_fuego_base - 165),
                )

                puntos_llamarada = []
                paso = max(10, w // 20)
                for x_pos in range(0, w + paso, paso):
                    x_pos = min(x_pos, w)
                    offset_y = (
                        math.sin(self.tiempo_fuego + x_pos * 0.05) * 15
                        + math.sin(self.tiempo_fuego * 1.7 + x_pos * 0.11) * 7
                    )
                    puntos_llamarada.append((x_pos, 48 + offset_y))

                puntos_llamarada.append((w, self.alto_fuego_base))
                puntos_llamarada.append((0, self.alto_fuego_base))

                if len(puntos_llamarada) >= 3:
                    pygame.draw.polygon(
                        fuego_surf,
                        (255, 72, 4, int(alpha * 0.94)),
                        puntos_llamarada,
                    )

                for x_pos in range(18, w, max(32, w // 12)):
                    punta_y = 18 + round(
                        17 * (0.5 + 0.5 * math.sin(self.tiempo_fuego * 1.3 + x_pos))
                    )
                    pygame.draw.polygon(
                        fuego_surf,
                        (255, 128, 12, alpha),
                        (
                            (x_pos - 16, 58),
                            (x_pos, punta_y),
                            (x_pos + 17, 58),
                        ),
                    )
                    pygame.draw.line(
                        fuego_surf,
                        (255, 225, 85, alpha),
                        (x_pos, punta_y + 8),
                        (x_pos + 3, 92),
                        2,
                    )

                pos_x = 0 if self.lado_fuego == "izquierda" else self.ancho_pantalla - w
                screen.blit(
                    fuego_surf,
                    (pos_x, self.pos_y),
                    pygame.Rect(0, 0, w, self.alto_fuego_base),
                )

        self.particles_surface.fill((0, 0, 0, 0))
        for particle in self.particulas:
            particle.draw(self.particles_surface, alpha_global=self.alpha_opacidad)
        screen.blit(self.particles_surface, (0, 0))


class ProyectilHolograma:
    image = pygame.Surface((96, 168), pygame.SRCALPHA)
    outer_shape = (
        (48, 0), (65, 34), (93, 52), (66, 75), (78, 105),
        (49, 168), (36, 112), (4, 88), (29, 66), (15, 43), (42, 51),
    )
    inner_shape = (
        (48, 10), (60, 39), (81, 54), (61, 75), (70, 99),
        (49, 151), (39, 107), (17, 86), (36, 67), (26, 48), (44, 54),
    )
    pygame.draw.polygon(image, (105, 0, 22, 100), outer_shape)
    pygame.draw.polygon(image, (235, 18, 24, 225), inner_shape)
    pygame.draw.polygon(
        image,
        (255, 67, 33, 255),
        ((48, 17), (56, 49), (69, 57), (53, 78), (60, 99), (48, 139), (43, 95), (28, 83), (44, 65), (36, 51)),
    )
    pygame.draw.lines(
        image,
        (255, 230, 185, 255),
        False,
        ((47, 21), (52, 53), (43, 70), (52, 87), (46, 125)),
        4,
    )
    pygame.draw.lines(
        image,
        (255, 115, 77, 220),
        False,
        ((14, 43), (38, 57), (22, 71)),
        3,
    )
    pygame.draw.lines(
        image,
        (255, 125, 75, 220),
        False,
        ((82, 54), (58, 68), (76, 80)),
        3,
    )

    def __init__(self, x, y):
        self.rect = pygame.Rect(round(x - 32), round(y), 64, 128)
        self.speed = 470
        self.damage = ajustar_dano_jefe(45)

    def update(self, dt):
        self.rect.y += round(self.speed * dt)

    def draw(self, screen):
        screen.blit(
            self.image,
            (
                self.rect.centerx - self.image.get_width() // 2,
                self.rect.centery - self.image.get_height() // 2,
            ),
        )


class LavaAscendente:
    def __init__(self, plataforma_y):
        self.plataforma_y = plataforma_y
        self.estado = "inactivo"
        self.timer = 1.5
        self.y = HEIGHT
        self.warning_duration = 1.0
        self.hold_duration = 1.6
        self.rise_speed = 320
        self.fall_speed = 400
        rng = random.Random(2905)
        self.warning_particles = tuple(
            (
                rng.randrange(24, WIDTH - 24),
                rng.random(),
                rng.randrange(2, 5),
            )
            for _ in range(28)
        )

    def reset(self):
        self.estado = "inactivo"
        self.timer = 1.5
        self.y = HEIGHT

    def disable(self):
        self.estado = "inactivo"
        self.timer = 0.0
        self.y = HEIGHT

    def update(self, dt, player):
        if self.estado == "inactivo":
            self.timer -= dt
            if self.timer <= 0:
                self.estado = "advertencia"
                self.timer = self.warning_duration
        elif self.estado == "advertencia":
            self.timer -= dt
            if self.timer <= 0:
                self.estado = "subiendo"
        elif self.estado == "subiendo":
            self.y = max(self.plataforma_y, self.y - self.rise_speed * dt)
            if self.y <= self.plataforma_y:
                self.estado = "activa"
                self.timer = self.hold_duration
        elif self.estado == "activa":
            self.timer -= dt
            if self.timer <= 0:
                self.estado = "bajando"
        elif self.estado == "bajando":
            self.y = min(HEIGHT, self.y + self.fall_speed * dt)
            if self.y >= HEIGHT:
                self.estado = "inactivo"
                self.timer = 3.5

        if (
            self.estado in ("subiendo", "activa", "bajando")
            and player.plataforma_actual is None
            and player.hurtbox.bottom >= self.y
        ):
            matar_jugador(player)

    def draw(self, screen):
        if self.estado == "inactivo":
            return
        if self.estado == "advertencia":
            elapsed = self.warning_duration - self.timer
            pygame.draw.line(
                screen,
                (150, 45, 12),
                (0, SUELO_Y - 1),
                (WIDTH, SUELO_Y - 1),
                2,
            )
            for x, phase, radius in self.warning_particles:
                pulse = (elapsed * 1.25 + phase) % 1.0
                y = SUELO_Y - 3 - round(pulse * 30)
                center = (x, y)
                pygame.draw.circle(screen, (150, 30, 5), center, radius + 2)
                pygame.draw.circle(screen, (255, 92, 12), center, radius)
                if radius > 2:
                    pygame.draw.circle(screen, (255, 220, 100), center, 1)
            return

        alto = max(0, HEIGHT - round(self.y))
        if alto == 0:
            return
        top = round(self.y)
        tiempo = pygame.time.get_ticks() / 190
        puntos = [
            (
                min(x, WIDTH),
                top + round(
                    9 * math.sin(tiempo + x / 48)
                    + 4 * math.sin(tiempo * 1.7 + x / 19)
                ),
            )
            for x in range(0, WIDTH + 41, 40)
        ]
        puntos.extend(((WIDTH, HEIGHT), (0, HEIGHT)))
        pygame.draw.rect(screen, (92, 9, 5), (0, top, WIDTH, HEIGHT - top))
        pygame.draw.polygon(screen, (190, 22, 6), puntos)

        onda_caliente = [
            (x, y + 7 + round(3 * math.sin(tiempo * 1.4 + x / 27)))
            for x, y in puntos[:-2]
        ]
        pygame.draw.lines(screen, (255, 78, 13), False, onda_caliente, 8)
        pygame.draw.lines(
            screen,
            (255, 193, 47),
            False,
            [(x, y - 2) for x, y in onda_caliente],
            2,
        )

        for index, x in enumerate(range(55, WIDTH, 125)):
            bubble_y = top + 36 + (index % 3) * 47 + round(
                7 * math.sin(tiempo * 1.8 + index)
            )
            if bubble_y < HEIGHT - 10:
                pygame.draw.circle(screen, (255, 105, 20), (x, bubble_y), 7)
                pygame.draw.circle(screen, (255, 210, 80), (x - 2, bubble_y - 2), 3)


def crear_imagen_holograma(image, alpha=185):
    holograma = image.copy()
    holograma.fill((255, 35, 35, 255), special_flags=pygame.BLEND_RGBA_MULT)
    holograma.set_alpha(alpha)
    return holograma


class HologramVolley:
    def __init__(self, attack_frames, width, count=5, excluded_x=None):
        self.attack_frames = [
            crear_imagen_holograma(frame)
            for frame in attack_frames
        ]
        if not self.attack_frames:
            raise ValueError("La animación attack1 de los hologramas está vacía.")
        posiciones = [
            round(width * (index + 1) / (count + 1))
            for index in range(count)
        ]
        if excluded_x is not None:
            radio_exclusion = max(
                image.get_width() // 2
                for image in self.attack_frames
            ) + 30
            posiciones = [
                x for x in posiciones
                if abs(x - excluded_x) > radio_exclusion
            ]
        if not posiciones:
            raise ValueError("No hay posiciones libres para los clones holográficos.")

        self.safe_index = random.randrange(len(posiciones))
        self.attack_duration = 0.6
        self.animation_time = 0.0
        self.clones = []
        self.state = "advertencia"
        self.timer = 0.65
        for index, x in enumerate(posiciones):
            rect = self.attack_frames[0].get_rect(midbottom=(x, 190))
            self.clones.append(
                {
                    "rect": rect,
                    "attacks": index != self.safe_index,
                }
            )

    def update(self, dt, projectiles):
        self.animation_time += dt
        self.timer -= dt
        if self.state == "advertencia" and self.timer <= 0:
            for clone in self.clones:
                if clone["attacks"]:
                    projectiles.append(
                        ProyectilHolograma(
                            clone["rect"].centerx,
                            clone["rect"].bottom,
                        )
                    )
            self.state = "disparando"
            self.timer = self.attack_duration
        elif self.state == "disparando" and self.timer <= 0:
            return True
        return False

    def draw(self, screen):
        frame_index = int(self.animation_time / 0.18) % len(self.attack_frames)
        image = self.attack_frames[frame_index]
        for index, clone in enumerate(self.clones):
            rect = clone["rect"]
            screen.blit(image, image.get_rect(midbottom=rect.midbottom))
            if self.state == "advertencia" and clone["attacks"]:
                pygame.draw.line(
                    screen, (255, 55, 55), (rect.centerx, rect.bottom),
                    (rect.centerx, HEIGHT), 2,
                )
            if index == self.safe_index:
                top = rect.top - 18
                pygame.draw.polygon(
                    screen,
                    (125, 255, 170),
                    ((rect.centerx, top - 8), (rect.centerx + 8, top),
                     (rect.centerx, top + 8), (rect.centerx - 8, top)),
                )


class BossBattleController:
    FIRST_BAR_HEALTH = 500
    SECOND_BAR_HEALTH = FIRST_BAR_HEALTH * 2

    def __init__(self, boss):
        self.phase = 1
        boss.max_health = self.FIRST_BAR_HEALTH
        boss.health = self.FIRST_BAR_HEALTH
        self.platform = pygame.Rect(60, 360, WIDTH - 120, 22)
        self.lava = LavaAscendente(self.platform.top)
        self.projectiles = []
        self.hologram_event = None
        self.hologram_timer = 0.0
        self.phase_banner_timer = 0.0

        self.phase3_state = "cargando_derecha"
        self.phase3_timer = 0.0
        self.lightning_countdown_font = fuente_cuenta_regresiva
        self.horizontal_beam = pygame.Rect(0, 0, 0, 0)
        self.horizontal_beam_hit = False
        self.teleport_flash_timer = 0.0
        self.vertical_state = "cargando"
        self.vertical_timer = 0.0
        self.vertical_x = 0
        self.vertical_rect = pygame.Rect(0, 0, 0, 0)
        self.vertical_image = None
        self.vertical_attack_frames = []
        self.vertical_animation_time = 0.0
        self.vertical_beam_hit = False

        self.execution_clones = []
        self.final_death = False

    def _detener_fuego(self, zona_fuego):
        zona_fuego.estado = "inactivo"
        zona_fuego.timer = 0.0
        zona_fuego.hitbox = pygame.Rect(0, 0, 0, 0)
        zona_fuego.particulas.clear()

    def _limpiar_hologramas(self):
        self.hologram_event = None
        self.projectiles.clear()

    def _iniciar_fase2(self, zona_fuego):
        self.phase = 2
        self.phase_banner_timer = 1.5
        self._detener_fuego(zona_fuego)
        self.lava.reset()
        self.hologram_timer = 1.4
        self._limpiar_hologramas()

    def _iniciar_fase3(self, boss, zona_fuego):
        mostrar_comic_segunda_barra()
        if accion_cierre_nivel is not None:
            return
        self.phase = 3
        self.phase_banner_timer = 1.5
        self._detener_fuego(zona_fuego)
        self.lava.disable()
        self._limpiar_hologramas()
        boss.max_health = self.SECOND_BAR_HEALTH
        boss.health = self.SECOND_BAR_HEALTH
        self.phase3_state = "cargando_derecha"
        self.phase3_timer = 5.0
        self.hologram_timer = 1.0
        self.horizontal_beam = pygame.Rect(0, 0, 0, 0)
        self.teleport_flash_timer = 0.0
        self.vertical_state = "cargando"
        self.vertical_timer = 5.0
        self.vertical_x = WIDTH // 2
        self.vertical_attack_frames = [
            crear_imagen_holograma(frame, alpha=220)
            for frame in boss.animaciones["attack1"][15:18]
        ]
        if len(self.vertical_attack_frames) != 3:
            raise ValueError("Impaler Boss necesita los fotogramas 16–18 de attack1.")
        self.vertical_animation_time = 0.0
        self.vertical_image = self.vertical_attack_frames[0]
        self.vertical_rect = self.vertical_image.get_rect(
            midbottom=(WIDTH // 2, 175)
        )
        boss.rect.x = WIDTH - boss.rect.width - 80
        boss.rect.bottom = SUELO_Y
        boss.hurtbox = boss.rect.copy()
        boss.velocity_y = 0
        boss.on_ground = True
        boss.attacking = False
        boss.hitbox = pygame.Rect(0, 0, 0, 0)
        boss.direction = "left"
        boss.estado_actual = "attack4"
        boss.frame_actual = 0.0
        self._poner_frame_boss(boss, boss.animaciones["attack4"][0])

    def _iniciar_fase4(self, boss, player, zona_fuego):
        self.phase = 4
        self.phase_banner_timer = 1.5
        self._detener_fuego(zona_fuego)
        self.lava.disable()
        self._limpiar_hologramas()
        self.vertical_state = "inactivo"
        self.horizontal_beam = pygame.Rect(0, 0, 0, 0)
        self.final_death = False

        boss.attacking = False
        boss.has_hit = False
        boss.hitbox = pygame.Rect(0, 0, 0, 0)
        boss.health = 1
        boss.rect.x = WIDTH - 230
        self._poner_frame_boss(boss, self._frame_muerte4(boss))
        boss.image = pygame.transform.scale(
            boss.image,
            (boss.image.get_width(), max(1, round(boss.image.get_height() * 0.68))),
        )
        boss.rect.height = boss.image.get_height()
        boss.rect.bottom = SUELO_Y
        boss.hurtbox = boss.rect.copy()

        player.set_position(min(player.pos_x, WIDTH // 3), SUELO_Y)

        clone_image = pygame.mask.from_surface(
            self._frame_muerte4(boss),
            threshold=1,
        ).to_surface(
            setcolor=(255, 255, 255, 255),
            unsetcolor=(0, 0, 0, 0),
        )
        start_x = player.hurtbox.centerx
        end_x = boss.rect.centerx
        self.execution_clones = []
        for index in range(4):
            x = round(start_x + (end_x - start_x) * (index + 1) / 5)
            surface = pygame.transform.scale(clone_image, (78, 105))
            rect = surface.get_rect(midbottom=(x, SUELO_Y))
            self.execution_clones.append(
                {
                    "surface": surface,
                    "rect": rect,
                    "alive": True,
                    "fade": 1.0,
                }
            )

    def registrar_golpe(self, player, boss, zona_fuego):
        if not player.atacando or player.has_hit:
            return

        if self.phase in (1, 2):
            if player.hitbox.colliderect(boss.hurtbox):
                boss.take_damage(25)
                player.has_hit = True
                if self.phase == 1 and boss.health <= self.FIRST_BAR_HEALTH * 0.5:
                    self._iniciar_fase2(zona_fuego)
                elif self.phase == 2 and boss.health <= 0:
                    self._iniciar_fase3(boss, zona_fuego)
            return

        if self.phase == 3:
            if player.hitbox.colliderect(boss.hurtbox):
                player.has_hit = True
                if self.phase3_state in (
                    "cargando_derecha",
                    "cargando_izquierda",
                ):
                    boss.take_damage(25)
                    if boss.health <= 0:
                        self._iniciar_fase4(boss, player, zona_fuego)
            return

        target = next(
            (clone for clone in self.execution_clones if clone["alive"]),
            None,
        )
        if target is not None:
            if player.hitbox.colliderect(target["rect"]):
                target["alive"] = False
                target["fade"] = 1.0
                player.has_hit = True
            return

        if player.hitbox.colliderect(boss.hurtbox):
            boss.take_damage(1)
            player.has_hit = True
            self.final_death = True

    def update_boss_phase3(self, dt, player, boss):
        boss.attacking = False
        boss.hitbox = pygame.Rect(0, 0, 0, 0)
        self.teleport_flash_timer = max(0.0, self.teleport_flash_timer - dt)
        right_x = WIDTH - boss.rect.width - 80
        left_x = self.platform.left + 20

        if self.phase3_state == "cargando_derecha":
            boss.rect.x = right_x
            boss.rect.bottom = SUELO_Y
            boss.direction = "left"
            self.phase3_timer = max(0.0, self.phase3_timer - dt)
            self._animar_carga_boss(boss)
            self.horizontal_beam = pygame.Rect(0, 0, 0, 0)
            if self.phase3_timer <= 0:
                self.phase3_state = "disparando_derecha"
                self.phase3_timer = 0.35
                self.horizontal_beam_hit = False
        elif self.phase3_state == "disparando_derecha":
            boss.rect.x = right_x
            boss.rect.bottom = SUELO_Y
            boss.direction = "left"
            self._animar_disparo_boss(boss)
            self.horizontal_beam = pygame.Rect(
                0, SUELO_Y - 50, max(1, boss.rect.left), 36
            )
            if (
                self.horizontal_beam.colliderect(player.hurtbox)
                and not self.horizontal_beam_hit
            ):
                matar_jugador(player)
                self.horizontal_beam_hit = True
            self.phase3_timer -= dt
            if self.phase3_timer <= 0:
                self.phase3_state = "cargando_izquierda"
                self.phase3_timer = 5.0
                boss.rect.x = left_x
                boss.rect.bottom = self.platform.top
                boss.estado_actual = "attack4"
                boss.frame_actual = 0.0
                self._poner_frame_boss(boss, boss.animaciones["attack4"][0])
                self.teleport_flash_timer = 0.18
                self.horizontal_beam = pygame.Rect(0, 0, 0, 0)
        elif self.phase3_state == "cargando_izquierda":
            boss.rect.x = left_x
            boss.rect.bottom = self.platform.top
            boss.direction = "right"
            self.phase3_timer = max(0.0, self.phase3_timer - dt)
            self._animar_carga_boss(boss)
            self.horizontal_beam = pygame.Rect(0, 0, 0, 0)
            if self.phase3_timer <= 0:
                self.phase3_state = "disparando_izquierda"
                self.phase3_timer = 0.35
                self.horizontal_beam_hit = False
        elif self.phase3_state == "disparando_izquierda":
            boss.rect.x = left_x
            boss.rect.bottom = self.platform.top
            boss.direction = "right"
            self._animar_disparo_boss(boss)
            self.horizontal_beam = pygame.Rect(
                boss.rect.right,
                self.platform.top - 50,
                max(1, WIDTH - boss.rect.right),
                36,
            )
            if (
                self.horizontal_beam.colliderect(player.hurtbox)
                and not self.horizontal_beam_hit
            ):
                matar_jugador(player)
                self.horizontal_beam_hit = True
            self.phase3_timer -= dt
            if self.phase3_timer <= 0:
                self.phase3_state = "cargando_derecha"
                self.phase3_timer = 5.0
                boss.rect.x = right_x
                boss.rect.bottom = SUELO_Y
                boss.direction = "left"
                boss.estado_actual = "attack4"
                boss.frame_actual = 0.0
                self._poner_frame_boss(boss, boss.animaciones["attack4"][0])
                self.teleport_flash_timer = 0.18
                self.horizontal_beam = pygame.Rect(0, 0, 0, 0)

        boss.hurtbox = boss.rect.copy()

    def _animar_boss(self, boss, state):
        if state not in boss.animaciones or not boss.animaciones[state]:
            state = "idle"
        boss.cambiar_estado(state)
        boss.actualizar_animacion()

    def _frame_muerte4(self, boss):
        frames = boss.animaciones.get("muerte", [])
        if len(frames) < 4:
            raise ValueError("Impaler Boss necesita el cuarto fotograma de muerte.")
        return frames[3]

    def _poner_frame_boss(self, boss, frame):
        boss.image = (
            pygame.transform.flip(frame, True, False)
            if boss.direction == "left"
            else frame
        )

    def _animar_carga_boss(self, boss):
        frames = boss.animaciones.get("attack4", [])
        if len(frames) < 11:
            raise ValueError("Impaler Boss necesita 11 fotogramas de attack4.")
        progreso = min(1.0, max(0.0, (5.0 - self.phase3_timer) / 5.0))
        indice = min(10, int(progreso * 11))
        boss.estado_actual = "attack4"
        boss.frame_actual = float(indice)
        self._poner_frame_boss(boss, frames[indice])

    def _animar_disparo_boss(self, boss):
        frames = boss.animaciones.get("attack1", [])
        if len(frames) < 18:
            raise ValueError("Impaler Boss necesita los fotogramas 16–18 de attack1.")
        progreso = min(1.0, max(0.0, (0.35 - self.phase3_timer) / 0.35))
        indice = 15 + min(2, int(progreso * 3))
        boss.estado_actual = "attack1"
        boss.frame_actual = float(indice)
        self._poner_frame_boss(boss, frames[indice])

    def _actualizar_hologramas(self, dt, boss):
        if self.hologram_event is None:
            self.hologram_timer -= dt
            if self.hologram_timer <= 0:
                self.hologram_event = HologramVolley(
                    boss.animaciones["attack1"][15:18],
                    WIDTH,
                    excluded_x=WIDTH // 2 if self.phase == 3 else None,
                )
                self.hologram_timer = random.uniform(
                    3.5,
                    4.5,
                )
        elif self.hologram_event.update(dt, self.projectiles):
            self.hologram_event = None

    def _actualizar_rayo_vertical(self, dt, player):
        self.vertical_animation_time += dt
        indice = int(self.vertical_animation_time / 0.18) % len(
            self.vertical_attack_frames
        )
        self.vertical_image = self.vertical_attack_frames[indice]
        self.vertical_rect = self.vertical_image.get_rect(
            midbottom=(WIDTH // 2, 175)
        )

        if self.vertical_state == "cargando":
            self.vertical_timer = max(0.0, self.vertical_timer - dt)
            if self.vertical_timer <= 0:
                self.vertical_state = "activo"
                self.vertical_timer = 0.35
                self.vertical_beam_hit = False
        elif self.vertical_state == "activo":
            laser = pygame.Rect(WIDTH // 2 - 24, 0, 48, HEIGHT)
            if laser.colliderect(player.hurtbox) and not self.vertical_beam_hit:
                matar_jugador(player)
                self.vertical_beam_hit = True
            self.vertical_timer -= dt
            if self.vertical_timer <= 0:
                self.vertical_state = "cargando"
                self.vertical_timer = 5.0
                self.vertical_x = WIDTH // 2

    def update(self, dt, player, boss, zona_fuego):
        self.phase_banner_timer = max(0.0, self.phase_banner_timer - dt)
        if self.phase == 1:
            zona_fuego.update(player, boss, dt)
            return

        self._detener_fuego(zona_fuego)
        if self.phase == 2:
            self.lava.update(dt, player)
            self._actualizar_hologramas(dt, boss)
        elif self.phase == 3:
            self._actualizar_hologramas(dt, boss)
            self._actualizar_rayo_vertical(dt, player)

        if self.phase in (2, 3):
            self._actualizar_proyectiles(dt, player)
        elif self.phase == 4:
            for clone in self.execution_clones:
                if not clone["alive"]:
                    clone["fade"] = max(0.0, clone["fade"] - dt * 3.5)
            self._limitar_avance_por_clon(player)

    def _limitar_avance_por_clon(self, player):
        clone = next(
            (clone for clone in self.execution_clones if clone["alive"]),
            None,
        )
        if clone is None:
            return

        limite_x = clone["rect"].left - player.hurtbox.width // 2
        if player.pos_x > limite_x:
            player.pos_x = float(limite_x)
            player.rect.centerx = limite_x
            player.velocidad_x = 0
            player.actualizar_hitboxes()

    def _actualizar_proyectiles(self, dt, player):
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if projectile.rect.colliderect(player.hurtbox):
                player.take_damage(projectile.damage, attacker=projectile)
                self.projectiles.remove(projectile)
            elif projectile.rect.top > HEIGHT:
                self.projectiles.remove(projectile)

    def draw_stage(self, screen):
        if self.phase == 2:
            self.lava.draw(screen)
        if self.phase in (2, 3):
            pygame.draw.rect(screen, (80, 52, 48), self.platform)
            pygame.draw.rect(screen, (180, 130, 95), self.platform, 4)
            pygame.draw.line(
                screen, (255, 205, 130),
                (self.platform.left, self.platform.top + 2),
                (self.platform.right, self.platform.top + 2),
                3,
            )

    def draw_effects(self, screen, boss):
        if self.hologram_event is not None:
            self.hologram_event.draw(screen)
        for projectile in self.projectiles:
            projectile.draw(screen)

        if self.phase == 3:
            if self.phase3_state in (
                "cargando_derecha",
                "cargando_izquierda",
                "disparando_derecha",
                "disparando_izquierda",
            ):
                segundos = (
                    0
                    if self.phase3_state.startswith("disparando")
                    else max(0, math.ceil(self.phase3_timer))
                )
                numero_sombra = self.lightning_countdown_font.render(
                    str(segundos),
                    True,
                    (35, 8, 5),
                )
                numero = self.lightning_countdown_font.render(
                    str(segundos),
                    True,
                    (255, 226, 135),
                )
                posicion = (boss.rect.centerx, boss.rect.top - 34)
                screen.blit(
                    numero_sombra,
                    numero_sombra.get_rect(
                        center=(posicion[0] + 2, posicion[1] + 3)
                    ),
                )
                screen.blit(numero, numero.get_rect(center=posicion))

            if self.phase3_state in (
                "disparando_derecha",
                "disparando_izquierda",
            ):
                pygame.draw.rect(
                    screen,
                    (90, 0, 20),
                    self.horizontal_beam.inflate(0, 36),
                )
                pygame.draw.rect(screen, (205, 12, 12), self.horizontal_beam)
                pygame.draw.rect(
                    screen,
                    (255, 95, 30),
                    self.horizontal_beam.inflate(0, -14),
                )
                pygame.draw.line(
                    screen,
                    (255, 238, 195),
                    (self.horizontal_beam.left, self.horizontal_beam.centery),
                    (self.horizontal_beam.right, self.horizontal_beam.centery),
                    5,
                )

            if self.vertical_image is not None:
                screen.blit(self.vertical_image, self.vertical_rect)
                x = self.vertical_x
                if self.vertical_state != "cargando":
                    pygame.draw.line(screen, (75, 0, 18), (x, 0), (x, HEIGHT), 94)
                    pygame.draw.line(screen, (190, 10, 14), (x, 0), (x, HEIGHT), 62)
                    pygame.draw.line(screen, (255, 45, 17), (x, 0), (x, HEIGHT), 36)
                    pygame.draw.line(screen, (255, 168, 93), (x, 0), (x, HEIGHT), 16)
                    pygame.draw.line(screen, (255, 246, 205), (x, 0), (x, HEIGHT), 6)

            if self.teleport_flash_timer > 0:
                pygame.draw.ellipse(
                    screen,
                    (190, 110, 255),
                    boss.rect.inflate(30, 18),
                    4,
                )

        if self.phase == 4:
            for clone in self.execution_clones:
                if clone["fade"] <= 0:
                    continue
                image = clone["surface"].copy()
                image.set_alpha(round(210 * clone["fade"]))
                screen.blit(image, clone["rect"])

        if self.phase_banner_timer > 0 and self.phase in (2, 3, 4):
            titulo = {
                2: "FASE 2 - LAVA Y HOLOGRAMAS",
                3: "FASE 3 - RAYOS Y CLONES",
                4: "FASE 4 - EJECUCION FINAL",
            }[self.phase]
            banner = fuente_fase.render(titulo, True, (255, 220, 165))
            screen.blit(banner, banner.get_rect(center=(WIDTH // 2, 84)))

    @property
    def clones_restantes(self):
        return sum(clone["alive"] for clone in self.execution_clones)


def dibujar_barras_vida(screen, player, enemy, phase=1):
    fuente = pygame.font.SysFont("Arial", 13, bold=True)

    e_health = getattr(enemy, "health", 0)
    e_max_health = getattr(enemy, "max_health", 1)
    pct_e = max(0.0, min(1.0, e_health / e_max_health if e_max_health > 0 else 0.0))
    x, y = WIDTH - 320, 8
    x_relleno = x + int(ANCHO_BARRA_JEFE * 0.08)
    y_relleno = y + int(ALTO_BARRA_JEFE * 0.44)
    ancho_relleno = int(ANCHO_BARRA_JEFE * 0.84)
    alto_relleno = max(1, int(ALTO_BARRA_JEFE * 0.40))
    ancho_actual = int(ancho_relleno * pct_e)
    pygame.draw.rect(
        screen,
        (20, 5, 5),
        (x_relleno, y_relleno, ancho_relleno, alto_relleno),
    )
    if ancho_actual > 0:
        pygame.draw.rect(
            screen,
            (190, 30, 30),
            (x_relleno, y_relleno, ancho_actual, alto_relleno),
        )
        pygame.draw.rect(
            screen,
            (240, 90, 90),
            (x_relleno, y_relleno, ancho_actual, max(1, alto_relleno // 3)),
        )
    screen.blit(BARRA_IGNIS, (x, y))
    phase_name = "Ejecucion final" if phase == 4 else f"Fase {phase}"
    screen.blit(
        fuente.render(
            f"Demon King: The Impaler - {phase_name}: {int(e_health)}",
            True,
            (255, 255, 255),
        ),
        (x + 5, y + ALTO_BARRA_JEFE + 4),
    )


player = globals().get("jugador_nivel4")
if player is None:
    player = crear_jugador(200, SUELO_Y, SUELO_Y, WIDTH, WIDTH)
    player.max_health = 150
    player.health = player.max_health
else:
    player.set_position(200, SUELO_Y)
enemy = ImpalerBoss(900, 500)
zona_fuego = ZonaFuego()
batalla = BossBattleController(enemy)

mostrar_intro_impaler()
running = accion_cierre_nivel is None

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if NIVEL_INTEGRADO:
                raise NivelIntegradoFinalizado(nivel_completado, "exit")
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player.procesar_evento(
                    pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN,
                        {
                            "button": pygame.BUTTON_LEFT,
                            "pos": player.hurtbox.center,
                        },
                    )
                )
            elif event.key == pygame.K_ESCAPE:
                action = pausar_juego(
                    screen,
                    devolver_accion=NIVEL_INTEGRADO,
                )
                if NIVEL_INTEGRADO and action in ("menu", "exit"):
                    solicitar_cierre_nivel(action)
                    running = False
                    break
            else:
                player.procesar_evento(event)
        else:
            player.procesar_evento(event)

    if not running:
        break

    plataforma = batalla.platform if batalla.phase in (2, 3) else None
    player.plataformas = [plataforma] if plataforma is not None else []
    player.update(0, transicion_realizada=True)

    if batalla.phase in (1, 2):
        enemy.update(
            player,
            dt,
            width=WIDTH,
            platform=batalla.platform if batalla.phase == 2 else None,
            ground_y=SUELO_Y,
        )
    elif batalla.phase == 3:
        batalla.update_boss_phase3(dt, player, enemy)
    elif batalla.final_death:
        enemy.update(player, dt, width=WIDTH)

    batalla.update(dt, player, enemy, zona_fuego)
    if accion_cierre_nivel is not None:
        running = False
        break
    batalla.registrar_golpe(player, enemy, zona_fuego)
    enemy.esta_rojo = False

    if (
        batalla.phase in (1, 2)
        and getattr(enemy, "attacking", False)
        and not getattr(enemy, "has_hit", False)
    ):
        if hasattr(enemy, "hitbox") and enemy.hitbox.colliderect(player.hurtbox):
            player.take_damage(ajustar_dano_jefe(18), attacker=enemy)
            enemy.has_hit = True

    if muerte_terminada(player):
        mostrar_menu_muerte()
        running = False
        break

    fondo_actual = (
        fondo_primera_barra
        if batalla.phase in (1, 2)
        else fondo_segunda_barra
    )
    screen.blit(fondo_actual, (0, 0))
    batalla.draw_stage(screen)
    enemy.draw(screen)
    screen.blit(player.image, player.rect)
    dibujar_barra_vida_jugador(screen, player)
    player.dibujar_barra_energia(screen)
    if batalla.phase == 1:
        zona_fuego.draw(screen)
    batalla.draw_effects(screen, enemy)
    dibujar_barras_vida(screen, player, enemy, batalla.phase)

    pygame.display.flip()

    if getattr(enemy, "muerto_definitivo", False):
        running = False

if getattr(enemy, "muerto_definitivo", False) and accion_cierre_nivel is None:
    mostrar_cinematica_final_definitiva()
    if accion_cierre_nivel is None:
        final_definitivo = True
        nivel_completado = True

if not NIVEL_INTEGRADO:
    pygame.quit()