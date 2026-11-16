import os
import runpy

import pygame

from jugador_nivel4 import JugadorSeleccionadoNivel4
from menu_pausa import NivelIntegradoFinalizado, pausar_juego


NIVEL_INTEGRADO = __name__ == "_nivel4_integrado"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANCHO, ALTO = 1350, 700
SUELO = 610
CAMBIO_PUERTA = 135
nivel_completado = False

pygame.init()
pantalla = pygame.display.get_surface()
if pantalla is None:
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 4 - Fortaleza Infernal")

reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("Arial", 24, bold=True)
fuente_ui = pygame.font.SysFont("Arial", 18, bold=True)

CARPETA_IMAGENES = os.path.join(BASE_DIR, "imagenes", "Nivel4")


def cargar_imagen_nivel4(nombre_archivo):
    ruta = os.path.join(CARPETA_IMAGENES, nombre_archivo)
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró la imagen del nivel 4: {ruta}")
    imagen = pygame.image.load(ruta).convert()
    return pygame.transform.scale(imagen, (ANCHO, ALTO))


def cerrar_nivel(action="exit"):
    if NIVEL_INTEGRADO:
        raise NivelIntegradoFinalizado(nivel_completado, action)
    pygame.quit()
    raise SystemExit


def mostrar_comic(nombre_archivo, instruccion="PRESIONA ENTER PARA CONTINUAR"):
    imagen = cargar_imagen_nivel4(nombre_archivo)
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                cerrar_nivel("exit")
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False
                elif evento.key == pygame.K_ESCAPE:
                    accion = pausar_juego(
                        pantalla,
                        devolver_accion=NIVEL_INTEGRADO,
                    )
                    if NIVEL_INTEGRADO and accion in ("menu", "exit"):
                        cerrar_nivel(accion)

        pantalla.blit(imagen, (0, 0))
        texto = fuente_ui.render(instruccion, True, (255, 255, 255))
        caja = texto.get_rect(center=(ANCHO // 2, ALTO - 28))
        fondo_texto = pygame.Surface((caja.width + 28, caja.height + 16))
        fondo_texto.fill((0, 0, 0))
        fondo_texto.set_alpha(190)
        pantalla.blit(fondo_texto, (caja.x - 14, caja.y - 8))
        pantalla.blit(texto, caja)
        pygame.display.flip()
        reloj.tick(60)


def iniciar_batalla(jugador):
    ruta_batalla = os.path.join(BASE_DIR, "Ignis_jefe_batalla.py")
    resultado = runpy.run_path(
        ruta_batalla,
        run_name=(
            "_nivel4_boss_integrado"
            if NIVEL_INTEGRADO
            else "__main__"
        ),
        init_globals={"jugador_seleccionado_nivel4": jugador},
    )
    return bool(resultado.get("nivel_completado", False))


def recorrer_escenarios(jugador):
    fondos = (
        cargar_imagen_nivel4("Fortaleza infernal entre ríos de lava.png"),
        cargar_imagen_nivel4("Pasillo gótico ante un paisaje volcánico.png"),
    )
    entradas = (1090, 1240)
    escenario = 0
    ejecutando = True

    while ejecutando:
        dt = reloj.tick(60) / 1000.0
        cerca_de_puerta = abs(jugador.pos_x - entradas[escenario]) <= CAMBIO_PUERTA

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                cerrar_nivel("exit")
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                accion = pausar_juego(
                    pantalla,
                    devolver_accion=NIVEL_INTEGRADO,
                )
                if NIVEL_INTEGRADO and accion in ("menu", "exit"):
                    cerrar_nivel(accion)
            elif (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_c
                and cerca_de_puerta
            ):
                if escenario == 0:
                    escenario = 1
                    jugador.set_position(170, SUELO)
                else:
                    mostrar_comic("Trono demoníaco en pixel art.png")
                    mostrar_comic(
                        "Señor de las llamas pixelado.png",
                        "PRESIONA ENTER PARA INICIAR LA BATALLA",
                    )
                    jugador.set_position(200, 590)
                    return iniciar_batalla(jugador)
            else:
                jugador.procesar_evento(evento)

        jugador.update(dt)
        pantalla.blit(fondos[escenario], (0, 0))
        jugador.draw(pantalla)

        ayuda = fuente_ui.render("A / D: MOVERSE   W: SALTAR", True, (255, 245, 220))
        pantalla.blit(ayuda, (28, 24))
        if cerca_de_puerta:
            aviso = fuente.render("PRESIONA C PARA ENTRAR", True, (255, 225, 160))
            caja = aviso.get_rect(center=(entradas[escenario], SUELO - 135))
            sombra = aviso.get_rect(center=(entradas[escenario], SUELO - 135))
            pygame.draw.rect(pantalla, (20, 8, 8), sombra.inflate(24, 16), border_radius=8)
            pantalla.blit(aviso, caja)

        pygame.display.flip()

    return False


def main():
    mostrar_comic("nivel4_1.png")
    mostrar_comic("nivel4_2.png")
    jugador = JugadorSeleccionadoNivel4(170, SUELO, ANCHO)
    return recorrer_escenarios(jugador)


if __name__ in ("__main__", "_nivel4_integrado"):
    try:
        nivel_completado = main()
    except NivelIntegradoFinalizado:
        raise
    except SystemExit:
        if NIVEL_INTEGRADO:
            raise
    finally:
        if not NIVEL_INTEGRADO and pygame.get_init():
            pygame.quit()
