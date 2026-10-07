import pygame
import os


# ============================================================
# FLECHA AÉREA
# ============================================================

class FlechaAerea(pygame.sprite.Sprite):

    def __init__(
        self,
        x,
        y,
        posicion_suelo,
        mirando_derecha
    ):

        super().__init__()

        # ====================================================
        # CONFIGURACIÓN
        # ====================================================

        self.posicion_suelo = posicion_suelo

        # Dirección del personaje al lanzar
        self.mirando_derecha = mirando_derecha

        # ====================================================
        # POSICIÓN REAL
        # ====================================================

        self.pos_x = float(x)
        self.pos_y = float(y)

        # ====================================================
        # VELOCIDAD
        # ====================================================

        # Movimiento horizontal
        if self.mirando_derecha:

            self.velocidad_x = 7

        else:

            self.velocidad_x = -7

        # Movimiento vertical inicial
        self.velocidad_y = 4

        # Gravedad de la flecha
        self.gravedad = 0.35

        # ====================================================
        # ESTADO
        # ====================================================

        self.estado = "flecha"

        # ====================================================
        # ANIMACIÓN
        # ====================================================

        self.frame_index = 0

        self.velocidad_animacion = 0.25

        # ====================================================
        # RUTAS
        # ====================================================

        base_path = os.path.join(
            "assets",
            "Heroes",
            "P_planta",
            "projectiles_and_effects"
        )

        ruta_flecha = os.path.join(
            base_path,
            "diagonal_arrow"
        )

        ruta_hit = os.path.join(
            base_path,
            "diagonal_arrow_hit"
        )

        # ====================================================
        # CARGAR FLECHA
        # ====================================================

        self.image = pygame.image.load(
            os.path.join(
                ruta_flecha,
                "diagonal_arrow_.png"
            )
        ).convert_alpha()

        # ====================================================
        # TAMAÑO DE LA FLECHA
        # ====================================================

        self.image = pygame.transform.scale(
            self.image,
            (120, 120)
        )

        # ====================================================
        # DIRECCIÓN DE LA FLECHA
        # ====================================================

        if not self.mirando_derecha:

            self.image = pygame.transform.flip(
                self.image,
                True,
                False
            )

        # ====================================================
        # RECTÁNGULO
        # ====================================================

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        # ====================================================
        # ANIMACIÓN DE IMPACTO
        # ====================================================

        self.animacion_hit = []

        for i in range(1, 7):

            img = pygame.image.load(
                os.path.join(
                    ruta_hit,
                    f"diagonal_arrow_hit_{i}.png"
                )
            ).convert_alpha()

            img = pygame.transform.scale(
                img,
                (180, 180)
            )

            self.animacion_hit.append(
                img
            )

    # ========================================================
    # ACTUALIZAR FLECHA
    # ========================================================

    def update(
        self,
        scroll_x=0
    ):

        # ====================================================
        # FLECHA VOLANDO
        # ====================================================

        if self.estado == "flecha":

            # ------------------------------------------------
            # MOVIMIENTO HORIZONTAL
            # ------------------------------------------------

            self.pos_x += self.velocidad_x

            # ------------------------------------------------
            # MOVIMIENTO VERTICAL
            # ------------------------------------------------

            self.pos_y += self.velocidad_y

            # ------------------------------------------------
            # GRAVEDAD
            # ------------------------------------------------

            self.velocidad_y += self.gravedad

            # ------------------------------------------------
            # POSICIÓN EN PANTALLA
            # ------------------------------------------------

            self.rect.centerx = int(
                self.pos_x - scroll_x
            )

            self.rect.centery = int(
                self.pos_y
            )

            # =================================================
            # COMPROBAR SUELO
            # =================================================

            if self.rect.bottom >= self.posicion_suelo:

                # Colocar exactamente sobre el suelo
                self.rect.bottom = (
                    self.posicion_suelo
                )

                # Cambiar a animación de impacto
                self.estado = "hit"

                # Empezar desde el primer frame
                self.frame_index = 0

                self.image = (
                    self.animacion_hit[0]
                )

                # Mantener el centro horizontal
                self.rect.centerx = int(
                    self.pos_x - scroll_x
                )

                # Colocar el impacto sobre el suelo
                self.rect.bottom = (
                    self.posicion_suelo
                )

        # ====================================================
        # ANIMACIÓN DE IMPACTO
        # ====================================================

        elif self.estado == "hit":

            # Avanzar animación
            self.frame_index += (
                self.velocidad_animacion
            )

            # =================================================
            # TERMINÓ EL IMPACTO
            # =================================================

            if self.frame_index >= len(
                self.animacion_hit
            ):

                self.kill()

                return

            # =================================================
            # FRAME ACTUAL
            # =================================================

            self.image = self.animacion_hit[
                int(self.frame_index)
            ]

            # Mantener el impacto sobre el suelo
            self.rect.bottom = (
                self.posicion_suelo
            )
