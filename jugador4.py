import pygame
import os
# ============================================================
# RUTAS DE RECURSOS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_PLANTA = os.path.join(
    BASE_DIR,
    "assets",
    "Heroes",
    "P_planta"
)

BASE_EFECTOS = os.path.join(
    BASE_PLANTA,
    "projectiles_and_effects"
)


# ============================================================
# FLECHA AÉREA: IMPACTA CONTRA EL SUELO
# ============================================================

class FlechaAerea(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo, mirando_derecha):

        super().__init__()

        self.posicion_suelo = posicion_suelo
        self.mirando_derecha = mirando_derecha

        self.pos_x = float(x)
        self.pos_y = float(y)

        self.velocidad_x = 7 if mirando_derecha else -7
        self.velocidad_y = 4
        self.gravedad = 0.35

        self.estado = "flecha"
        self.frame_index = 0
        self.velocidad_animacion = 0.25

        ruta_flecha = os.path.join(
            BASE_EFECTOS,
            "arrow",
            "arrow_.png"
        )

        ruta_hit = os.path.join(
            BASE_EFECTOS,
            "diagonal_arrow_hit"
        )

        self.image = pygame.image.load(
            ruta_flecha
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (120, 120)
        )

        if not mirando_derecha:
            self.image = pygame.transform.flip(
                self.image,
                True,
                False
            )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.animacion_hit = []

        for i in range(1, 7):

            ruta = os.path.join(
                ruta_hit,
                f"diagonal_arrow_hit_{i}.png"
            )

            imagen = pygame.image.load(
                ruta
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (180, 180)
            )

            self.animacion_hit.append(imagen)

    def update(self, scroll_x=0):

        if self.estado == "flecha":

            self.pos_x += self.velocidad_x
            self.pos_y += self.velocidad_y

            self.velocidad_y += self.gravedad

            self.rect.centerx = int(
                self.pos_x - scroll_x
            )

            self.rect.centery = int(self.pos_y)

            # Impacto contra el suelo.

            if self.rect.bottom >= self.posicion_suelo:

                centro_x = self.rect.centerx

                self.estado = "hit"
                self.frame_index = 0

                self.image = self.animacion_hit[0]

                self.rect = self.image.get_rect(
                    midbottom=(
                        centro_x,
                        self.posicion_suelo
                    )
                )

        elif self.estado == "hit":

            self.frame_index += self.velocidad_animacion

            if self.frame_index >= len(self.animacion_hit):
                self.kill()
                return

            centro_x = self.rect.centerx

            self.image = self.animacion_hit[
                int(self.frame_index)
            ]

            self.rect = self.image.get_rect(
                midbottom=(
                    centro_x,
                    self.posicion_suelo
                )
            )


# ============================================================
# FLECHA HORIZONTAL: IMPACTA CONTRA LA PARED
# ============================================================

class FlechaHorizontal(pygame.sprite.Sprite):

    def __init__(
        self,
        x,
        y,
        mirando_derecha,
        ancho_mundo
    ):

        super().__init__()

        self.mirando_derecha = mirando_derecha
        self.ancho_mundo = ancho_mundo

        self.pos_x = float(x)
        self.pos_y = float(y)

        self.velocidad_x = 12 if mirando_derecha else -12

        self.estado = "flecha"
        self.frame_index = 0
        self.velocidad_animacion = 0.25

        ruta_flecha = os.path.join(
            BASE_EFECTOS,
            "arrow",
            "arrow_.png"
        )

        ruta_hit = os.path.join(
            BASE_EFECTOS,
            "arrow_hit"
        )

        self.image = pygame.image.load(
            ruta_flecha
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (120, 120)
        )

        if not mirando_derecha:
            self.image = pygame.transform.flip(
                self.image,
                True,
                False
            )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.animacion_hit = []

        for i in range(1, 7):

            ruta = os.path.join(
                ruta_hit,
                f"arrow_hit_{i}.png"
            )

            imagen = pygame.image.load(
                ruta
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (180, 180)
            )

            self.animacion_hit.append(imagen)

    def update(self, scroll_x=0):

        if self.estado == "flecha":

            # Movimiento horizontal sin gravedad.

            self.pos_x += self.velocidad_x

            self.rect.centerx = int(
                self.pos_x - scroll_x
            )

            self.rect.centery = int(self.pos_y)

            # Pared derecha del mundo.

            if self.mirando_derecha:

                if self.pos_x + self.rect.width / 2 >= self.ancho_mundo:

                    self.pos_x = (
                        self.ancho_mundo
                        - self.rect.width / 2
                    )

                    self.iniciar_impacto(scroll_x)

            # Pared izquierda del mundo.

            else:

                if self.pos_x - self.rect.width / 2 <= 0:

                    self.pos_x = self.rect.width / 2

                    self.iniciar_impacto(scroll_x)

        elif self.estado == "hit":

            self.frame_index += self.velocidad_animacion

            if self.frame_index >= len(self.animacion_hit):
                self.kill()
                return

            centro_x = self.rect.centerx
            centro_y = self.rect.centery

            self.image = self.animacion_hit[
                int(self.frame_index)
            ]

            self.rect = self.image.get_rect(
                center=(centro_x, centro_y)
            )

    def iniciar_impacto(self, scroll_x=0):

        self.estado = "hit"
        self.frame_index = 0

        centro_x = int(self.pos_x - scroll_x)
        centro_y = int(self.pos_y)

        self.image = self.animacion_hit[0]

        self.rect = self.image.get_rect(
            center=(centro_x, centro_y)
        )


# ============================================================
# RÁFAGA DEL TERCER ATAQUE
# UNA SOLA ANIMACIÓN DE SEIS FOTOGRAMAS
# ============================================================

class RafagaFlechas(pygame.sprite.Sprite):

    def __init__(
        self,
        x,
        posicion_suelo,
        mirando_derecha
    ):

        super().__init__()

        self.pos_x = float(x)
        self.posicion_suelo = posicion_suelo
        self.mirando_derecha = mirando_derecha

        self.frame_index = 0
        self.velocidad_animacion = 0.25

        # ----------------------------------------------------
        # CARGAR LOS SEIS FOTOGRAMAS
        # ----------------------------------------------------

        ruta_animacion = os.path.join(
            BASE_EFECTOS,
            "arrow_shower_effect"
        )

        self.animacion = []

        for i in range(1, 7):

            ruta = os.path.join(
                ruta_animacion,
                f"arrow_shower_effect_{i}.png"
            )

            imagen = pygame.image.load(
                ruta
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                (300, 220)
            )

            if not mirando_derecha:

                imagen = pygame.transform.flip(
                    imagen,
                    True,
                    False
                )

            self.animacion.append(imagen)

        self.image = self.animacion[0]

        # El borde inferior queda sobre el suelo.

        self.rect = self.image.get_rect(
            midbottom=(
                int(self.pos_x),
                self.posicion_suelo
            )
        )

    def update(self, scroll_x=0):

        self.frame_index += self.velocidad_animacion

        # La animación se reproduce una sola vez.

        if self.frame_index >= len(self.animacion):

            self.kill()
            return

        centro_x = int(self.pos_x - scroll_x)

        self.image = self.animacion[
            int(self.frame_index)
        ]

        # Mantener todos los fotogramas apoyados en el suelo.

        self.rect = self.image.get_rect(
            midbottom=(
                centro_x,
                self.posicion_suelo
            )
        )



class p_planta(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo):
        super().__init__()

        # ====================================================
        # CONFIGURACIÓN
        # ====================================================

        self.ancho_heroe = 600
        self.alto_heroe = 240
        self.posicion_suelo = posicion_suelo

        # ====================================================
        # ANIMACIONES
        # ====================================================

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

        # ====================================================
        # ESTADO
        # ====================================================

        self.estado = "idle"
        self.frame_index = 0
        self.velocidad_animacion = 0.22

        self.image = self.animaciones["idle"][0]
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.pos_x = float(x)

        # ====================================================
        # FÍSICA
        # ====================================================

        self.velocidad_x = 0
        self.velocidad_y = 0

        self.velocidad_movimiento = 7
        self.fuerza_salto = -16
        self.gravedad = 0.8

        # ====================================================
        # ESTADOS DEL PERSONAJE
        # ====================================================

        self.mirando_derecha = True
        self.en_suelo = True
        self.rodando = False
        self.defendiendo = False
        self.atacando = False
        self.combo_siguiente = False

        # ====================================================
        # RAFAGA DEL TERCER ATAQUE
        # ====================================================

        self.frame_rafaga = 8
        self.rafaga_creada = False

        # ====================================================
        # PROYECTILES
        # ====================================================

        self.proyectiles = pygame.sprite.Group()

    # ========================================================
    # CARGAR ANIMACIONES
    # ========================================================

    def cargar_animaciones(self):

        escala = (self.ancho_heroe, self.alto_heroe)

        base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "Heroes",
            "P_planta"
        )

        configuracion = {
            "idle": ("idle", "idle", 12),
            "run": ("run", "run", 10),
            "roll": ("roll", "roll", 8),
            "j_up": ("j_up", "jump_up", 3),
            "defend": ("defend", "defend", 19),
            "1_atk": ("1_atk", "1_atk", 10),
            "2_atk": ("2_atk", "2_atk", 15),
            "3_atk": ("3_atk", "3_atk", 12),
            "air_atk": ("air_atk", "air_atk", 10),
            "sp_atk": ("sp_atk", "sp_atk", 17)
        }

        for estado, (carpeta, prefijo, cantidad) in configuracion.items():

            for i in range(1, cantidad + 1):

                ruta = os.path.join(
                    base_path,
                    carpeta,
                    f"{prefijo}_{i}.png"
                )

                imagen = pygame.image.load(ruta).convert_alpha()
                imagen = pygame.transform.scale(imagen, escala)

                self.animaciones[estado].append(imagen)

    # ========================================================
    # PROCESAR EVENTOS
    # ========================================================

    def procesar_evento(self, evento):

        if evento.type not in (
            pygame.KEYDOWN,
            pygame.MOUSEBUTTONDOWN
        ):
            return

        # SALTO: W
        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_w
            and self.en_suelo
            and not (self.atacando or self.rodando or self.defendiendo)
        ):
            self.velocidad_y = self.fuerza_salto
            self.en_suelo = False

        # RODAR: Q
        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_q
            and self.en_suelo
            and not (self.rodando or self.atacando or self.defendiendo)
        ):
            self.rodando = True
            self.frame_index = 0

        # DEFENSA: CLIC DERECHO
        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_RIGHT
            and self.en_suelo
            and not (self.rodando or self.atacando or self.defendiendo)
        ):
            self.defendiendo = True
            self.frame_index = 0

        # ATAQUE ESPECIAL: E
        elif (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_e
            and self.en_suelo
            and not (self.rodando or self.atacando or self.defendiendo)
        ):
            self.atacando = True
            self.estado = "sp_atk"
            self.frame_index = 0

        # ATAQUES: CLIC IZQUIERDO
        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_LEFT
        ):

            # ATAQUE AÉREO
            if not self.en_suelo and not self.atacando:

                self.atacando = True
                self.estado = "air_atk"
                self.frame_index = 0

                flecha = FlechaAerea(
                    self.pos_x,
                    self.rect.centery,
                    self.posicion_suelo,
                    self.mirando_derecha
                )

                self.proyectiles.add(flecha)

            # ATAQUE TERRESTRE Y COMBOS
            elif (
                self.en_suelo
                and not (self.rodando or self.defendiendo)
            ):

                if not self.atacando:

                    self.atacando = True
                    self.estado = "1_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False

                elif self.estado in ("1_atk", "2_atk"):

                    self.combo_siguiente = True

    # ========================================================
    # MOVIMIENTO CONTINUO
    # ========================================================

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
    # ANIMAR Y GENERAR RAFAGA EN EL FRAME 8
    # ========================================================

    def animar(self):

        anim = self.animaciones[self.estado]

        # ----------------------------------------------------
        # GENERAR LA RAFAGA UNA SOLA VEZ EN EL OCTAVO FRAME
        # ----------------------------------------------------

        if (
            self.estado == "3_atk"
            and int(self.frame_index) + 1 >= self.frame_rafaga
            and not self.rafaga_creada
        ):

            self.rafaga_creada = True

            distancia = 300

            x_rafaga = (
                self.pos_x + distancia
                if self.mirando_derecha
                else self.pos_x - distancia
            )

            rafaga = RafagaFlechas(
                x_rafaga,
                self.posicion_suelo,
                self.mirando_derecha
            )

            self.proyectiles.add(rafaga)

        # ----------------------------------------------------
        # AVANZAR ANIMACIÓN
        # ----------------------------------------------------

        self.frame_index += self.velocidad_animacion

        if self.frame_index >= len(anim):

            # ROLL
            if self.rodando:
                self.rodando = False

            # DEFENSA
            elif self.defendiendo:
                self.defendiendo = False

            # ATAQUES QUE TERMINAN
            elif self.estado in ("air_atk", "sp_atk", "3_atk"):
                self.atacando = False

            # ATAQUE 1
            elif self.estado == "1_atk":

                if self.combo_siguiente:
                    self.estado = "2_atk"
                    self.combo_siguiente = False
                else:
                    self.atacando = False

            # ATAQUE 2
            elif self.estado == "2_atk":

                if self.combo_siguiente:
                    self.estado = "3_atk"
                    self.frame_index = 0
                    self.rafaga_creada = False
                    self.combo_siguiente = False
                else:
                    self.atacando = False

            self.frame_index = 0

            anim = self.animaciones[self.estado]

        # ----------------------------------------------------
        # MOSTRAR FRAME ACTUAL
        # ----------------------------------------------------

        frame_actual = anim[int(self.frame_index)]

        if not self.mirando_derecha:
            self.image = pygame.transform.flip(
                frame_actual,
                True,
                False
            )
        else:
            self.image = frame_actual

    # ========================================================
    # APLICAR GRAVEDAD
    # ========================================================

    def aplicar_gravedad(self):

        self.velocidad_y += self.gravedad
        self.rect.y += self.velocidad_y

        if self.rect.bottom >= self.posicion_suelo:

            self.rect.bottom = self.posicion_suelo
            self.velocidad_y = 0
            self.en_suelo = True

        else:
            self.en_suelo = False

    # ========================================================
    # ACTUALIZAR JUGADOR
    # ========================================================

    def update(self, scroll_x, ancho_mundo):

        self.manejar_movimiento_continuo()

        if self.rodando:

            self.velocidad_x = (
                self.velocidad_movimiento + 3
            ) * (1 if self.mirando_derecha else -1)

        self.pos_x += self.velocidad_x

        limite_izquierdo = scroll_x + 80

        self.pos_x = max(
            limite_izquierdo,
            min(self.pos_x, ancho_mundo - 80)
        )

        self.rect.centerx = int(self.pos_x - scroll_x)

        self.aplicar_gravedad()
        self.actualizar_estado()
        self.animar()

        # Actualizar proyectiles
        self.proyectiles.update(scroll_x)