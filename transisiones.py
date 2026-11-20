"""
transiciones.py
===============
Utilidades visuales compartidas y pantallas cinemáticas de REQUIEM:

  * PantallaCitaBiblica : cita de Apocalipsis 12:12 antes del cómic del prólogo.
  * PantallaCourTitulo  : fundido a negro tras el cómic + "Cour I - The Invasion".
  * Helpers: fuentes con fallback, resplandores (glow), brasas/partículas, easing.

Todo es procedural (superficies y primitivas de pygame-ce). No usa archivos de
imagen ni de audio, así que no puede fallar por rutas inexistentes.
"""

import math
import random

import pygame

from config import BASE_DIR


# ============================================================
# MATEMÁTICAS / EASING
# ============================================================

def clamp(valor, minimo=0.0, maximo=1.0):
    return max(minimo, min(maximo, valor))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def mult_color(color, k):
    return tuple(max(0, min(255, int(c * k))) for c in color)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


# ============================================================
# FUENTES (con fallback seguro)
# ============================================================

_EXTENSIONES = (".ttf", ".otf")

# Se evita "old"/"goth" a secas: coincidirían con "Bold" o "Gotham".
_PALABRAS_ORNAMENTALES = (
    "blackletter", "fraktur", "oldenglish", "gothic", "gotica", "rune", "runic",
    "cinzel", "uncial", "medieval", "celtic", "pirata", "almendra", "germania",
    "vampire", "trajan", "ornament",
)

_FUENTES_SISTEMA = (
    "Old English Text MT", "Blackadder ITC", "Algerian", "Vivaldi",
    "Garamond", "Palatino Linotype", "Book Antiqua", "Georgia",
    "Times New Roman",
)

_cache_fuentes = {}


def _fuentes_del_proyecto():
    rutas = []
    for sub in (("assets", "fonts"), ("assets", "fuentes"), ("fonts",), ("fuentes",), ("assets",)):
        carpeta = BASE_DIR.joinpath(*sub)
        if carpeta.is_dir():
            try:
                rutas.extend(p for p in carpeta.iterdir() if p.suffix.lower() in _EXTENSIONES)
            except OSError:
                pass
    return rutas


def cargar_fuente_ornamental(size, bold=False):
    """Fuente gótica/rúnica del proyecto si existe; si no, la mejor serif del sistema."""
    clave = ("orn", size, bold)
    if clave in _cache_fuentes:
        return _cache_fuentes[clave]

    fuente = None
    for ruta in _fuentes_del_proyecto():
        if any(p in ruta.stem.lower() for p in _PALABRAS_ORNAMENTALES):
            try:
                fuente = pygame.font.Font(str(ruta), size)
                break
            except (pygame.error, OSError):
                continue

    if fuente is None:
        for nombre in _FUENTES_SISTEMA:
            if pygame.font.match_font(nombre):
                fuente = pygame.font.SysFont(nombre, size, bold=bold)
                break

    if fuente is None:
        fuente = pygame.font.SysFont("georgia,timesnewroman,serif", size, bold=bold)

    _cache_fuentes[clave] = fuente
    return fuente


def cargar_fuente_serif(size, italic=False, bold=False):
    clave = ("serif", size, italic, bold)
    if clave not in _cache_fuentes:
        _cache_fuentes[clave] = pygame.font.SysFont(
            "georgia,palatinolinotype,garamond,timesnewroman,serif",
            size, bold=bold, italic=italic,
        )
    return _cache_fuentes[clave]


def ajustar_texto(texto, fuente, ancho_max):
    """Word-wrap limpio: devuelve una lista de líneas que caben en ancho_max."""
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = palabra if not actual else actual + " " + palabra
        if not actual or fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


# ============================================================
# RESPLANDORES (glow) CON CACHÉ
# ============================================================

_glow_base = None
_glow_escalado = {}
_glow_teñido = {}


def _base_resplandor():
    global _glow_base
    if _glow_base is None:
        radio = 128
        sup = pygame.Surface((radio * 2, radio * 2), 0, 32)
        sup.fill((0, 0, 0))
        for r in range(radio, 0, -2):
            v = int(255 * (1 - r / radio) ** 2)
            pygame.draw.circle(sup, (v, v, v), (radio, radio), r)
        _glow_base = sup
    return _glow_base


def resplandor(color, ancho, alto=None):
    """
    Superficie RGB con un degradado radial teñido. Se dibuja con
    special_flags=pygame.BLEND_RGB_ADD. Los tamaños se redondean a múltiplos de 8
    y el color a 32 niveles para que la caché sea efectiva.
    """
    alto = ancho if alto is None else alto
    ancho = max(8, (int(ancho) + 7) // 8 * 8)
    alto = max(8, (int(alto) + 7) // 8 * 8)
    q = tuple(max(0, min(255, int(c))) >> 3 for c in color)
    clave = (ancho, alto) + q

    sup = _glow_teñido.get(clave)
    if sup is None:
        g = _glow_escalado.get((ancho, alto))
        if g is None:
            if len(_glow_escalado) > 40:
                _glow_escalado.clear()
            g = pygame.transform.smoothscale(_base_resplandor(), (ancho, alto))
            _glow_escalado[(ancho, alto)] = g
        if len(_glow_teñido) > 300:
            _glow_teñido.clear()
        sup = g.copy()
        sup.fill(tuple((c << 3) + (4 if c else 0) for c in q), special_flags=pygame.BLEND_RGB_MULT)
        _glow_teñido[clave] = sup
    return sup


def sumar_brillo(destino, brillo, cx, cy):
    destino.blit(
        brillo,
        (cx - brillo.get_width() // 2, cy - brillo.get_height() // 2),
        special_flags=pygame.BLEND_RGB_ADD,
    )


def desenfocar(sup, factor, pasadas=1):
    """Desenfoque barato: reduce y vuelve a ampliar. Conserva el canal alfa."""
    w, h = sup.get_size()
    chico = pygame.transform.smoothscale(sup, (max(1, w // factor), max(1, h // factor)))
    grande = pygame.transform.smoothscale(chico, (w, h))
    salida = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(pasadas):
        salida.blit(grande, (0, 0))
    return salida


# ============================================================
# BRASAS / PARTÍCULAS ASCENDENTES
# ============================================================

class Brasas:
    def __init__(self, size, cantidad=120, seed=1604, velocidad=(10, 34), radios=(1, 1, 2, 2, 3)):
        self.w, self.h = size
        rng = random.Random(seed)
        self.particulas = tuple(
            (
                rng.randrange(self.w),
                rng.randrange(self.h),
                rng.uniform(*velocidad),
                rng.random() * math.tau,
                rng.choice(radios),
            )
            for _ in range(cantidad)
        )
        self.t = 0.0
        self.capa = pygame.Surface(size)

    def update(self, dt):
        self.t += max(0.0, dt)

    def draw(self, destino, color=(255, 120, 40), intensidad=1.0):
        if intensidad <= 0.01:
            return
        capa = self.capa
        capa.fill((0, 0, 0))
        t, w, h = self.t, self.w, self.h
        for x0, y0, v, fase, r in self.particulas:
            y = int((y0 - t * v) % (h + 20)) - 10
            x = int(x0 + math.sin(t * 0.4 + fase) * 9) % w
            fl = 0.5 + 0.5 * math.sin(t * 1.7 + fase)
            k = min(1.0, intensidad * (0.35 + 0.65 * fl))
            pygame.draw.circle(
                capa, (int(color[0] * k), int(color[1] * k), int(color[2] * k)), (x, y), r
            )
        destino.blit(capa, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


# ============================================================
# 1) PANTALLA PRE-CÓMIC: CITA BÍBLICA
# ============================================================

class PantallaCitaBiblica:
    TEXTO = (
        "¡Ay de los moradores de la tierra y del mar!, porque el diablo "
        "ha descendido a vosotros, teniendo gran ira."
    )
    REFERENCIA = "Apocalipsis 12:12"

    FADE_IN = 1.8
    HOLD = 4.2
    FADE_OUT = 1.5
    PAUSA_FINAL = 0.5
    MARGEN_SALTO = 0.8   # segundos de seguridad antes de poder saltar

    def __init__(self, size):
        self.w, self.h = size
        self.brasas = Brasas(size, cantidad=60, seed=1212, velocidad=(5, 16), radios=(1, 1, 2))
        self.t = 0.0
        self.fase = "in"
        self.fase_t = 0.0
        self.alpha = 0.0
        self._alpha_salida = 1.0
        self._preparar_texto()

    def _preparar_texto(self):
        e = self.h / 720
        fuente = cargar_fuente_serif(max(16, int(38 * e)), italic=True)
        fuente_ref = cargar_fuente_serif(max(12, int(22 * e)), bold=True)
        ancho_max = int(self.w * 0.62)

        lineas = ajustar_texto("“" + self.TEXTO + "”", fuente, ancho_max)
        render = [fuente.render(l, True, (232, 224, 208)) for l in lineas]
        interlinea = int(fuente.get_linesize() * 1.12)
        ref = fuente_ref.render("— " + self.REFERENCIA, True, (176, 44, 38))

        sep_ancho = int(ancho_max * 0.35)
        alto = interlinea * len(render) + int(34 * e) + ref.get_height() + int(20 * e)
        bloque = pygame.Surface((ancho_max + 40, alto + 10), pygame.SRCALPHA)
        y = 0
        for surf in render:
            bloque.blit(surf, surf.get_rect(midtop=(bloque.get_width() // 2, y)))
            y += interlinea

        y += int(14 * e)
        cx = bloque.get_width() // 2
        for x in range(sep_ancho):
            t = abs(x / max(1, sep_ancho - 1) - 0.5) * 2
            a = int(200 * (1 - t) ** 0.8)
            bloque.set_at((cx - sep_ancho // 2 + x, y), (150, 40, 36, a))
        pygame.draw.polygon(
            bloque, (176, 44, 38),
            [(cx, y - 4), (cx + 5, y), (cx, y + 4), (cx - 5, y)],
        )
        y += int(20 * e)
        bloque.blit(ref, ref.get_rect(midtop=(cx, y)))

        self.bloque = bloque
        self.bloque_pos = bloque.get_rect(center=(self.w // 2, self.h // 2))

    def _cambiar(self, fase):
        self.fase = fase
        self.fase_t = 0.0
        if fase == "out":
            self._alpha_salida = self.alpha

    def saltar(self):
        if self.t < self.MARGEN_SALTO or self.fase in ("out", "end"):
            return
        self._cambiar("out")

    def update(self, dt):
        dt = min(dt, 0.05)
        self.t += dt
        self.fase_t += dt
        self.brasas.update(dt)

        if self.fase == "in":
            self.alpha = ease_in_out(self.fase_t / self.FADE_IN)
            if self.fase_t >= self.FADE_IN:
                self._cambiar("hold")
        elif self.fase == "hold":
            self.alpha = 1.0
            if self.fase_t >= self.HOLD:
                self._cambiar("out")
        elif self.fase == "out":
            self.alpha = self._alpha_salida * (1 - ease_in_out(self.fase_t / self.FADE_OUT))
            if self.fase_t >= self.FADE_OUT:
                self.alpha = 0.0
                self._cambiar("end")
        elif self.fase == "end":
            self.alpha = 0.0
            if self.fase_t >= self.PAUSA_FINAL:
                return "done"
        return None

    def draw(self, pantalla):
        pantalla.fill((3, 2, 4))
        a = self.alpha
        if a <= 0.003:
            return
        # Resplandor apagado, muy tenue
        brillo = resplandor(mult_color((70, 12, 12), 0.45 * a), int(self.w * 0.9), int(self.h * 0.7))
        sumar_brillo(pantalla, brillo, self.w // 2, self.h // 2)
        self.brasas.draw(pantalla, (130, 38, 22), 0.35 * a)
        self.bloque.set_alpha(int(255 * a))
        pantalla.blit(self.bloque, self.bloque_pos)


# ============================================================
# 2) PANTALLA POST-CÓMIC: "Cour I - The Invasion"
# ============================================================

class PantallaCourTitulo:
    TEXTO = "Cour I - The Invasion"
    FASES = (
        ("fade_negro", 1.4),
        ("negro", 0.7),
        ("titulo_in", 3.0),
        ("titulo_hold", 3.8),
        ("titulo_out", 1.8),
        ("final", 0.5),
    )
    MARGEN_SALTO = 1.6   # segundos desde que empieza a aparecer el título

    def __init__(self, size, fondo_previo=None):
        self.w, self.h = size
        self.fondo_previo = fondo_previo
        self.t = 0.0
        self.t_titulo = 0.0
        self.idx = 0
        self.fase_t = 0.0
        self.alpha = 0.0
        self._alpha_salida = 1.0
        self._idx_out = [n for n, _ in self.FASES].index("titulo_out")
        self.motas = Brasas(size, cantidad=70, seed=808, velocidad=(8, 24), radios=(1, 1, 2, 2))
        self.negro = pygame.Surface(size)
        self.negro.fill((0, 0, 0))
        self.rayos = pygame.Surface((max(1, self.w // 4), max(1, self.h // 4)), pygame.SRCALPHA)
        self._preparar_texto()
        self._preparar_ornamento()

    # ---------- preparación ----------

    def _preparar_texto(self):
        tam = max(24, int(self.h * 0.105))
        while True:
            fuente = cargar_fuente_ornamental(tam)
            if fuente.size(self.TEXTO)[0] <= self.w * 0.82 or tam <= 20:
                break
            tam -= 4

        base = fuente.render(self.TEXTO, True, (255, 246, 220))
        dorado = fuente.render(self.TEXTO, True, (232, 178, 72))
        halo_txt = fuente.render(self.TEXTO, True, (255, 205, 110))

        pad = int(self.h * 0.14)
        tw, th = base.get_size()
        W, H = tw + 2 * pad, th + 2 * pad

        nucleo = pygame.Surface((W, H), pygame.SRCALPHA)
        for dx, dy in ((2, 2), (-1, -1), (2, -1), (-1, 2)):
            nucleo.blit(dorado, (pad + dx, pad + dy))
        nucleo.blit(base, (pad, pad))

        fuente_halo = pygame.Surface((W, H), pygame.SRCALPHA)
        fuente_halo.blit(halo_txt, (pad, pad))

        self.nucleo = nucleo
        self.halo_cerca = desenfocar(fuente_halo, 4, 3)
        self.halo_lejos = desenfocar(fuente_halo, 12, 5)
        self.alto_texto = th

    def _preparar_ornamento(self):
        ancho = int(self.w * 0.46)
        alto = 16
        mid = alto // 2
        orn = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        for x in range(ancho):
            t = abs(x / max(1, ancho - 1) - 0.5) * 2
            a = int(230 * (1 - t) ** 0.8)
            orn.set_at((x, mid), (255, 225, 150, a))
            orn.set_at((x, mid + 1), (255, 225, 150, a // 2))
        cx = ancho // 2
        pygame.draw.polygon(
            orn, (255, 238, 184),
            [(cx, mid - 6), (cx + 7, mid), (cx, mid + 6), (cx - 7, mid)],
        )
        self.ornamento = orn

    # ---------- control ----------

    def saltar(self):
        nombre = self.FASES[self.idx][0] if self.idx < len(self.FASES) else ""
        if nombre in ("titulo_in", "titulo_hold") and self.t_titulo >= self.MARGEN_SALTO:
            self._alpha_salida = self.alpha
            self.idx = self._idx_out
            self.fase_t = 0.0

    def _siguiente(self):
        self.idx += 1
        self.fase_t = 0.0
        if self.idx < len(self.FASES) and self.FASES[self.idx][0] == "titulo_out":
            self._alpha_salida = self.alpha

    def update(self, dt):
        dt = min(dt, 0.05)
        self.t += dt
        self.motas.update(dt)
        if self.idx >= len(self.FASES):
            return "done"

        nombre, dur = self.FASES[self.idx]
        self.fase_t += dt
        if nombre.startswith("titulo"):
            self.t_titulo += dt

        p = clamp(self.fase_t / dur)
        if nombre == "titulo_in":
            self.alpha = ease_in_out(p)
        elif nombre == "titulo_hold":
            self.alpha = 1.0
        elif nombre == "titulo_out":
            self.alpha = self._alpha_salida * (1 - ease_in_out(p))
        else:
            self.alpha = 0.0

        if self.fase_t >= dur:
            self._siguiente()
        return "done" if self.idx >= len(self.FASES) else None

    # ---------- dibujo ----------

    @staticmethod
    def _escalar(sup, escala):
        if abs(escala - 1.0) < 0.002:
            return sup.copy()
        return pygame.transform.smoothscale(
            sup, (max(1, int(sup.get_width() * escala)), max(1, int(sup.get_height() * escala)))
        )

    def draw(self, pantalla):
        nombre = self.FASES[self.idx][0] if self.idx < len(self.FASES) else "final"

        if nombre == "fade_negro":
            if self.fondo_previo is not None:
                pantalla.blit(self.fondo_previo, (0, 0))
            else:
                pantalla.fill((0, 0, 0))
            a = int(255 * ease_in_out(self.fase_t / self.FASES[0][1]))
            self.negro.set_alpha(a)
            pantalla.blit(self.negro, (0, 0))
            return

        pantalla.fill((0, 0, 0))
        a = self.alpha
        if a <= 0.003:
            return

        pulso = 0.5 + 0.5 * math.sin(self.t * 1.7)
        cx, cy = self.w // 2, self.h // 2

        # Rayos de luz muy suaves (se dibujan pequeños y se amplían = difuminado)
        capa = self.rayos
        capa.fill((0, 0, 0, 0))
        rx, ry = capa.get_width() // 2, capa.get_height() // 2
        radio = math.hypot(*capa.get_size())
        for k in range(14):
            ang = self.t * 0.05 + k * math.tau / 14
            a1, a2 = ang - 0.045, ang + 0.045
            pts = [
                (rx, ry),
                (rx + math.cos(a1) * radio, ry + math.sin(a1) * radio),
                (rx + math.cos(a2) * radio, ry + math.sin(a2) * radio),
            ]
            pygame.draw.polygon(capa, (255, 225, 150, 38 if k % 2 else 24), pts)
        grande = pygame.transform.smoothscale(capa, (self.w, self.h))
        grande.set_alpha(int(255 * a * 0.55))
        pantalla.blit(grande, (0, 0))

        # Aura cálida + motas doradas
        aura = resplandor(
            mult_color((255, 205, 120), 0.40 * a * (0.85 + 0.15 * pulso)),
            int(self.w * 0.95), int(self.h * 0.55),
        )
        sumar_brillo(pantalla, aura, cx, cy)
        self.motas.draw(pantalla, (255, 225, 150), 0.75 * a)

        # Ornamentos
        sep = int(self.alto_texto / 2 + self.h * 0.055)
        self.ornamento.set_alpha(int(255 * a))
        pantalla.blit(self.ornamento, self.ornamento.get_rect(center=(cx, cy - sep)))
        pantalla.blit(self.ornamento, self.ornamento.get_rect(center=(cx, cy + sep)))

        # Texto: expansión muy sutil al aparecer + leve pulso
        prog = clamp(self.t_titulo / 3.0)
        escala = lerp(0.955, 1.0, ease_out(prog)) + 0.012 * pulso

        for halo, k in ((self.halo_lejos, 0.75), (self.halo_cerca, 0.9)):
            s = self._escalar(halo, escala)
            s.set_alpha(int(255 * clamp(a * k * (0.8 + 0.2 * pulso))))
            pantalla.blit(s, s.get_rect(center=(cx, cy)))

        s = self._escalar(self.nucleo, escala)
        s.set_alpha(int(255 * a))
        pantalla.blit(s, s.get_rect(center=(cx, cy)))