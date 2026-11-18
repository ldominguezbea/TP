from config import BASE_DIR, SCREEN_HEIGHT, SCREEN_WIDTH
from comic_viewer import ComicViewer


def prologue():
    """Crea el lector guiado para las páginas del prólogo."""
    comic_directory = BASE_DIR / "assets" / "Prologo"
    return ComicViewer((SCREEN_WIDTH, SCREEN_HEIGHT), comic_directory)
