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
# FLECHA AEREA
# ============================================================

class FlechaAerea(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo, mirando_derecha):
        super().__init__()

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

        self.dano = 15

        ruta_flecha = os.path.join(
            BASE_EFECTOS, "arrow", "arrow_.png"
        )

        ruta_hit = os.path.join(
            BASE_EFECTOS, "diagonal_arrow_hit"
        )

        self.image = pygame.image.load(
            ruta_flecha
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image, (160, 160)
        )

        if not mirando_derecha:
            self.image = pygame.transform.flip(
                self.image, True, False
            )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.actualizar_hitbox()

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
                imagen, (180, 180)
            )

            self.animacion_hit.append(imagen)

    def actualizar_hitbox(self):

        if self.estado != "flecha":
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            return

        limites_visibles = self.image.get_bounding_rect(
            min_alpha=1
        )

        # HITBOX EN COORDENADAS DEL MUNDO

        izquierda_mundo = round(
            self.pos_x - self.image.get_width() / 2
        )

        arriba_mundo = round(
            self.pos_y - self.image.get_height() / 2
        )

        self.hitbox = limites_visibles.move(
            izquierda_mundo,
            arriba_mundo
        ).inflate(20, 20)

    def comprobar_golpe(self, enemigo):

        if self.estado != "flecha":
            return False

        hurtbox_enemigo = getattr(
            enemigo,
            "hurtbox",
            getattr(enemigo, "rect", None)
        )

        if hurtbox_enemigo is None:
            return False

        if self.hitbox.colliderect(hurtbox_enemigo):

            if hasattr(enemigo, "recibir_dano"):
                enemigo.recibir_dano(self.dano)

            elif hasattr(enemigo, "take_damage"):
                enemigo.take_damage(self.dano)

            elif hasattr(enemigo, "vida"):
                enemigo.vida = max(
                    0, enemigo.vida - self.dano
                )

            self.kill()
            return True

        return False

    def colocar_animacion_apoyada(self, centro_x_pantalla):

        limites_visibles = self.image.get_bounding_rect(
            min_alpha=1
        )

        self.rect = self.image.get_rect()
        self.rect.centerx = int(centro_x_pantalla)

        self.rect.top = (
            self.posicion_suelo - limites_visibles.bottom
        )

    def iniciar_impacto_suelo(self, scroll_x=0):

        self.estado = "hit"
        self.frame_index = 0

        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.image = self.animacion_hit[0]

        centro_x_pantalla = int(
            self.pos_x - scroll_x
        )

        self.colocar_animacion_apoyada(
            centro_x_pantalla
        )

    def update(self, scroll_x=0):

        if self.estado == "flecha":

            self.pos_x += self.velocidad_x
            self.pos_y += self.velocidad_y
            self.velocidad_y += self.gravedad

            # RECT EN COORDENADAS DE PANTALLA

            self.rect.centerx = int(
                self.pos_x - scroll_x
            )

            self.rect.centery = int(self.pos_y)

            # HITBOX EN COORDENADAS DEL MUNDO

            self.actualizar_hitbox()

            if self.pos_y >= self.posicion_suelo:

                self.pos_y = float(self.posicion_suelo)

                self.iniciar_impacto_suelo(scroll_x)

        elif self.estado == "hit":

            self.frame_index += self.velocidad_animacion

            if self.frame_index >= len(self.animacion_hit):
                self.kill()
                return

            self.image = self.animacion_hit[
                int(self.frame_index)
            ]

            centro_x_pantalla = int(
                self.pos_x - scroll_x
            )

            self.colocar_animacion_apoyada(
                centro_x_pantalla
            )


# ============================================================
# FLECHA HORIZONTAL
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

        self.velocidad_x = (
            12 if mirando_derecha else -12
        )

        self.estado = "flecha"
        self.frame_index = 0
        self.velocidad_animacion = 0.25

        self.dano = 20

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

        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.actualizar_hitbox()

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

    def actualizar_hitbox(self):

        if self.estado != "flecha":
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            return

        limites_visibles = self.image.get_bounding_rect(
            min_alpha=1
        )

        # HITBOX EN COORDENADAS DEL MUNDO

        izquierda_mundo = round(
            self.pos_x - self.image.get_width() / 2
        )

        arriba_mundo = round(
            self.pos_y - self.image.get_height() / 2
        )

        self.hitbox = limites_visibles.move(
            izquierda_mundo,
            arriba_mundo
        ).inflate(20, 20)

    def comprobar_golpe(self, enemigo):

        if self.estado != "flecha":
            return False

        hurtbox_enemigo = getattr(
            enemigo,
            "hurtbox",
            getattr(enemigo, "rect", None)
        )

        if hurtbox_enemigo is None:
            return False

        if self.hitbox.colliderect(hurtbox_enemigo):

            if hasattr(enemigo, "recibir_dano"):
                enemigo.recibir_dano(self.dano)

            elif hasattr(enemigo, "take_damage"):
                enemigo.take_damage(self.dano)

            elif hasattr(enemigo, "vida"):
                enemigo.vida = max(
                    0,
                    enemigo.vida - self.dano
                )

            self.kill()
            return True

        return False

    def update(self, scroll_x=0):

        if self.estado == "flecha":

            self.pos_x += self.velocidad_x

            # RECT EN COORDENADAS DE PANTALLA

            self.rect.centerx = int(
                self.pos_x - scroll_x
            )

            self.rect.centery = int(self.pos_y)

            # HITBOX EN COORDENADAS DEL MUNDO

            self.actualizar_hitbox()

            # PARED DERECHA

            if self.mirando_derecha:

                if (
                    self.pos_x + self.rect.width / 2
                    >= self.ancho_mundo
                ):

                    self.pos_x = (
                        self.ancho_mundo
                        - self.rect.width / 2
                    )

                    self.iniciar_impacto(scroll_x)

            # PARED IZQUIERDA

            else:

                if (
                    self.pos_x - self.rect.width / 2
                    <= 0
                ):

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

        self.hitbox = pygame.Rect(0, 0, 0, 0)

        centro_x = int(
            self.pos_x - scroll_x
        )

        centro_y = int(self.pos_y)

        self.image = self.animacion_hit[0]

        self.rect = self.image.get_rect(
            center=(centro_x, centro_y)
        )


# ============================================================
# RAFAGA DEL TERCER ATAQUE
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

        self.dano_por_frame = 4

        self.ultimo_frame_golpeado = 0
        self.enemigos_golpeados_frame = set()

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

        self.rect = self.image.get_rect(
            midbottom=(
                int(self.pos_x),
                self.posicion_suelo
            )
        )

        # HITBOX EN COORDENADAS DEL MUNDO

        self.hitbox = pygame.Rect(
            0,
            0,
            self.image.get_width(),
            self.image.get_height()
        )

        self.hitbox.midbottom = (
            round(self.pos_x),
            self.posicion_suelo
        )

    def comprobar_golpe(self, enemigo):

        indice_actual = int(self.frame_index)

        if indice_actual >= len(self.animacion):
            return False

        if indice_actual != self.ultimo_frame_golpeado:

            self.ultimo_frame_golpeado = indice_actual
            self.enemigos_golpeados_frame.clear()

        if enemigo in self.enemigos_golpeados_frame:
            return False

        hurtbox_enemigo = getattr(
            enemigo,
            "hurtbox",
            getattr(enemigo, "rect", None)
        )

        if hurtbox_enemigo is None:
            return False

        if self.hitbox.colliderect(hurtbox_enemigo):

            if hasattr(enemigo, "recibir_dano"):
                enemigo.recibir_dano(self.dano_por_frame)

            elif hasattr(enemigo, "take_damage"):
                enemigo.take_damage(self.dano_por_frame)

            elif hasattr(enemigo, "vida"):
                enemigo.vida = max(
                    0,
                    enemigo.vida - self.dano_por_frame
                )

            self.enemigos_golpeados_frame.add(enemigo)

            return True

        return False

    def update(self, scroll_x=0):

        self.frame_index += self.velocidad_animacion

        if self.frame_index >= len(self.animacion):

            self.hitbox = pygame.Rect(0, 0, 0, 0)
            self.kill()
            return

        centro_x = int(
            self.pos_x - scroll_x
        )

        self.image = self.animacion[
            int(self.frame_index)
        ]

        # RECT EN COORDENADAS DE PANTALLA

        self.rect = self.image.get_rect(
            midbottom=(
                centro_x,
                self.posicion_suelo
            )
        )

        # HITBOX EN COORDENADAS DEL MUNDO

        self.hitbox = pygame.Rect(
            0,
            0,
            self.image.get_width(),
            self.image.get_height()
        )

        self.hitbox.midbottom = (
            round(self.pos_x),
            self.posicion_suelo
        )
# ============================================================
# CLASE DEL HEROE PLANTA
# ============================================================

class p_planta(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo):
        super().__init__()

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

        self.dano_ataque_especial = 30
        self.enemigos_golpeados_especial = set()

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

        escala = (
            self.ancho_heroe,
            self.alto_heroe
        )

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

                imagen = pygame.image.load(
                    ruta
                ).convert_alpha()

                imagen = pygame.transform.scale(
                    imagen,
                    escala
                )

                self.animaciones[estado].append(imagen)

        # RECIBIR DAÑO: 6 IMAGENES

        for i in range(1, 7):

            ruta = os.path.join(
                base_path,
                "take_hit",
                f"take_hit_{i}.png"
            )

            imagen = pygame.image.load(
                ruta
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                escala
            )

            self.animaciones["take_hit"].append(imagen)

        # MUERTE: 19 IMAGENES

        for i in range(1, 20):

            ruta = os.path.join(
                base_path,
                "death",
                f"death_{i}.png"
            )

            imagen = pygame.image.load(
                ruta
            ).convert_alpha()

            imagen = pygame.transform.scale(
                imagen,
                escala
            )

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

        # INVULNERABILIDAD DURANTE EL ATAQUE ESPECIAL

        if (
            self.rodando
            or self.defendiendo
            or self.inmune_dano
            or (self.atacando and self.estado == "sp_atk")
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
            self.estado = "death"

        else:

            self.recibiendo_dano = True
            self.estado = "take_hit"
        # ========================================================
    # HITBOX DEL PRIMER ATAQUE Y ATAQUE ESPECIAL
    # ========================================================

    def actualizar_hitbox(self):

        self.hitbox = pygame.Rect(0, 0, 0, 0)

        # ATAQUE 1: SOLAMENTE IMAGEN 6

        if self.estado == "1_atk" and self.atacando:

            if int(self.frame_index) == 5:

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

        # ATAQUE ESPECIAL: SOLAMENTE IMAGEN 10

        elif self.estado == "sp_atk" and self.atacando:

            if int(self.frame_index) == 9:

                ancho_rayo = 730
                alto_rayo = 85

                centro_y_rayo = self.hurtbox.centery - 80

                if self.mirando_derecha:

                    self.hitbox = pygame.Rect(
                        self.hurtbox.right,
                        centro_y_rayo - alto_rayo // 2,
                        ancho_rayo,
                        alto_rayo
                    )

                else:

                    self.hitbox = pygame.Rect(
                        self.hurtbox.left - ancho_rayo,
                        centro_y_rayo - alto_rayo // 2,
                        ancho_rayo,
                        alto_rayo
                    )

    # ========================================================
    # COMPROBAR GOLPES DEL HEROE
    # ========================================================

    def comprobar_golpe(self, enemigo):

        if self.hitbox.width <= 0:
            return

        hurtbox_enemigo = getattr(
            enemigo,
            "hurtbox",
            getattr(enemigo, "rect", None)
        )

        if hurtbox_enemigo is None:
            return

        if not self.hitbox.colliderect(hurtbox_enemigo):
            return

        # ATAQUE ESPECIAL

        if self.estado == "sp_atk":

            if enemigo in self.enemigos_golpeados_especial:
                return

            dano = self.dano_ataque_especial

            self.enemigos_golpeados_especial.add(enemigo)

        # ATAQUE 1

        elif self.estado == "1_atk":

            if self.golpe_aplicado:
                return

            dano = self.dano_ataque_1
            self.golpe_aplicado = True

        else:
            return

        if hasattr(enemigo, "recibir_dano"):

            enemigo.recibir_dano(dano)

        elif hasattr(enemigo, "take_damage"):

            enemigo.take_damage(dano)

        elif hasattr(enemigo, "vida"):

            enemigo.vida = max(
                0,
                enemigo.vida - dano
            )

    # ========================================================
    # COMPROBAR GOLPES DE LOS PROYECTILES
    # ========================================================

    def comprobar_golpes_proyectiles(self, enemigos):

        for proyectil in list(self.proyectiles):

            if not hasattr(proyectil, "comprobar_golpe"):
                continue

            for enemigo in enemigos:

                if proyectil not in self.proyectiles:
                    break

                proyectil.comprobar_golpe(enemigo)

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

            self.enemigos_golpeados_especial.clear()

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

                # APARECER DELANTE DE LA HURTBOX

                if self.mirando_derecha:

                    x_flecha = (
                        self.pos_x
                        + self.hurtbox.width // 2
                        + 80
                    )

                else:

                    x_flecha = (
                        self.pos_x
                        - self.hurtbox.width // 2
                        - 80
                    )

                flecha = FlechaAerea(
                    x_flecha,
                    self.hurtbox.centery,
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

            # APARECER DELANTE DE LA HURTBOX

            distancia = (
                self.hurtbox.width // 2
                + 150
            )

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

            # APARECER DELANTE DE LA HURTBOX

            if self.mirando_derecha:

                x_flecha = (
                    self.pos_x
                    + self.hurtbox.width // 2
                    + 80
                )

            else:

                x_flecha = (
                    self.pos_x
                    - self.hurtbox.width // 2
                    - 80
                )

            y_flecha = self.hurtbox.centery

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

            # MUERTE: REPRODUCIR UNA SOLA VEZ

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

        # ACTUALIZAR INMUNIDAD TEMPORAL

        if (
            self.inmune_dano
            and not self.recibiendo_dano
            and not self.muerto
            and pygame.time.get_ticks() - self.tiempo_ultimo_dano
            >= self.duracion_inmunidad
        ):

            self.inmune_dano = False

        # DURANTE LA MUERTE

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
            ) * (
                1 if self.mirando_derecha else -1
            )

        self.pos_x += self.velocidad_x

        limite_izquierdo = scroll_x + 80

        self.pos_x = max(
            limite_izquierdo,
            min(
                self.pos_x,
                ancho_mundo - 80
            )
        )

        self.rect.centerx = int(
            self.pos_x - scroll_x
        )

        self.aplicar_gravedad()
        self.actualizar_estado()
        self.animar()

        self.actualizar_hurtbox()
        self.actualizar_hitbox()

        # ACTUALIZAR PROYECTILES

        self.proyectiles.update(scroll_x)