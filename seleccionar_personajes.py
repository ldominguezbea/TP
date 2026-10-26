import os
import sys
import pygame

ANCHO, ALTO = 1000, 600
FPS = 60

# Las imágenes van en una carpeta "imagenes" al lado de este archivo
CARPETA = os.path.dirname(os.path.abspath(__file__))
CARPETA_IMG = os.path.join(CARPETA, "imagenes")

PERSONAJES = [
    {"nombre": "Diana",     "elemento": "Planta", "imagen": "diana.png",     "color": (76, 175, 80)},
    {"nombre": "Korg",      "elemento": "Roca",   "imagen": "korg.png",      "color": (141, 110, 99)},
    {"nombre": "Fei Liang", "elemento": "Viento", "imagen": "fei_liang.png", "color": (100, 181, 246)},
    {"nombre": "Escanor",   "elemento": "Fuego",  "imagen": "escanor.png",   "color": (255, 112, 67)},
]

# Tamaño de cada carta y de la zona de la imagen
CARTA_W, CARTA_H = 200, 340
SEPARACION = 30
IMG_CAJA = (CARTA_W - 20, 220)

FONDO = (24, 26, 33)
BLANCO = (245, 245, 245)
GRIS = (60, 63, 75)


def cargar_imagen(personaje):
    """Carga la imagen del personaje; si no existe, crea un cuadro de color con su inicial."""
    ruta = os.path.join(CARPETA_IMG, personaje["imagen"])
    try:
        img = pygame.image.load(ruta).convert_alpha()
        w, h = img.get_size()
        escala = min(IMG_CAJA[0] / w, IMG_CAJA[1] / h)
        return pygame.transform.smoothscale(img, (int(w * escala), int(h * escala)))
    except (pygame.error, FileNotFoundError):
        sup = pygame.Surface(IMG_CAJA, pygame.SRCALPHA)
        pygame.draw.rect(sup, personaje["color"], sup.get_rect(), border_radius=12)
        letra = pygame.font.SysFont("arial", 90, bold=True).render(personaje["nombre"][0], True, BLANCO)
        sup.blit(letra, letra.get_rect(center=(IMG_CAJA[0] // 2, IMG_CAJA[1] // 2)))
        return sup


def crear_cartas():
    total = len(PERSONAJES) * CARTA_W + (len(PERSONAJES) - 1) * SEPARACION
    x0 = (ANCHO - total) // 2
    y0 = 130
    cartas = []
    for i, p in enumerate(PERSONAJES):
        rect = pygame.Rect(x0 + i * (CARTA_W + SEPARACION), y0, CARTA_W, CARTA_H)
        cartas.append({"personaje": p, "rect": rect, "imagen": cargar_imagen(p)})
    return cartas


def seleccionar_personaje(pantalla):
    """Muestra la pantalla de selección y devuelve el diccionario del personaje elegido."""
    reloj = pygame.time.Clock()
    f_titulo = pygame.font.SysFont("arial", 44, bold=True)
    f_nombre = pygame.font.SysFont("arial", 26, bold=True)
    f_elem = pygame.font.SysFont("arial", 20)
    f_boton = pygame.font.SysFont("arial", 26, bold=True)

    cartas = crear_cartas()
    boton = pygame.Rect(0, 0, 220, 54)
    boton.center = (ANCHO // 2, 540)

    seleccionada = None  # índice de la carta elegida

    while True:
        pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if evento.key == pygame.K_RIGHT:
                    seleccionada = 0 if seleccionada is None else (seleccionada + 1) % len(cartas)
                if evento.key == pygame.K_LEFT:
                    seleccionada = len(cartas) - 1 if seleccionada is None else (seleccionada - 1) % len(cartas)
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and seleccionada is not None:
                    return cartas[seleccionada]["personaje"] | {"imagen_surf": cartas[seleccionada]["imagen"]}

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for i, c in enumerate(cartas):
                    if c["rect"].collidepoint(evento.pos):
                        seleccionada = i
                if boton.collidepoint(evento.pos) and seleccionada is not None:
                    return cartas[seleccionada]["personaje"] | {"imagen_surf": cartas[seleccionada]["imagen"]}

        # ---- Dibujo ----
        pantalla.fill(FONDO)
        titulo = f_titulo.render("Elige tu personaje", True, BLANCO)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 65)))

        for i, c in enumerate(cartas):
            p, r = c["personaje"], c["rect"]
            encima = r.collidepoint(pos)
            elegida = i == seleccionada

            # Las cartas "suben" un poco al pasar el mouse o al ser elegidas
            r_dib = r.move(0, -10 if (encima or elegida) else 0)

            pygame.draw.rect(pantalla, GRIS, r_dib, border_radius=16)
            borde = p["color"] if (elegida or encima) else (90, 93, 105)
            pygame.draw.rect(pantalla, borde, r_dib, width=5 if elegida else 3, border_radius=16)

            img = c["imagen"]
            pantalla.blit(img, img.get_rect(center=(r_dib.centerx, r_dib.y + 20 + IMG_CAJA[1] // 2)))

            nombre = f_nombre.render(p["nombre"], True, BLANCO)
            pantalla.blit(nombre, nombre.get_rect(center=(r_dib.centerx, r_dib.y + 275)))
            elem = f_elem.render(p["elemento"], True, p["color"])
            pantalla.blit(elem, elem.get_rect(center=(r_dib.centerx, r_dib.y + 308)))

        # Botón confirmar
        activo = seleccionada is not None
        color_boton = (76, 175, 80) if activo else (70, 72, 82)
        if activo and boton.collidepoint(pos):
            color_boton = (102, 200, 106)
        pygame.draw.rect(pantalla, color_boton, boton, border_radius=12)
        txt = f_boton.render("Confirmar", True, BLANCO if activo else (130, 132, 140))
        pantalla.blit(txt, txt.get_rect(center=boton.center))

        pygame.display.flip()
        reloj.tick(FPS)


if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Selección de personajes")

    elegido = seleccionar_personaje(pantalla)
    print(f"Personaje elegido: {elegido['nombre']} ({elegido['elemento']})")

    pygame.quit()