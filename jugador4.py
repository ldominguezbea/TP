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
# FLECHA AEREA: IMPACTA EN EL SUELO DEL JUGADOR
# ============================================================

class FlechaAerea(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo, mirando_derecha):
        super().__init__()

        # Es la coordenada Y del suelo donde se apoya el jugador.
        self.posicion_suelo = int(posicion_suelo)
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
            BASE_EFECTOS, "arrow", "arrow_.png"
        )
        ruta_hit = os.path.join(
            BASE_EFECTOS, "diagonal_arrow_hit"
        )

        self.image = pygame.image.load(ruta_flecha).convert_alpha()
        self.image = pygame.transform.scale(self.image, (160, 160))

        if not mirando_derecha:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect(center=(x, y))

        self.animacion_hit = []
        for i in range(1, 7):
            ruta = os.path.join(ruta_hit, f"diagonal_arrow_hit_{i}.png")
            imagen = pygame.image.load(ruta).convert_alpha()
            imagen = pygame.transform.scale(imagen, (180, 180))
            self.animacion_hit.append(imagen)

    def colocar_animacion_apoyada(self, centro_x_pantalla):
        # Alinear el último píxel VISIBLE con el suelo. Algunas imágenes
        # tienen margen transparente abajo, así que midbottom por sí solo
        # puede dejar el efecto visual flotando.
        limites_visibles = self.image.get_bounding_rect(min_alpha=1)
        self.rect = self.image.get_rect()
        self.rect.centerx = int(centro_x_pantalla)
        self.rect.top = self.posicion_suelo - limites_visibles.bottom

    def iniciar_impacto_suelo(self, scroll_x=0):
        # Conservar la X del punto donde la flecha llegó al suelo y apoyar
        # el contenido visible de la animación sobre el suelo del jugador.
        self.estado = "hit"
        self.frame_index = 0
        self.image = self.animacion_hit[0]
        centro_x_pantalla = int(self.pos_x - scroll_x)
        self.colocar_animacion_apoyada(centro_x_pantalla)

    def update(self, scroll_x=0):
        if self.estado == "flecha":
            self.pos_x += self.velocidad_x
            self.pos_y += self.velocidad_y
            self.velocidad_y += self.gravedad

            self.rect.centerx = int(self.pos_x - scroll_x)
            self.rect.centery = int(self.pos_y)

            # No usar rect.bottom aquí: la imagen de la flecha tiene
            # transparencia y su rectángulo puede tocar el suelo antes
            # de que la flecha visualmente llegue a él. Esperar a que su
            # trayectoria alcance la altura real del suelo.
            if self.pos_y >= self.posicion_suelo:
                self.pos_y = float(self.posicion_suelo)
                self.iniciar_impacto_suelo(scroll_x)

        elif self.estado == "hit":
            self.frame_index += self.velocidad_animacion

            if self.frame_index >= len(self.animacion_hit):
                self.kill()
                return

            self.image = self.animacion_hit[int(self.frame_index)]
            centro_x_pantalla = int(self.pos_x - scroll_x)

            # Recolocar cada fotograma usando sus píxeles visibles, para
            # que ninguno quede flotando por el margen transparente inferior.
            self.colocar_animacion_apoyada(centro_x_pantalla)


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
            (160, 160)
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
        # CONFIGURACION
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
        # HURTBOX Y HITBOX
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
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.pos_x = float(x)

        # ====================================================
        # FISICA
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
        # FLECHA HORIZONTAL DEL SEGUNDO ATAQUE
        # ====================================================

        self.frame_flecha_horizontal = 8
        self.flecha_horizontal_creada = False
        self.ancho_mundo = 0

        # ====================================================
        # PROYECTILES
        # ====================================================

        self.proyectiles = pygame.sprite.Group()

        self.actualizar_hurtbox()

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

        # ----------------------------------------------------
        # RECIBIR DAÑO: 6 IMAGENES
        # ----------------------------------------------------

        for i in range(1, 7):

            ruta = os.path.join(
                base_path,
                "take_hit",
                f"take_hit_{i}.png"
            )

            imagen = pygame.image.load(ruta).convert_alpha()
            imagen = pygame.transform.scale(imagen, escala)

            self.animaciones["take_hit"].append(imagen)

        # ----------------------------------------------------
        # MUERTE: 19 IMAGENES
        # ----------------------------------------------------

        for i in range(1, 20):

            ruta = os.path.join(
                base_path,
                "death",
                f"death_{i}.png"
            )

            imagen = pygame.image.load(ruta).convert_alpha()
            imagen = pygame.transform.scale(imagen, escala)

            self.animaciones["death"].append(imagen)

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

        if self.rodando or self.defendiendo or self.inmune_dano:
            return

        self.vida = max(0, self.vida - cantidad)

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
            self.estado = "death"
        else:
            self.recibiendo_dano = True
            self.estado = "take_hit"

    # ========================================================
    # HITBOX DEL PRIMER ATAQUE
    # ========================================================

    def actualizar_hitbox(self):

        self.hitbox = pygame.Rect(0, 0, 0, 0)

        if self.estado != "1_atk" or not self.atacando:
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
                enemigo.recibir_dano(self.dano_ataque_1)

            elif hasattr(enemigo, "take_damage"):
                enemigo.take_damage(self.dano_ataque_1)

            elif hasattr(enemigo, "vida"):
                enemigo.vida = max(
                    0,
                    enemigo.vida - self.dano_ataque_1
                )

            self.golpe_aplicado = True

    # ========================================================
    # PROCESAR EVENTOS
    # ========================================================

    def procesar_evento(self, evento):

        if self.muerto or self.recibiendo_dano:
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

        # DEFENSA: CLIC DERECHO

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

        # ATAQUES: CLIC IZQUIERDO

        elif (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_LEFT
        ):

            # ATAQUE AEREO

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
                    self.golpe_aplicado = False

                elif self.estado in ("1_atk", "2_atk"):

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
    # ANIMAR Y GENERAR PROYECTILES
    # ========================================================

    def animar(self):

        anim = self.animaciones[self.estado]

        # ----------------------------------------------------
        # RAFAGA DEL TERCER ATAQUE
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
        # FLECHA HORIZONTAL DEL SEGUNDO ATAQUE
        # ----------------------------------------------------

        if (
            self.estado == "2_atk"
            and int(self.frame_index) + 1
            >= self.frame_flecha_horizontal
            and not self.flecha_horizontal_creada
        ):

            self.flecha_horizontal_creada = True

            distancia = 100

            x_flecha = (
                self.pos_x + distancia
                if self.mirando_derecha
                else self.pos_x - distancia
            )

            y_flecha = self.rect.bottom - 80

            flecha = FlechaHorizontal(
                x_flecha,
                y_flecha,
                self.mirando_derecha,
                self.ancho_mundo
            )

            self.proyectiles.add(flecha)

        # ----------------------------------------------------
        # AVANZAR ANIMACION
        # ----------------------------------------------------

        self.frame_index += self.velocidad_animacion

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

            elif self.estado in ("air_atk", "sp_atk", "3_atk"):
                self.atacando = False

            # ATAQUE 1

            elif self.estado == "1_atk":

                if self.combo_siguiente:
                    self.estado = "2_atk"
                    self.combo_siguiente = False
                    self.flecha_horizontal_creada = False
                    self.golpe_aplicado = False

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

            anim = self.animaciones[self.estado]

        # ----------------------------------------------------
        # MOSTRAR FRAME ACTUAL
        # ----------------------------------------------------

        indice = min(
            int(self.frame_index),
            len(anim) - 1
        )

        frame_actual = anim[indice]

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

        if self.muerto:
            return

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

        self.ancho_mundo = ancho_mundo

        # Actualizar inmunidad temporal.

        if (
            self.inmune_dano
            and not self.recibiendo_dano
            and not self.muerto
            and pygame.time.get_ticks() - self.tiempo_ultimo_dano
            >= self.duracion_inmunidad
        ):
            self.inmune_dano = False

        # Durante la muerte no se mueve, pero sigue la animación.

        if self.muerto:
            self.velocidad_x = 0
            self.velocidad_y = 0

            self.actualizar_hurtbox()
            self.animar()
            self.proyectiles.update(scroll_x)

            return

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

        self.actualizar_hurtbox()
        self.actualizar_hitbox()

        # Actualizar proyectiles originales y nuevos.
        self.proyectiles.update(scroll_x)
