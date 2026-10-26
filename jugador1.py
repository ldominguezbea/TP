
import pygame
import os


class p_viento(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo):
        super().__init__()

        self.ancho_heroe = 600
        self.alto_heroe = 240
        self.posicion_suelo = posicion_suelo

        self.animaciones = {
            "idle": [], "run": [], "roll": [], "j_up": [],
            "defend": [], "1_atk": [], "2_atk": [], "3_atk": [],
            "air_atk": [], "sp_atk": []
        }

        self.cargar_animaciones()

        self.estado = "idle"
        self.frame_index = 0
        self.velocidad_animacion = 0.22

        self.image = self.animaciones["idle"][0]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.pos_x = float(x)

        # Vida y combate
        self.health = 100
        self.max_health = 100
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.hurtbox = pygame.Rect(0, 0, 0, 0)
        self.has_hit = False

        # Física
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.velocidad_movimiento = 7
        self.fuerza_salto = -16
        self.gravedad = 0.8

        self.plataformas = []
        self.scroll_x_actual = 0

        # Estados
        self.mirando_derecha = True
        self.en_suelo = True
        self.rodando = False
        self.defendiendo = False
        self.atacando = False
        self.combo_siguiente = False

    # =========================================================
    # ANIMACIONES
    # =========================================================

    def cargar_animaciones(self):
        escala = (self.ancho_heroe, self.alto_heroe)
        base_path = os.path.join("assets", "Heroes", "P_viento")

        secuencias = {
            "idle": range(1, 9),
            "run": range(1, 9),
            "roll": range(1, 7),
            "j_up": range(1, 4),
            "defend": range(1, 9),
            "1_atk": range(1, 9),
            "2_atk": range(7, 19),
            "3_atk": range(12, 27),
            "air_atk": range(1, 8),
            "sp_atk": range(1, 31),
        }

        for carpeta, frames in secuencias.items():
            for i in frames:
                ruta = os.path.join(
                    base_path, carpeta, f"{carpeta}_{i}.png"
                )

                try:
                    img = pygame.image.load(ruta).convert_alpha()
                    img = pygame.transform.scale(img, escala)
                    self.animaciones[carpeta].append(img)
                except (pygame.error, FileNotFoundError) as e:
                    raise RuntimeError(
                        f"No se pudo cargar la animación: {ruta}"
                    ) from e

    # =========================================================
    # EVENTOS Y CONTROLES
    # =========================================================

    def procesar_evento(self, evento):
        if evento.type not in (
            pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN
        ):
            return

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_w
            and self.en_suelo
            and not (
                self.atacando or self.rodando or self.defendiendo
            )
        ):
            self.velocidad_y = self.fuerza_salto
            self.en_suelo = False

        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_q
            and self.en_suelo
            and not (
                self.rodando or self.atacando or self.defendiendo
            )
        ):
            self.rodando = True
            self.frame_index = 0

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_RIGHT
            and self.en_suelo
            and not (
                self.rodando or self.atacando or self.defendiendo
            )
        ):
            self.defendiendo = True
            self.frame_index = 0

        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_e
            and self.en_suelo
            and not (
                self.rodando or self.atacando or self.defendiendo
            )
        ):
            self.atacando = True
            self.has_hit = False
            self.estado = "sp_atk"
            self.frame_index = 0

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_LEFT
        ):
            if not self.en_suelo and not self.atacando:
                self.atacando = True
                self.has_hit = False
                self.estado = "air_atk"
                self.frame_index = 0

            elif (
                self.en_suelo
                and not (self.rodando or self.defendiendo)
            ):
                if not self.atacando:
                    self.atacando = True
                    self.has_hit = False
                    self.estado = "1_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False

                elif self.estado in ("1_atk", "2_atk"):
                    self.combo_siguiente = True

    # =========================================================
    # MOVIMIENTO
    # =========================================================

    def manejar_movimiento_continuo(self):
        teclas = pygame.key.get_pressed()

        if (
            self.rodando
            or self.defendiendo
            or (self.atacando and self.en_suelo)
        ):
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

    # =========================================================
    # ANIMACIÓN Y COMBOS
    # =========================================================

    def animar(self):
        anim = self.animaciones[self.estado]

        self.frame_index += self.velocidad_animacion

        if self.frame_index >= len(anim):
            self.frame_index = 0

            if self.rodando:
                self.rodando = False

            elif self.defendiendo:
                self.defendiendo = False

            elif self.estado in ("air_atk", "sp_atk", "3_atk"):
                self.atacando = False

            elif self.estado == "1_atk":
                if self.combo_siguiente:
                    self.estado = "2_atk"
                    self.has_hit = False
                    self.combo_siguiente = False
                else:
                    self.atacando = False

            elif self.estado == "2_atk":
                if self.combo_siguiente:
                    self.estado = "3_atk"
                    self.has_hit = False
                    self.combo_siguiente = False
                else:
                    self.atacando = False

        frame_actual = anim[int(self.frame_index)]

        if self.mirando_derecha:
            self.image = frame_actual
        else:
            self.image = pygame.transform.flip(
                frame_actual, True, False
            )

    # =========================================================
    # HITBOXES
    # =========================================================

    def actualizar_hitboxes(self):
        self.hurtbox = pygame.Rect(0, 0, 60, 100)
        self.hurtbox.midbottom = self.rect.midbottom

        if not self.atacando:
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            return

        if self.estado == "sp_atk":
            ancho, alto = 140, 60
        else:
            ancho, alto = 110, 45

        y = self.rect.bottom - alto - 10

        if self.mirando_derecha:
            self.hitbox = pygame.Rect(
                self.rect.centerx + 10, y, ancho, alto
            )
        else:
            self.hitbox = pygame.Rect(
                self.rect.centerx - 10 - ancho, y, ancho, alto
            )

    # =========================================================
    # DAÑO RECIBIDO
    # =========================================================

    def take_damage(self, damage):
        if self.rodando or (
            self.atacando and self.estado == "sp_atk"
        ):
            return

        self.health = max(0, self.health - damage)

    # =========================================================
    # GRAVEDAD Y PLATAFORMAS
    # =========================================================

    def aplicar_gravedad(self):
        bottom_anterior = self.rect.bottom

        self.en_suelo = False
        self.velocidad_y += self.gravedad
        self.rect.y += self.velocidad_y

        if self.velocidad_y >= 0:
            for plataforma in self.plataformas:
                rect_plataforma = plataforma.move(
                    -self.scroll_x_actual, 0
                )
                zona = rect_plataforma.inflate(-20, 0)

                pisa = (
                    bottom_anterior <= zona.top
                    and self.rect.bottom >= zona.top
                    and self.rect.centerx + 30 > zona.left
                    and self.rect.centerx - 30 < zona.right
                )

                if pisa:
                    self.rect.bottom = zona.top
                    self.velocidad_y = 0
                    self.en_suelo = True
                    break

        if (
            not self.en_suelo
            and self.rect.bottom >= self.posicion_suelo
        ):
            self.rect.bottom = self.posicion_suelo
            self.velocidad_y = 0
            self.en_suelo = True

    # =========================================================
    # UPDATE COMPATIBLE CON NIVEL1.PY
    # =========================================================

    def update(
        self,
        scroll_x=0,
        transicion_realizada=False,
        limite_max_x=None,
        ancho_mundo=None
    ):
        self.scroll_x_actual = scroll_x
        self.manejar_movimiento_continuo()

        if self.rodando:
            self.velocidad_x = (
                self.velocidad_movimiento + 3
            ) * (1 if self.mirando_derecha else -1)

        self.pos_x += self.velocidad_x

        if ancho_mundo is None:
            ancho_mundo = globals().get("ANCHO_MUNDO", 10000)

        if limite_max_x is None:
            limite_max_x = ancho_mundo - 80

        limite_izquierdo = scroll_x + 80

        if transicion_realizada and scroll_x == 0:
            limite_izquierdo = 80
            limite_derecho = globals().get("ANCHO", 1350) - 80
        elif transicion_realizada:
            limite_derecho = ancho_mundo - 80
        else:
            limite_derecho = limite_max_x

        self.pos_x = max(
            limite_izquierdo,
            min(self.pos_x, limite_derecho)
        )

        self.rect.centerx = int(self.pos_x - scroll_x)

        self.aplicar_gravedad()
        self.actualizar_estado()
        self.animar()
        self.actualizar_hitboxes()
