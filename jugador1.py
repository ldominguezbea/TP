import pygame
import os


class p_viento(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo):

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
            "sp_atk": [],
            "take_hit": [],
            "death": []
        }

        self.cargar_animaciones()

        # ====================================================
        # ESTADO
        # ====================================================

        self.estado = "idle"
        self.frame_index = 0
        self.velocidad_animacion = 0.22

        self.image = self.animaciones["idle"][0]

        self.rect = self.image.get_rect(
            midbottom=(x, y)
        )

        self.pos_x = float(x)

        # ====================================================
        # VIDA
        # ====================================================

        self.vida_maxima = 100
        self.vida = 100
        self.muerto = False

        # ====================================================
        # HURTBOX
        # ====================================================

        self.hurtbox = pygame.Rect(0, 0, 60, 100)
        self.color_hurtbox = (0, 255, 0)

        # ====================================================
        # RECIBIR DAÑO
        # ====================================================

        self.recibiendo_dano = False
        self.inmune_dano = False
        self.tiempo_inmunidad = 0
        self.duracion_inmunidad = 500

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

        # ====================================================
        # DAÑO DE LOS ATAQUES
        # ====================================================

        # Ataque 1
        self.dano_ataque_1 = 15
        self.golpe_aplicado = False

        # Ataque 2: imágenes 8 a 12
        self.dano_ataque_2 = 3
        self.frames_golpe_ataque_2 = {3, 4, 5, 6, 7}
        self.frames_que_ya_danaron = set()

        # Ataque 3: imágenes 18, 19 y 20
        self.dano_ataque_3 = 20
        self.golpe_tercer_ataque_aplicado = False

        # Ataque aéreo: tercera imagen
        self.dano_ataque_aereo = 15
        self.golpe_aereo_aplicado = False

        # Ataque especial: imágenes 12, 18 y 20
        self.dano_ataque_especial = 10
        self.frames_golpe_especial = {11, 17, 19}
        self.frames_especial_que_danaron = set()

        # ====================================================
        # HITBOX
        # ====================================================

        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.hitbox_activa = False
        self.color_hitbox = (255, 0, 0)

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
            "P_viento"
        )

        # IDLE
        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "idle",
                    f"idle_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["idle"].append(
                pygame.transform.scale(img, escala)
            )

        # RUN
        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "run",
                    f"run_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["run"].append(
                pygame.transform.scale(img, escala)
            )

        # ROLL
        for i in range(1, 7):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "roll",
                    f"roll_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["roll"].append(
                pygame.transform.scale(img, escala)
            )

        # SALTO
        for i in range(1, 4):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "j_up",
                    f"j_up_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["j_up"].append(
                pygame.transform.scale(img, escala)
            )

        # DEFENSA
        for i in range(1, 9):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "defend",
                    f"defend_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["defend"].append(
                pygame.transform.scale(img, escala)
            )

        # ATAQUE 1
        for i in range(1, 6):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "1_atk",
                    f"1_atk_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["1_atk"].append(
                pygame.transform.scale(img, escala)
            )

        # ATAQUE 2
        for i in range(5, 14):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "2_atk",
                    f"2_atk_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["2_atk"].append(
                pygame.transform.scale(img, escala)
            )

        # ATAQUE AÉREO
        for i in range(1, 8):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "air_atk",
                    f"air_atk_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["air_atk"].append(
                pygame.transform.scale(img, escala)
            )

        # ATAQUE ESPECIAL
        for i in range(1, 31):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "sp_atk",
                    f"sp_atk_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["sp_atk"].append(
                pygame.transform.scale(img, escala)
            )

        # ATAQUE 3
        for i in range(12, 27):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "3_atk",
                    f"3_atk_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["3_atk"].append(
                pygame.transform.scale(img, escala)
            )

        # ANIMACIÓN DE DAÑO
        for i in range(1, 7):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "take_hit",
                    f"take_hit_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["take_hit"].append(
                pygame.transform.scale(img, escala)
            )

        # ANIMACIÓN DE MUERTE
        for i in range(1, 20):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "death",
                    f"death_{i}.png"
                )
            ).convert_alpha()

            self.animaciones["death"].append(
                pygame.transform.scale(img, escala)
            )

    # ========================================================
    # RECIBIR DAÑO
    # ========================================================

    def recibir_dano(self, cantidad):

        if self.vida <= 0 or self.muerto:
            return

        if self.recibiendo_dano or self.inmune_dano:
            return

        if self.rodando or self.defendiendo:
            return

        self.vida = max(0, self.vida - cantidad)

        if self.vida <= 0:

            self.muerto = True
            self.recibiendo_dano = False

            self.estado = "death"
            self.frame_index = 0

            self.velocidad_x = 0
            self.velocidad_y = 0

            self.atacando = False
            self.rodando = False
            self.defendiendo = False

            self.combo_siguiente = False
            self.hitbox_activa = False

            return

        self.recibiendo_dano = True
        self.estado = "take_hit"
        self.frame_index = 0

        self.velocidad_x = 0
        self.atacando = False
        self.combo_siguiente = False
        self.hitbox_activa = False

        self.inmune_dano = True
        self.tiempo_inmunidad = pygame.time.get_ticks()

    # ========================================================
    # ACTUALIZAR INMUNIDAD
    # ========================================================

    def actualizar_inmunidad(self):

        if not self.inmune_dano:
            return

        tiempo_actual = pygame.time.get_ticks()

        if (
            tiempo_actual - self.tiempo_inmunidad
            >= self.duracion_inmunidad
        ):
            self.inmune_dano = False

    # ========================================================
    # ACTUALIZAR HURTBOX
    # ========================================================

    def actualizar_hurtbox(self):

        self.hurtbox.centerx = self.rect.centerx
        self.hurtbox.bottom = self.rect.bottom

    # ========================================================
    # DIBUJAR HURTBOX VERDE
    # ========================================================

    def dibujar_hurtbox(self, pantalla):

        if self.muerto:
            return

        pygame.draw.rect(
            pantalla,
            self.color_hurtbox,
            self.hurtbox,
            2
        )

    # ========================================================
    # EVENTOS DEL JUGADOR
    # ========================================================

    def procesar_evento(self, evento):

        if self.recibiendo_dano or self.muerto:
            return

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
            and not (
                self.atacando
                or self.rodando
                or self.defendiendo
            )
        ):

            self.velocidad_y = self.fuerza_salto
            self.en_suelo = False

        # RODAR: Q
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

        # DEFENDER: CLICK DERECHO
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

        # ATAQUE ESPECIAL: E
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

            self.frames_especial_que_danaron.clear()

        # ATAQUE: CLICK IZQUIERDO
        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_LEFT
        ):

            # ATAQUE AÉREO
            if (
                not self.en_suelo
                and not self.atacando
                and not self.rodando
                and not self.defendiendo
            ):

                self.atacando = True
                self.estado = "air_atk"
                self.frame_index = 0

                self.golpe_aereo_aplicado = False

            # ATAQUE TERRESTRE
            elif (
                self.en_suelo
                and not self.rodando
                and not self.defendiendo
            ):

                if not self.atacando:

                    self.atacando = True
                    self.estado = "1_atk"
                    self.frame_index = 0

                    self.combo_siguiente = False
                    self.golpe_aplicado = False

                elif self.estado in ["1_atk", "2_atk"]:

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

        # IZQUIERDA: A
        if teclas[pygame.K_a]:

            self.velocidad_x = -self.velocidad_movimiento
            self.mirando_derecha = False

        # DERECHA: D
        if teclas[pygame.K_d]:

            self.velocidad_x = self.velocidad_movimiento
            self.mirando_derecha = True

    # ========================================================
    # ACTUALIZAR ESTADO
    # ========================================================

    def actualizar_estado(self):

        if self.muerto:

            self.estado = "death"

        elif self.recibiendo_dano:

            self.estado = "take_hit"

        elif self.rodando:

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

        # MUERTE
        if self.muerto:

            anim = self.animaciones["death"]

            self.frame_index += self.velocidad_animacion

            if self.frame_index >= len(anim):

                self.frame_index = len(anim) - 1
                self.image = anim[-1]

                if not self.muerte_terminada:
                    self.muerte_terminada = True
                    self.kill()

                return

            frame_actual = anim[int(self.frame_index)]

            if not self.mirando_derecha:
                self.image = pygame.transform.flip(
                    frame_actual, True, False
                )
            else:
                self.image = frame_actual

            return

        anim = self.animaciones[self.estado]

        self.frame_index += self.velocidad_animacion

        # FIN DE ANIMACIÓN
        if self.frame_index >= len(anim):

            self.frame_index = 0

            if self.recibiendo_dano:

                self.recibiendo_dano = False
                self.estado = "idle"
                self.velocidad_x = 0

            elif self.rodando:

                self.rodando = False

            elif self.defendiendo:

                self.defendiendo = False

            elif self.estado in [
                "air_atk",
                "sp_atk",
                "3_atk"
            ]:

                self.atacando = False

            elif self.estado == "1_atk":

                if self.combo_siguiente:

                    self.estado = "2_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False

                    self.frames_que_ya_danaron.clear()

                else:

                    self.atacando = False

            elif self.estado == "2_atk":

                if self.combo_siguiente:

                    self.estado = "3_atk"
                    self.frame_index = 0
                    self.combo_siguiente = False

                    self.golpe_tercer_ataque_aplicado = False

                else:

                    self.atacando = False

        # ACTUALIZAR IMAGEN
        anim = self.animaciones[self.estado]

        frame_actual = anim[
            min(int(self.frame_index), len(anim) - 1)
        ]

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

        if self.rect.bottom >= self.posicion_suelo:

            self.rect.bottom = self.posicion_suelo

            self.velocidad_y = 0
            self.en_suelo = True

        else:

            self.en_suelo = False

    # ========================================================
    # ACTUALIZAR HITBOX
    # ========================================================

    def actualizar_hitbox(self, scroll_x):

        self.hitbox_activa = False

        if (
            self.muerto
            or self.recibiendo_dano
            or not self.atacando
        ):
            return

        frame_actual = int(self.frame_index)

        # ====================================================
        # ATAQUE 1
        # ====================================================

        if self.estado == "1_atk":

            if frame_actual != 0 or self.golpe_aplicado:
                return

            ancho_hitbox = 80
            alto_hitbox = 30
            y_hitbox = self.rect.top + 100

            if self.mirando_derecha:
                x_hitbox = self.rect.right - 20
            else:
                x_hitbox = self.rect.left - ancho_hitbox + 20

        # ====================================================
        # ATAQUE 2: IMÁGENES 8 A 12
        # ====================================================

        elif self.estado == "2_atk":

            if frame_actual not in self.frames_golpe_ataque_2:
                return

            if frame_actual in self.frames_que_ya_danaron:
                return

            ancho_hitbox = 80
            alto_hitbox = 30
            y_hitbox = self.rect.top + 100

            if self.mirando_derecha:
                x_hitbox = self.rect.right - 20
            else:
                x_hitbox = self.rect.left - ancho_hitbox + 20

        # ====================================================
        # ATAQUE 3: TORNADO EN IMÁGENES 18, 19 Y 20
        # ====================================================

        elif self.estado == "3_atk":

            # 3_atk carga los archivos 12 a 26.
            # Índices 6, 7 y 8 corresponden a los archivos 18 a 20.
            if frame_actual not in (6, 7, 8):
                return

            if self.golpe_tercer_ataque_aplicado:
                return

            # Hitbox en la zona del tornado, delante del héroe.
            ancho_hitbox = 150
            alto_hitbox = 180
            y_hitbox = self.rect.top + 60

            if self.mirando_derecha:
                x_hitbox = self.rect.right - 10
            else:
                x_hitbox = self.rect.left - ancho_hitbox + 10

        # ====================================================
        # ATAQUE AÉREO: TERCERA IMAGEN
        # ====================================================

        elif self.estado == "air_atk":

            if frame_actual != 2:
                return

            if self.golpe_aereo_aplicado:
                return

            ancho_hitbox = 100
            alto_hitbox = 60
            y_hitbox = self.rect.top + 100

            if self.mirando_derecha:
                x_hitbox = self.rect.right - 10
            else:
                x_hitbox = self.rect.left - ancho_hitbox + 10

        # ====================================================
        # ATAQUE ESPECIAL: IMÁGENES 12, 18 Y 20
        # ====================================================

        elif self.estado == "sp_atk":

            if frame_actual not in self.frames_golpe_especial:
                return

            if frame_actual in self.frames_especial_que_danaron:
                return

            # Hitbox aproximada sobre los slashes.
            ancho_hitbox = 150
            alto_hitbox = 100
            y_hitbox = self.rect.top + 70

            if self.mirando_derecha:
                x_hitbox = self.rect.right - 10
            else:
                x_hitbox = self.rect.left - ancho_hitbox + 10

        else:
            return

        self.hitbox = pygame.Rect(
            x_hitbox,
            y_hitbox,
            ancho_hitbox,
            alto_hitbox
        )

        self.hitbox_activa = True

    # ========================================================
    # DIBUJAR HITBOX ROJA
    # ========================================================

    def dibujar_hitbox(self, pantalla):

        if not self.hitbox_activa or self.muerto:
            return

        pygame.draw.rect(
            pantalla,
            self.color_hitbox,
            self.hitbox,
            3
        )

    # ========================================================
    # COMPROBAR GOLPE
    # ========================================================

    def comprobar_golpe(self, enemigo):

        if self.muerto or enemigo is None:
            return

        if not self.hitbox_activa:
            return

        if not enemigo.alive() or enemigo.vida <= 0:
            return

        if not self.hitbox.colliderect(enemigo.hurtbox):
            return

        frame_actual = int(self.frame_index)

        # ATAQUE 1: 15 DE DAÑO
        if self.estado == "1_atk":

            if self.golpe_aplicado:
                return

            enemigo.recibir_dano(self.dano_ataque_1)

            self.golpe_aplicado = True
            self.hitbox_activa = False

        # ATAQUE 2: 3 DE DAÑO POR IMAGEN
        elif self.estado == "2_atk":

            if frame_actual not in self.frames_golpe_ataque_2:
                return

            if frame_actual in self.frames_que_ya_danaron:
                return

            enemigo.recibir_dano(self.dano_ataque_2)

            self.frames_que_ya_danaron.add(frame_actual)
            self.hitbox_activa = False

        # ATAQUE 3: 20 DE DAÑO
        elif self.estado == "3_atk":

            if frame_actual not in (6, 7, 8):
                return

            if self.golpe_tercer_ataque_aplicado:
                return

            enemigo.recibir_dano(self.dano_ataque_3)

            self.golpe_tercer_ataque_aplicado = True
            self.hitbox_activa = False

        # ATAQUE AÉREO: 15 DE DAÑO
        elif self.estado == "air_atk":

            if frame_actual != 2:
                return

            if self.golpe_aereo_aplicado:
                return

            enemigo.recibir_dano(self.dano_ataque_aereo)

            self.golpe_aereo_aplicado = True
            self.hitbox_activa = False

        # ATAQUE ESPECIAL: 10 POR CADA IMAGEN
        elif self.estado == "sp_atk":

            if frame_actual not in self.frames_golpe_especial:
                return

            if frame_actual in self.frames_especial_que_danaron:
                return

            enemigo.recibir_dano(self.dano_ataque_especial)

            self.frames_especial_que_danaron.add(frame_actual)
            self.hitbox_activa = False

    # ========================================================
    # ACTUALIZAR JUGADOR
    # ========================================================

    def update(
        self,
        scroll_x,
        ancho_mundo,
        enemigo=None
    ):

        # Inicializar este atributo para que exista durante la muerte.
        if not hasattr(self, "muerte_terminada"):
            self.muerte_terminada = False

        # MUERTE: solo reproducir la animación.
        if self.muerto:

            self.animar()
            return

        self.actualizar_inmunidad()
        self.manejar_movimiento_continuo()

        # VELOCIDAD AL RODAR
        if self.rodando and not self.recibiendo_dano:

            self.velocidad_x = (
                self.velocidad_movimiento + 3
            ) * (
                1 if self.mirando_derecha else -1
            )

        # POSICIÓN GLOBAL
        self.pos_x += self.velocidad_x

        # LÍMITES DEL MUNDO
        limite_izquierdo = scroll_x + 80

        self.pos_x = max(
            limite_izquierdo,
            min(self.pos_x, ancho_mundo - 80)
        )

        # POSICIÓN EN PANTALLA
        self.rect.centerx = int(
            self.pos_x - scroll_x
        )

        # FÍSICA
        self.aplicar_gravedad()

        # ACTUALIZAR HURTBOX
        self.actualizar_hurtbox()

        # ESTADO Y ANIMACIÓN
        self.actualizar_estado()
        self.animar()

        # HITBOX Y COLISIÓN
        self.actualizar_hitbox(scroll_x)
        self.comprobar_golpe(enemigo)