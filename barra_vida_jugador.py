from pathlib import Path

import pygame


_RUTA_BARRA = (
    Path(__file__).resolve().parent
    / "assets"
    / "barras de vida"
    / "Barra_de_vida_jugador.png"
)
_imagen_barra = None
_barra_cargada = False
_fuente_barra = None


def dibujar_barra_vida_jugador(screen, player):
    global _imagen_barra, _barra_cargada, _fuente_barra

    if not _barra_cargada:
        if _RUTA_BARRA.is_file():
            _imagen_barra = pygame.image.load(str(_RUTA_BARRA)).convert_alpha()
        _barra_cargada = True

    if _fuente_barra is None:
        _fuente_barra = pygame.font.SysFont("Arial", 16, bold=True)

    porcentaje = max(
        0.0,
        min(
            1.0,
            player.health / player.max_health if player.max_health > 0 else 0,
        ),
    )

    if _imagen_barra is not None:
        ancho_barra = 280
        alto_barra = int(
            _imagen_barra.get_height() * ancho_barra / _imagen_barra.get_width()
        )
        barra = pygame.transform.scale(_imagen_barra, (ancho_barra, alto_barra))
        x, y = 25, 20
        x_relleno = x + int(ancho_barra * 0.08)
        y_relleno = y + int(alto_barra * 0.44)
        ancho_relleno = int(ancho_barra * 0.84)
        alto_relleno = int(alto_barra * 0.40)
        ancho_actual = int(ancho_relleno * porcentaje)

        pygame.draw.rect(
            screen,
            (20, 5, 5),
            (x_relleno, y_relleno, ancho_relleno, alto_relleno),
        )
        if ancho_actual > 0:
            pygame.draw.rect(
                screen,
                (190, 30, 30),
                (x_relleno, y_relleno, ancho_actual, alto_relleno),
            )
            pygame.draw.rect(
                screen,
                (240, 90, 90),
                (x_relleno, y_relleno, ancho_actual, max(1, alto_relleno // 3)),
            )

        screen.blit(barra, (x, y))
        texto = _fuente_barra.render(
            f"JUGADOR: {int(player.health)} / {player.max_health}",
            True,
            (255, 255, 255),
        )
        screen.blit(texto, (x + 5, y + alto_barra + 4))
        return

    ancho_barra, alto_barra = 200, 18
    x, y = 30, 30
    pygame.draw.rect(
        screen,
        (10, 10, 10),
        (x - 2, y - 2, ancho_barra + 4, alto_barra + 4),
    )
    if porcentaje > 0:
        pygame.draw.rect(
            screen,
            (190, 30, 30),
            (x, y, int(ancho_barra * porcentaje), alto_barra),
        )
    pygame.draw.rect(
        screen,
        (200, 200, 200),
        (x - 2, y - 2, ancho_barra + 4, alto_barra + 4),
        2,
    )
    texto = _fuente_barra.render(
        f"JUGADOR: {int(player.health)} / {player.max_health}",
        True,
        (255, 255, 255),
    )
    screen.blit(texto, (x, 8))
