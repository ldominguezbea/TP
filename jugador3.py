
import pygame
import os


class p_fuego(pygame.sprite.Sprite):

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
        # VIDA Y DAÑO
        # ====================================================

        self.vida_maxima = 100
        self.vida = 100

        self.muerto = False
        self.muerte_terminada = False

        self.recibiendo_dano = False
        self.inmune_dano = False

        self.tiempo_ultimo_dano = 0
        self.duracion_inmunidad = 500

        # ====================================================
        # HITBOX Y HURTBOX
        # ====================================================

        self.hurtbox = pygame.Rect(0, 0, 60, 100)
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.dano_ataque_1 = 15
        self.golpe_aplicado = False

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
            "sp_atk": [],
            "10_take_hit": [],
            "11_death": []
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

        self.actualizar_hurtbox()

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
            "P_fuego",
            "p_fuego"
        )

        # ----------------------------------------------------
        # IDLE: 8 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "idle",
                    f"idle_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["idle"].append(img)

        # ----------------------------------------------------
        # RUN: 8 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "run",
                    f"run_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["run"].append(img)

        # ----------------------------------------------------
        # ROLL: 8 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "roll",
                    f"roll_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["roll"].append(img)

        # ----------------------------------------------------
        # SALTO: 3 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 4):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "j_up",
                    f"jump_up_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["j_up"].append(img)

        # ----------------------------------------------------
        # DEFENSA: 8 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "defend",
                    f"defend_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["defend"].append(img)

        # ----------------------------------------------------
        # ATAQUE 1: 11 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 12):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "1_atk",
                    f"1_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["1_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE 2: IMÁGENES 9 A 19
        # ----------------------------------------------------

        for i in range(9, 20):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "2_atk",
                    f"2_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["2_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE AÉREO: 8 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "air_atk",
                    f"air_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["air_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE ESPECIAL: 18 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 19):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "sp_atk",
                    f"sp_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["sp_atk"].append(img)

        # ----------------------------------------------------
        # ATAQUE 3: IMÁGENES 20 A 28
        # ----------------------------------------------------

        for i in range(20, 29):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "3_atk",
                    f"3_atk_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["3_atk"].append(img)

        # ----------------------------------------------------
        # RECIBIR DAÑO: 6 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 7):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "10_take_hit",
                    f"take_hit_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["10_take_hit"].append(img)

        # ----------------------------------------------------
        # MUERTE: 19 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 14):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "11_death",
                    f"death_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(img, escala)

            self.animaciones["11_death"].append(img)

    # ========================================================
    # HURTBOX
    # ========================================================

    def actualizar_hurtbox(self):

        self.hurtbox.width = 60
        self.hurtbox.height = 100

        self.hurtbox.midbottom = self.rect.midbottom

    def dibujar_hurtbox(self, pantalla, scroll_x=0):

        hurtbox_pantalla = self.hurtbox.copy()
        hurtbox_pantalla.x -= scroll_x

        pygame.draw.rect(
            pantalla,
            (0, 255, 0),
            hurtbox_pantalla,
            2
        )

    # ========================================================
    # RECIBIR DAÑO
    # ========================================================

    def recibir_dano(self, cantidad):

        if self.muerto or self.recibiendo_dano:
            return

        if (
            self.rodando
            or self.defendiendo
            or self.inmune_dano
        ):
            return

        self.vida = max(
            0,
            self.vida - cantidad
        )

        self.inmune_dano = True
        self.tiempo_ultimo_dano = pygame.time.get_ticks()

        self.velocidad_x = 0

        self.atacando = False
        self.combo_siguiente = False
        self.rodando = False
        self.defendiendo = False

        self.frame_index = 0

        if self.vida <= 0:

            self.muerto = True
            self.recibiendo_dano = False
            self.estado = "11_death"

        else:

            self.recibiendo_dano = True
            self.estado = "take_hit"

    # ========================================================
    # HITBOX DEL PRIMER ATAQUE
    # ========================================================

    def actualizar_hitbox(self):

        self.hitbox = pygame.Rect(0, 0, 0, 0)

        if (
            self.estado != "1_atk"
            or not self.atacando
        ):
            return

        if self.frame_index < 3:

            if self.mirando_derecha:

                self.hitbox = pygame.Rect(
                    self.hurtbox.right - 5,
                    self.hurtbox.centery - 10,
                    80,
                    30
                )

            else:

                self.hitbox = pygame.Rect(
                    self.hurtbox.left - 75,
                    self.hurtbox.centery - 10,
                    80,
                    30
                )

    def dibujar_hitbox(self, pantalla, scroll_x=0):

        if self.hitbox.width > 0 and self.hitbox.height > 0:

            hitbox_pantalla = self.hitbox.copy()
            hitbox_pantalla.x -= scroll_x

            pygame.draw.rect(
                pantalla,
                (255, 0, 0),
                hitbox_pantalla,
                2
            )

    def comprobar_golpe(self, enemigo):

        if self.golpe_aplicado or self.hitbox.width <= 0:
            return

        hurtbox_enemigo = getattr(
            enemigo,
            "hurtbox",
            getattr(enemigo, "rect", None)
        )

        if hurtbox_enemigo is None:
            return

        if self.hitbox.colliderect(hurtbox_enemigo):

            if hasattr(enemigo, "recibir_dano"):

                enemigo.recibir_dano(
                    self.dano_ataque_1
                )

            elif hasattr(enemigo, "take_damage"):

                enemigo.take_damage(
                    self.dano_ataque_1
                )

            elif hasattr(enemigo, "vida"):

                enemigo.vida = max(
                    0,
                    enemigo.vida - self.dano_ataque_1
                )

            self.golpe_aplicado = True

    # ========================================================
    # EVENTOS DEL JUGADOR
    # ========================================================

    def procesar_evento(self, evento):

        if self.muerto or self.recibiendo_dano:
            return

        if evento.type not in (
            pygame.KEYDOWN,
            pygame.MOUSEBUTTONDOWN
        ):
            return

        # ====================================================
        # SALTO - W
        # ====================================================

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_w
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
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_q
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
        # DEFENDER - CLICK DERECHO
        # ====================================================

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_RIGHT
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
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_e
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
        # ATAQUE - CLICK IZQUIERDO
        # ====================================================

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_LEFT
        ):

            # ATAQUE AÉREO

            if (
                not self.en_suelo
                and not self.atacando
            ):

                self.atacando = True
                self.estado = "air_atk"
                self.frame_index = 0

            # ATAQUE TERRESTRE

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
                    self.golpe_aplicado = False

                elif self.estado in (
                    "1_atk",
                    "2_atk"
                ):

                    self.combo_siguiente = True

    # ========================================================
    # MOVIMIENTO CONTINUO
    # ========================================================

    def manejar_movimiento_continuo(self):

        teclas = pygame.key.get_pressed()

        if (
            self.muerto
            or self.recibiendo_dano
            or self.rodando
            or self.defendiendo
            or (
                self.atacando
                and self.en_suelo
            )
        ):

            self.velocidad_x = 0
            return

        self.velocidad_x = 0

        # IZQUIERDA - A

        if teclas[pygame.K_a]:

            self.velocidad_x = -self.velocidad_movimiento
            self.mirando_derecha = False

        # DERECHA - D

        if teclas[pygame.K_d]:

            self.velocidad_x = self.velocidad_movimiento
            self.mirando_derecha = True

    # ========================================================
    # ACTUALIZAR ESTADO
    # ========================================================

    def actualizar_estado(self):

        if self.muerto:

            self.estado = "11_death"

        elif self.recibiendo_dano:

            self.estado = "10_take_hit"

        elif self.rodando:

            self.estado = "roll"

        elif self.defendiendo:

            self.estado = "defend"

        elif self.atacando:

            # Mantener animación de ataque
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

        # FINAL DE ANIMACIÓN

        if self.frame_index >= len(anim):

            # MUERTE: reproducir una sola vez.

            if self.muerto:

                self.frame_index = len(anim) - 1

                if not self.muerte_terminada:

                    self.muerte_terminada = True
                    self.kill()

                return

            self.frame_index = 0

            # TERMINÓ TAKE HIT

            if self.recibiendo_dano:

                self.recibiendo_dano = False
                self.inmune_dano = False
                self.estado = "idle"

            # ROLL

            elif self.rodando:

                self.rodando = False

            # DEFENSA

            elif self.defendiendo:

                self.defendiendo = False

            # ATAQUES QUE TERMINAN

            elif self.estado in (
                "air_atk",
                "sp_atk",
                "3_atk"
            ):

                self.atacando = False
                self.combo_siguiente = False

            # ATAQUE 1

            elif self.estado == "1_atk":

                if self.combo_siguiente:

                    self.estado = "2_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False
                    self.golpe_aplicado = False

                else:

                    self.atacando = False

            # ATAQUE 2

            elif self.estado == "2_atk":

                if self.combo_siguiente:

                    self.estado = "3_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False
                    self.golpe_aplicado = False

                else:

                    self.atacando = False

        # FRAME ACTUAL

        anim = self.animaciones[self.estado]

        indice = min(
            int(self.frame_index),
            len(anim) - 1
        )

        frame_actual = anim[indice]

        # GIRAR PERSONAJE

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

        if self.muerto:
            return

        self.velocidad_y += self.gravedad

        self.rect.y += self.velocidad_y

        # SUELO

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

        # ACTUALIZAR INMUNIDAD TEMPORAL

        if (
            self.inmune_dano
            and not self.recibiendo_dano
            and not self.muerto
            and pygame.time.get_ticks() - self.tiempo_ultimo_dano
            >= self.duracion_inmunidad
        ):

            self.inmune_dano = False

        # MUERTE: BLOQUEAR MOVIMIENTO

        if self.muerto:

            self.velocidad_x = 0
            self.velocidad_y = 0

            self.actualizar_hurtbox()
            self.animar()

            return

        self.manejar_movimiento_continuo()

        # VELOCIDAD AL RODAR

        if self.rodando:

            self.velocidad_x = (
                self.velocidad_movimiento + 3
            ) * (
                1
                if self.mirando_derecha
                else -1
            )

        # POSICIÓN GLOBAL

        self.pos_x += self.velocidad_x

        # LÍMITES DEL MUNDO

        limite_izquierdo = scroll_x + 80

        self.pos_x = max(
            limite_izquierdo,
            min(
                self.pos_x,
                ancho_mundo - 80
            )
        )

        # POSICIÓN EN PANTALLA

        self.rect.centerx = int(
            self.pos_x - scroll_x
        )

        # FÍSICA

        self.aplicar_gravedad()

        # ESTADO

        self.actualizar_estado()

        # ANIMACIÓN

        self.animar()

        # HURTBOX Y HITBOX

        self.actualizar_hurtbox()
        self.actualizar_hitbox()
