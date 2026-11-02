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

indice_imagen = 0

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        # Avanzar página al presionar Enter
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                indice_imagen += 1
                
                # Al pasar la última página (Pag_6.png), cierra el prólogo
                if indice_imagen >= len(imagenes):
                    ejecutando = False

    ventana.fill((0, 0, 0))

    # Dibujar la página actual SOLO si el índice está dentro del rango
    if imagenes and indice_imagen < len(imagenes):
        ventana.blit(imagenes[indice_imagen], (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()

from pathlib import Path
from animacion_menu import GAME_WIDTH, GAME_HEIGHT

BASE_DIR = Path(__file__).resolve().parent

def abrir_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                print(linea.strip().split(","))
    except FileNotFoundError:
        print("No se encontro un archivo en la ruta enviada.")

def prologue():
    ruta_mapa = BASE_DIR / "fondo_escuela.txt" # Cambiado para que lea la metadata del fondo escuela
    
    # Llama obligatoriamente a la funcion de apertura personalizada
    abrir_archivo(ruta_mapa)
    
    # Instancia de forma nativa la superficie grafica del escenario escolar sin .load()
    school_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    school_bg.fill((35, 35, 45))
    
    # Elemento visual representativo de la escuela
    pygame.draw.rect(school_bg, (80, 80, 95), (50, 40, 220, 140)) 
    return school_bg

