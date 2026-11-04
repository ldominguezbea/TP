import os

import pygame

from jugador1  import p_viento
from jugador2 import p_tierra
from jugador3 import p_fuego
from jugador4 import p_planta


PERSONAJE_SELECCIONADO_ENV = "REQUIEM_SELECTED_CHARACTER"
PERSONAJE_POR_DEFECTO = "Fei Liang"


class _AdaptadorJugadorNivel:
    def __init__(self, x, y, posicion_suelo):
        super().__init__(x, y, posicion_suelo)
        self.plataformas = []
        self.plataforma_actual = None
        self.plataforma_ignorada = None
        self.scroll_x_actual = 0
        self.enemigos_golpeados = set()
        self._has_hit = False

    @property
    def health(self):
        return self.vida

    @health.setter
    def health(self, value):
        self.vida = value

    @property
    def max_health(self):
        return self.vida_maxima

    @max_health.setter
    def max_health(self, value):
        self.vida_maxima = value

    @property
    def has_hit(self):
        return self._has_hit

    @has_hit.setter
    def has_hit(self, value):
        self._has_hit = value

    def take_damage(self, damage):
        self.recibir_dano(damage)

    def procesar_evento(self, evento):
        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_s
            and self.plataforma_actual is not None
        ):
            self.plataforma_ignorada = self.plataforma_actual
            self.plataforma_actual = None
            self.en_suelo = False
            self.velocidad_y = max(2, self.gravedad)
            return

        if (
            evento.type == pygame.KEYDOWN
            and evento.key in (pygame.K_f, pygame.K_e)
        ) or (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == pygame.BUTTON_LEFT
        ):
            self._has_hit = False
            self.enemigos_golpeados.clear()

        super().procesar_evento(evento)

    def aplicar_gravedad(self):
        bottom_anterior = self.rect.bottom
        self.en_suelo = False
        self.plataforma_actual = None
        self.velocidad_y += self.gravedad
        self.rect.y += self.velocidad_y

        if self.velocidad_y >= 0:
            for plataforma in self.plataformas:
                plataforma_pantalla = plataforma.move(-self.scroll_x_actual, 0)
                if self.plataforma_ignorada is plataforma:
                    if self.rect.bottom >= plataforma_pantalla.bottom:
                        self.plataforma_ignorada = None
                    else:
                        continue

                zona_suelo = plataforma_pantalla.inflate(-20, 0)
                pisa_plataforma = (
                    bottom_anterior <= zona_suelo.top
                    and self.rect.bottom >= zona_suelo.top
                    and self.rect.centerx + 30 > zona_suelo.left
                    and self.rect.centerx - 30 < zona_suelo.right
                )
                if pisa_plataforma:
                    self.rect.bottom = zona_suelo.top
                    self.velocidad_y = 0
                    self.en_suelo = True
                    self.plataforma_actual = plataforma
                    break

        if not self.en_suelo and self.rect.bottom >= self.posicion_suelo:
            self.rect.bottom = self.posicion_suelo
            self.velocidad_y = 0
            self.en_suelo = True

    def actualizar_hitboxes(self):
        self.actualizar_hurtbox()
        if self._hitbox_uses_scroll:
            self.actualizar_hitbox(self.scroll_x_actual)
        else:
            self.actualizar_hitbox()

    def update(
        self,
        scroll_x,
        transicion_realizada=False,
        limite_max_x=None,
        limite_min_x=None,
    ):
        self.scroll_x_actual = scroll_x
        self.ancho_mundo = self._ancho_mundo
        super().update(scroll_x, self._ancho_mundo)

        if transicion_realizada and scroll_x == 0:
            limite_izquierdo = 80
            limite_derecho = self._ancho_pantalla - 80
        elif transicion_realizada:
            limite_izquierdo = scroll_x + 80
            limite_derecho = self._ancho_mundo - 80
        else:
            limite_izquierdo = scroll_x + 80
            limite_derecho = (
                limite_max_x
                if limite_max_x is not None
                else self._ancho_mundo - 80
            )

        if limite_min_x is not None:
            limite_izquierdo = max(limite_izquierdo, limite_min_x)

        self.pos_x = max(limite_izquierdo, min(self.pos_x, limite_derecho))
        self.rect.centerx = int(self.pos_x - scroll_x)
        self.actualizar_hitboxes()


_PERSONAJES = {
    "Fei Liang": (p_viento, True),
    "Korg": (p_tierra, True),
    "Escanor": (p_fuego, False),
    "Diana": (p_planta, False),
}


def personaje_seleccionado():
    nombre = os.environ.get(
        PERSONAJE_SELECCIONADO_ENV,
        PERSONAJE_POR_DEFECTO,
    )
    if nombre not in _PERSONAJES:
        raise ValueError(f"Personaje seleccionado no válido: {nombre}")
    return nombre


def crear_jugador(x, y, posicion_suelo, ancho_mundo, ancho_pantalla):
    nombre = personaje_seleccionado()
    clase_jugador, usa_scroll_en_hitbox = _PERSONAJES[nombre]
    clase_adaptada = type(
        f"{clase_jugador.__name__}Nivel",
        (_AdaptadorJugadorNivel, clase_jugador),
        {
            "_hitbox_uses_scroll": usa_scroll_en_hitbox,
            "_ancho_mundo": ancho_mundo,
            "_ancho_pantalla": ancho_pantalla,
        },
    )
    return clase_adaptada(x, y, posicion_suelo)
