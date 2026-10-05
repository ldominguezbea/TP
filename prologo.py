import pygame
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
