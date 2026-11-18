import os
import random
import math
import pygame
from Jefes_enemigos import ImpalerBoss
from personajes import crear_jugador
from menu_pausa import NivelIntegradoFinalizado, pausar_juego


pygame.init()
NIVEL_INTEGRADO = __name__ in (
    "_nivel4_integrado",
    "_nivel4_boss_integrado",
)
nivel_completado = False

WIDTH = 1350
HEIGHT = 700
SUELO_Y = 590

screen = pygame.display.get_surface()
if screen is None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batalla contra ignis")

clock = pygame.time.Clock()
fuente_aviso = pygame.font.SysFont("Arial", 24, bold=True)
fuente_fase = pygame.font.SysFont("Georgia", 26, bold=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_FONDOS_BATALLA = os.path.join(BASE_DIR, "imagenes", "Nivel4")
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
                if event.key == pygame.K_RETURN:
                    esperando = False
                elif event.key == pygame.K_ESCAPE:
                    action = pausar_juego(
                        screen,
                        devolver_accion=NIVEL_INTEGRADO,
                    )
                    if NIVEL_INTEGRADO and action in ("menu", "exit"):
                        raise NivelIntegradoFinalizado(nivel_completado, action)

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

            # Si el jugador toca el fuego, simplemente recibe daño
            if player.hurtbox.colliderect(self.hitbox):
                player.take_damage(20 * dt, attacker=self.hitbox)

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
        self.damage = 25

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
            and player.hurtbox.bottom > self.y
        ):
            player.take_damage(45 * dt)

    def draw(self, screen):
        if self.estado == "inactivo":
            return
        if self.estado == "advertencia":
            if int(pygame.time.get_ticks() / 160) % 2 == 0:
                pygame.draw.rect(screen, (80, 8, 4), (0, HEIGHT - 70, WIDTH, 70))
                pygame.draw.rect(
                    screen,
                    (255, 55, 10),
                    (0, HEIGHT - 70, WIDTH, 70),
                    3,
                )
                pygame.draw.line(
                    screen,
                    (255, 140, 30),
                    (0, HEIGHT - 65),
                    (WIDTH, HEIGHT - 65),
                    3,
                )
                texto = fuente_aviso.render(
                    "¡LAVA SUBIENDO! SALTA A LA PLATAFORMA",
                    True,
                    (255, 240, 190),
                )
                screen.blit(texto, texto.get_rect(center=(WIDTH // 2, HEIGHT - 35)))
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
    MAX_HEALTH = 300

    def __init__(self, boss):
        self.phase = 1
        boss.max_health = self.MAX_HEALTH
        boss.health = self.MAX_HEALTH
        self.platform = pygame.Rect(60, 360, WIDTH - 120, 22)
        self.lava = LavaAscendente(self.platform.top)
        self.projectiles = []
        self.hologram_event = None
        self.hologram_timer = 0.0
        self.phase_banner_timer = 0.0

        self.phase3_state = "cargando_derecha"
        self.phase3_timer = 0.0
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
        if NIVEL_INTEGRADO:
            mostrar_comic_segunda_barra()
        self.phase = 3
        self.phase_banner_timer = 1.5
        self._detener_fuego(zona_fuego)
        self.lava.disable()
        self._limpiar_hologramas()
        boss.max_health = self.MAX_HEALTH
        boss.health = self.MAX_HEALTH
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

        clone_image = crear_imagen_holograma(self._frame_muerte4(boss), alpha=210)
        start_x = player.hurtbox.centerx
        end_x = boss.rect.centerx
        self.execution_clones = []
        for index in range(4):
            x = round(start_x + (end_x - start_x) * (index + 1) / 5)
            surface = pygame.transform.scale(clone_image, (78, 105))
            rect = surface.get_rect(midbottom=(x, SUELO_Y))
            self.execution_clones.append(
                {"surface": surface, "rect": rect, "alive": True, "fade": 1.0}
            )

    def registrar_golpe(self, player, boss, zona_fuego):
        if not player.atacando or player.has_hit:
            return

        if self.phase in (1, 2):
            if player.hitbox.colliderect(boss.hurtbox):
                boss.take_damage(25)
                player.has_hit = True
                if self.phase == 1 and boss.health <= self.MAX_HEALTH * 0.5:
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
                player.take_damage(45, attacker=boss)
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
                player.take_damage(45, attacker=boss)
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
                player.take_damage(45, attacker=boss)
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
            ):
                y = (
                    SUELO_Y - 32
                    if self.phase3_state == "cargando_derecha"
                    else self.platform.top - 32
                )
                aviso = fuente_fase.render(
                    f"CARGANDO RAYO: {max(0, math.ceil(self.phase3_timer))}",
                    True,
                    (255, 210, 100),
                )
                screen.blit(aviso, aviso.get_rect(center=(boss.rect.centerx, y - 34)))
            elif self.phase3_state in (
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
            restantes = sum(clone["alive"] for clone in self.execution_clones)
            texto = fuente_aviso.render(
                f"ELIMINA LOS CLONES: {4 - restantes}/4",
                True,
                (255, 220, 180),
            )
            screen.blit(texto, texto.get_rect(center=(WIDTH // 2, 100)))

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
    fuente = pygame.font.SysFont("Arial", 16, bold=True)
    
    # Barra de vida del Jugador
    pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 20))
    pct_p = max(0, player.health / player.max_health)
    pygame.draw.rect(screen, (0, 220, 0), (20, 20, int(200 * pct_p), 20))
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20), 2)
    screen.blit(fuente.render(f"Jugador: {int(player.health)}", True, (255, 255, 255)), (20, 45))

    # Barra de vida del Jefe
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 320, 20, 300, 20))
    e_health = getattr(enemy, "health", 0)
    e_max_health = getattr(enemy, "max_health", 1)
    pct_e = max(0, e_health / e_max_health)
    pygame.draw.rect(screen, (220, 20, 20), (WIDTH - 320, 20, int(300 * pct_e), 20))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 320, 20, 300, 20), 2)
    phase_name = "Ejecucion final" if phase == 4 else f"Fase {phase}"
    screen.blit(
        fuente.render(f"Impaler Boss - {phase_name}: {int(e_health)}", True, (255, 255, 255)),
        (WIDTH - 320, 45),
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

running = True

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
                    raise NivelIntegradoFinalizado(nivel_completado, action)
            else:
                player.procesar_evento(event)
        else:
            player.procesar_evento(event)

    plataforma = batalla.platform if batalla.phase in (2, 3) else None
    player.plataformas = [plataforma] if plataforma is not None else []
    player.update(0, transicion_realizada=True)

    if batalla.phase in (1, 2):
        enemy.update(player, dt, width=WIDTH)
    elif batalla.phase == 3:
        batalla.update_boss_phase3(dt, player, enemy)
    elif batalla.final_death:
        enemy.update(player, dt, width=WIDTH)

    batalla.update(dt, player, enemy, zona_fuego)
    batalla.registrar_golpe(player, enemy, zona_fuego)
    enemy.esta_rojo = False

    if (
        batalla.phase in (1, 2)
        and getattr(enemy, "attacking", False)
        and not getattr(enemy, "has_hit", False)
    ):
        if hasattr(enemy, "hitbox") and enemy.hitbox.colliderect(player.hurtbox):
            player.take_damage(20, attacker=enemy)
            enemy.has_hit = True

    fondo_actual = (
        fondo_primera_barra
        if batalla.phase in (1, 2)
        else fondo_segunda_barra
    )
    screen.blit(fondo_actual, (0, 0))
    batalla.draw_stage(screen)
    pygame.draw.line(screen, (200, 200, 200), (0, SUELO_Y), (WIDTH, SUELO_Y), 4)

    enemy.draw(screen)
    screen.blit(player.image, player.rect)
    player.dibujar_barra_energia(screen)
    if batalla.phase == 1:
        zona_fuego.draw(screen)
    batalla.draw_effects(screen, enemy)
    dibujar_barras_vida(screen, player, enemy, batalla.phase)

    pygame.display.flip()

    if getattr(enemy, "muerto_definitivo", False):
        nivel_completado = True
        running = False

if not NIVEL_INTEGRADO:
    pygame.quit()