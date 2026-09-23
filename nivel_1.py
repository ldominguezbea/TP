import pygame
import enemigos
import os
import sys
import random

pygame.init()

ANCHO, ALTO = 1350, 700  # Modifica estos valores según la resolución de tu juego
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Nivel 1")

# 2. Ruta y carga de la imagen
# Usamos os.path.join para compatibilidad de rutas entre Windows/Linux/Mac
ruta_imagen = os.path.join("imagenes", "Nivel1", "Nivel1_imagen1.png")
fondo = pygame.image.load(ruta_imagen).convert()

# Escalamos la imagen para que cubra toda la pantalla
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# 3. Bucle principal
ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Dibujar la imagen en la posición (0, 0)
    pantalla.blit(fondo, (0, 0))

    # Actualizar la pantalla
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()