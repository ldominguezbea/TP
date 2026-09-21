import pygame
import os
import sys

pygame.init()

# Configuración de pantalla
ANCHO = 1290
ALTO = 800
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Prólogo")

# 1. Rutas exactas basadas en la estructura de tu proyecto
rutas_imagenes = [
    os.path.join("assets", "Prologo", "Pag_1.png"),
    os.path.join("assets", "Prologo", "Pag_2.png"),
    os.path.join("assets", "Prologo", "Pag_3.png"),
    os.path.join("assets", "Prologo", "Pag_4.png"),
    os.path.join("assets", "Prologo", "Pag_5.png"),
    os.path.join("assets", "Prologo", "Pag_6.png")
]

# 2. Cargar y escalar todas las páginas
imagenes = []
for ruta in rutas_imagenes:
    try:
        img_original = pygame.image.load(ruta).convert()
        img_escalada = pygame.transform.scale(img_original, (ANCHO, ALTO))
        imagenes.append(img_escalada)
    except pygame.error as e:
        print(f"Error al cargar la imagen {ruta}: {e}")

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