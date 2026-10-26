import pygame
from config import BASE_DIR, SCREEN_WIDTH, SCREEN_HEIGHT


def prologue():
    """Carga las páginas narrativas del prólogo en su orden de lectura."""
    carpeta = BASE_DIR / "assets" / "sprites" / "Prologo"
    nombres_imagenes = (
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "Pag_6.png",
    )
    imagenes = []

    for nombre in nombres_imagenes:
        ruta = carpeta / nombre
        if ruta.exists():
            try:
                imagen = pygame.image.load(str(ruta)).convert()
                imagenes.append(
                    pygame.transform.scale(imagen, (SCREEN_WIDTH, SCREEN_HEIGHT))
                )
            except pygame.error as e:
                print(f"[PROLOGO] Error al cargar la imagen {ruta}: {e}")
        else:
            print(f"[PROLOGO] No se encontró la imagen {ruta}.")

    if not imagenes:
        fondo_respaldo = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fondo_respaldo.fill((35, 35, 45))
        imagenes.append(fondo_respaldo)

    return imagenes