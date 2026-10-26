
import os
import pygame


class p_tierra(pygame.sprite.Sprite):

    def __init__(self, x, y, posicion_suelo):
        super().__init__()

        # -------------------------------------------------
        # CONFIGURACION DEL PERSONAJE
        # -------------------------------------------------

        self.ancho_heroe = 300
        self.alto_heroe = 300

        self.posicion_suelo = posicion_suelo

        self.pos_x = float(x)
        self.pos_y = float(y - self.alto_heroe)

        self.velocidad = 7
        self.gravedad = 0.8
        self.fuerza_salto = -16
        self.velocidad_y = 0

        self.en_suelo = True
        self.mirando_derecha = True

        self.health = 150
        self.max_health = 150

        self.invulnerable = False
        self.tiempo_invulnerable = 0
        self.duracion_invulnerable = 500

        self.rodando = False
        self.defendiendo = False

        self.atacando = False
        self.has_hit = False

        self.estado = "idle"
        self.frame_index = 0
        self.tiempo_animacion = 0
        self.velocidad_animacion = 100

        self.cooldown_ataque = 0
        self.cooldown_especial = 0

        self.plataformas = []
        self.scroll_x_actual = 0

        self.limite_max_x = None
        self.transicion_realizada = False

        self.daño_ataque = 20

        # -------------------------------------------------
        # CARGA DE ANIMACIONES
        # -------------------------------------------------

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

        # -------------------------------------------------
        # RECTANGULOS Y COLISIONES
        # -------------------------------------------------

        self.image = pygame.Surface(
            (self.ancho_heroe, self.alto_heroe),
            pygame.SRCALPHA
        )

        self.rect = self.image.get_rect()

        self.rect.x = int(self.pos_x)
        self.rect.bottom = int(self.posicion_suelo)

        self.hurtbox = pygame.Rect(
            self.rect.x + 100,
            self.rect.y + 60,
            100,
            220
        )

        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.actualizar_hitboxes()
        self.actualizar_animacion(0)

    # =====================================================
    # CARGA DE IMAGENES
    # =====================================================

    def cargar_animaciones(self):

        carpeta_base = os.path.join(
            "assets",
            "Heroes",
            "P_tierra"
        )

        configuracion = {
            "idle": (1, 6),
            "run": (1, 8),
            "roll": (1, 6),
            "j_up": (1, 3),
            "defend": (1, 13),
            "1_atk": (1, 6),
            "2_atk": (5, 12),
            "3_atk": (11, 23),
            "air_atk": (1, 7),
            "sp_atk": (1, 25)
        }

        for nombre, rango in configuracion.items():

            inicio, final = rango

            posibles_carpetas = [
                os.path.join(carpeta_base, nombre),
                os.path.join(carpeta_base, nombre.replace("_", "")),
                os.path.join(carpeta_base, nombre.upper()),
                os.path.join("assets", "Heroes", "P_tierra", nombre)
            ]

            for numero in range(inicio, final + 1):

                imagen = None

                posibles_nombres = [
                    f"{numero}.png",
                    f"{numero:02d}.png",
                    f"{nombre}{numero}.png",
                    f"{nombre}_{numero}.png",
                    f"{nombre}{numero:02d}.png",
                    f"{nombre}_{numero:02d}.png"
                ]

                for carpeta in posibles_carpetas:

                    for nombre_archivo in posibles_nombres:

                        ruta = os.path.join(
                            carpeta,
                            nombre_archivo
                        )

                        if os.path.exists(ruta):

                            try:
                                imagen = pygame.image.load(
                                    ruta
                                ).convert_alpha()

                                imagen = pygame.transform.scale(
                                    imagen,
                                    (
                                        self.ancho_heroe,
                                        self.alto_heroe
                                    )
                                )

                                break

                            except pygame.error as error:
                                print(
                                    f"No se pudo cargar {ruta}: {error}"
                                )

                    if imagen is not None:
                        break

                if imagen is not None:
                    self.animaciones[nombre].append(imagen)

                else:
                    print(
                        f"No se encontró el fotograma {numero} "
                        f"de la animación {nombre}."
                    )

        # Si faltan imágenes de idle, se utiliza una imagen
        # disponible para evitar que el personaje quede sin imagen.
        if not self.animaciones["idle"]:

            for animacion in self.animaciones.values():

                if animacion:
                    self.animaciones["idle"] = [
                        animacion[0]
                    ]
                    break

        if not self.animaciones["idle"]:

            imagen = pygame.Surface(
                (self.ancho_heroe, self.alto_heroe),
                pygame.SRCALPHA
            )

            pygame.draw.rect(
                imagen,
                (100, 160, 90),
                (100, 30, 100, 220)
            )

            self.animaciones["idle"] = [imagen]

    # =====================================================
    # ANIMACIONES
    # =====================================================

    def cambiar_estado(self, nuevo_estado, reiniciar=False):

        if nuevo_estado not in self.animaciones:
            nuevo_estado = "idle"

        if not self.animaciones[nuevo_estado]:
            nuevo_estado = "idle"

        if self.estado != nuevo_estado or reiniciar:

            self.estado = nuevo_estado
            self.frame_index = 0
            self.tiempo_animacion = 0

            if nuevo_estado in (
                "1_atk",
                "2_atk",
                "3_atk",
                "air_atk",
                "sp_atk"
            ):
                self.atacando = True
                self.has_hit = False

            else:
                self.atacando = False

    def actualizar_animacion(self, dt):

        frames = self.animaciones.get(self.estado, [])

        if not frames:
            frames = self.animaciones["idle"]

        if not frames:
            return

        self.tiempo_animacion += dt

        velocidad = self.velocidad_animacion

        if self.estado == "roll":
            velocidad = 65

        elif self.estado in (
            "1_atk",
            "2_atk",
            "3_atk",
            "air_atk",
            "sp_atk"
        ):
            velocidad = 65

        while self.tiempo_animacion >= velocidad:

            self.tiempo_animacion -= velocidad
            self.frame_index += 1

            if self.frame_index >= len(frames):

                if self.estado in (
                    "1_atk",
                    "2_atk",
                    "3_atk",
                    "air_atk",
                    "sp_atk"
                ):

                    self.atacando = False
                    self.has_hit = False
                    self.cooldown_ataque = 250

                    self.cambiar_estado(
                        "idle" if self.en_suelo else "j_up"
                    )

                    break

                elif self.estado == "roll":

                    self.rodando = False

                    self.cambiar_estado(
                        "idle" if self.en_suelo else "j_up"
                    )

                    break

                else:
                    self.frame_index = 0

        frames = self.animaciones.get(self.estado, [])

        if not frames:
            frames = self.animaciones["idle"]

        if not frames:
            return

        indice = min(
            int(self.frame_index),
            len(frames) - 1
        )

        imagen = frames[indice]

        if not self.mirando_derecha:
            imagen = pygame.transform.flip(
                imagen,
                True,
                False
            )

        posicion_anterior = self.rect.midbottom

        self.image = imagen
        self.rect = self.image.get_rect()

        self.rect.midbottom = posicion_anterior

        self.actualizar_hitboxes()

    # =====================================================
    # HITBOXES Y HURTBOX
    # =====================================================

    def actualizar_hitboxes(self):

        self.hurtbox = pygame.Rect(
            self.rect.x + 100,
            self.rect.y + 60,
            100,
            220
        )

        if self.atacando:

            ancho_hitbox = 120
            alto_hitbox = 100

            if self.mirando_derecha:

                self.hitbox = pygame.Rect(
                    self.rect.right - 115,
                    self.rect.bottom - 190,
                    ancho_hitbox,
                    alto_hitbox
                )

            else:

                self.hitbox = pygame.Rect(
                    self.rect.left - 5,
                    self.rect.bottom - 190,
                    ancho_hitbox,
                    alto_hitbox
                )

        else:

            self.hitbox = pygame.Rect(
                0,
                0,
                0,
                0
            )

    def actualizar_hurtbox(self):
        self.actualizar_hitboxes()

    # =====================================================
    # SISTEMA DE DAÑO
    # =====================================================

    def take_damage(self, damage):

        if self.health <= 0:
            return

        if self.invulnerable or self.rodando:
            return

        if self.estado == "sp_atk":
            return

        if self.defendiendo:
            damage = max(1, int(damage * 0.35))

        self.health = max(
            0,
            self.health - damage
        )

        self.invulnerable = True
        self.tiempo_invulnerable = pygame.time.get_ticks()

    # =====================================================
    # CONTROLES
    # =====================================================

    def procesar_evento(self, evento):

        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_w:

                if self.en_suelo and not self.atacando:

                    self.velocidad_y = self.fuerza_salto
                    self.en_suelo = False

                    self.cambiar_estado("j_up", True)

            elif evento.key == pygame.K_q:

                if (
                    not self.rodando
                    and not self.atacando
                    and self.en_suelo
                ):

                    self.rodando = True
                    self.cambiar_estado("roll", True)

            elif evento.key == pygame.K_e:

                if (
                    not self.atacando
                    and self.cooldown_especial <= 0
                ):

                    self.cambiar_estado("sp_atk", True)
                    self.cooldown_especial = 1500

            elif evento.key == pygame.K_r:

                if not self.atacando:
                    self.defendiendo = True
                    self.cambiar_estado("defend", True)

        elif evento.type == pygame.KEYUP:

            if evento.key == pygame.K_r:

                self.defendiendo = False

                if not self.atacando and not self.rodando:
                    self.cambiar_estado(
                        "idle" if self.en_suelo else "j_up"
                    )

        elif evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1:

                if (
                    not self.atacando
                    and not self.rodando
                    and self.cooldown_ataque <= 0
                ):

                    if not self.en_suelo:
                        self.cambiar_estado("air_atk", True)

                    else:
                        self.cambiar_estado("1_atk", True)

            elif evento.button == 3:

                if not self.atacando:
                    self.defendiendo = True
                    self.cambiar_estado("defend", True)

        elif evento.type == pygame.MOUSEBUTTONUP:

            if evento.button == 3:

                self.defendiendo = False

                if not self.atacando and not self.rodando:
                    self.cambiar_estado(
                        "idle" if self.en_suelo else "j_up"
                    )

    # =====================================================
    # ACTUALIZACION DEL JUGADOR
    # =====================================================

    def update(
        self,
        scroll_x=0,
        transicion_realizada=False,
        limite_max_x=None,
        ancho_mundo=None
    ):

        dt = 16.67

        self.scroll_x_actual = scroll_x
        self.transicion_realizada = transicion_realizada

        self.limite_max_x = limite_max_x

        teclas = pygame.key.get_pressed()

        if self.health <= 0:

            self.atacando = False
            self.cambiar_estado("idle")

            self.actualizar_animacion(dt)
            return

        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= dt

        if self.cooldown_especial > 0:
            self.cooldown_especial -= dt

        if self.invulnerable:

            tiempo_actual = pygame.time.get_ticks()

            if (
                tiempo_actual - self.tiempo_invulnerable
                >= self.duracion_invulnerable
            ):

                self.invulnerable = False

        # -------------------------------------------------
        # MOVIMIENTO HORIZONTAL
        # -------------------------------------------------

        movimiento = 0

        bloqueado = (
            self.atacando
            or self.rodando
            or self.defendiendo
        )

        if not bloqueado:

            if teclas[pygame.K_a]:

                movimiento = -self.velocidad
                self.mirando_derecha = False

            elif teclas[pygame.K_d]:

                movimiento = self.velocidad
                self.mirando_derecha = True

        self.pos_x += movimiento

        if self.pos_x < 0:
            self.pos_x = 0

        if (
            self.limite_max_x is not None
            and self.pos_x > self.limite_max_x
        ):

            self.pos_x = self.limite_max_x

        # -------------------------------------------------
        # GRAVEDAD Y SALTO
        # -------------------------------------------------

        self.velocidad_y += self.gravedad
        self.pos_y += self.velocidad_y

        suelo_y = (
            self.posicion_suelo
            - self.alto_heroe
        )

        if self.pos_y >= suelo_y:

            self.pos_y = suelo_y
            self.velocidad_y = 0
            self.en_suelo = True

        else:
            self.en_suelo = False

        # -------------------------------------------------
        # COLISION CON PLATAFORMAS
        # -------------------------------------------------

        rect_mundo = pygame.Rect(
            int(self.pos_x),
            int(self.pos_y),
            self.ancho_heroe,
            self.alto_heroe
        )

        if self.velocidad_y >= 0:

            for plataforma in self.plataformas:

                if (
                    rect_mundo.colliderect(plataforma)
                    and rect_mundo.bottom - self.velocidad_y
                    <= plataforma.top + 5
                ):

                    rect_mundo.bottom = plataforma.top

                    self.pos_y = rect_mundo.y
                    self.velocidad_y = 0
                    self.en_suelo = True

                    break

        # -------------------------------------------------
        # POSICION Y ANIMACION
        # -------------------------------------------------

        self.rect.x = int(self.pos_x - scroll_x)
        self.rect.y = int(self.pos_y)

        if not self.atacando and not self.rodando:

            if self.defendiendo:

                if self.estado != "defend":
                    self.cambiar_estado("defend")

            elif not self.en_suelo:

                if self.estado != "j_up":
                    self.cambiar_estado("j_up")

            elif movimiento != 0:

                if self.estado != "run":
                    self.cambiar_estado("run")

            elif self.estado not in (
                "idle",
                "defend"
            ):

                self.cambiar_estado("idle")

        self.actualizar_animacion(dt)

        # Mantener la posición del sprite sincronizada con el mundo.
        self.rect.x = int(self.pos_x - scroll_x)
        self.rect.y = int(self.pos_y)

        self.actualizar_hitboxes()

    # =====================================================
    # DIBUJO
    # =====================================================

    def draw(self, pantalla):

        if self.invulnerable:

            tiempo = pygame.time.get_ticks()

            if (tiempo // 80) % 2 == 0:
                return

        pantalla.blit(
            self.image,
            self.rect
        )
