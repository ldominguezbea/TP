"""Pantalla de Selección de Personajes de REQUIEM (pygame-ce).

Uso desde main.py:

    pantalla_sel = SeleccionPersonajes(screen, characters,
                                       sonido_nav=navigation_sound,
                                       audio_disponible=audio_disponible,
                                       base_dir=BASE_DIR)
    pantalla_sel.reset(selected_char_index)      # al entrar en la pantalla
    accion = pantalla_sel.handle_event(event)    # None | "back"
    if pantalla_sel.update(elapsed_ms) == "seleccionado":
        nombre = characters[pantalla_sel.indice]["name"]
    pantalla_sel.draw(screen)

Los sprites de idle se buscan solos (ver `_buscar_carpeta_idle`). Todo lo demás
(auras, partículas, runas, barras, destellos) se dibuja con primitivas de pygame.
Los sprites se escalan SIEMPRE con factor entero y vecino más cercano para
conservar la nitidez del pixel art.
"""
import array
import math
import os
import random
import re
import sys
from pathlib import Path

import pygame

from fuentes_requiem import (
    FUENTES_GOTICAS, FUENTES_IMPACTO, FUENTES_TEXTO,
    cargar_fuente, envolver_texto, recortar_texto, texto_con_resplandor,
)

try:
    from config import BASE_DIR
except Exception:  # ejecución suelta del archivo
    BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# DATOS DE LOS HÉROES (editables)
# ============================================================
# Las claves son los nombres EXACTOS de la lista `characters` de main.py.
# Stats de 0 a 100. Los poderes están redactados a partir de la biografía de cada
# héroe: cámbialos por los nombres reales de tus habilidades cuando quieras.
HEROES_DATOS = {
    "Fei Liang": {
        "titulo": "Heraldo de la Tormenta",
        "elemento": "Viento",
        "acento": (110, 175, 255),       # azul espectral
        "stats": (("VIDA", 58), ("DAÑO", 72), ("VELOCIDAD", 98), ("ENERGÍA ARCANA", 84)),
        "habilidades": (
            ("Ráfaga", "Lanza ráfagas de aire cortante.", "spiral"),
            ("Impulso", "Corrientes que potencian su movimiento.", "dash"),
            ("Evasión", "Esquiva ataques a velocidad extrema.", "star"),
        ),
    },
    "Korg": {
        "titulo": "Bastión de Roca",
        "elemento": "Roca",
        "acento": (240, 165, 55),        # dorado infernal
        "stats": (("VIDA", 98), ("DAÑO", 82), ("VELOCIDAD", 38), ("ENERGÍA ARCANA", 58)),
        "habilidades": (
            ("Roca viva", "Crea y lanza roca del suelo.", "rock"),
            ("Barrera", "Levanta muros de piedra protectores.", "shield"),
            ("Golpe térreo", "Potencia sus golpes con energía de tierra.", "star"),
        ),
    },
    "Diana": {
        "titulo": "Guardiana del Bosque",
        "elemento": "Planta",
        "acento": (80, 205, 140),        # esmeralda arcano
        "stats": (("VIDA", 55), ("DAÑO", 76), ("VELOCIDAD", 70), ("ENERGÍA ARCANA", 95)),
        "habilidades": (
            ("Arco", "Disparos precisos a larga distancia.", "arrow"),
            ("Enredadera", "Raíces y lianas que atrapan enemigos.", "leaf"),
            ("Savia", "Ataques de energía vegetal.", "spiral"),
        ),
    },
    "Escanor": {
        "titulo": "Portador de la Llama",
        "elemento": "Fuego",
        "acento": (225, 55, 60),         # carmesí
        "stats": (("VIDA", 74), ("DAÑO", 98), ("VELOCIDAD", 52), ("ENERGÍA ARCANA", 68)),
        "habilidades": (
            ("Mandoble", "Golpes brutales con su espada enorme.", "sword"),
            ("Fuego concentrado", "Acumula llamas para ganar fuerza.", "flame"),
            ("Temple", "Domina su temperamento y su poder.", "shield"),
        ),
    },
}

DATOS_DEFECTO = {
    "titulo": "Héroe de Requiem",
    "elemento": "Arcano",
    "acento": (190, 150, 230),
    "stats": (("VIDA", 60), ("DAÑO", 60), ("VELOCIDAD", 60), ("ENERGÍA ARCANA", 60)),
    "habilidades": (("Poder", "Habilidad por definir.", "star"),),
}

_PATRON_IDLE = re.compile(r"^idle[ _\-]?(\d+)\.(png|webp|bmp|jpg|jpeg)$", re.IGNORECASE)


# ============================================================
# AUXILIARES
# ============================================================

def _clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def _mezclar(c1, c2, t):
    t = _clamp(t)
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))


def _escalar(c, f):
    f = _clamp(f)
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def _ease_out(t):
    t = _clamp(t)
    return 1 - (1 - t) ** 3


def _norm(nombre):
    return re.sub(r"[\s_\-]+", "", nombre).lower()


def _sprite_radial(tam, color, intensidad=1.0, exponente=2.0):
    """Degradado radial (o elíptico) con alfa, generado en pequeño y escalado suave."""
    n = 40
    peq = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            d = math.hypot((x - c) / c, (y - c) / c)
            a = max(0.0, 1.0 - d) ** exponente * intensidad
            peq.set_at((x, y), (*color[:3], int(255 * _clamp(a))))
    return pygame.transform.smoothscale(peq, (max(2, int(tam[0])), max(2, int(tam[1]))))


def _icono(sup, tipo, cx, cy, r, col):
    """Icono de habilidad dibujado con primitivas dentro de un medallón."""
    pygame.draw.circle(sup, (22, 18, 26), (cx, cy), r)
    pygame.draw.circle(sup, col, (cx, cy), r, max(1, r // 8))
    q = r * 0.55
    g = max(1, r // 7)
    if tipo == "spiral":
        for k, rr in enumerate((0.62, 0.40, 0.18)):
            lado = max(2, int(2 * r * rr))
            rect = pygame.Rect(0, 0, lado, lado)
            rect.center = (cx, cy)
            pygame.draw.arc(sup, col, rect, 0.5 + k * 1.3, 0.5 + k * 1.3 + 4.3, g)
    elif tipo == "dash":
        for off in (-q * 0.7, 0, q * 0.7):
            pygame.draw.lines(sup, col, False, [
                (cx + off - q * 0.35, cy - q * 0.7), (cx + off + q * 0.35, cy),
                (cx + off - q * 0.35, cy + q * 0.7)], g)
    elif tipo == "star":
        pts = []
        for k in range(8):
            ang = k * math.pi / 4 - math.pi / 2
            rad = q * 1.25 if k % 2 == 0 else q * 0.45
            pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
        pygame.draw.polygon(sup, col, pts)
    elif tipo == "shield":
        pts = [(cx - q, cy - q * 0.9), (cx + q, cy - q * 0.9), (cx + q, cy + q * 0.1),
               (cx, cy + q * 1.2), (cx - q, cy + q * 0.1)]
        pygame.draw.polygon(sup, col, pts, g)
        pygame.draw.line(sup, col, (cx, cy - q * 0.9), (cx, cy + q * 1.2), g)
    elif tipo == "rock":
        pts = [(cx + math.cos(k * math.pi / 3) * q * 1.1, cy + math.sin(k * math.pi / 3) * q * 1.1)
               for k in range(6)]
        pygame.draw.polygon(sup, col, pts, g)
        pygame.draw.lines(sup, col, False, [pts[0], (cx, cy), pts[2]], g)
        pygame.draw.line(sup, col, (cx, cy), pts[4], g)
    elif tipo == "leaf":
        pts = []
        for k in range(0, 21):
            u = k / 20
            pts.append((cx - q * 1.1 + u * q * 2.2, cy - math.sin(u * math.pi) * q * 0.75 - (u - 0.5) * q * 0.7))
        for k in range(20, -1, -1):
            u = k / 20
            pts.append((cx - q * 1.1 + u * q * 2.2, cy + math.sin(u * math.pi) * q * 0.75 - (u - 0.5) * q * 0.7))
        pygame.draw.polygon(sup, col, pts)
    elif tipo == "arrow":
        pygame.draw.line(sup, col, (cx - q * 1.1, cy + q * 1.1), (cx + q * 1.1, cy - q * 1.1), g)
        pygame.draw.polygon(sup, col, [(cx + q * 1.3, cy - q * 1.3), (cx + q * 0.3, cy - q * 0.9),
                                       (cx + q * 0.9, cy - q * 0.3)])
        pygame.draw.line(sup, col, (cx - q * 1.1, cy + q * 1.1), (cx - q * 0.6, cy + q * 0.4), g)
        pygame.draw.line(sup, col, (cx - q * 1.1, cy + q * 1.1), (cx - q * 0.4, cy + q * 0.9), g)
    elif tipo == "flame":
        pts = [(cx, cy - q * 1.3), (cx + q * 0.7, cy - q * 0.1), (cx + q * 0.5, cy + q * 0.9),
               (cx, cy + q * 1.2), (cx - q * 0.5, cy + q * 0.9), (cx - q * 0.7, cy - q * 0.1),
               (cx - q * 0.2, cy + q * 0.1)]
        pygame.draw.polygon(sup, col, pts)
    elif tipo == "sword":
        pygame.draw.line(sup, col, (cx, cy - q * 1.3), (cx, cy + q * 0.8), g + 1)
        pygame.draw.line(sup, col, (cx - q * 0.7, cy + q * 0.3), (cx + q * 0.7, cy + q * 0.3), g)
        pygame.draw.line(sup, col, (cx, cy + q * 0.8), (cx, cy + q * 1.3), g)
    else:
        pygame.draw.circle(sup, col, (cx, cy), int(q * 0.8), g)


# ============================================================
# PANTALLA
# ============================================================

class SeleccionPersonajes:
    FPS_IDLE = 9            # fotogramas por segundo de la animación de idle
    T_CONF_FADE = 1.05      # segundo en que empieza el fundido final tras confirmar
    T_CONF_FIN = 1.75       # segundo en que termina la secuencia de confirmación

    def __init__(self, pantalla, characters=None, sonido_nav=None,
                 audio_disponible=True, base_dir=None):
        self.W, self.H = pantalla.get_size()
        self.s = self.H / 720.0
        self.base_dir = Path(base_dir) if base_dir else Path(BASE_DIR)
        self.audio = bool(audio_disponible) and pygame.mixer.get_init() is not None

        if characters is None:
            characters = [{"name": n, "file": None, "color": d["acento"], "desc": ""}
                          for n, d in HEROES_DATOS.items()]

        self._crear_fuentes()
        self.heroes = [self._crear_heroe(c) for c in characters]
        self._calcular_layout()
        self._crear_recursos_visuales()
        self._crear_sonidos(sonido_nav)

        self.layer = pygame.Surface((self.W, self.H)).convert()
        self.scene = pygame.Surface((self.W, self.H)).convert()
        self.overlay = pygame.Surface((self.W, self.H)).convert()
        self.rng = random.Random(77)
        self.reset(0)

    # --------------------------------------------------------
    # Construcción
    # --------------------------------------------------------

    def _f(self, lista, tam, bold=False, italic=False):
        return cargar_fuente(lista, tam * self.s, bold=bold, italic=italic)

    def _crear_fuentes(self):
        self.f_titulo = self._f(FUENTES_GOTICAS, 54)
        self.f_nombre = self._f(FUENTES_IMPACTO, 38)
        self.f_etiqueta = self._f(FUENTES_IMPACTO, 21)
        self.f_sub = self._f(FUENTES_TEXTO, 16, italic=True)
        self.f_txt = self._f(FUENTES_TEXTO, 14)
        self.f_txt_b = self._f(FUENTES_TEXTO, 15, bold=True)
        self.f_peq = self._f(FUENTES_TEXTO, 12, bold=True)
        self.f_ayuda = self._f(FUENTES_TEXTO, 15, bold=True)

    # ---- sprites ---------------------------------------------------------

    def _buscar_carpeta_idle(self, nombre):
        """Devuelve la carpeta con los idle_N.png del héroe, o None.

        1) Rutas habituales:   <assets>/sprites/seleccion_personajes/<Heroe>/idle,
                               <assets>/sprites/<Heroe>, <assets>/<Heroe>, etc.
        2) Si no, busca por debajo de /assets una carpeta llamada como el héroe
           (o 'idle' dentro de ella) que contenga archivos idle_N.png.
        """
        variantes = {nombre, nombre.replace(" ", "_"), nombre.replace(" ", "_").lower(),
                     nombre.lower(), nombre.replace(" ", "")}
        raices = (
            self.base_dir / "assets" / "sprites" / "seleccion_personajes",
            self.base_dir / "assets" / "sprites",
            self.base_dir / "assets" / "Heroes",
            self.base_dir / "assets",
        )

        def tiene_idle(carpeta):
            try:
                return any(_PATRON_IDLE.match(f.name) for f in carpeta.iterdir() if f.is_file())
            except OSError:
                return False

        for raiz in raices:
            for v in variantes:
                for cand in (raiz / v / "idle", raiz / v, raiz / "idle" / v):
                    if cand.is_dir() and tiene_idle(cand):
                        return cand

        objetivo = _norm(nombre)
        raiz = self.base_dir / "assets"
        if raiz.is_dir():
            base_depth = len(raiz.parts)
            for actual, dirs, _files in os.walk(raiz):
                p = Path(actual)
                if len(p.parts) - base_depth >= 6:
                    dirs[:] = []
                    continue
                n = _norm(p.name)
                coincide = n == objetivo or (n == "idle" and _norm(p.parent.name) == objetivo)
                if coincide and tiene_idle(p):
                    return p
        return None

    def _cargar_idle(self, nombre):
        carpeta = self._buscar_carpeta_idle(nombre)
        if carpeta is None:
            return []
        archivos = sorted(
            (f for f in carpeta.iterdir() if f.is_file() and _PATRON_IDLE.match(f.name)),
            key=lambda f: int(_PATRON_IDLE.match(f.name).group(1)))
        frames = []
        for f in archivos:
            try:
                frames.append(pygame.image.load(str(f)).convert_alpha())
            except pygame.error as e:
                print(f"[SELECCION] No se pudo cargar {f}: {e}")
        if frames:
            print(f"[SELECCION] {nombre}: {len(frames)} frames de idle en {carpeta}")
        return frames

    def _crear_heroe(self, ch):
        nombre = ch["name"]
        d = HEROES_DATOS.get(nombre, DATOS_DEFECTO)
        h = {
            "nombre": nombre,
            "color": ch.get("color", d["acento"]),
            "acento": d["acento"],
            "titulo": d["titulo"],
            "elemento": d["elemento"],
            "stats": d["stats"],
            "habilidades": d["habilidades"],
            "desc": ch.get("desc", "") or "",
            "frames": [], "pixel": True, "pivot": 0.5,
            "cache": {}, "anim_t": random.random() * 2.0, "especial": 0.0,
        }

        frames = self._cargar_idle(nombre)
        if not frames:
            # Respaldo 1: imagen estática de `characters` (ruta ya existente en main.py)
            archivo = ch.get("file")
            if archivo is not None and Path(archivo).is_file():
                try:
                    img = pygame.image.load(str(archivo)).convert_alpha()
                    r = img.get_bounding_rect()
                    if r.width > 0:
                        frames = [img.subsurface(r).copy()]
                        h["pixel"] = False
                        h["pivot"] = 0.5
                except pygame.error as e:
                    print(f"[SELECCION] Error cargando {archivo}: {e}")
        if not frames:
            # Respaldo 2: silueta dibujada
            print(f"[SELECCION] No hay sprites para {nombre}; se usa una silueta.")
            sil = pygame.Surface((28, 44), pygame.SRCALPHA)
            pygame.draw.rect(sil, h["acento"], (4, 14, 20, 30), border_radius=3)
            pygame.draw.circle(sil, _mezclar(h["acento"], (255, 255, 255), 0.5), (14, 8), 7)
            frames = [sil]
        elif h["pixel"]:
            rects = [f.get_bounding_rect() for f in frames]
            rects = [r for r in rects if r.width > 0 and r.height > 0]
            if rects:
                union = rects[0].unionall(rects[1:])
                # El pivote horizontal es el centro del lienzo original: así el
                # personaje conserva el anclaje que tiene en el juego (la espada de
                # Escanor, por ejemplo, no desplaza su cuerpo).
                h["pivot"] = (frames[0].get_width() / 2 - union.x) / union.width
                frames = [f.subsurface(union).copy() for f in frames]
        h["frames"] = frames
        return h

    # ---- layout ----------------------------------------------------------

    def _calcular_layout(self):
        W, H, s = self.W, self.H, self.s
        n = len(self.heroes)
        self.y_piso = int(0.55 * H)
        self.alt_w = int(0.19 * W)
        self.alt_h = int(0.035 * H)
        self.slot_x = [int(W * (0.5 + (i - (n - 1) / 2) * 0.25)) for i in range(n)]
        self.panel_rect = pygame.Rect(int(0.05 * W), int(0.675 * H), int(0.90 * W), int(0.255 * H))

        altos = [f.get_height() for h in self.heroes if h["pixel"] for f in h["frames"]]
        self.alto_nativo = max(altos) if altos else 44
        disponible = self.y_piso - int(0.20 * H) - 14 * s
        # k = escala entera en reposo; k+1 = escala entera del héroe enfocado.
        self.k = max(1, int(disponible // self.alto_nativo) - 1)

        # Líneas de lore (primer párrafo de la biografía) ajustadas al ancho de la columna 1
        pad = int(22 * s)
        w_inner = self.panel_rect.w - 2 * pad
        self.col1_w = int(w_inner * 0.31)
        for h in self.heroes:
            parrafo = h["desc"].split("\n\n")[0].replace("\n", " ").strip()
            lineas = envolver_texto(parrafo, self.f_txt, self.col1_w) if parrafo else []
            if len(lineas) > 4:
                lineas = lineas[:4]
                lineas[-1] = recortar_texto(lineas[-1] + " ...", self.f_txt, self.col1_w)
            h["lore"] = lineas

    # ---- recursos visuales ----------------------------------------------

    def _crear_recursos_visuales(self):
        W, H, s = self.W, self.H, self.s

        # Fondo: degradado oscuro + resplandor violeta central + horizonte
        fondo = pygame.Surface((W, H))
        for y in range(H):
            t = y / H
            fondo.fill(_mezclar((8, 6, 12), (22, 14, 24), t ** 1.3), (0, y, W, 1))
        halo = _sprite_radial((int(W * 1.1), int(H * 0.95)), (70, 30, 95), 0.55, 1.6)
        fondo.blit(halo, halo.get_rect(center=(W // 2, int(H * 0.38))))
        horiz = _sprite_radial((int(W * 1.3), int(H * 0.18)), (60, 25, 40), 0.6, 1.4)
        fondo.blit(horiz, horiz.get_rect(center=(W // 2, self.y_piso + int(0.03 * H))))
        self.fondo = fondo.convert()

        # Viñeta
        n_w, n_h = 48, 27
        v = pygame.Surface((n_w, n_h), pygame.SRCALPHA)
        for y in range(n_h):
            for x in range(n_w):
                d = math.hypot((x / (n_w - 1) - 0.5) * 2, (y / (n_h - 1) - 0.5) * 2)
                a = _clamp((d - 0.55) / 0.85) ** 1.6
                v.set_at((x, y), (0, 0, 0, int(215 * a)))
        self.vineta = pygame.transform.smoothscale(v, (W, H)).convert_alpha()

        # Niebla: manchas elípticas suaves que derivan lentamente
        rng = random.Random(21)
        self.niebla_sprite = _sprite_radial((int(W * 0.75), int(H * 0.24)), (70, 62, 96), 0.30, 1.4)
        self.niebla = [[rng.uniform(-0.4, 1.0) * W, rng.uniform(0.22, 0.62) * H,
                        rng.uniform(6, 16) * s * (1 if rng.random() < 0.5 else -1)]
                       for _ in range(7)]

        # Brasas ascendentes: [x, y, velocidad, fase, tamaño]
        self.brasas = [[rng.uniform(0, W), rng.uniform(0, H), rng.uniform(14, 46) * s,
                        rng.random() * math.tau, rng.choice((1, 1, 1, 2)) * max(1, round(s))]
                       for _ in range(150)]

        # Recursos por héroe
        alto_cono = int(0.36 * H)
        radio = int(0.19 * H)
        for h in self.heroes:
            ac = h["acento"]
            h["halo"] = _sprite_radial((int(0.56 * H), int(0.56 * H)), ac, 0.50, 2.0)
            h["glow_piso"] = _sprite_radial((int(self.alt_w * 1.9), int(self.alt_w * 0.62)), ac, 0.85, 1.6)
            h["cono"] = self._crear_cono(self.alt_w, alto_cono, ac)
            h["runas_ext"], h["runas_int"] = self._crear_circulo_runico(radio, ac)
            h["especial"] = 0.0

        # Texto del título (con resplandor) y sus adornos: estático
        self.titulo_surf = texto_con_resplandor(
            self.f_titulo, "SELECCIONA TU HÉROE", (232, 48, 48), (170, 20, 25), radio=int(16 * s))

        # Superficies del panel
        r = self.panel_rect
        self.panel_bg = pygame.Surface(r.size, pygame.SRCALPHA)
        self.panel_ct = pygame.Surface(r.size, pygame.SRCALPHA)

    @staticmethod
    def _crear_cono(ancho, alto, color):
        sup = pygame.Surface((int(ancho * 1.1), alto), pygame.SRCALPHA)
        w = sup.get_width()
        for y in range(alto):
            u = y / alto
            media = w * (0.28 + 0.22 * u)
            a = int(70 * (u ** 1.7))
            pygame.draw.line(sup, (*color, a), (w / 2 - media, y), (w / 2 + media, y))
        return sup

    @staticmethod
    def _crear_circulo_runico(r, color):
        """Devuelve (anillo exterior con runas, sello interior) como superficies SRCALPHA."""
        lado = 2 * r + 6
        c = lado // 2
        rng = random.Random(1604)
        claro = _mezclar(color, (255, 255, 255), 0.35)

        ext = pygame.Surface((lado, lado), pygame.SRCALPHA)
        pygame.draw.circle(ext, (*color, 230), (c, c), r, 3)
        pygame.draw.circle(ext, (*color, 150), (c, c), int(r * 0.90), 1)
        pygame.draw.circle(ext, (*color, 200), (c, c), int(r * 0.66), 2)
        for j in range(72):                                   # marcas del reloj arcano
            a = j * math.tau / 72
            largo = 0.075 if j % 6 == 0 else 0.035
            p1 = (c + math.cos(a) * r * 0.90, c + math.sin(a) * r * 0.90)
            p2 = (c + math.cos(a) * r * (0.90 + largo), c + math.sin(a) * r * (0.90 + largo))
            pygame.draw.line(ext, (*claro, 210), p1, p2, 1)
        for j in range(12):                                   # glifos entre los anillos
            a = j * math.tau / 12
            gx, gy = c + math.cos(a) * r * 0.78, c + math.sin(a) * r * 0.78
            ux, uy = -math.sin(a), math.cos(a)                # tangente
            vx, vy = math.cos(a), math.sin(a)                 # radial
            tam = r * 0.055
            pts = [(rng.uniform(-1, 1) * tam, rng.uniform(-1, 1) * tam) for _ in range(rng.randint(3, 4))]
            glifo = [(gx + ux * px + vx * py, gy + uy * px + vy * py) for px, py in pts]
            pygame.draw.lines(ext, (*claro, 235), False, glifo, 2)

        interior = pygame.Surface((lado, lado), pygame.SRCALPHA)
        for rot in (-math.pi / 2, math.pi / 2):               # hexagrama
            tri = [(c + math.cos(rot + k * math.tau / 3) * r * 0.58,
                    c + math.sin(rot + k * math.tau / 3) * r * 0.58) for k in range(3)]
            pygame.draw.polygon(interior, (*color, 190), tri, 2)
        pygame.draw.circle(interior, (*color, 160), (c, c), int(r * 0.30), 1)
        for j in range(6):
            a = j * math.tau / 6
            pygame.draw.circle(interior, (*claro, 220), (int(c + math.cos(a) * r * 0.58),
                                                         int(c + math.sin(a) * r * 0.58)), 3)
        return ext, interior

    # ---- sonido ----------------------------------------------------------

    def _crear_sonidos(self, sonido_nav):
        self.snd_nav = sonido_nav
        self.snd_confirmar = None
        if not self.audio:
            return
        try:
            rate, fmt, canales = pygame.mixer.get_init()
            if fmt != -16:
                return
            self.snd_confirmar = self._sintetizar_impacto(rate, canales)
            if self.snd_nav is None:
                self.snd_nav = self._sintetizar_tick(rate, canales)
        except (pygame.error, ValueError, OverflowError) as e:
            print(f"[SELECCION] Sin sonidos de interfaz: {e}")

    @staticmethod
    def _sintetizar_tick(rate, canales):
        n = int(rate * 0.09)
        buf = array.array("h")
        fase = 0.0
        for i in range(n):
            u = i / n
            fase += math.tau * (900 + 700 * u) / rate
            v = math.sin(fase) * (1 - u) ** 2 * min(1.0, i / (rate * 0.003))
            buf.extend([int(v * 9000)] * canales)
        snd = pygame.mixer.Sound(buffer=buf.tobytes())
        snd.set_volume(0.5)
        return snd

    @staticmethod
    def _sintetizar_impacto(rate, canales):
        """Impacto grave con crujido y un brillo arcano que se apaga."""
        n = int(rate * 1.25)
        buf = array.array("h")
        rng = random.Random(7)
        fase = 0.0
        pasa_bajos = 0.0
        for i in range(n):
            t = i / rate
            fase += math.tau * (36 + 80 * math.exp(-t * 8)) / rate
            v = math.sin(fase) * math.exp(-t * 3.0) * 0.95
            pasa_bajos += 0.22 * (rng.uniform(-1, 1) - pasa_bajos)
            v += pasa_bajos * math.exp(-t * 16) * 0.9
            v += 0.16 * math.sin(math.tau * 660 * t) * math.exp(-t * 4.5)
            v += 0.11 * math.sin(math.tau * 990 * t) * math.exp(-t * 5.5)
            v += 0.07 * math.sin(math.tau * 1480 * t) * math.exp(-t * 7)
            v = math.tanh(v * 1.4) * 0.9
            buf.extend([int(v * 32000)] * canales)
        snd = pygame.mixer.Sound(buffer=buf.tobytes())
        snd.set_volume(0.8)
        return snd

    def _sonar(self, snd):
        if snd is not None and self.audio:
            try:
                snd.play()
            except pygame.error:
                pass

    # --------------------------------------------------------
    # Estado
    # --------------------------------------------------------

    def reset(self, indice=0):
        n = len(self.heroes)
        self.indice = indice % n if n else 0
        self.t = 0.0
        self.fase = "seleccion"          # "seleccion" | "confirmando"
        self.t_conf = 0.0
        self.terminado = False
        self.foco = [1.0 if i == self.indice else 0.0 for i in range(n)]
        self.acento = list(self.heroes[self.indice]["acento"])
        self.stats_vis = [0.0] * 4       # arrancan vacías y se llenan al entrar
        self.panel_a = 0.25
        self.chispas = []
        self.anillos = []
        self.shake = 0.0
        self.destello = 0.0
        self.t_guarda = 0.35             # evita confirmar por un Enter arrastrado
        for h in self.heroes:
            h["especial"] = 0.0
            h["anim_t"] = random.random() * 2.0
        self.heroes[self.indice]["especial"] = 1.0

    @property
    def confirmando(self):
        return self.fase == "confirmando"

    @property
    def nombre_elegido(self):
        return self.heroes[self.indice]["nombre"]

    def _slot_en(self, pos):
        W, H = self.W, self.H
        for i, cx in enumerate(self.slot_x):
            r = pygame.Rect(0, int(0.14 * H), int(0.25 * W), int(self.panel_rect.top - 0.14 * H))
            r.centerx = cx
            if r.collidepoint(pos):
                return i
        return None

    def _enfocar(self, i):
        if i == self.indice or self.fase != "seleccion":
            return
        self.indice = i
        h = self.heroes[i]
        h["especial"] = 1.0
        self.panel_a = 0.2
        self._sonar(self.snd_nav)
        self._rafaga_chispas(i, 16, 1.0)

    def _confirmar(self):
        if self.fase != "seleccion" or self.t_guarda > 0:
            return
        self.fase = "confirmando"
        self.t_conf = 0.0
        h = self.heroes[self.indice]
        h["especial"] = 1.0
        self.shake = 1.0
        self.destello = 1.0
        cx = self.slot_x[self.indice]
        cy = self.y_piso - int(0.21 * self.H)
        for k in range(3):
            self.anillos.append({"t": -0.13 * k, "cx": cx, "cy": cy})
        self._rafaga_chispas(self.indice, 90, 2.2)
        self._sonar(self.snd_confirmar)

    def _rafaga_chispas(self, i, cantidad, fuerza):
        s = self.s
        ac = _mezclar(self.heroes[i]["acento"], (255, 255, 255), 0.45)
        x = self.slot_x[i]
        y = self.y_piso - 6 * s
        for _ in range(cantidad):
            ang = self.rng.uniform(math.pi * 1.05, math.pi * 1.95)
            vel = self.rng.uniform(50, 190) * s * fuerza
            vida = self.rng.uniform(0.55, 1.2)
            self.chispas.append([x + self.rng.uniform(-30, 30) * s, y,
                                 math.cos(ang) * vel, math.sin(ang) * vel,
                                 vida, vida, ac, max(1, round(self.rng.choice((1, 2, 2, 3)) * s * 0.8))])

    # --------------------------------------------------------
    # Entrada
    # --------------------------------------------------------

    def handle_event(self, event):
        """Devuelve "back" si el jugador pide volver al menú; si no, None."""
        if self.fase != "seleccion":
            return None
        n = len(self.heroes)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._enfocar((self.indice - 1) % n)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._enfocar((self.indice + 1) % n)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._confirmar()

        elif event.type == pygame.MOUSEMOTION:
            i = self._slot_en(event.pos)
            if i is not None:
                self._enfocar(i)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            i = self._slot_en(event.pos)
            if i is not None:
                self._enfocar(i)
                self._confirmar()
        return None

    # --------------------------------------------------------
    # Actualización
    # --------------------------------------------------------

    def update(self, dt_ms):
        """Avanza la pantalla. Devuelve "seleccionado" cuando termina la secuencia épica."""
        dt = min(max(dt_ms, 0) / 1000.0, 0.05)
        self.t += dt
        self.t_guarda = max(0.0, self.t_guarda - dt)

        k_foco = 1 - math.exp(-dt * 9)
        for i, h in enumerate(self.heroes):
            objetivo = 1.0 if i == self.indice else 0.0
            self.foco[i] += (objetivo - self.foco[i]) * k_foco
            vel = 1.0 + 1.4 * h["especial"]
            h["anim_t"] += dt * vel
            h["especial"] = max(0.0, h["especial"] - dt / (1.2 if self.fase == "confirmando" else 0.8))

        objetivo_ac = self.heroes[self.indice]["acento"]
        k_ac = 1 - math.exp(-dt * 6)
        for j in range(3):
            self.acento[j] += (objetivo_ac[j] - self.acento[j]) * k_ac

        k_st = 1 - math.exp(-dt * 4.5)
        for j, (_, valor) in enumerate(self.heroes[self.indice]["stats"]):
            self.stats_vis[j] += (valor - self.stats_vis[j]) * k_st

        self.panel_a = min(1.0, self.panel_a + dt * 4.0)

        for c in self.chispas:
            c[0] += c[2] * dt
            c[1] += c[3] * dt
            c[2] *= (1 - 1.2 * dt)
            c[3] = c[3] * (1 - 1.2 * dt) - 22 * self.s * dt
            c[4] -= dt
        self.chispas = [c for c in self.chispas if c[4] > 0]

        for a in self.anillos:
            a["t"] += dt
        self.anillos = [a for a in self.anillos if a["t"] < 1.0]

        if self.fase == "confirmando":
            self.t_conf += dt
            self.shake = max(0.0, 1.0 - self.t_conf / 0.75) ** 2
            self.destello = max(0.0, 1.0 - self.t_conf / 0.55)
            if self.t_conf >= self.T_CONF_FIN and not self.terminado:
                self.terminado = True
                return "seleccionado"
        return None

    # --------------------------------------------------------
    # Dibujo
    # --------------------------------------------------------

    def draw(self, destino):
        sc = self.scene
        W, H, s = self.W, self.H, self.s
        sc.blit(self.fondo, (0, 0))
        self._dibujar_niebla(sc)

        n = len(self.heroes)
        y_c = self.y_piso - int(0.21 * H)
        for i, h in enumerate(self.heroes):
            f = self.foco[i]
            if f < 0.02:
                continue
            cx = self.slot_x[i]
            halo = h["halo"]
            halo.set_alpha(int(255 * f))
            sc.blit(halo, halo.get_rect(center=(cx, y_c)))
            ang = self.t * 14.0
            ext = pygame.transform.rotate(h["runas_ext"], ang)
            ext.set_alpha(int(215 * f))
            sc.blit(ext, ext.get_rect(center=(cx, y_c)))
            inte = pygame.transform.rotate(h["runas_int"], -ang * 1.7)
            inte.set_alpha(int(190 * f))
            sc.blit(inte, inte.get_rect(center=(cx, y_c)))

        for i in range(n):
            self._dibujar_altar(sc, i)
        for i in range(n):
            self._dibujar_heroe(sc, i)

        self._dibujar_capa_aditiva(sc)
        self._dibujar_titulo(sc)
        self._dibujar_etiquetas(sc)
        self._dibujar_panel(sc)
        sc.blit(self.vineta, (0, 0))

        # Composición final: sacudida de pantalla
        ox = oy = 0
        if self.shake > 0.01:
            amp = 16 * s * self.shake
            ox = int(self.rng.uniform(-amp, amp))
            oy = int(self.rng.uniform(-amp, amp))
            destino.fill((0, 0, 0))
        destino.blit(sc, (ox, oy))

        # Destello arcano
        if self.destello > 0.01:
            col = _mezclar((255, 255, 255), self.acento, 0.35)
            self.overlay.fill(col)
            self.overlay.set_alpha(int(255 * self.destello ** 1.5))
            destino.blit(self.overlay, (0, 0))

        # Fundidos: entrada desde negro / salida hacia negro tras confirmar
        negro = 0.0
        if self.t < 0.6:
            negro = 1.0 - self.t / 0.6
        if self.fase == "confirmando" and self.t_conf > self.T_CONF_FADE:
            negro = max(negro, _clamp((self.t_conf - self.T_CONF_FADE) / (self.T_CONF_FIN - self.T_CONF_FADE)))
        if negro > 0.003:
            self.overlay.fill((0, 0, 0))
            self.overlay.set_alpha(int(255 * negro))
            destino.blit(self.overlay, (0, 0))

    # ---- fondo -----------------------------------------------------------

    def _dibujar_niebla(self, sc):
        spr = self.niebla_sprite
        ancho = spr.get_width()
        total = self.W + ancho
        for b in self.niebla:
            x = (b[0] + self.t * b[2]) % total - ancho
            sc.blit(spr, (int(x), int(b[1])))

    def _dibujar_capa_aditiva(self, sc):
        """Brasas, chispas y ondas de choque: se suman sobre la escena."""
        s = self.s
        capa = self.layer
        capa.fill((0, 0, 0))
        t = self.t
        ac = _mezclar((255, 125, 45), self.acento, 0.55)
        atenua = 0.35 if self.fase == "confirmando" and self.t_conf > self.T_CONF_FADE else 1.0
        W, H = self.W, self.H

        for x0, y0, vel, fase, tam in self.brasas:
            y = (y0 - t * vel) % (H + 20) - 10
            x = (x0 + math.sin(t * 0.5 + fase) * 14 * s) % W
            fl = 0.55 + 0.45 * math.sin(t * 2.0 + fase * 3)
            pygame.draw.circle(capa, _escalar(ac, fl * 0.85 * atenua), (int(x), int(y)), tam)

        for cx, cy, vx, vy, vida, vmax, col, tam in self.chispas:
            f = vida / vmax
            pygame.draw.circle(capa, _escalar(col, f), (int(cx), int(cy)), tam)

        for a in self.anillos:
            p = a["t"]
            if p <= 0:
                continue
            e = _ease_out(p)
            r = int(e * 0.62 * self.H)
            if r < 4:
                continue
            col = _escalar(_mezclar(self.acento, (255, 255, 255), 0.5), (1 - p) ** 1.2)
            grosor = max(1, int(9 * s * (1 - p)))
            pygame.draw.circle(capa, col, (a["cx"], a["cy"]), r, min(grosor, r))
            for j in range(48):                                 # marcas rúnicas del anillo
                ang = j * math.tau / 48 + p * 2.5
                r1, r2 = r * 0.93, r * (1.03 if j % 2 else 1.07)
                pygame.draw.line(capa, col,
                                 (a["cx"] + math.cos(ang) * r1, a["cy"] + math.sin(ang) * r1),
                                 (a["cx"] + math.cos(ang) * r2, a["cy"] + math.sin(ang) * r2), 2)
            rect = pygame.Rect(0, 0, 2 * r, int(r * 0.56))
            rect.center = (a["cx"], self.y_piso)
            pygame.draw.ellipse(capa, _escalar(col, 0.8), rect, max(1, grosor // 2))

        sc.blit(capa, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ---- altares y héroes ------------------------------------------------

    def _dibujar_altar(self, sc, i):
        h = self.heroes[i]
        f = self.foco[i]
        s = self.s
        cx, piso = self.slot_x[i], self.y_piso
        aw, ah = self.alt_w, self.alt_h
        eh = int(aw * 0.26)
        ac = h["acento"]

        if f > 0.02:
            g = h["glow_piso"]
            g.set_alpha(int(255 * f))
            sc.blit(g, g.get_rect(center=(cx, piso + int(ah * 0.4))))
            cono = h["cono"]
            cono.set_alpha(int(255 * f))
            sc.blit(cono, cono.get_rect(midbottom=(cx, piso)))

        lado = (28, 23, 32)
        pygame.draw.rect(sc, lado, (cx - aw // 2, piso, aw, ah))
        pygame.draw.ellipse(sc, lado, (cx - aw // 2, piso + ah - eh // 2, aw, eh))
        tapa = pygame.Rect(cx - aw // 2, piso - eh // 2, aw, eh)
        pygame.draw.ellipse(sc, (48, 41, 54), tapa)
        interior = tapa.inflate(-int(aw * 0.14), -int(eh * 0.22))
        pygame.draw.ellipse(sc, _mezclar((30, 26, 36), ac, f * 0.30), interior)
        pygame.draw.ellipse(sc, _mezclar((78, 68, 88), ac, f), tapa, max(1, int(2 * s + f * 2)))

        rx, ry = aw * 0.43, eh * 0.43
        giro = self.t * 0.6 * (0.3 + f)
        for j in range(16):
            a = giro + j * math.tau / 16
            brillo = 0.35 + 0.65 * f * (0.5 + 0.5 * math.sin(a * 2 + self.t * 3))
            col = _mezclar((70, 62, 80), _mezclar(ac, (255, 255, 255), 0.25), brillo)
            pygame.draw.circle(sc, col, (int(cx + math.cos(a) * rx), int(piso + math.sin(a) * ry)),
                               max(1, int(2 * s)))

    def _superficies_heroe(self, h, idx, sc_f, con_normal, con_flash):
        """Devuelve (oscuro, normal, destello, ancho) a la escala flotante `sc_f`.

        En reposo (escala entera) se usan superficies cacheadas, escaladas con vecino
        más cercano. Solo durante el instante del cambio de foco se re-escala entre k y
        k+1, así que la imagen queda perfectamente nítida en cuanto se asienta.
        """
        k = self.k
        if sc_f <= k + 0.012:
            esc, exacto = k, True
        elif sc_f >= k + 0.988:
            esc, exacto = k + 1, True
        else:
            esc, exacto = k + 1, False

        def variante(var):
            clave = (idx, esc, var)
            sup = h["cache"].get(clave)
            if sup is None:
                base = self._frames_escala(h, esc)[idx]
                if var == "n":
                    sup = base
                elif var == "d":
                    sup = base.copy()
                    sup.fill((140, 135, 158, 255), special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    sup = base.copy()
                    sup.fill((125, 125, 125, 0), special_flags=pygame.BLEND_RGB_ADD)
                h["cache"][clave] = sup
            return sup

        oscuro = variante("d")
        normal = variante("n") if con_normal else None
        flash = variante("f") if con_flash else None
        if not exacto:
            tam = (max(1, int(round(oscuro.get_width() * sc_f / esc))),
                   max(1, int(round(oscuro.get_height() * sc_f / esc))))
            oscuro = pygame.transform.scale(oscuro, tam)
            normal = pygame.transform.scale(normal, tam) if normal is not None else None
            flash = pygame.transform.scale(flash, tam) if flash is not None else None
        return oscuro, normal, flash

    def _frames_escala(self, h, esc):
        clave = ("base", esc)
        lista = h["cache"].get(clave)
        if lista is None:
            lista = []
            for f in h["frames"]:
                if h["pixel"]:
                    lista.append(pygame.transform.scale(f, (f.get_width() * esc, f.get_height() * esc)))
                else:   # ilustración estática (respaldo): sí admite suavizado
                    alto = int(self.alto_nativo * esc)
                    ancho = max(1, int(f.get_width() * alto / f.get_height()))
                    lista.append(pygame.transform.smoothscale(f, (ancho, alto)))
            h["cache"][clave] = lista
        return lista

    def _dibujar_heroe(self, sc, i):
        h = self.heroes[i]
        f = self.foco[i]
        s = self.s
        sp = h["especial"]
        conf = self.fase == "confirmando"
        elegido = i == self.indice
        idx = int(h["anim_t"] * self.FPS_IDLE) % len(h["frames"])

        # "Pose especial": salto breve + destello al enfocar / confirmar
        hop = 0.0
        if sp > 0:
            hop = math.sin((1 - sp) * math.pi) * (22 if (conf and elegido) else 10) * s
        elev = f * 14 * s + hop
        if conf and elegido:
            elev += _ease_out(self.t_conf / 0.5) * 12 * s

        oscuro, normal, flash = self._superficies_heroe(
            h, idx, self.k + f, con_normal=f > 0.012, con_flash=sp > 0.02)

        ancho, alto = oscuro.get_size()
        cx = self.slot_x[i]
        izq = int(round(cx - h["pivot"] * ancho))
        arriba = int(round(self.y_piso - 5 * s - elev - alto))

        # Los no elegidos se apagan casi del todo mientras se confirma
        if conf and not elegido:
            oscuro = oscuro.copy()
            oscuro.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)

        oscuro.set_alpha(255)
        sc.blit(oscuro, (izq, arriba))
        if normal is not None:
            normal.set_alpha(int(255 * _clamp(f)))
            sc.blit(normal, (izq, arriba))
        if flash is not None:
            flash.set_alpha(int(190 * _clamp(sp)))
            sc.blit(flash, (izq, arriba))

    # ---- interfaz --------------------------------------------------------

    def _dibujar_titulo(self, sc):
        s, W, H = self.s, self.W, self.H
        t = self.titulo_surf
        sc.blit(t, t.get_rect(center=(W // 2, int(0.075 * H))))
        # Divisor ornamental: líneas doradas con rombo central teñido por el acento
        y = int(0.138 * H)
        oro = (150, 118, 52)
        mitad = int(W * 0.17)
        for lado in (-1, 1):
            for j in range(mitad):
                u = j / mitad
                col = _mezclar(oro, (14, 10, 18), u ** 1.2)
                x = W // 2 + lado * (int(12 * s) + j)
                sc.set_at((x, y), col)
                sc.set_at((x, y + 1), _escalar(col, 0.6))
        d = int(7 * s)
        pygame.draw.polygon(sc, _mezclar((200, 160, 70), self.acento, 0.5),
                            [(W // 2, y - d), (W // 2 + d, y), (W // 2, y + d), (W // 2 - d, y)])
        pygame.draw.polygon(sc, (20, 14, 22),
                            [(W // 2, y - d // 2), (W // 2 + d // 2, y), (W // 2, y + d // 2), (W // 2 - d // 2, y)])

    def _dibujar_etiquetas(self, sc):
        s = self.s
        for i, h in enumerate(self.heroes):
            f = self.foco[i]
            cx = self.slot_x[i]
            y = self.y_piso + self.alt_h + int(14 * s)
            col = _mezclar((120, 114, 130), (255, 255, 255), f)
            txt = self.f_etiqueta.render(h["nombre"].upper(), True, col)
            sc.blit(txt, txt.get_rect(midtop=(cx, y)))
            elem = self.f_peq.render(h["elemento"].upper(), True, _mezclar((84, 78, 92), h["acento"], f))
            sc.blit(elem, elem.get_rect(midtop=(cx, y + txt.get_height() + int(2 * s))))

        # Flechas de navegación pulsantes
        pulso = math.sin(self.t * 5) * 5 * s
        ac = _mezclar((200, 160, 70), self.acento, 0.4)
        yf = self.y_piso - int(0.17 * self.H)
        xl, xr = int(0.02 * self.W + 14 * s - pulso), int(0.98 * self.W - 14 * s + pulso)
        g = int(14 * s)
        pygame.draw.polygon(sc, ac, [(xl + g, yf - g), (xl, yf), (xl + g, yf + g)], max(1, int(2 * s)))
        pygame.draw.polygon(sc, ac, [(xr - g, yf - g), (xr, yf), (xr - g, yf + g)], max(1, int(2 * s)))

        ayuda = self.f_ayuda.render(
            "A / D  o  < >  elegir      ENTER / ESPACIO  confirmar      ESC  volver al menú",
            True, (128, 122, 140))
        sc.blit(ayuda, ayuda.get_rect(center=(self.W // 2, int(0.962 * self.H))))

    def _dibujar_panel(self, sc):
        s = self.s
        r = self.panel_rect
        h = self.heroes[self.indice]
        ac = tuple(int(v) for v in self.acento)

        bg = self.panel_bg
        bg.fill((0, 0, 0, 0))
        rad = int(14 * s)
        pygame.draw.rect(bg, (16, 12, 20, 232), bg.get_rect(), border_radius=rad)
        pygame.draw.rect(bg, (*_mezclar((92, 74, 48), ac, 0.55), 255), bg.get_rect(),
                         max(1, int(2 * s)), border_radius=rad)
        interior = bg.get_rect().inflate(-int(12 * s), -int(12 * s))
        pygame.draw.rect(bg, (*_mezclar((50, 40, 40), ac, 0.3), 150), interior, 1, border_radius=int(10 * s))
        d = int(6 * s)
        for (x, y) in ((int(6 * s), int(6 * s)), (r.w - int(6 * s), int(6 * s)),
                       (int(6 * s), r.h - int(6 * s)), (r.w - int(6 * s), r.h - int(6 * s))):
            pygame.draw.polygon(bg, (205, 165, 75), [(x, y - d), (x + d, y), (x, y + d), (x - d, y)])
        sc.blit(bg, r.topleft)

        ct = self.panel_ct
        ct.fill((0, 0, 0, 0))
        pad = int(22 * s)
        pw, ph = r.size
        y0 = int(16 * s)
        c1x = pad
        c1w = self.col1_w
        c2x = c1x + c1w + int(28 * s)
        c2w = int((pw - 2 * pad) * 0.27)
        c3x = c2x + c2w + int(28 * s)
        c3w = pw - pad - c3x

        # --- Columna 1: nombre, título, elemento y lore
        nombre = self.f_nombre.render(h["nombre"].upper(), True, (255, 255, 255))
        ct.blit(nombre, (c1x, y0 - int(4 * s)))
        y = y0 - int(4 * s) + nombre.get_height()
        sub = self.f_sub.render(h["titulo"], True, ac)
        ct.blit(sub, (c1x, y))
        y += sub.get_height() + int(4 * s)
        dd = int(5 * s)
        pygame.draw.polygon(ct, ac, [(c1x + dd, y + dd), (c1x + 2 * dd, y + 2 * dd),
                                     (c1x + dd, y + 3 * dd), (c1x, y + 2 * dd)])
        el = self.f_peq.render("ELEMENTO  ·  " + h["elemento"].upper(), True, (190, 180, 168))
        ct.blit(el, (c1x + 3 * dd, y + int(2 * s)))
        y += el.get_height() + int(8 * s)
        for linea in h["lore"]:
            ct.blit(self.f_txt.render(linea, True, (205, 200, 208)), (c1x, y))
            y += self.f_txt.get_linesize()

        # --- Columna 2: barras de atributos animadas
        self._cabecera(ct, "ATRIBUTOS", c2x, y0, c2w, ac)
        fila = int(31 * s)
        for j, (etiqueta, valor) in enumerate(h["stats"]):
            yy = y0 + int(30 * s) + j * fila
            ct.blit(self.f_peq.render(etiqueta, True, (200, 190, 175)), (c2x, yy))
            vis = self.stats_vis[j]
            vtxt = self.f_peq.render(str(int(round(vis))), True, _mezclar((200, 190, 175), ac, 0.6))
            ct.blit(vtxt, (c2x + c2w - vtxt.get_width(), yy))
            barra = pygame.Rect(c2x, yy + int(16 * s), c2w, max(4, int(8 * s)))
            pygame.draw.rect(ct, (36, 31, 42), barra, border_radius=4)
            ancho = int(barra.w * _clamp(vis / 100.0))
            if ancho > 2:
                relleno = pygame.Rect(barra.x, barra.y, ancho, barra.h)
                pygame.draw.rect(ct, _mezclar(ac, (0, 0, 0), 0.35), relleno, border_radius=4)
                brillo = pygame.Rect(barra.x, barra.y, ancho, max(2, barra.h // 2))
                pygame.draw.rect(ct, ac, brillo, border_radius=4)
                pygame.draw.circle(ct, _mezclar(ac, (255, 255, 255), 0.7),
                                   (barra.x + ancho - 1, barra.centery), max(2, barra.h // 2 + 1))
            for q in (0.25, 0.5, 0.75):
                x = barra.x + int(barra.w * q)
                pygame.draw.line(ct, (16, 12, 20), (x, barra.y), (x, barra.bottom - 1))

        # --- Columna 3: poderes con icono
        self._cabecera(ct, "PODERES", c3x, y0, c3w, ac)
        fila = int(41 * s)
        rr = int(15 * s)
        for j, (nom, desc, icono) in enumerate(h["habilidades"]):
            yy = y0 + int(30 * s) + j * fila
            _icono(ct, icono, c3x + rr, yy + rr, rr, ac)
            tx = c3x + 2 * rr + int(10 * s)
            ct.blit(self.f_txt_b.render(nom, True, (245, 240, 232)), (tx, yy - int(1 * s)))
            ct.blit(self.f_txt.render(recortar_texto(desc, self.f_txt, c3w - (tx - c3x)), True, (178, 172, 186)),
                    (tx, yy + int(17 * s)))

        ct.set_alpha(int(255 * _clamp(self.panel_a)))
        sc.blit(ct, r.topleft)

    def _cabecera(self, sup, texto, x, y, ancho, ac):
        t = self.f_peq.render(" ".join(texto), True, (215, 172, 78))
        sup.blit(t, (x, y))
        yl = y + t.get_height() // 2
        x1 = x + t.get_width() + int(10 * self.s)
        pygame.draw.line(sup, _mezclar((120, 94, 48), ac, 0.4), (x1, yl), (x + ancho, yl), 1)


# ============================================================
# COMPATIBILIDAD: función independiente (como el archivo original)
# ============================================================

def seleccionar_personaje(pantalla, characters=None):
    """Bucle propio de la pantalla; devuelve {"nombre", "name", "elemento", "color"}."""
    reloj = pygame.time.Clock()
    sel = SeleccionPersonajes(pantalla, characters)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if sel.handle_event(ev) == "back":
                pygame.quit()
                sys.exit()
        if sel.update(reloj.tick(60)) == "seleccionado":
            h = sel.heroes[sel.indice]
            return {"nombre": h["nombre"], "name": h["nombre"],
                    "elemento": h["elemento"], "color": h["acento"]}
        sel.draw(pantalla)
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass
    ventana = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Selección de personajes")
    elegido = seleccionar_personaje(ventana)
    print(f"Personaje elegido: {elegido['nombre']} ({elegido['elemento']})")
    pygame.quit()