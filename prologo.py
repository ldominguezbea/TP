import pygame
from pathlib import Path
from config import BASE_DIR, SCREEN_WIDTH, SCREEN_HEIGHT

def prologue():
    """Carga y devuelve la imagen del prólogo adaptada a la pantalla completa."""
    rutas_posibles = [
        BASE_DIR / "fondo_escuela.jpg",
        BASE_DIR / "assets" / "fondo_escuela.jpg",
        BASE_DIR / "imagenes" / "fondo_escuela.jpg",
        BASE_DIR / "assets" / "sprites" / "fondo_escuela.jpg"
    ]
    
    imagen_cargada = None
    for ruta in rutas_posibles:
        if ruta.exists():
            try:
                imagen_cargada = pygame.image.load(str(ruta)).convert()
                break
            except pygame.error as e:
                print(f"[PROLOGO] Error al cargar la imagen {ruta}: {e}")

    if imagen_cargada:
        # Escala la imagen directamente a la pantalla de alta resolución
        school_bg = pygame.transform.scale(imagen_cargada, (SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        print("[PROLOGO] No se encontró fondo_escuela.jpg. Generando fondo de respaldo.")
        school_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        school_bg.fill((35, 35, 45))

    return school_bg