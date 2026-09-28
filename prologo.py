def prologue():
    from animacion_menu import GAME_WIDTH, GAME_HEIGHT
    import pygame
    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ruta_imagen = os.path.join(BASE_DIR, "fondo_escuela.jpg")

    try:
        school_bg = pygame.image.load(ruta_imagen).convert_alpha()
        school_bg = pygame.transform.scale(school_bg, (GAME_WIDTH, GAME_HEIGHT))
        print("-> La imagen 'fondo_escuela.jpg' se cargó con éxito.")
    except FileNotFoundError:
        print("-> ADVERTENCIA: No se encontró la imagen. Se usará un fondo provisorio.")
        school_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        school_bg.fill((50, 50, 60))
