import math
from pathlib import Path

import pygame


TIEMPO_CARGA_ENERGIA_MS = 35_000
SALTOS_MAXIMOS = 2
RUTA_BARRA_ENERGIA = (
    Path(__file__).resolve().parent
    / "assets"
    / "barras de vida"
    / "Barra_de_energia_jugador.png"
)

_barra_energia = None
_fuente_energia = None


def _cargar_barra_energia():
    global _barra_energia
    if _barra_energia is None:
        if not RUTA_BARRA_ENERGIA.is_file():
            raise FileNotFoundError(
                f"No se encontró la barra de energía del jugador: {RUTA_BARRA_ENERGIA}"
            )
        _barra_energia = pygame.image.load(str(RUTA_BARRA_ENERGIA)).convert_alpha()
    return _barra_energia


def _obtener_fuente_energia():
    global _fuente_energia
    if _fuente_energia is None:
        _fuente_energia = pygame.font.SysFont("Arial", 16, bold=True)
    return _fuente_energia


class HabilidadesJugador:
    def bloquea_ataque_en_direccion(self, atacante):
        if atacante is None:
            return False

        rect_atacante = (
            atacante
            if isinstance(atacante, pygame.Rect)
            else getattr(atacante, "rect", None)
        )
        if rect_atacante is None:
            rect_atacante = getattr(atacante, "hitbox", None)

        if isinstance(rect_atacante, pygame.Rect):
            atacante_x = rect_atacante.centerx
        else:
            atacante_x = getattr(atacante, "pos_x", None)
            if atacante_x is None:
                return False

        jugador_x = getattr(self, "pos_x", None)
        if jugador_x is None:
            rect_jugador = getattr(
                self, "hurtbox", getattr(self, "rect", None)
            )
            if rect_jugador is None:
                return False
            jugador_x = rect_jugador.centerx

        if atacante_x == jugador_x:
            return False

        return (atacante_x > jugador_x) == self.mirando_derecha

    def inicializar_habilidades(self, color_energia):
        self.saltos_restantes = SALTOS_MAXIMOS
        self.color_energia = color_energia
        self.energia_cargada_ms = TIEMPO_CARGA_ENERGIA_MS
        self.energia_ultima_actualizacion = pygame.time.get_ticks()

    @property
    def energia_lista(self):
        return self.energia_cargada_ms >= TIEMPO_CARGA_ENERGIA_MS

    def registrar_salto(self):
        if self.saltos_restantes <= 0:
            return False
        self.saltos_restantes -= 1
        return True

    def restaurar_saltos(self):
        self.saltos_restantes = SALTOS_MAXIMOS

    def actualizar_energia(self):
        ahora = pygame.time.get_ticks()
        transcurrido = min(
            100,
            max(0, ahora - self.energia_ultima_actualizacion),
        )
        self.energia_ultima_actualizacion = ahora
        self.energia_cargada_ms = min(
            TIEMPO_CARGA_ENERGIA_MS,
            self.energia_cargada_ms + transcurrido,
        )

    def usar_energia(self):
        if not self.energia_lista:
            return False
        self.energia_cargada_ms = 0
        self.energia_ultima_actualizacion = pygame.time.get_ticks()
        return True

    def dibujar_barra_energia(self, superficie, x=25, y=126):
        barra = _cargar_barra_energia()
        porcentaje = max(
            0,
            min(1, self.energia_cargada_ms / TIEMPO_CARGA_ENERGIA_MS),
        )
        interior = pygame.Rect(x + 14, y + 12, 32, 32)
        pygame.draw.ellipse(superficie, (20, 20, 26), interior)

        altura_carga = round(interior.height * porcentaje)
        if altura_carga > 0:
            area_carga = pygame.Rect(
                interior.left,
                interior.bottom - altura_carga,
                interior.width,
                altura_carga,
            )
            clip_anterior = superficie.get_clip()
            try:
                superficie.set_clip(clip_anterior.clip(area_carga))
                pygame.draw.ellipse(superficie, self.color_energia, interior)
            finally:
                superficie.set_clip(clip_anterior)

        superficie.blit(barra, (x, y))

        texto = (
            "E: LISTO"
            if self.energia_lista
            else f"E: {math.ceil((TIEMPO_CARGA_ENERGIA_MS - self.energia_cargada_ms) / 1000)}s"
        )
        indicador = _obtener_fuente_energia().render(texto, True, (255, 255, 255))
        superficie.blit(
            indicador,
            (
                x + barra.get_width() + 8,
                y + barra.get_height() // 2 - indicador.get_height() // 2,
            ),
        )
