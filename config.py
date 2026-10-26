from pathlib import Path

# Configuraciones globales de resolución
SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 720
GAME_WIDTH = 320
GAME_HEIGHT = 180

BASE_DIR = Path(__file__).resolve().parent

def abrir_archivo(ruta):
    """Función de apertura obligatoria sin métodos .load() binarios"""
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                pass
    except FileNotFoundError:
        print(f"No se encontro el archivo en la ruta enviada: {ruta}")
