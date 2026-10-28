
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

        self.image = self.animaciones[
            self.estado
        ][0]

        self.rect = self.image.get_rect(
            midbottom=(x, y)
        )

        # Posición real dentro del mundo
        self.pos_x = float(x)

        # ====================================================
        # VIDA DEL HÉROE
        # ====================================================

        self.vida_maxima = 100
        self.vida = 100

        # ====================================================
        # MUERTE DEL HÉROE
        # ====================================================

        self.muerto = False

        # ====================================================
        # HURTBOX DEL HÉROE
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

        # Daño del primer ataque
        self.dano_ataque_1 = 15

        # Hitbox invisible
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.hitbox_activa = False

        # Evita repetir el daño durante el mismo ataque
        self.golpe_aplicado = False

        # Actualizar la hurtbox inicial
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

        for i in range(1, 6):

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

        for i in range(5, 14):

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

        # ----------------------------------------------------
        # ANIMACIÓN HIT: 6 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 7):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "take_hit",
                    f"take_hit_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["take_hit"].append(img)

        # ----------------------------------------------------
        # ANIMACIÓN DE MUERTE: 19 IMÁGENES
        # ----------------------------------------------------

        for i in range(1, 20):

            img = pygame.image.load(
                os.path.join(
                    base_path,
                    "death",
                    f"death_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                escala
            )

            self.animaciones["death"].append(img)

    # ========================================================
    # RECIBIR DAÑO
    # ========================================================

    def recibir_dano(self, cantidad):

        if self.vida <= 0 or self.muerto:
            return

        if self.recibiendo_dano or self.inmune_dano:
            return

        # Rodar y defenderse conservan su protección.
        if self.rodando or self.defendiendo:
            return

        # Reducir la vida.
        self.vida = max(
            0,
            self.vida - cantidad
        )

        # Si la vida llega a cero, iniciar la muerte.
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

        # Iniciar la animación de daño.
        self.recibiendo_dano = True
        self.estado = "take_hit"
        self.frame_index = 0

        # Detener el movimiento y cancelar el ataque actual.
        self.velocidad_x = 0
        self.atacando = False
        self.combo_siguiente = False
        self.hitbox_activa = False

        # Evitar recibir golpes consecutivos inmediatamente.
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

        # No permitir acciones si recibe daño o está muerto.
        if self.recibiendo_dano or self.muerto:
            return

        # Aceptar teclado y mouse
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
                    self.golpe_aplicado = False

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

        # Bloquear movimiento durante acciones.
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

        # La muerte tiene prioridad sobre los demás estados.
        if self.muerto:

            self.estado = "death"

        # La animación de daño tiene prioridad.
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

        # ----------------------------------------------------
        # ANIMACIÓN DE MUERTE
        # ----------------------------------------------------

        if self.muerto:

            anim = self.animaciones["death"]

            self.frame_index += self.velocidad_animacion

            # La animación se reproduce una sola vez.
            if self.frame_index >= len(anim):

                self.kill()
                return

            frame_actual = anim[
                int(self.frame_index)
            ]

            # Girar personaje según su dirección.
            if not self.mirando_derecha:

                self.image = pygame.transform.flip(
                    frame_actual,
                    True,
                    False
                )

            else:

                self.image = frame_actual

            return

        anim = self.animaciones[self.estado]

        self.frame_index += self.velocidad_animacion

        # ----------------------------------------------------
        # FINAL DE ANIMACIÓN
        # ----------------------------------------------------

        if self.frame_index >= len(anim):

            self.frame_index = 0

            # Animación de daño.
            if self.recibiendo_dano:

                self.recibiendo_dano = False
                self.estado = "idle"
                self.velocidad_x = 0

                # Obtener el primer fotograma de idle.
                anim = self.animaciones["idle"]

            # Roll
            elif self.rodando:

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

        # Si la animación de daño terminó, usar idle.
        if not self.recibiendo_dano and self.estado == "idle":
            anim = self.animaciones["idle"]

        frame_actual = anim[
            min(int(self.frame_index), len(anim) - 1)
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

        else:

            self.en_suelo = False

    # ========================================================
    # ACTUALIZAR HITBOX
    # ========================================================

    def actualizar_hitbox(self, scroll_x):

        self.hitbox_activa = False

        if self.estado != "1_atk" or not self.atacando:
            return

        # Ventana de impacto: primera imagen de la animación.
        if int(self.frame_index) != 0 or self.golpe_aplicado:
            return

        ancho_hitbox = 80
        alto_hitbox = 30
        y_hitbox = self.rect.top + 100

        if self.mirando_derecha:

            self.hitbox = pygame.Rect(
                self.rect.right - 20,
                y_hitbox,
                ancho_hitbox,
                alto_hitbox
            )

        else:

            self.hitbox = pygame.Rect(
                self.rect.left - ancho_hitbox + 20,
                y_hitbox,
                ancho_hitbox,
                alto_hitbox
            )

        self.hitbox_activa = True

    # ========================================================
    # COMPROBAR GOLPE
    # ========================================================

    def comprobar_golpe(self, enemigo):

        if self.muerto:
            return

        if enemigo is None:
            return

        if not self.hitbox_activa or self.golpe_aplicado:
            return

        if not enemigo.alive() or enemigo.vida <= 0:
            return

        if self.hitbox.colliderect(enemigo.hurtbox):

            enemigo.recibir_dano(self.dano_ataque_1)

            self.golpe_aplicado = True
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

        # Si está muerto, solo reproducir la animación de muerte.
        # No aplicar movimiento, gravedad ni ataques.
        if self.muerto:

            self.animar()
            return

        # Actualizar inmunidad.
        self.actualizar_inmunidad()

        self.manejar_movimiento_continuo()

        # ----------------------------------------------------
        # VELOCIDAD AL RODAR
        # ----------------------------------------------------

        if self.rodando and not self.recibiendo_dano:

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

        # Actualizar hurtbox.
        self.actualizar_hurtbox()

        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------

        self.actualizar_estado()

        # ----------------------------------------------------
        # ANIMACIÓN
        # ----------------------------------------------------

        self.animar()

        # Actualizar hitbox y comprobar impacto.
        self.actualizar_hitbox(scroll_x)
        self.comprobar_golpe(enemigo)
