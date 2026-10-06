import pygame
import sys
import math
import subprocess
import os
import random
import numpy as np
 
# Requiere:  pip install pygame numpy
 
pygame.init()
pygame.font.init()
 
# ----------------------------------------------------------------------------
# Ventana
# ----------------------------------------------------------------------------
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Selector de Niveles")
clock = pygame.time.Clock()
 
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
CYAN = (0, 210, 255)
RED = (255, 40, 40)
ORANGE = (255, 120, 0)
 
PLANET_RADIUS = 185
R = PLANET_RADIUS
D = R * 2
CENTER_X, CENTER_Y = WIDTH // 2, 300
NODE_R = 38
 
# ----------------------------------------------------------------------------
# Niveles (lat / lon en grados sobre la superficie)
# boss: clave de la silueta del jefe | tag/big: texto del cartel
# ----------------------------------------------------------------------------
tierra_levels = [
    {"id": "Nivel 2", "file": "nivel_2.py", "lat": 0, "lon": -110, "boss": "2", "tag": "NIVEL", "big": "2"},
    {"id": "Nivel 1", "file": "nivel_1.py", "lat": 25, "lon": 0, "boss": "1", "tag": "NIVEL", "big": "1"},
    {"id": "Nivel 3", "file": "nivel_3.py", "lat": 0, "lon": 110, "boss": "3", "tag": "NIVEL", "big": "3"},
]
gehena_levels = [
    {"id": "Nivel 4", "file": "nivel_4.py", "lat": 20, "lon": -80, "boss": "4", "tag": "NIVEL", "big": "4"},
    {"id": "Nivel Secreto", "file": "nivel_5.py", "lat": -10, "lon": 80, "boss": "?", "tag": "???", "big": "SECRETO"},
]
 
current_planet = "TIERRA"
active_levels = tierra_levels
current_index = 1
planet_rotation = 0.0
target_rotation = 0.0
env_t = 0.0          # 0 = espacio de la Tierra, 1 = espacio de Gehena
env_target = 0.0
SUN_LON = 35.0       # posicion del sol en el "mundo" (gira junto con el planeta)
 
 
def ejecutar_nivel(script_name):
    """Abre el nivel seleccionado y espera a que termine."""
    if not script_name:
        print("[Aviso] Este nivel aún no está disponible.")
        return

    carpeta_selector = os.path.dirname(os.path.abspath(__file__))
    ruta_nivel = os.path.abspath(os.path.join(carpeta_selector, script_name))

    if not os.path.isfile(ruta_nivel):
        print("[ERROR] No se encontró el nivel:")
        print(ruta_nivel)
        input("Presioná ENTER para cerrar...")
        return

    print(f"[OK] Abriendo nivel: {ruta_nivel}")

    ejecutable_python = sys.executable
    if ejecutable_python.lower().endswith("pythonw.exe"):
        ejecutable_python = os.path.join(
            os.path.dirname(ejecutable_python),
            "python.exe"
        )

    try:
        pygame.quit()

        # El selector espera mientras se ejecuta el nivel.
        # Esto evita que el proceso del nivel dependa del selector.
        resultado = subprocess.run(
            [ejecutable_python, ruta_nivel],
            cwd=carpeta_selector
        )

        print(f"[INFO] Nivel terminado. Código: {resultado.returncode}")
        sys.exit()

    except Exception as error:
        print(f"[ERROR] No se pudo iniciar el nivel: {error}")
        input("Presioná ENTER para cerrar...")

def lerp(a, b, t):
    return a + (b - a) * t
 
 
def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)
 
 
def mix(a, b, t):
    """Mezcla de colores con broadcasting: a + (b-a)*t[..., None]."""
    return a + (b - a) * t[..., None]
 
 
def col3(r, g, b):
    return np.array([r, g, b], dtype=np.float32)
 
 
_font_cache = {}
 
 
def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(
            "impact,bahnschrift,arialblack,segoeui,verdana,consolas", size)
    return _font_cache[size]
 
 
def fancy_text(text, font, top, bottom, outline, spacing=0, ow=2,
               shadow=(0, 0, 0)):
    """Texto con degradado vertical, contorno y sombra."""
    glyphs = [font.render(ch, True, (255, 255, 255)) for ch in text]
    w = sum(g.get_width() for g in glyphs) + spacing * (len(text) - 1)
    h = font.get_height()
    base = pygame.Surface((w, h), pygame.SRCALPHA)
    x = 0
    for g in glyphs:
        base.blit(g, (x, 0))
        x += g.get_width() + spacing
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        c = (int(lerp(top[0], bottom[0], t)), int(lerp(top[1], bottom[1], t)),
             int(lerp(top[2], bottom[2], t)), 255)
        pygame.draw.line(grad, c, (0, y), (w, y))
    fill = base.copy()
    fill.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
 
    tint = base.copy()
    tint.fill(outline + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    sh = base.copy()
    sh.fill(shadow + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    out = pygame.Surface((w + 2 * ow + 2, h + 2 * ow + 4), pygame.SRCALPHA)
    out.blit(sh, (ow + 1, ow + 3))
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx * dx + dy * dy <= ow * ow + 1:
                out.blit(tint, (ow + dx, ow + dy))
    out.blit(fill, (ow, ow))
    return out
 
 
# ----------------------------------------------------------------------------
# Ruido (periodico en el eje X para que la textura de la esfera cierre bien)
# ----------------------------------------------------------------------------
def _upsample(grid, w, h, cx, cy):
    xs = np.arange(w) / w * cx
    ys = np.arange(h) / h * cy
    x0 = np.floor(xs).astype(int)
    fx = xs - x0
    x1 = (x0 + 1) % cx
    x0 = x0 % cx
    y0 = np.floor(ys).astype(int)
    fy = ys - y0
    y1 = y0 + 1
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    g00 = grid[x0][:, y0]
    g10 = grid[x1][:, y0]
    g01 = grid[x0][:, y1]
    g11 = grid[x1][:, y1]
    top = g00 * (1 - fx)[:, None] + g10 * fx[:, None]
    bot = g01 * (1 - fx)[:, None] + g11 * fx[:, None]
    return top * (1 - fy)[None, :] + bot * fy[None, :]
 
 
def fbm(w, h, base, octaves, rng, persistence=0.5):
    total = np.zeros((w, h), dtype=np.float32)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        cx = base * (2 ** o)
        cy = max(2, (base // 2) * (2 ** o))
        grid = rng.random((cx, cy + 1)).astype(np.float32)
        total += amp * _upsample(grid, w, h, cx, cy)
        norm += amp
        amp *= persistence
    return total / norm
 
 
# ----------------------------------------------------------------------------
# Texturas de los planetas (mapa equirectangular)
# ----------------------------------------------------------------------------
TW, TH = 1024, 512
 
CONTINENTS = [
    # Norteamerica
    [(-168, 66), (-160, 70), (-140, 70), (-125, 70), (-95, 72), (-80, 70), (-65, 60),
     (-62, 50), (-67, 45), (-76, 38), (-81, 31), (-80, 25), (-83, 29), (-90, 30),
     (-97, 27), (-97, 22), (-91, 19), (-87, 21), (-88, 16), (-83, 15), (-83, 9),
     (-79, 9), (-85, 10), (-92, 14), (-97, 16), (-105, 20), (-108, 25), (-113, 31),
     (-117, 32), (-121, 35), (-124, 40), (-124, 48), (-128, 51), (-135, 58),
     (-145, 60), (-152, 59), (-158, 57), (-165, 54), (-160, 59), (-166, 61), (-165, 65)],
    # Groenlandia
    [(-55, 60), (-45, 60), (-20, 70), (-18, 78), (-30, 83), (-60, 82), (-72, 78), (-58, 70)],
    # Sudamerica
    [(-80, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-35, -5), (-35, -9), (-39, -14),
     (-41, -22), (-48, -26), (-53, -34), (-58, -38), (-63, -41), (-65, -47), (-68, -53),
     (-72, -54), (-74, -47), (-73, -37), (-71, -30), (-70, -18), (-76, -14), (-81, -6),
     (-80, -2), (-78, 2), (-77, 8)],
    # Africa
    [(-17, 21), (-13, 28), (-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12),
     (51, 12), (48, 4), (40, -3), (40, -15), (35, -24), (33, -28), (27, -34), (19, -35),
     (15, -27), (12, -17), (13, -6), (9, 3), (5, 5), (-8, 4), (-13, 8), (-17, 14)],
    # Eurasia
    [(-9, 43), (-9, 37), (-5, 36), (0, 39), (3, 43), (8, 44), (13, 42), (16, 40), (18, 40),
     (23, 37), (26, 40), (29, 41), (36, 36), (35, 33), (35, 28), (43, 13), (52, 16),
     (59, 23), (56, 26), (51, 25), (48, 30), (57, 27), (62, 25), (68, 23), (73, 20),
     (77, 8), (80, 13), (80, 16), (87, 21), (92, 22), (97, 16), (98, 8), (103, 1),
     (101, 6), (105, 10), (109, 12), (106, 19), (110, 21), (117, 23), (122, 30),
     (121, 37), (125, 40), (129, 36), (130, 43), (141, 50), (140, 58), (155, 60),
     (163, 60), (180, 65), (180, 69), (150, 71), (130, 72), (110, 77), (90, 76),
     (70, 73), (60, 69), (45, 68), (40, 66), (30, 70), (20, 70), (12, 66), (5, 61),
     (5, 58), (10, 57), (10, 54), (8, 54), (4, 52), (-1, 50), (-4, 48), (-1, 45)],
    # Reino Unido / Irlanda
    [(-5, 50), (1, 51), (2, 53), (-2, 57), (-5, 58), (-6, 56), (-3, 54)],
    [(-10, 52), (-6, 52), (-6, 55), (-10, 54)],
    # Madagascar
    [(44, -25), (47, -25), (50, -15), (49, -12), (44, -17)],
    # Australia
    [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -26),
     (150, -37), (141, -38), (135, -34), (129, -32), (115, -34), (114, -26)],
    # Indonesia / Nueva Guinea / Japon / Nueva Zelanda
    [(95, 5), (104, -3), (106, -6), (100, -2)],
    [(109, 2), (117, 7), (119, 0), (116, -4), (110, -3)],
    [(131, -1), (141, -3), (150, -10), (142, -9), (135, -4)],
    [(130, 32), (135, 34), (140, 36), (142, 40), (141, 43), (139, 38), (133, 34)],
    [(172, -34), (178, -38), (175, -41), (172, -41)],
    [(167, -46), (174, -41), (171, -46)],
    # Antartida
    [(-180, -71), (-120, -74), (-60, -70), (0, -69), (60, -67), (120, -66), (180, -71),
     (180, -90), (-180, -90)],
]
 
 
def _lonlat_px(lon, lat):
    return ((lon + 180) / 360 * TW, (90 - lat) / 180 * TH)
 
 
def build_earth():
    rng = np.random.default_rng(11)
    ms = pygame.Surface((TW, TH))
    ms.fill((0, 0, 0))
    for poly in CONTINENTS:
        pygame.draw.polygon(ms, (255, 255, 255), [_lonlat_px(lo, la) for lo, la in poly])
    small = pygame.transform.smoothscale(ms, (TW // 10, TH // 10))
    blur = pygame.transform.smoothscale(small, (TW, TH))
    m_blur = pygame.surfarray.array3d(blur)[:, :, 0].astype(np.float32) / 255.0
 
    n1 = fbm(TW, TH, 8, 5, rng)
    n2 = fbm(TW, TH, 12, 5, rng)
    n3 = fbm(TW, TH, 6, 4, rng)
    n4 = fbm(TW, TH, 16, 5, rng)
 
    landf = smoothstep(0.46, 0.54, m_blur + (n1 - 0.5) * 0.6)
    lat = (90 - (np.arange(TH) + 0.5) / TH * 180).astype(np.float32)[None, :]
    A = np.abs(lat) * np.ones((TW, 1), dtype=np.float32)
 
    # Tierra firme
    c = mix(col3(46, 132, 58), col3(52, 88, 60), np.clip((A - 46) / 16, 0, 1))
    jungle = np.clip(1 - A / 16, 0, 1) * 0.85 * np.clip((n2 - 0.25) * 3 + 0.3, 0, 1)
    c = mix(c, col3(22, 96, 44), jungle)
    desert = np.exp(-((A - 23) / 8.5) ** 2) * np.clip((n3 - 0.38) * 3.5, 0, 1)
    c = mix(c, col3(206, 178, 110), desert)
    mt = np.clip((n4 - 0.6) * 5, 0, 1) * (1 - desert * 0.5)
    c = mix(c, col3(112, 98, 84), mt * 0.8)
    snow = np.clip((A - 66 + (n2 - 0.5) * 16) / 5, 0, 1)
    snow = np.maximum(snow, mt * np.clip((n4 - 0.72) * 8, 0, 1) * 0.9)
    c = mix(c, col3(240, 244, 250), snow)
    c = c * (0.84 + 0.32 * n2)[..., None]
 
    # Oceano
    shore = np.clip(m_blur * 2.0 + (n1 - 0.5) * 0.4, 0, 1) ** 1.2
    w = mix(col3(6, 28, 92), col3(26, 116, 172), shore)
    ice = np.clip((A - 72 + (n2 - 0.5) * 10) / 4, 0, 1)
    w = mix(w, col3(225, 240, 250), ice)
 
    final = mix(w, c, landf)
    coast = landf * (1 - landf) * 4
    final = final + coast[..., None] * col3(34, 32, 10)
 
    nc = fbm(TW, TH, 5, 5, rng)
    cloud = np.clip((nc - 0.5) * 3.4, 0, 1)
    return {
        "tex": np.clip(final, 0, 255).astype(np.uint8),
        "water": ((1 - landf) * (1 - ice)).astype(np.float32),
        "cloud": cloud.astype(np.float32),
        "cloud_col": col3(255, 255, 255),
        "cloud_a": 0.78,
    }
 
 
def build_gehena():
    rng = np.random.default_rng(23)
    n1 = fbm(TW, TH, 6, 6, rng)
    n2 = fbm(TW, TH, 10, 4, rng)
    n3 = fbm(TW, TH, 20, 3, rng)
 
    ash_amt = smoothstep(0.47, 0.53, n1 + (n3 - 0.5) * 0.12)   # 1 = ceniza, 0 = lava
    d = 1 - ash_amt                                            # profundidad de lava
    edge = ash_amt * d * 4
 
    # Ceniza gris con costra oscura junto a la lava
    ash = mix(col3(58, 54, 54), col3(132, 124, 118), np.clip(n3 * 1.3 - 0.15, 0, 1))
    ash = ash * (1 - 0.45 * edge)[..., None]
    ash = ash + edge[..., None] * col3(95, 24, 0)
    crack = np.exp(-((n2 - 0.5) / 0.025) ** 2) * ash_amt
    ash = mix(ash, col3(255, 110, 14), crack * 0.85)
 
    # Lava: rojo oscuro en el borde -> naranja -> amarillo en el centro
    t = np.clip(d * 1.2 + (n2 - 0.5) * 0.6 - 0.1, 0, 1)
    lava = mix(col3(150, 22, 4), col3(255, 110, 12), np.clip(t * 2, 0, 1))
    lava = mix(lava, col3(255, 208, 72), np.clip(t * 2 - 1, 0, 1))
    lava = lava * (0.8 + 0.4 * n3)[..., None]
 
    final = mix(ash, lava, d)
    emis = np.clip(d ** 0.8 + crack * 0.6, 0, 1)
 
    nc = fbm(TW, TH, 5, 5, rng)
    smoke = np.clip((nc - 0.5) * 2.6, 0, 1)
    lava_mask = d > 0.85
    pts = np.argwhere(lava_mask[::2, ::2]) * 2
    return {
        "tex": np.clip(final, 0, 255).astype(np.uint8),
        "emis": emis.astype(np.float32),
        "cloud": smoke.astype(np.float32),
        "cloud_col": col3(46, 36, 36),
        "cloud_a": 0.5,
        "lava_pts": pts,
    }
 
 
PLANET_TEX = {"TIERRA": build_earth(), "GEHENA": build_gehena()}
 
# ----------------------------------------------------------------------------
# Geometria precalculada de la esfera
# ----------------------------------------------------------------------------
_idx = (np.arange(D, dtype=np.float32) + 0.5 - R) / R
NXg, NYg = np.meshgrid(_idx, _idx, indexing="ij")          # [x, y]
_R2 = NXg ** 2 + NYg ** 2
NZg = np.sqrt(np.clip(1 - _R2, 0, 1)).astype(np.float32)
NUP = (-NYg).astype(np.float32)
_LAT = np.arcsin(np.clip(NUP, -1, 1))
_LON = np.arctan2(NXg, NZg)
V_IDX = np.clip(((0.5 - _LAT / math.pi) * TH).astype(np.int32), 0, TH - 1)
LON_PX = (_LON / (2 * math.pi) * TW).astype(np.float32)
ALPHA = (np.clip((1 - np.sqrt(_R2)) * R, 0, 1) * 255).astype(np.uint8)
RIM = ((1 - NZg) ** 2.4).astype(np.float32)
LIMB = (0.62 + 0.38 * NZg ** 0.45).astype(np.float32)
 
PLANET_SURF = pygame.Surface((D, D), pygame.SRCALPHA)
FX_PLANET = pygame.Surface((D, D), pygame.SRCALPHA)
 
 
def render_planet(kind, rot_deg, ticks, light):
    P = PLANET_TEX[kind]
    shift = math.radians(rot_deg) / (2 * math.pi) * TW
    u = (LON_PX - shift).astype(np.int32) % TW
    col = P["tex"][u, V_IDX].astype(np.float32)
 
    drift = int(ticks * (0.010 if kind == "TIERRA" else 0.016))
    cu = (u + drift) % TW
    c = (P["cloud"][cu, V_IDX] * P["cloud_a"])[..., None]
    col = col * (1 - c) + P["cloud_col"] * c
 
    lx, ly, lz = light
    ndl = NXg * lx + NUP * ly + NZg * lz
    if kind == "TIERRA":
        diff = np.clip(ndl * 1.15 + 0.08, 0, 1) ** 0.8
        col *= (0.20 + 0.80 * diff)[..., None]
        hx, hy, hz = lx, ly, lz + 1.0
        hn = math.sqrt(hx * hx + hy * hy + hz * hz) or 1.0
        hx, hy, hz = hx / hn, hy / hn, hz / hn
        spec = np.clip(NXg * hx + NUP * hy + NZg * hz, 0, 1) ** 36
        spec = spec * P["water"][u, V_IDX] * (ndl > 0) * 0.85
        col += spec[..., None] * col3(255, 245, 225)
        rim = RIM * (0.25 + 0.75 * np.clip(ndl + 0.35, 0, 1))
        col += rim[..., None] * col3(70, 140, 255) * 1.3
    else:
        flick = 0.88 + 0.12 * np.sin(ticks * 0.004 + u * 0.045 + V_IDX * 0.07)
        em = P["emis"][u, V_IDX] * flick
        shade = 0.14 + 0.55 * np.clip(ndl, 0, 1)
        col *= (shade * (1 - em) + em * 1.25)[..., None]
        col += RIM[..., None] * col3(255, 80, 20) * 0.9
    col *= LIMB[..., None]
    np.clip(col, 0, 255, out=col)
    pygame.surfarray.blit_array(PLANET_SURF, col.astype(np.uint8))
    a = pygame.surfarray.pixels_alpha(PLANET_SURF)
    a[:] = ALPHA
    del a
    return PLANET_SURF
 
 
def make_planet_glow(color):
    size = D + 120
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    steps = 46
    for i in range(steps):
        rad = R + steps - i
        alpha = int(95 * ((i + 1) / steps) ** 2.2)
        pygame.draw.circle(surf, color + (alpha,), (c, c), rad)
    return surf
 
 
GLOW_TIERRA = make_planet_glow((70, 150, 255))
GLOW_GEHENA = make_planet_glow((255, 70, 15))
 
# ----------------------------------------------------------------------------
# Burbujas de lava (viven en coordenadas de la textura y giran con el planeta)
# ----------------------------------------------------------------------------
bubbles = []
_rng = random.Random(5)
 
 
def spawn_bubble(ticks):
    pts = PLANET_TEX["GEHENA"]["lava_pts"]
    if len(pts) == 0:
        return
    u, v = pts[_rng.randrange(len(pts))]
    bubbles.append({
        "u": int(u), "v": int(v), "born": ticks,
        "life": _rng.randint(800, 1700), "maxr": _rng.uniform(3.5, 8.5),
        "sparks": [_rng.uniform(0, math.tau) for _ in range(6)],
    })
 
 
def draw_bubbles(rot_deg, ticks):
    FX_PLANET.fill((0, 0, 0, 0))
    rot = math.radians(rot_deg)
    alive = []
    for b in bubbles:
        p = (ticks - b["born"]) / b["life"]
        if p >= 1:
            continue
        alive.append(b)
        lon = b["u"] / TW * math.tau + rot
        lat = (0.5 - b["v"] / TH) * math.pi
        fz = math.cos(lat) * math.cos(lon)
        if fz < 0.12:
            continue
        sx = R + R * math.cos(lat) * math.sin(lon)
        sy = R - R * math.sin(lat)
        fw = max(0.35, fz)
        mr = b["maxr"]
        if p < 0.78:
            q = p / 0.78
            r = mr * (0.25 + 0.75 * q)
            rect = pygame.Rect(0, 0, max(2, int(2 * r * fw)), max(2, int(2 * r)))
            rect.center = (sx, sy)
            pygame.draw.ellipse(FX_PLANET, (210, 55, 6, 235), rect)
            pygame.draw.ellipse(FX_PLANET, (255, 215, 110, 255), rect, 2)
            pygame.draw.circle(FX_PLANET, (255, 255, 225, 255),
                               (sx - r * 0.3 * fw, sy - r * 0.35), max(1, r * 0.22))
        else:
            q = (p - 0.78) / 0.22
            r = mr * (1 + 1.4 * q)
            a = int(230 * (1 - q))
            rect = pygame.Rect(0, 0, max(2, int(2 * r * fw)), max(2, int(2 * r)))
            rect.center = (sx, sy)
            if q < 0.35:
                pygame.draw.ellipse(FX_PLANET, (255, 230, 140, int(200 * (1 - q / 0.35))),
                                    rect.inflate(-4, -4))
            pygame.draw.ellipse(FX_PLANET, (255, 190, 70, a), rect, 2)
            for ang in b["sparks"]:
                dist = mr * (1 + 2.4 * q)
                px = sx + math.cos(ang) * dist * fw
                py = sy + math.sin(ang) * dist - 10 * q * (1 - q) * mr * 0.3
                pygame.draw.circle(FX_PLANET, (255, 220, 120, a), (px, py), max(1, 2 * (1 - q)))
    bubbles[:] = alive
    return FX_PLANET
 
 
# ----------------------------------------------------------------------------
# Siluetas y escenarios de los jefes (se dibujan a 2x y se reducen = suavizado)
# ----------------------------------------------------------------------------
def silhouette(s, polys, fill, rim, k):
    scaled = [[(x * k, y * k) for x, y in p] for p in polys]
    for p in scaled:
        pygame.draw.polygon(s, rim, p, max(2, int(2.4 * k)))
    for p in scaled:
        pygame.draw.polygon(s, fill, p)
 
 
def poly(s, color, pts, k):
    pygame.draw.polygon(s, color, [(x * k, y * k) for x, y in pts])
 
 
def crescent(cx, cy, r1, r2, off, a0, a1, n=18):
    outer = [(cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a)))
             for a in np.linspace(a0, a1, n)]
    inner = [(cx + off[0] + r2 * math.cos(math.radians(a)),
              cy + off[1] + r2 * math.sin(math.radians(a)))
             for a in np.linspace(a1, a0, n)]
    return outer + inner
 
 
def scene_boss1(k):
    """Demonio rojo con tajador. Escenario: muro gris, linea roja de piso, lamparas de fuego."""
    s = pygame.Surface((int(100 * k), int(100 * k)))
    s.fill((108, 118, 120))
    for x in range(0, 100, 20):
        pygame.draw.line(s, (98, 108, 110), (x * k, 0), (x * k, 66 * k), max(1, int(k)))
    pygame.draw.rect(s, (86, 94, 96), (0, 66 * k, 100 * k, 34 * k))
    pygame.draw.line(s, (214, 72, 42), (0, 66 * k), (100 * k, 66 * k), max(2, int(1.8 * k)))
    for lx in (22, 78):
        pygame.draw.line(s, (40, 34, 34), (lx * k, 0), (lx * k, 12 * k), max(1, int(1.4 * k)))
        poly(s, (255, 150, 30), [(lx - 4, 14), (lx, 3), (lx + 4, 14)], k)
        pygame.draw.circle(s, (255, 196, 40), (lx * k, 17 * k), 6 * k)
        pygame.draw.circle(s, (255, 242, 170), (lx * k, 17 * k), 3 * k)
    body = [
        [(38, 22), (42, 17), (51, 17), (56, 22), (56, 30), (51, 35), (43, 35), (38, 30)],      # cabeza
        [(39, 21), (33, 10), (35, 3), (41, 12), (45, 19)],                                       # cuerno izq
        [(52, 19), (58, 10), (64, 4), (61, 15), (56, 24)],                                       # cuerno der
        [(32, 34), (60, 34), (68, 48), (63, 62), (50, 67), (40, 65), (32, 54)],                  # torso
        [(33, 38), (24, 52), (20, 66), (27, 66), (33, 54)],                                      # brazo izq
        [(60, 40), (72, 52), (77, 66), (70, 68), (62, 52)],                                      # brazo der
        [(40, 62), (30, 76), (24, 93), (35, 93), (45, 77)],                                      # pierna izq
        [(52, 64), (60, 77), (66, 93), (77, 93), (71, 72)],                                      # pierna der
    ]
    silhouette(s, body, (26, 8, 8), (214, 84, 24), k)
    silhouette(s, [[(62, 72), (88, 62), (96, 72), (72, 84), (60, 79)]], (88, 70, 72), (210, 190, 180), k)
    pygame.draw.circle(s, (255, 214, 60), (45 * k, 26 * k), 1.8 * k)
    pygame.draw.circle(s, (255, 214, 60), (52 * k, 26 * k), 1.8 * k)
    return s
 
 
def scene_boss2(k):
    """Bestia de fauces abiertas y cola gris. Escenario: lienzo claro con tinta roja."""
    s = pygame.Surface((int(100 * k), int(100 * k)))
    for y in range(100):
        t = y / 99
        pygame.draw.line(s, (int(lerp(236, 204, t)), int(lerp(236, 204, t)), int(lerp(240, 212, t))),
                         (0, y * k), (100 * k, y * k), int(k) + 1)
    rr = random.Random(3)
    for _ in range(12):
        x0, y0 = rr.uniform(0, 100), rr.uniform(0, 100)
        pygame.draw.line(s, (150, 22, 34), (x0 * k, y0 * k),
                         ((x0 + rr.uniform(-18, 18)) * k, (y0 + rr.uniform(-18, 18)) * k),
                         max(1, int(rr.uniform(0.8, 2.2) * k)))
    pygame.draw.line(s, (130, 16, 28), (34 * k, 8 * k), (78 * k, 50 * k), max(2, int(2 * k)))
    pygame.draw.line(s, (130, 16, 28), (80 * k, 8 * k), (40 * k, 52 * k), max(2, int(1.6 * k)))
    # Cola
    silhouette(s, [[(50, 40), (30, 48), (10, 66), (3, 93), (18, 87), (34, 71), (52, 59), (60, 49)]],
               (66, 66, 74), (30, 30, 36), k)
    # Interior de la boca
    poly(s, (176, 22, 38), [(62, 36), (74, 28), (90, 30), (95, 44), (95, 57), (74, 45), (58, 47)], k)
    jaws = [
        [(46, 24), (62, 12), (86, 14), (98, 26), (91, 31), (74, 29), (62, 37), (50, 41)],       # mandibula sup
        [(56, 47), (74, 45), (95, 57), (99, 71), (89, 67), (76, 63), (62, 61)],                 # mandibula inf
        [(45, 27), (40, 8), (53, 21)],                                                           # oreja
        [(36, 31), (26, 16), (42, 27)],
    ]
    silhouette(s, jaws, (52, 6, 14), (190, 40, 50), k)
    for tx in (68, 76, 84, 90):
        poly(s, (244, 228, 228), [(tx - 2.5, 30), (tx + 2.5, 30), (tx, 37)], k)
    for tx in (80, 86, 91):
        poly(s, (244, 228, 228), [(tx - 2.5, 53), (tx + 2.5, 51), (tx + 0.5, 46)], k)
    pygame.draw.circle(s, (255, 70, 70), (66 * k, 22 * k), 1.8 * k)
    return s
 
 
def scene_boss3(k):
    """Segador morado con guadaña. Escenario: sala morada tenue."""
    s = pygame.Surface((int(100 * k), int(100 * k)))
    for y in range(100):
        t = y / 99
        pygame.draw.line(s, (int(lerp(112, 84, t)), int(lerp(102, 76, t)), int(lerp(168, 130, t))),
                         (0, y * k), (100 * k, y * k), int(k) + 1)
    pygame.draw.rect(s, (58, 52, 98), (0, 72 * k, 100 * k, 28 * k))
    pygame.draw.line(s, (130, 120, 190), (0, 72 * k), (100 * k, 72 * k), max(1, int(k)))
    silhouette(s, [crescent(66, 62, 24, 18, (-6, -5), -10, 125)], (236, 236, 244), (150, 150, 170), k)
    pygame.draw.line(s, (30, 14, 40), (73 * k, 40 * k), (60 * k, 74 * k), max(2, int(2 * k)))
    body = [
        [(42, 10), (50, 7), (58, 10), (62, 24), (55, 35), (45, 35), (38, 24)],                   # capucha
        [(38, 34), (62, 34), (70, 56), (64, 74), (36, 74), (30, 56)],                            # manto
        [(38, 38), (26, 52), (24, 67), (31, 67), (38, 54)],                                      # brazo izq
        [(62, 38), (72, 52), (71, 64), (64, 57)],                                                # brazo der
        [(40, 72), (37, 93), (46, 93), (49, 74)],
        [(51, 74), (54, 93), (63, 93), (60, 72)],
    ]
    silhouette(s, body, (34, 12, 48), (150, 86, 196), k)
    pygame.draw.ellipse(s, (14, 4, 20), (43 * k, 15 * k, 14 * k, 18 * k))
    pygame.draw.ellipse(s, (246, 240, 240), (47 * k, 19 * k, 6 * k, 9 * k))
    pygame.draw.circle(s, (220, 40, 50), (50 * k, 23.5 * k), 1.7 * k)
    return s
 
 
def scene_boss4(k):
    """Guerrero cornudo con lanza y rastro de fuego. Escenario: cielo de brasas."""
    s = pygame.Surface((int(100 * k), int(100 * k)))
    for y in range(100):
        t = y / 99
        pygame.draw.line(s, (int(lerp(70, 238, t)), int(lerp(22, 130, t)), int(lerp(26, 48, t))),
                         (0, y * k), (100 * k, y * k), int(k) + 1)
    poly(s, (36, 18, 18), [(0, 100), (0, 82), (14, 78), (28, 84), (44, 79), (62, 85), (80, 80),
                           (100, 84), (100, 100)], k)
    rr = random.Random(9)
    colors = [(176, 28, 30), (255, 122, 30), (255, 196, 80), (220, 60, 30)]
    for i in range(16):
        ang = math.radians(rr.uniform(-30, 26))
        ln = rr.uniform(40, 58)
        sx, sy = 50, 52
        tx, ty = sx + math.cos(ang) * ln, sy + math.sin(ang) * ln
        nx, ny = -math.sin(ang) * rr.uniform(1.2, 2.6), math.cos(ang) * rr.uniform(1.2, 2.6)
        poly(s, colors[i % 4], [(sx + nx, sy + ny), (tx, ty), (sx - nx, sy - ny)], k)
    pygame.draw.line(s, (40, 28, 24), (36 * k, 60 * k), (98 * k, 46 * k), max(2, int(1.6 * k)))
    body = [
        [(31, 26), (37, 25), (42, 30), (40, 37), (33, 37), (30, 32)],                            # cabeza
        [(32, 27), (28, 13), (37, 23)],                                                          # cuernos
        [(40, 26), (47, 12), (45, 29)],
        [(29, 38), (46, 40), (51, 56), (41, 65), (30, 53)],                                      # torso
        [(44, 42), (62, 49), (62, 53), (44, 50)],                                                # brazo con lanza
        [(32, 52), (19, 60), (14, 73), (21, 73), (30, 64)],                                      # pierna trasera
        [(42, 60), (55, 70), (53, 83), (45, 79), (40, 69)],                                      # pierna delantera
    ]
    silhouette(s, body, (30, 24, 20), (230, 110, 40), k)
    pygame.draw.circle(s, (255, 220, 120), (35.5 * k, 31 * k), 1.2 * k)
    return s
 
 
def scene_secret(k):
    """Jefe todavía sin definir: signo de pregunta entre niebla."""
    s = pygame.Surface((int(100 * k), int(100 * k)))
    for y in range(100):
        t = y / 99
        pygame.draw.line(s, (int(lerp(26, 14, t)), int(lerp(22, 12, t)), int(lerp(46, 28, t))),
                         (0, y * k), (100 * k, y * k), int(k) + 1)
    fog = pygame.Surface((int(100 * k), int(100 * k)), pygame.SRCALPHA)
    for cx, cy, rr in ((20, 78, 30), (70, 86, 34), (50, 60, 24)):
        pygame.draw.circle(fog, (110, 90, 150, 60), (cx * k, cy * k), rr * k)
    s.blit(fog, (0, 0))
    f = pygame.font.SysFont("impact,arialblack,verdana", int(78 * k))
    q = f.render("?", True, (150, 130, 200))
    s.blit(q, q.get_rect(center=(50 * k, 52 * k)))
    return s
 
 
SCENES = {"1": scene_boss1, "2": scene_boss2, "3": scene_boss3, "4": scene_boss4, "?": scene_secret}
 
 
# ----------------------------------------------------------------------------
# ICONOS ANIMADOS DE LOS NIVELES
# ----------------------------------------------------------------------------
def _portal_colors(kind):
    return {
        "1": ((255, 55, 45), (120, 8, 20), (255, 170, 90)),   # rojo
        "2": ((135, 20, 55), (55, 5, 25), (235, 55, 110)),     # bordo
        "3": ((55, 235, 115), (5, 75, 45), (150, 255, 170)),   # verde
    }[kind]


def draw_animated_portal(cx, cy, radius, kind, ticks):
    """Portal que gira constantemente sobre sí mismo."""
    outer, inner, glow = _portal_colors(kind)

    # Halo pulsante.
    pulse = 0.92 + 0.10 * math.sin(ticks * 0.006)
    for i in range(7, 0, -1):
        rr = int(radius * (1.0 + i * 0.075))
        alpha = int(10 * (8 - i) * pulse)
        pygame.draw.circle(
            screen, glow + (max(0, min(70, alpha)),),
            (cx, cy), rr, max(1, int(radius * 0.035))
        )

    # Núcleo.
    pygame.draw.circle(screen, (7, 5, 12), (cx, cy), int(radius * 0.92))
    pygame.draw.circle(screen, inner, (cx, cy), int(radius * 0.86))

    # Anillos giratorios.
    rot = ticks * 0.0045
    for ring in range(3):
        rr = radius * (0.42 + ring * 0.18)
        points = []
        segments = 30
        phase = rot * (1 if ring % 2 == 0 else -1) + ring * 1.7

        for j in range(segments):
            a = math.tau * j / segments + phase
            wobble = 1.0 + 0.055 * math.sin(ticks * 0.008 + j * 1.9 + ring)
            points.append((
                cx + math.cos(a) * rr * wobble,
                cy + math.sin(a) * rr * wobble
            ))

        pygame.draw.lines(
            screen, outer, True, points,
            max(2, int(radius * 0.045))
        )

    # Tres brazos de energía que giran en sentido contrario.
    for arm in range(3):
        pts = []
        start = rot * (1.25 if arm % 2 == 0 else -1.0) + arm * math.tau / 3
        for j in range(24):
            t = j / 23
            a = start + t * math.tau * 1.5
            rr = radius * (0.08 + t * 0.62)
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        pygame.draw.lines(
            screen, glow, False, pts,
            max(2, int(radius * 0.032))
        )

    # Núcleo luminoso.
    core_r = max(2, int(radius * (0.11 + 0.025 * math.sin(ticks * 0.012))))
    pygame.draw.circle(screen, glow, (cx, cy), core_r)
    pygame.draw.circle(screen, (255, 245, 220), (cx, cy), max(1, core_r // 3))


def draw_animated_fire(cx, cy, radius, ticks):
    """Icono del Nivel 4 formado solamente por fuego animado."""
    surf_size = int(radius * 2.6)
    fire = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    c = surf_size // 2
    base_y = int(radius * 1.22)

    # Resplandor.
    for i in range(7, 0, -1):
        rr = int(radius * (0.75 + i * 0.11))
        pygame.draw.circle(fire, (255, 55, 5, 10), (c, base_y), rr)

    flames = [
        (-0.62, 0.90, 0.95, 0.0),
        (-0.38, 1.08, 1.20, 1.8),
        (-0.12, 0.82, 1.00, 3.2),
        (0.12, 1.18, 1.30, 0.9),
        (0.40, 0.98, 1.10, 2.5),
        (0.64, 0.82, 0.92, 4.1),
    ]

    for ox, hmul, wmul, phase in flames:
        sway = math.sin(ticks * 0.010 + phase) * radius * 0.10
        flick = 1.0 + 0.12 * math.sin(ticks * 0.013 + phase * 1.7)
        x = c + ox * radius + sway
        h = radius * hmul * flick
        w = radius * 0.42 * wmul

        # Rojo exterior.
        pts = [
            (x - w * 0.62, base_y),
            (x - w * 0.72, base_y - h * 0.35),
            (x - w * 0.25, base_y - h * 0.72),
            (x - w * 0.10, base_y - h),
            (x + w * 0.10, base_y - h * 0.72),
            (x + w * 0.52, base_y - h * 0.52),
            (x + w * 0.70, base_y),
        ]
        pygame.draw.polygon(fire, (205, 22, 5, 255), pts)

        # Naranja.
        iw, ih = w * 0.68, h * 0.68
        ipts = [
            (x - iw * 0.60, base_y),
            (x - iw * 0.52, base_y - ih * 0.35),
            (x - iw * 0.10, base_y - ih * 0.76),
            (x + iw * 0.03, base_y - ih),
            (x + iw * 0.22, base_y - ih * 0.58),
            (x + iw * 0.55, base_y),
        ]
        pygame.draw.polygon(fire, (255, 105, 10, 255), ipts)

        # Amarillo interior.
        yw, yh = w * 0.34, h * 0.42
        ypts = [
            (x - yw, base_y),
            (x - yw * 0.75, base_y - yh * 0.40),
            (x, base_y - yh),
            (x + yw * 0.75, base_y - yh * 0.35),
            (x + yw, base_y),
        ]
        pygame.draw.polygon(fire, (255, 220, 65, 255), ypts)

    # Chispas ascendentes.
    for i in range(18):
        phase = i * 1.73
        x = c + math.sin(ticks * 0.004 + phase) * radius * 0.95
        cycle = (ticks * (0.035 + (i % 4) * 0.006) + i * 37) % int(radius * 1.65)
        y = base_y - cycle
        alpha = int(220 * (1 - cycle / (radius * 1.65)))
        if alpha > 0:
            pygame.draw.circle(
                fire,
                (255, 185 + (i % 2) * 35, 45, alpha),
                (int(x), int(y)),
                max(1, int(radius * 0.035))
            )

    # Recorte circular.
    mask = pygame.Surface(fire.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), int(radius * 1.02))
    fire.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(fire, fire.get_rect(center=(cx, cy)))



def make_node_surface(key):
    big = SCENES[key](2.0)
    dd = NODE_R * 2
    surf = pygame.transform.smoothscale(big, (dd, dd)).convert_alpha()
    vig = pygame.Surface((dd, dd), pygame.SRCALPHA)
    for i in range(10):
        pygame.draw.circle(vig, (20, 0, 0, max(0, 140 - i * 15)), (NODE_R, NODE_R), NODE_R - i, 2)
    surf.blit(vig, (0, 0))
    mask = pygame.Surface((dd, dd), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (NODE_R, NODE_R), NODE_R)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surf
 
 
NODE_SURFS = {key: make_node_surface(key) for key in SCENES}
 
 
def make_radial_glow(size, color, max_alpha):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    for r in range(c, 0, -2):
        a = int(max_alpha * (1 - r / c) ** 2)
        pygame.draw.circle(surf, color + (a,), (c, c), r)
    return surf
 
 
NODE_GLOW = make_radial_glow(220, (255, 140, 30), 150)
 
# Carteles de nivel (cacheados)
_plaque_cache = {}
 
 
def get_plaque(tag, big, selected):
    key = (tag, big, selected)
    if key in _plaque_cache:
        return _plaque_cache[key]
    small = fancy_text(tag, get_font(13), (255, 190, 80), (255, 110, 20), (50, 12, 0), spacing=4, ow=1)
    if selected:
        top, bot = (255, 252, 210), (255, 190, 40)
    else:
        top, bot = (240, 244, 255), (150, 165, 200)
    size = 28 if len(big) <= 2 else 20
    bigs = fancy_text(big, get_font(size), top, bot, (50, 18, 0), spacing=2, ow=2)
    w = max(small.get_width(), bigs.get_width()) + 40
    h = small.get_height() + bigs.get_height() + 8
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    border = (255, 200, 60) if selected else (130, 140, 170)
    pygame.draw.rect(surf, (14, 10, 16, 225), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(surf, border, (0, 0, w, h), 2, border_radius=10)
    pygame.draw.rect(surf, border[:3] + (90,), (4, 4, w - 8, h - 8), 1, border_radius=7)
    for dx in (9, w - 9):
        pygame.draw.polygon(surf, (255, 140, 30), [(dx, h // 2 - 4), (dx + 4, h // 2), (dx, h // 2 + 4), (dx - 4, h // 2)])
    surf.blit(small, small.get_rect(midtop=(w // 2, 2)))
    surf.blit(bigs, bigs.get_rect(midbottom=(w // 2, h - 2)))
    _plaque_cache[key] = surf
    return surf
 
 
def draw_level_node(cx, cy, lvl, selected, ticks, scale):
    pulse = math.sin(ticks * 0.008)
    r = NODE_R * scale * (1 + 0.06 * pulse if selected else 1)

    if selected:
        gs = int(r * 5.2)
        g = pygame.transform.smoothscale(NODE_GLOW, (gs, gs))
        screen.blit(g, g.get_rect(center=(cx, cy)))

    # Niveles 1, 2 y 3: portales animados.
    if lvl["boss"] in ("1", "2", "3"):
        draw_animated_portal(cx, cy, r, lvl["boss"], ticks)

    # Nivel 4: fuego animado.
    elif lvl["boss"] == "4":
        draw_animated_fire(cx, cy, r, ticks)

    # Nivel secreto: se conserva el signo de interrogación.
    else:
        inner = pygame.transform.smoothscale(
            NODE_SURFS[lvl["boss"]],
            (max(4, int(2 * r)), max(4, int(2 * r)))
        )
        screen.blit(inner, inner.get_rect(center=(cx, cy)))

    pygame.draw.circle(
        screen, (255, 140, 20), (cx, cy), r + 3,
        max(2, int(3 * scale))
    )
    pygame.draw.circle(
        screen,
        (255, 226, 120) if selected else (255, 190, 70),
        (cx, cy), r, max(1, int(scale))
    )

    plaque = get_plaque(lvl["tag"], lvl["big"], selected)
    if scale < 0.98:
        plaque = pygame.transform.smoothscale(
            plaque,
            (
                int(plaque.get_width() * max(0.7, scale)),
                int(plaque.get_height() * max(0.7, scale))
            )
        )

    prect = plaque.get_rect(midtop=(cx, cy + r + 10))
    screen.blit(plaque, prect)

    return pygame.Rect(
        cx - r - 6,
        cy - r - 6,
        2 * r + 12,
        int(2 * r + 12 + prect.height + 10)
    )


# ----------------------------------------------------------------------------
# Fondo espacial
# ----------------------------------------------------------------------------
def make_star_layer(n, seed, rmax, tints):
    rr = random.Random(seed)
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for _ in range(n):
        x, y = rr.randrange(WIDTH), rr.randrange(HEIGHT)
        t = rr.choice(tints)
        a = rr.randint(110, 230)
        r = 1 if rr.random() > 0.15 else rmax
        pygame.draw.circle(surf, t + (a,), (x, y), r)
    return surf
 
 
STAR_LAYERS = [
    (make_star_layer(150, 1, 1, [(255, 255, 255), (200, 220, 255)]), 0.15),
    (make_star_layer(80, 2, 2, [(255, 255, 255), (255, 235, 200), (190, 210, 255)]), 0.32),
    (make_star_layer(26, 3, 2, [(255, 240, 210), (170, 200, 255), (255, 190, 170)]), 0.58),
]
_tr = random.Random(8)
TWINKLE = [(_tr.randrange(WIDTH), _tr.randrange(HEIGHT), _tr.uniform(0, 6.28), _tr.uniform(0.002, 0.006))
           for _ in range(48)]
 
BG_GRAD = pygame.Surface((WIDTH, HEIGHT))
for _y in range(HEIGHT):
    _t = _y / (HEIGHT - 1)
    pygame.draw.line(BG_GRAD, (int(lerp(3, 10, _t)), int(lerp(5, 9, _t)), int(lerp(16, 28, _t))),
                     (0, _y), (WIDTH, _y))
 
 
def make_cloud_layer(seed, base, octaves, color_a, color_b, max_alpha, thresh, gain):
    rng = np.random.default_rng(seed)
    w, h = 192, 108
    n = fbm(w, h, base, octaves, rng)
    n2 = fbm(w, h, base + 1, 3, rng)
    alpha = np.clip((n - thresh) * gain, 0, 1) * max_alpha
    rgb = mix(col3(*color_a), col3(*color_b), np.clip(n2, 0, 1))
    small = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.surfarray.blit_array(small, np.clip(rgb, 0, 255).astype(np.uint8))
    a = pygame.surfarray.pixels_alpha(small)
    a[:] = alpha.astype(np.uint8)
    del a
    return pygame.transform.smoothscale(small, (WIDTH, HEIGHT))
 
 
NEBULA = make_cloud_layer(31, 3, 4, (40, 70, 170), (120, 40, 150), 80, 0.45, 2.5)
FOG_A = make_cloud_layer(41, 3, 4, (130, 44, 30), (90, 40, 40), 130, 0.43, 2.4)
FOG_B = make_cloud_layer(53, 4, 4, (74, 64, 74), (110, 60, 50), 100, 0.45, 2.2)
 
MIST = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
for _y in range(150):
    pygame.draw.line(MIST, (70, 18, 10, int(120 * (_y / 149) ** 1.6)), (0, _y), (WIDTH, _y))
 
DARK_OVERLAY = pygame.Surface((WIDTH, HEIGHT))
DARK_OVERLAY.fill((8, 0, 2))
FX_SPACE = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
 
 
def blit_wrapped(surf, offset, alpha):
    surf.set_alpha(alpha)
    off = int(offset) % WIDTH
    screen.blit(surf, (-off, 0))
    screen.blit(surf, (WIDTH - off, 0))
 
 
# Sol
def make_sun_glow():
    size = 300
    g = make_radial_glow(size, (255, 190, 80), 120)
    c = size // 2
    core = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(core, (255, 150, 40, 255), (c, c), 50)
    pygame.draw.circle(core, (255, 214, 96, 255), (c, c), 44)
    pygame.draw.circle(core, (255, 244, 190, 255), (c, c), 34)
    for sx, sy, sr in ((-12, -8, 7), (10, 12, 5), (14, -14, 4), (-16, 14, 4)):
        pygame.draw.circle(core, (255, 255, 230, 170), (c + sx, c + sy), sr)
    g.blit(core, (0, 0))
    return g
 
 
def make_sun_rays():
    size = 300
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    for i in range(14):
        a = i * math.tau / 14
        ln = 140 if i % 2 == 0 else 100
        w = 0.07
        pts = [(c + math.cos(a - w) * 40, c + math.sin(a - w) * 40),
               (c + math.cos(a) * ln, c + math.sin(a) * ln),
               (c + math.cos(a + w) * 40, c + math.sin(a + w) * 40)]
        pygame.draw.polygon(surf, (255, 220, 120, 70), pts)
    return surf
 
 
SUN_GLOW = make_sun_glow()
SUN_RAYS = make_sun_rays()
 
 
def sun_state(rot_deg):
    theta = math.radians(SUN_LON + rot_deg)
    sx = CENTER_X + 360 * math.sin(theta)
    sy = CENTER_Y - 120 - 60 * math.cos(theta)
    return sx, sy, theta
 
 
def draw_sun(sx, sy, theta, ticks, env):
    sc = (0.8 + 0.25 * math.cos(theta)) * (1 + 0.02 * math.sin(ticks * 0.003))
    alpha = int(255 * (1 - 0.6 * env))
    size = max(8, int(300 * sc))
    rays = pygame.transform.rotozoom(SUN_RAYS, ticks * 0.008, sc)
    rays.set_alpha(alpha)
    screen.blit(rays, rays.get_rect(center=(sx, sy)))
    g = pygame.transform.smoothscale(SUN_GLOW, (size, size))
    g.set_alpha(alpha)
    screen.blit(g, g.get_rect(center=(sx, sy)))
 
 
# Meteoritos, trozos de tierra desprendida y brasas (solo Gehena)
_gr = random.Random(77)
 
 
def _rock_shape(n=8, jitter=0.35):
    return [(math.tau * i / n, 1 + _gr.uniform(-jitter, jitter)) for i in range(n)]
 
 
METEORS = [{
    "x": _gr.uniform(0, WIDTH), "y": _gr.uniform(-HEIGHT, 0),
    "vx": _gr.uniform(-0.16, -0.08), "vy": _gr.uniform(0.07, 0.15),
    "size": _gr.uniform(4, 9), "rot": _gr.uniform(0, 6.28), "rv": _gr.uniform(-0.004, 0.004),
    "shape": _rock_shape(),
} for _ in range(7)]
 
CHUNKS = [{
    "a0": _gr.uniform(0, math.tau), "rad": R + _gr.uniform(28, 140),
    "spd": _gr.choice((-1, 1)) * _gr.uniform(0.00004, 0.00011),
    "size": _gr.uniform(9, 22), "bob": _gr.uniform(0, 6.28), "rot": _gr.uniform(0, 6.28),
    "shape": _rock_shape(9, 0.3),
} for _ in range(11)]
 
EMBERS = [{
    "x": _gr.uniform(0, WIDTH), "y": _gr.uniform(0, HEIGHT), "vy": _gr.uniform(0.01, 0.04),
    "ph": _gr.uniform(0, 6.28), "r": _gr.choice((1, 1, 2)),
} for _ in range(36)]
 
 
def draw_rock(surf, cx, cy, size, rot, shape, fill, edge, alpha):
    pts = [(cx + math.cos(a + rot) * size * j, cy + math.sin(a + rot) * size * j * 0.82) for a, j in shape]
    pygame.draw.polygon(surf, fill + (alpha,), pts)
    pygame.draw.polygon(surf, edge + (alpha,), pts, 2)
    return pts
 
 
def draw_gehena_fx(ticks, dt, rot_deg, env):
    FX_SPACE.fill((0, 0, 0, 0))
    a_full = int(255 * env)
    for e in EMBERS:
        e["y"] -= e["vy"] * dt
        if e["y"] < -4:
            e["y"] = HEIGHT + 4
            e["x"] = _gr.uniform(0, WIDTH)
        flick = 0.5 + 0.5 * math.sin(ticks * 0.004 + e["ph"])
        x = (e["x"] + math.sin(ticks * 0.0008 + e["ph"]) * 14) % WIDTH
        pygame.draw.circle(FX_SPACE, (255, 140 + int(70 * flick), 40, int(190 * env * flick)), (x, e["y"]), e["r"])
    for m in METEORS:
        m["x"] += m["vx"] * dt
        m["y"] += m["vy"] * dt
        m["rot"] += m["rv"] * dt
        if m["y"] > HEIGHT + 60 or m["x"] < -60:
            m["x"] = _gr.uniform(WIDTH * 0.3, WIDTH + 200)
            m["y"] = _gr.uniform(-200, -20)
        speed = math.hypot(m["vx"], m["vy"])
        ux, uy = m["vx"] / speed, m["vy"] / speed
        for i in range(10):
            f = 1 - i / 10
            pygame.draw.circle(FX_SPACE, (255, int(90 + 90 * f), 30, int(a_full * f * 0.55)),
                               (m["x"] - ux * i * 5.5, m["y"] - uy * i * 5.5), max(1, m["size"] * f * 0.8))
        draw_rock(FX_SPACE, m["x"], m["y"], m["size"], m["rot"], m["shape"], (72, 52, 46), (190, 90, 40), a_full)
    for ch in CHUNKS:
        ang = ch["a0"] + ticks * ch["spd"] + math.radians(rot_deg) * 0.25
        x = CENTER_X + ch["rad"] * math.cos(ang)
        y = CENTER_Y + ch["rad"] * 0.82 * math.sin(ang) + math.sin(ticks * 0.0013 + ch["bob"]) * 5
        s = ch["size"]
        gl = int(s * 3)
        pygame.draw.circle(FX_SPACE, (255, 90, 20, int(60 * env)), (x, y + s * 0.5), gl // 2)
        rot = ch["rot"] + ticks * 0.0003 * (1 if ch["spd"] > 0 else -1)
        pts = draw_rock(FX_SPACE, x, y, s, rot, ch["shape"], (58, 50, 48), (150, 70, 30), a_full)
        # cara superior de ceniza clara y vena de lava
        top = [(px, py - s * 0.18) for px, py in pts[:5]]
        pygame.draw.polygon(FX_SPACE, (112, 104, 98, a_full), top)
        pygame.draw.line(FX_SPACE, (255, 120, 20, a_full), (x - s * 0.5, y + s * 0.25), (x + s * 0.4, y + s * 0.1), 2)
    screen.blit(FX_SPACE, (0, 0))
 
 
def draw_space(ticks, dt, rot_deg, env):
    screen.blit(BG_GRAD, (0, 0))
    if env < 0.999:
        blit_wrapped(NEBULA, rot_deg * 0.25, int(255 * (1 - env)))
    for layer, f in STAR_LAYERS:
        blit_wrapped(layer, rot_deg * f, int(255 * (1 - 0.55 * env)))
    for x, y, ph, sp in TWINKLE:
        b = 0.5 + 0.5 * math.sin(ticks * sp + ph)
        c = int((120 + 135 * b) * (1 - 0.5 * env))
        xx = (x - rot_deg * 0.4) % WIDTH
        pygame.draw.circle(screen, (c, c, min(255, c + 20)), (xx, y), 1)
        if b > 0.85:
            pygame.draw.line(screen, (c, c, c), (xx - 3, y), (xx + 3, y))
            pygame.draw.line(screen, (c, c, c), (xx, y - 3), (xx, y + 3))
    if env > 0.001:
        DARK_OVERLAY.set_alpha(int(150 * env))
        screen.blit(DARK_OVERLAY, (0, 0))
        blit_wrapped(FOG_A, ticks * 0.012 + rot_deg * 0.7, int(255 * env))
        blit_wrapped(FOG_B, -ticks * 0.006 + rot_deg * 1.1, int(255 * env))
        draw_gehena_fx(ticks, dt, rot_deg, env)
 
 
# ----------------------------------------------------------------------------
# Interfaz
# ----------------------------------------------------------------------------
TITLE_SURFS = {
    "TIERRA": fancy_text("TIERRA", get_font(56), (235, 252, 255), (70, 200, 255), (6, 40, 96), spacing=10, ow=3),
    "GEHENA": fancy_text("GEHENA", get_font(56), (255, 240, 130), (255, 70, 20), (80, 6, 0), spacing=10, ow=3),
}
SUBTITLES = {
    "TIERRA": fancy_text("MUNDO DE LA VIDA", get_font(15), (200, 230, 255), (120, 180, 240), (10, 30, 70), spacing=5, ow=1),
    "GEHENA": fancy_text("REINO DE CENIZA Y FUEGO", get_font(15), (255, 210, 150), (255, 120, 60), (70, 8, 0), spacing=5, ow=1),
}
ACCENT = {"TIERRA": (80, 200, 255), "GEHENA": (255, 110, 30)}
BTN_TEXT = {
    "TIERRA": fancy_text("IR A GEHENA", get_font(16), (255, 240, 170), (255, 120, 40), (70, 8, 0), spacing=2, ow=1),
    "GEHENA": fancy_text("IR A TIERRA", get_font(16), (230, 250, 255), (90, 200, 255), (6, 40, 96), spacing=2, ow=1),
}
HUD_TEXT = fancy_text("A / D  o  FLECHAS: GIRAR     ENTER: JUGAR     CLIC: ELEGIR NIVEL",
                      get_font(14), (240, 244, 255), (170, 180, 210), (10, 10, 20), spacing=2, ow=1)
 
 
def draw_diamond(x, y, r, color):
    pygame.draw.polygon(screen, color, [(x, y - r), (x + r, y), (x, y + r), (x - r, y)])
 
 
def draw_title(planet, ticks):
    ts = TITLE_SURFS[planet]
    acc = ACCENT[planet]
    rect = ts.get_rect(center=(WIDTH // 2, 48))
    plate = rect.inflate(70, 14)
    pl = pygame.Surface(plate.size, pygame.SRCALPHA)
    pygame.draw.rect(pl, (8, 10, 20, 205), pl.get_rect(), border_radius=14)
    pygame.draw.rect(pl, acc + (255,), pl.get_rect(), 2, border_radius=14)
    pygame.draw.rect(pl, acc + (90,), pl.get_rect().inflate(-8, -8), 1, border_radius=10)
    screen.blit(pl, plate.topleft)
    for side in (-1, 1):
        x0 = plate.centerx + side * (plate.width // 2)
        for i in range(3):
            pygame.draw.line(screen, tuple(int(c * (1 - i * 0.3)) for c in acc),
                             (x0 + side * 8, plate.centery + (i - 1) * 6),
                             (x0 + side * (70 - i * 14), plate.centery + (i - 1) * 6), 2 if i == 1 else 1)
        draw_diamond(x0 + side * 8, plate.centery, 5, acc)
        draw_diamond(x0 + side * 74, plate.centery, 4, WHITE)
    screen.blit(ts, rect)
    # destello que recorre el titulo
    sweep = (ticks * 0.12) % (rect.width + 160) - 80
    shine = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shine, (255, 255, 255, 70),
                        [(sweep, 0), (sweep + 26, 0), (sweep + 6, rect.height), (sweep - 20, rect.height)])
    mask = ts.copy()
    mask.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MAX)
    shine.blit(ts, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    screen.blit(shine, rect.topleft)
    sub = SUBTITLES[planet]
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, plate.bottom + 14)))
 
 
def draw_arrow_button(rect, direction, hover):
    c = GOLD if hover else WHITE
    pygame.draw.rect(screen, (22, 24, 38), rect, border_radius=12)
    pygame.draw.rect(screen, c, rect, 2, border_radius=12)
    cx, cy = rect.center
    s = 12 * direction
    pygame.draw.polygon(screen, c, [(cx + s, cy), (cx - s * 0.6, cy - 13), (cx - s * 0.6, cy + 13)])
 
 
# ----------------------------------------------------------------------------
# Bucle principal
# ----------------------------------------------------------------------------
running = True
last_ticks = pygame.time.get_ticks()
while running:
    ticks = pygame.time.get_ticks()
    dt = min(50, ticks - last_ticks)
    last_ticks = ticks
    mouse_pos = pygame.mouse.get_pos()
 
    # Transicion Tierra <-> Gehena
    env_t += max(-0.025, min(0.025, env_target - env_t))
    new_planet = "GEHENA" if env_t > 0.5 else "TIERRA"
    if new_planet != current_planet:
        current_planet = new_planet
        active_levels = gehena_levels if current_planet == "GEHENA" else tierra_levels
        current_index = 0 if current_planet == "GEHENA" else 1
        planet_rotation = -active_levels[current_index]["lon"] + 80
    transitioning = abs(env_t - env_target) > 0.001
 
    target_rotation = -active_levels[current_index]["lon"]
    planet_rotation += (target_rotation - planet_rotation) * 0.1
 
    # Sol (gira con el mundo) y luz
    sun_x, sun_y, theta = sun_state(planet_rotation)
    lx = math.sin(theta)
    ly = (CENTER_Y - sun_y) / 260.0
    lz = math.cos(theta) * 0.8 + 0.45
    ln_ = math.sqrt(lx * lx + ly * ly + lz * lz)
    light = (lx / ln_, ly / ln_, lz / ln_)
 
    draw_space(ticks, dt, planet_rotation, env_t)
    draw_sun(sun_x, sun_y, theta, ticks, env_t)
 
    # Planeta
    glow = GLOW_GEHENA if current_planet == "GEHENA" else GLOW_TIERRA
    screen.blit(glow, glow.get_rect(center=(CENTER_X, CENTER_Y)))
    planet_surf = render_planet(current_planet, planet_rotation, ticks, light)
    screen.blit(planet_surf, (CENTER_X - R, CENTER_Y - R))
    if current_planet == "GEHENA":
        if len(bubbles) < 46 and random.random() < 0.6:
            spawn_bubble(ticks)
        screen.blit(draw_bubbles(planet_rotation, ticks), (CENTER_X - R, CENTER_Y - R))
    elif bubbles:
        bubbles.clear()
 
    if env_t > 0.001:
        MIST.set_alpha(int(255 * env_t))
        screen.blit(MIST, (0, HEIGHT - 150))
 
    # Nodos de nivel (con ocultacion trasera 3D)
    nodes = []
    for idx, node in enumerate(active_levels):
        rad_lon = math.radians(node["lon"] + planet_rotation)
        rad_lat = math.radians(node["lat"])
        x3 = R * math.cos(rad_lat) * math.sin(rad_lon)
        y3 = -R * math.sin(rad_lat)
        z3 = R * math.cos(rad_lat) * math.cos(rad_lon)
        fz = z3 / R
        if fz > 0.12:
            nodes.append((fz, idx, int(CENTER_X + x3), int(CENTER_Y + y3)))
    nodes.sort()
    clickable_nodes = []
    for fz, idx, sx, sy in nodes:
        rect = draw_level_node(sx, sy, active_levels[idx], idx == current_index, ticks, 0.55 + 0.45 * fz)
        clickable_nodes.append((rect, idx))
 
    # UI
    draw_title(current_planet, ticks)
 
    btn_planet = pygame.Rect(WIDTH - 190, 22, 170, 42)
    hover_p = btn_planet.collidepoint(mouse_pos) and not transitioning
    acc = GOLD if hover_p else ACCENT["GEHENA" if current_planet == "TIERRA" else "TIERRA"]
    pygame.draw.rect(screen, (22, 24, 38), btn_planet, border_radius=10)
    pygame.draw.rect(screen, acc, btn_planet, 2, border_radius=10)
    bt = BTN_TEXT[current_planet]
    tx = btn_planet.centerx - bt.get_width() // 2 + (8 if current_planet == "TIERRA" else 0) - (0 if current_planet == "TIERRA" else -8)
    screen.blit(bt, bt.get_rect(center=(btn_planet.centerx + (-8 if current_planet == "TIERRA" else 8), btn_planet.centery)))
    if current_planet == "TIERRA":
        ax = btn_planet.right - 18
        pygame.draw.polygon(screen, acc, [(ax + 6, btn_planet.centery), (ax - 5, btn_planet.centery - 8), (ax - 5, btn_planet.centery + 8)])
    else:
        ax = btn_planet.left + 18
        pygame.draw.polygon(screen, acc, [(ax - 6, btn_planet.centery), (ax + 5, btn_planet.centery - 8), (ax + 5, btn_planet.centery + 8)])
 
    btn_left = pygame.Rect(36, HEIGHT // 2 - 28, 56, 56)
    btn_right = pygame.Rect(WIDTH - 92, HEIGHT // 2 - 28, 56, 56)
    draw_arrow_button(btn_left, -1, btn_left.collidepoint(mouse_pos))
    draw_arrow_button(btn_right, 1, btn_right.collidepoint(mouse_pos))
 
    screen.blit(HUD_TEXT, HUD_TEXT.get_rect(center=(WIDTH // 2, HEIGHT - 18)))
 
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                current_index = max(0, current_index - 1)
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                current_index = min(len(active_levels) - 1, current_index + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                ejecutar_nivel(active_levels[current_index]["file"])
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_left.collidepoint(event.pos):
                current_index = max(0, current_index - 1)
            elif btn_right.collidepoint(event.pos):
                current_index = min(len(active_levels) - 1, current_index + 1)
            elif btn_planet.collidepoint(event.pos):
                if not transitioning:
                    env_target = 1.0 if current_planet == "TIERRA" else 0.0
            else:
                for rect, idx in clickable_nodes:
                    if rect.collidepoint(event.pos):
                        current_index = idx
                        ejecutar_nivel(active_levels[current_index]["file"])
                        break
 
    pygame.display.flip()
    clock.tick(60)
 
pygame.quit()
sys.exit()