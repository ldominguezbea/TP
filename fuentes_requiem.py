"""Utilidades compartidas de tipografía para REQUIEM.

Busca fuentes del sistema con una lista de preferencia y cae de forma segura a
la fuente por defecto de pygame si ninguna existe.
"""
import pygame

# Más ornamentales / góticas primero; las últimas son serif legibles de respaldo.
FUENTES_GOTICAS = (
    "Old English Text MT", "Blackadder ITC", "UnifrakturMaguntia", "Cinzel",
    "Trajan Pro", "Algerian", "Palatino Linotype", "Book Antiqua", "Garamond",
    "Georgia", "Times New Roman",
)
FUENTES_TEXTO = ("Georgia", "Palatino Linotype", "Book Antiqua", "Segoe UI", "Arial")
FUENTES_IMPACTO = ("Impact", "Arial Black", "Arial")

_cache = {}


def cargar_fuente(candidatas, tam, bold=False, italic=False):
    """Devuelve la primera fuente disponible de `candidatas` (con fallback seguro)."""
    tam = max(6, int(round(tam)))
    clave = (tuple(candidatas), tam, bold, italic)
    if clave in _cache:
        return _cache[clave]

    fuente = None
    for nombre in candidatas:
        try:
            ruta = pygame.font.match_font(nombre, bold=bold, italic=italic)
            if ruta:
                fuente = pygame.font.Font(ruta, tam)
                break
        except (OSError, pygame.error):
            continue

    if fuente is None:
        fuente = pygame.font.Font(None, int(tam * 1.3))

    _cache[clave] = fuente
    return fuente


def envolver_texto(texto, fuente, ancho_max):
    """Divide `texto` en líneas que caben en `ancho_max` (respeta saltos de línea)."""
    lineas = []
    for parrafo in texto.split("\n"):
        palabras = parrafo.split(" ")
        actual = ""
        for palabra in palabras:
            prueba = palabra if not actual else actual + " " + palabra
            if fuente.size(prueba)[0] <= ancho_max or not actual:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        lineas.append(actual)
    return lineas


def recortar_texto(texto, fuente, ancho_max):
    """Recorta `texto` con puntos suspensivos si no cabe en `ancho_max`."""
    if fuente.size(texto)[0] <= ancho_max:
        return texto
    while texto and fuente.size(texto + "...")[0] > ancho_max:
        texto = texto[:-1]
    return texto.rstrip() + "..."


def halo_de_texto(fuente, texto, color_halo, radio=20):
    """Superficie con el halo difuso (sin el texto) de `texto`."""
    mascara = fuente.render(texto, True, color_halo)
    w, h = mascara.get_size()
    lienzo = pygame.Surface((w + 2 * radio, h + 2 * radio), pygame.SRCALPHA)
    # Mantener el RGB del halo en los píxeles transparentes evita bordes oscuros al suavizar.
    lienzo.fill((*color_halo[:3], 0))
    lienzo.blit(mascara, (radio, radio))
    cw, ch = lienzo.get_size()
    pequeno = pygame.transform.smoothscale(lienzo, (max(1, cw // 4), max(1, ch // 4)))
    return pygame.transform.smoothscale(pequeno, (cw, ch))


def texto_con_resplandor(fuente, texto, color, color_halo, radio=20, pasadas=2):
    """Texto nítido con un resplandor suave detrás (superficie SRCALPHA con margen)."""
    base = fuente.render(texto, True, color)
    halo = halo_de_texto(fuente, texto, color_halo, radio)
    salida = pygame.Surface(halo.get_size(), pygame.SRCALPHA)
    for _ in range(max(1, pasadas)):
        salida.blit(halo, (0, 0))
    salida.blit(base, (radio, radio))
    return salida