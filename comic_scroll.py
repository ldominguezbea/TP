"""Lector de cómic con desplazamiento vertical para REQUIEM (pygame-ce).

Cada página aparece por su parte SUPERIOR y hay que bajar con la rueda del mouse
(o con las flechas, RePág/AvPág o Espacio) para leerla. Solo al llegar al final de
la página se puede pasar a la siguiente con ENTER; ESC salta todo el cómic. Así no
se ve el final de una página antes de leerla (sin spoilers).

Interfaz compatible con la que usa main.py para el prólogo:
    handle_key(key)    -> "finished" al terminar la última página, si no None
    handle_click(pos)  -> se ignora a propósito (un tick de rueda también genera clic)
    handle_scroll(y)   -> desplaza (y > 0 sube, y < 0 baja)
    update(dt_seg), draw(pantalla), consume_action() -> "skip" tras ESC
"""
import math
import re
from pathlib import Path

import pygame

from fuentes_requiem import FUENTES_TEXTO, cargar_fuente

EXTENSIONES = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def cargar_paginas(carpeta):
    """Lista ordenada (orden natural: pagina2 antes que pagina10) de imágenes de `carpeta`."""
    carpeta = Path(carpeta)
    if not carpeta.is_dir():
        return []

    def clave(p):
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]

    return sorted((p for p in carpeta.iterdir() if p.suffix.lower() in EXTENSIONES), key=clave)


class ScrollComic:
    def __init__(self, paginas, tam, sonido_pagina=None, ancho_rel=0.80):
        """
        paginas       : lista de rutas (str/Path) o de pygame.Surface.
        tam           : (ancho, alto) de la pantalla.
        sonido_pagina : pygame.mixer.Sound opcional que suena al pasar de página.
        ancho_rel     : ancho de la página respecto al de la pantalla (0..1).
        """
        self.W, self.H = tam
        self.s = self.H / 720.0
        self.paginas = list(paginas)
        self.sonido_pagina = sonido_pagina
        self.ancho_pag = int(self.W * ancho_rel)

        self.indice = 0
        self.scroll = 0.0
        self.scroll_obj = 0.0
        self.t = 0.0
        self.aparece = 0.0            # fundido de entrada de la página actual (0..1)
        self.aviso = 0.0              # parpadeo de "baja hasta el final"
        self._accion = None
        self._cache = {}

        self.f_hint = cargar_fuente(FUENTES_TEXTO, 18 * self.s, bold=True)
        self.f_peq = cargar_fuente(FUENTES_TEXTO, 14 * self.s, bold=True)

        self.degradado = pygame.Surface((self.W, int(110 * self.s)), pygame.SRCALPHA)
        for y in range(self.degradado.get_height()):
            a = int(235 * (y / self.degradado.get_height()) ** 1.5)
            self.degradado.fill((6, 4, 9, a), (0, y, self.W, 1))

        self._precargar(0)

    # ---- páginas ---------------------------------------------------------

    def _pagina(self, i):
        if i < 0 or i >= len(self.paginas):
            return None
        sup = self._cache.get(i)
        if sup is None:
            origen = self.paginas[i]
            try:
                img = origen if isinstance(origen, pygame.Surface) else pygame.image.load(str(origen))
                img = img.convert_alpha()
                w, h = img.get_size()
                alto = max(1, int(h * self.ancho_pag / w))
                sup = pygame.transform.smoothscale(img, (self.ancho_pag, alto))
            except (pygame.error, FileNotFoundError, OSError) as e:
                print(f"[COMIC] No se pudo cargar la página {origen}: {e}")
                sup = pygame.Surface((self.ancho_pag, self.H))
                sup.fill((18, 14, 20))
            self._cache[i] = sup
            # Mantener solo la página actual y las vecinas en memoria
            for k in [k for k in self._cache if abs(k - self.indice) > 1]:
                del self._cache[k]
        return sup

    def _precargar(self, i):
        self._pagina(i)
        self._pagina(i + 1)

    @property
    def _max_scroll(self):
        pag = self._pagina(self.indice)
        return max(0, pag.get_height() - self.H) if pag is not None else 0

    @property
    def _al_final(self):
        return self.scroll_obj >= self._max_scroll - 4 and self.scroll >= self._max_scroll - 8

    # ---- entrada ---------------------------------------------------------

    def handle_scroll(self, y):
        self.scroll_obj = max(0.0, min(float(self._max_scroll), self.scroll_obj - y * 90 * self.s))

    def handle_click(self, pos):
        return None

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self._accion = "skip"
            return None
        if key in (pygame.K_PAGEDOWN, pygame.K_SPACE):
            if key == pygame.K_SPACE and self._al_final:
                return self._siguiente()
            self.handle_scroll(-self.H * 0.8 / (90 * self.s))
            return None
        if key == pygame.K_PAGEUP:
            self.handle_scroll(self.H * 0.8 / (90 * self.s))
            return None
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self._al_final:
                return self._siguiente()
            self.aviso = 1.0
        return None

    def consume_action(self):
        accion, self._accion = self._accion, None
        return accion

    def _siguiente(self):
        if self.indice >= len(self.paginas) - 1:
            return "finished"
        self.indice += 1
        self.scroll = self.scroll_obj = 0.0
        self.aparece = 0.0
        self.aviso = 0.0
        self._precargar(self.indice)
        if self.sonido_pagina is not None:
            try:
                self.sonido_pagina.play()
            except pygame.error:
                pass
        return None

    # ---- actualización y dibujo -----------------------------------------

    def update(self, dt):
        dt = min(max(dt, 0.0), 0.05)
        self.t += dt
        self.aparece = min(1.0, self.aparece + dt / 0.45)
        self.aviso = max(0.0, self.aviso - dt * 1.5)

        teclas = pygame.key.get_pressed()
        mov = 0.0
        if teclas[pygame.K_DOWN]:
            mov += 650 * self.s * dt
        if teclas[pygame.K_UP]:
            mov -= 650 * self.s * dt
        if mov:
            self.scroll_obj = max(0.0, min(float(self._max_scroll), self.scroll_obj + mov))

        self.scroll += (self.scroll_obj - self.scroll) * (1 - math.exp(-dt * 14))
        if abs(self.scroll_obj - self.scroll) < 0.3:
            self.scroll = self.scroll_obj

    def draw(self, pantalla):
        W, H, s = self.W, self.H, self.s
        pantalla.fill((7, 5, 10))
        pag = self._pagina(self.indice)
        if pag is None:
            return
        x0 = (W - pag.get_width()) // 2
        y0 = -int(round(self.scroll))
        if pag.get_height() < H:                      # página corta: centrada, sin scroll
            y0 = (H - pag.get_height()) // 2
        pag.set_alpha(int(255 * self.aparece))
        pantalla.blit(pag, (x0, y0))

        # Barra de progreso de la página (derecha)
        maximo = self._max_scroll
        if maximo > 0:
            pista = pygame.Rect(W - int(14 * s), int(40 * s), max(3, int(4 * s)), H - int(80 * s))
            pygame.draw.rect(pantalla, (36, 30, 40), pista, border_radius=3)
            asa_h = max(int(30 * s), int(pista.h * H / (H + maximo)))
            asa_y = pista.y + int((pista.h - asa_h) * (self.scroll / maximo))
            pygame.draw.rect(pantalla, (200, 160, 80), (pista.x, asa_y, pista.w, asa_h), border_radius=3)

        # Contador y ESC
        cont = self.f_peq.render(f"PÁGINA {self.indice + 1} / {len(self.paginas)}", True, (190, 180, 168))
        pantalla.blit(cont, (int(18 * s), int(14 * s)))
        esc = self.f_peq.render("ESC  saltar", True, (150, 142, 135))
        pantalla.blit(esc, esc.get_rect(topright=(W - int(30 * s), int(14 * s))))

        # Pista inferior
        pantalla.blit(self.degradado, (0, H - self.degradado.get_height()))
        pulso = 0.6 + 0.4 * math.sin(self.t * 4)
        cy = H - int(34 * s)
        if self._al_final:
            ultima = self.indice >= len(self.paginas) - 1
            txt = self.f_hint.render("ENTER  " + ("continuar" if ultima else "siguiente página"),
                                     True, (int(255 * pulso), int(215 * pulso), int(120 * pulso)))
            pantalla.blit(txt, txt.get_rect(center=(W // 2, cy)))
        else:
            col = (255, int(120 + 60 * self.aviso), int(100 + 60 * self.aviso)) if self.aviso > 0 else \
                  (int(210 * pulso), int(195 * pulso), int(170 * pulso))
            txt = self.f_hint.render("Baja con la rueda para seguir leyendo", True, col)
            r = txt.get_rect(center=(W // 2, cy))
            pantalla.blit(txt, r)
            d = int(7 * s)
            for x in (r.left - int(22 * s), r.right + int(22 * s)):   # flechitas dibujadas, sin depender de la fuente
                pygame.draw.polygon(pantalla, col, [(x - d, cy - d // 2), (x + d, cy - d // 2), (x, cy + d)])