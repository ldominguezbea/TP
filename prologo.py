from config import BASE_DIR, SCREEN_HEIGHT, SCREEN_WIDTH
from comic_scroll import ScrollComic, cargar_paginas

COMIC_DIRECTORY = BASE_DIR / "assets" / "Prologo"


def prologue():
    """Crea el lector del prólogo: cómic con scroll vertical (rueda + ENTER al final).

    Si la carpeta no tiene imágenes, vuelve al lector guiado anterior (ComicViewer).
    """
    paginas = cargar_paginas(COMIC_DIRECTORY)

    if paginas:
        return ScrollComic(paginas, (SCREEN_WIDTH, SCREEN_HEIGHT))

    print(f"[COMIC] No hay páginas en {COMIC_DIRECTORY}; se usa el lector anterior.")
    from comic_viewer import ComicViewer
    return ComicViewer((SCREEN_WIDTH, SCREEN_HEIGHT), COMIC_DIRECTORY)