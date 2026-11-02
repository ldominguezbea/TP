import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

import Nivel3


def main():
    heroe = Nivel3.Jugador(180, Nivel3.POSICION_SUELO)
    Nivel3.ejecutar_batalla_ciclope(
        Nivel3.pantalla,
        heroe,
        Nivel3.fondo_batalla,
    )
    Nivel3.pygame.quit()


if __name__ == "__main__":
    main()
