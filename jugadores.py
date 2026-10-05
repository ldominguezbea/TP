import pygame
import os


class p_viento(pygame.sprite.Sprite):

    def __init__(
        self,
        x,
        y,
        posicion_suelo
    ):

        super().__init__()

        # ====================================================
        # CONFIGURACIÓN DEL PERSONAJE
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

        self.image = self.animaciones[
            self.estado
        ][0]

        self.rect = self.image.get_rect(
            midbottom=(x, y)
        )

        # Posición real dentro del mundo
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
        # ESTADOS
        # ====================================================

        self.mirando_derecha = True

        self.en_suelo = True

        self.rodando = False
        self.defendiendo = False
        self.atacando = False

        self.combo_siguiente = False

    # ========================================================
    # CARGAR ANIMACIONES
    # ========================================================

    def cargar_animaciones(self):

        escala = (
            self.ancho_heroe,
            self.alto_heroe
        )

        base_path = os.path.join(
            "assets",
            "Heroes",
            "P_viento"
        )

        # ----------------------------------------------------
        # IDLE
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "idle",
                    f"idle_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["idle"].append(img)

        # ----------------------------------------------------
        # RUN
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "run",
                    f"run_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["run"].append(img)

        # ----------------------------------------------------
        # ROLL
        # ----------------------------------------------------

        for i in range(1, 7):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "roll",
                    f"roll_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["roll"].append(img)

        # ----------------------------------------------------
        # SALTO
        # ----------------------------------------------------

        for i in range(1, 4):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "j_up",
                    f"j_up_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["j_up"].append(img)

        # ----------------------------------------------------
        # DEFENSA
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "defend",
                    f"defend_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["defend"].append(img)

        # ----------------------------------------------------
        # ATAQUE 1
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "1_atk",
                    f"1_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["1_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE 2
        # ----------------------------------------------------

        for i in range(1, 19):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "2_atk",
                    f"2_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["2_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE AÉREO
        # ----------------------------------------------------

        for i in range(1, 8):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "air_atk",
                    f"air_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["air_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE ESPECIAL
        # ----------------------------------------------------

        for i in range(1, 31):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "sp_atk",
                    f"sp_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["sp_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE 3
        # ----------------------------------------------------

        for i in range(12, 27):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "3_atk",
                    f"3_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["3_atk"].append(img)

    # ========================================================
    # EVENTOS DEL JUGADOR
    # ========================================================

    def procesar_evento(self, evento):

        if evento.type != pygame.KEYDOWN:
            return

        # ====================================================
        # SALTO - W
        # ====================================================

        if (
            evento.key == pygame.K_w
            and self.en_suelo
            and not (
                self.atacando
                or self.rodando
                or self.defendiendo
            )
        ):

            self.velocidad_y = self.fuerza_salto
            self.en_suelo = False

        # ====================================================
        # RODAR - Q
        # ====================================================

        elif (
            evento.key == pygame.K_q
            and self.en_suelo
            and not (
                self.rodando
                or self.atacando
                or self.defendiendo
            )
        ):

            self.rodando = True
            self.frame_index = 0

        # ====================================================
        # DEFENDER - R
        # ====================================================

        elif (
            evento.key == pygame.K_r
            and self.en_suelo
            and not (
                self.rodando
                or self.atacando
                or self.defendiendo
            )
        ):

            self.defendiendo = True
            self.frame_index = 0

        # ====================================================
        # ATAQUE ESPECIAL - E
        # ====================================================

        elif (
            evento.key == pygame.K_e
            and self.en_suelo
            and not (
                self.rodando
                or self.atacando
                or self.defendiendo
            )
        ):

            self.atacando = True
            self.estado = "sp_atk"
            self.frame_index = 0

        # ====================================================
        # ATAQUE - F
        # ====================================================

        elif evento.key == pygame.K_f:

            # ------------------------------------------------
            # ATAQUE AÉREO
            # ------------------------------------------------

            if (
                not self.en_suelo
                and not self.atacando
            ):

                self.atacando = True
                self.estado = "air_atk"
                self.frame_index = 0

            # ------------------------------------------------
            # ATAQUE TERRESTRE
            # ------------------------------------------------

            elif (
                self.en_suelo
                and not (
                    self.rodando
                    or self.defendiendo
                )
            ):

                if not self.atacando:

                    self.atacando = True
                    self.estado = "1_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False

                elif self.estado in [
                    "1_atk",
                    "2_atk"
                ]:

                    self.combo_siguiente = True

    # ========================================================
    # MOVIMIENTO CONTINUO
    # ========================================================

    def manejar_movimiento_continuo(self):

        teclas = pygame.key.get_pressed()

        # Bloquear movimiento durante acciones
        if (
            self.rodando
            or self.defendiendo
            or (
                self.atacando
                and self.en_suelo
            )
        ):

            self.velocidad_x = 0
            return

        self.velocidad_x = 0

        # ----------------------------------------------------
        # IZQUIERDA - A
        # ----------------------------------------------------

        if teclas[pygame.K_a]:

            self.velocidad_x = -self.velocidad_movimiento
            self.mirando_derecha = False

        # ----------------------------------------------------
        # DERECHA - D
        # ----------------------------------------------------

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
    # ANIMAR
    # ========================================================

    def animar(self):

        anim = self.animaciones[self.estado]

        self.frame_index += self.velocidad_animacion

        # ----------------------------------------------------
        # FINAL DE ANIMACIÓN
        # ----------------------------------------------------

        if self.frame_index >= len(anim):

            self.frame_index = 0

            # Roll
            if self.rodando:

                self.rodando = False

            # Defensa
            elif self.defendiendo:

                self.defendiendo = False

            # Ataques que terminan
            elif self.estado in [
                "air_atk",
                "sp_atk",
                "3_atk"
            ]:

                self.atacando = False

            # Ataque 1
            elif self.estado == "1_atk":

                if self.combo_siguiente:

                    self.estado = "2_atk"
                    self.combo_siguiente = False

                else:

                    self.atacando = False

            # Ataque 2
            elif self.estado == "2_atk":

                if self.combo_siguiente:

                    self.estado = "3_atk"
                    self.combo_siguiente = False

                else:

                    self.atacando = False

        # ----------------------------------------------------
        # FRAME ACTUAL
        # ----------------------------------------------------

        frame_actual = anim[
            int(self.frame_index)
        ]

        # Girar personaje
        if not self.mirando_derecha:

            self.image = pygame.transform.flip(
                frame_actual,
                True,
                False
            )

        else:

            self.image = frame_actual

    # ========================================================
    # GRAVEDAD
    # ========================================================

    def aplicar_gravedad(self):

        self.velocidad_y += self.gravedad

        self.rect.y += self.velocidad_y

        # ----------------------------------------------------
        # SUELO
        # ----------------------------------------------------

        if self.rect.bottom >= self.posicion_suelo:

            self.rect.bottom = self.posicion_suelo

            self.velocidad_y = 0
            self.en_suelo = True

    # ========================================================
    # ACTUALIZAR JUGADOR
    # ========================================================

    def update(
        self,
        scroll_x,
        ancho_mundo
    ):

        self.manejar_movimiento_continuo()

        # ----------------------------------------------------
        # VELOCIDAD AL RODAR
        # ----------------------------------------------------

        if self.rodando:

            self.velocidad_x = (
                self.velocidad_movimiento + 3
            ) * (
                1
                if self.mirando_derecha
                else -1
            )

        # ----------------------------------------------------
        # POSICIÓN GLOBAL
        # ----------------------------------------------------

        self.pos_x += self.velocidad_x

        # ----------------------------------------------------
        # LÍMITES DEL MUNDO
        # ----------------------------------------------------

        limite_izquierdo = scroll_x + 80

        self.pos_x = max(
            limite_izquierdo,
            min(
                self.pos_x,
                ancho_mundo - 80
            )
        )

        # ----------------------------------------------------
        # POSICIÓN EN PANTALLA
        # ----------------------------------------------------

        self.rect.centerx = int(
            self.pos_x - scroll_x
        )

        # ----------------------------------------------------
        # FÍSICA
        # ----------------------------------------------------

        self.aplicar_gravedad()

        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------

        self.actualizar_estado()

        # ----------------------------------------------------
        # ANIMACIÓN
        # ----------------------------------------------------

        self.animar()
