

import math
import random
from collections import deque
 
import numpy as np
import pygame
 
 
def _lerp(a, b, t):
    return a + (b - a) * t
 
 
# ----------------------------------------------------------------------------
# Remolino de luz (estilo de la imagen de referencia)
# ----------------------------------------------------------------------------
def make_swirl(size=256):
    c = (size - 1) / 2
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float32)
    dx = (xs - c) / c
    dy = (ys - c) / c
    r = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
 
    # Espiral: el multiplicador entero (3) evita costura en el angulo +-pi
    phase = th / (2 * np.pi) + r * 1.6
    u = (phase * 4.0) % 4.0
    i0 = np.floor(u).astype(np.int32) % 4
    f = u - np.floor(u)
    fs = f * f * (3 - 2 * f)
 
    palette = np.array([(255, 45, 40),     # rojo
                        (255, 150, 30),    # naranja
                        (60, 235, 90),     # verde
                        (50, 130, 255)],   # azul
                       dtype=np.float32)
    col = palette[i0] * (1 - fs[..., None]) + palette[(i0 + 1) % 4] * fs[..., None]
 
    # Linea dorada tenue entre bandas
    edge = np.exp(-((f - 0.5) / 0.07) ** 2)
    col = col + edge[..., None] * np.array([255, 225, 110], dtype=np.float32) * 0.35
 
    # Bordes que se aclaran hacia el blanco
    t = np.clip((r - 0.5) / 0.5, 0, 1)
    w = (t * t * (3 - 2 * t) * 0.55)[..., None]
    col = col * (1 - w) + 255.0 * w
 
    alpha = (np.clip((1 - r) / 0.5, 0, 1) ** 1.1) * 255
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rgb = np.ascontiguousarray(np.clip(col, 0, 255).astype(np.uint8).transpose(1, 0, 2))
    pygame.surfarray.blit_array(surf, rgb)
    a = pygame.surfarray.pixels_alpha(surf)
    a[:] = alpha.astype(np.uint8).T
    del a
    return surf
 
 
def draw_sparkle(surf, x, y, s, col=(255, 255, 255)):
    pygame.draw.line(surf, col, (x - s, y), (x + s, y), 1)
    pygame.draw.line(surf, col, (x, y - s), (x, y + s), 1)
    d = s * 0.45
    pygame.draw.line(surf, col, (x - d, y - d), (x + d, y + d), 1)
    pygame.draw.line(surf, col, (x - d, y + d), (x + d, y - d), 1)
    pygame.draw.circle(surf, col, (x, y), max(1, int(s * 0.28)))
 
 
class SwirlCursor:
    """Remolino de luz que sigue al nivel seleccionado y viaja hacia el nuevo."""
 
    def __init__(self, screen_size):
        self.base = make_swirl(256)
        self.beam = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.x = None
        self.y = None
        self.trail = deque(maxlen=30)
        self.speed = 0.0
        self.strength = 0.0
        self.particles = []
        self.rng = random.Random(12)
        rr = random.Random(4)
        self.orbit = [(rr.uniform(0, math.tau), rr.uniform(0.55, 1.25),
                       rr.uniform(0.0004, 0.0012) * rr.choice((-1, 1)), rr.uniform(0, 6.28))
                      for _ in range(14)]
 
    def snap(self, x, y):
        self.x, self.y = x, y
        self.trail.clear()
        self.speed = 0.0
 
    def update(self, tx, ty, strength, dt):
        if self.x is None:
            self.snap(tx, ty)
        dt = max(1, dt)
        k = 1 - math.exp(-dt * 0.011)
        mx, my = (tx - self.x) * k, (ty - self.y) * k
        self.x += mx
        self.y += my
        inst = math.hypot(mx, my) * 16.0 / dt
        self.speed += (inst - self.speed) * 0.3
        self.strength += (strength - self.strength) * 0.2
        self.trail.append((self.x, self.y))
 
        if self.speed > 1.0 and self.strength > 0.3 and len(self.particles) < 80:
            for _ in range(2):
                self.particles.append([
                    self.x + self.rng.uniform(-6, 6), self.y + self.rng.uniform(-6, 6),
                    self.rng.uniform(-0.5, 0.5), self.rng.uniform(-0.5, 0.5),
                    0.0, self.rng.uniform(300, 650)])
        alive = []
        for p in self.particles:
            p[0] += p[2] * dt * 0.04
            p[1] += p[3] * dt * 0.04
            p[4] += dt
            if p[4] < p[5]:
                alive.append(p)
        self.particles = alive
 
    def draw(self, screen, node_r, ticks):
        """Solo se ve mientras viaja de un nivel a otro; en reposo desaparece."""
        if self.x is None:
            return
        ws = node_r / 38.0
        # visibilidad: 0 en reposo, 1 en pleno viaje
        vis = max(0.0, min(1.0, (self.speed - 0.5) / 3.0)) * self.strength
 
        if vis > 0.02 and len(self.trail) > 2:
            # Estela: angosta en la cola, ancha cerca de la cabeza
            pts = list(self.trail)
            n = len(pts)
            self.beam.fill((0, 0, 0, 0))
            for col, wmul, amul in (((255, 45, 40), 20, 80),
                                    ((50, 130, 255), 16, 90),
                                    ((255, 150, 30), 12, 100),
                                    ((60, 235, 90), 8, 110),
                                    ((255, 255, 255), 3.5, 230)):
                for i in range(1, n):
                    f = (i / n) ** 1.3
                    w = max(1, int(wmul * ws * f * vis))
                    a = int(amul * f * vis)
                    pygame.draw.line(self.beam, col + (a,), pts[i - 1], pts[i], w)
            screen.blit(self.beam, (0, 0))
 
            # Cabeza de la estela: remolino chico que gira
            sc = (node_r * 2 * 1.15) / 256.0
            head = pygame.transform.rotozoom(self.base, ticks * 0.2, sc)
            head.set_alpha(int(255 * vis))
            screen.blit(head, head.get_rect(center=(self.x, self.y)))
 
            if vis > 0.3:
                for ang0, rad_f, spd, ph in self.orbit[:8]:
                    a = ang0 + ticks * spd * 3
                    px = self.x + math.cos(a) * node_r * 0.8 * rad_f
                    py = self.y + math.sin(a) * node_r * 0.8 * rad_f
                    b = 0.5 + 0.5 * math.sin(ticks * 0.01 + ph)
                    c = int(255 * b * vis)
                    draw_sparkle(screen, px, py, (2 + 4 * b) * ws, (c, c, c))
 
        # Chispas que quedan en el camino (se apagan solas)
        for i, p in enumerate(self.particles):
            f = 1 - p[4] / p[5]
            base = ((255, 70, 60), (70, 150, 255), (255, 170, 50), (90, 240, 110))[i % 4]
            col = tuple(int(v * f) for v in base)
            draw_sparkle(screen, p[0], p[1], (1.5 + 4 * f) * ws, col)
 
 
# ----------------------------------------------------------------------------
# Icono del Nivel 4: portal infernal con demonio cornudo
# ----------------------------------------------------------------------------
def _flame_pts(x0, base_y, h, w, sway, phase, ticks, n=9):
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        half = w * (1 - t) ** 0.75 * (0.85 + 0.15 * math.sin(t * 5 + phase + ticks * 0.012))
        off = sway * (t ** 1.6) * math.sin(ticks * 0.008 + phase + t * 2.2)
        y = base_y - h * t
        left.append((x0 + off - half, y))
        right.append((x0 + off + half, y))
    return left + right[::-1]
 
 
_FACE = [(-0.45, -0.35), (0.45, -0.35), (0.55, 0.05), (0.35, 0.55), (0.12, 0.88),
         (-0.12, 0.88), (-0.35, 0.55), (-0.55, 0.05)]
_HORN_L = [(-0.40, -0.28), (-0.78, -0.40), (-1.05, -0.70), (-1.12, -1.22),
           (-0.80, -0.92), (-0.50, -0.78), (-0.30, -0.55)]
_HORN_R = [(-x, y) for x, y in _HORN_L]
_EYE_L = [(-0.40, -0.06), (-0.12, 0.02), (-0.15, 0.11), (-0.42, 0.00)]
_EYE_R = [(-x, y) for x, y in _EYE_L]
 
 
def _fire_border(screen, cx, cy, r, ticks):
    n = 26
    layers = (((190, 24, 2), 1.0), ((255, 110, 12), 0.68), ((255, 215, 80), 0.38))
    for layer, (color, frac) in enumerate(layers):
        for k in range(n):
            ang = k * math.tau / n + ticks * 0.0004
            ln = (0.30 + 0.18 * math.sin(ticks * 0.012 + k * 1.9)
                  + 0.10 * math.sin(ticks * 0.021 + k * 3.1)) * r * frac
            sway = 0.14 * math.sin(ticks * 0.009 + k)
            hw = math.pi / n * 1.2 * (1 - layer * 0.2)
            b1 = (cx + math.cos(ang - hw) * r * 0.98, cy + math.sin(ang - hw) * r * 0.98)
            b2 = (cx + math.cos(ang + hw) * r * 0.98, cy + math.sin(ang + hw) * r * 0.98)
            tip = (cx + math.cos(ang + sway) * (r + 2 + ln), cy + math.sin(ang + sway) * (r + 2 + ln))
            pygame.draw.polygon(screen, color, [b1, tip, b2])
 
 
def draw_fire_icon(screen, cx, cy, r, ticks):
    r = float(r)
    _fire_border(screen, cx, cy, r, ticks)
 
    S = int(2 * r) + 4
    c = S / 2
    s = pygame.Surface((S, S), pygame.SRCALPHA)
 
    # Fondo: brasa que pulsa desde el centro
    pulse = 0.5 + 0.5 * math.sin(ticks * 0.004)
    steps = 9
    for i in range(steps):
        t = i / (steps - 1)
        rad = r * (1.0 - t * 0.95)
        e = t ** 1.5
        col = (int(_lerp(18, 150 + 40 * pulse, e)), int(_lerp(2, 28, e)), int(_lerp(6, 8, t)))
        pygame.draw.circle(s, col, (c, c), rad)
 
    # Brazos de energía en espiral
    rot = ticks * 0.0014
    for arm in range(3):
        a0 = rot + arm * math.tau / 3
        pts = []
        for j in range(20):
            t = j / 19
            a = a0 + t * math.pi * 1.5
            rr = r * (0.12 + 0.75 * t)
            pts.append((c + math.cos(a) * rr, c + math.sin(a) * rr))
        pygame.draw.lines(s, (150, 35, 8), False, pts, max(2, int(r * 0.09)))
        pygame.draw.lines(s, (255, 120, 20), False, pts, max(1, int(r * 0.035)))
 
    # Anillo de runas incandescentes
    for j in range(16):
        a = -rot * 1.6 + j * math.tau / 16
        flick = 0.6 + 0.4 * math.sin(ticks * 0.01 + j * 1.7)
        col = (255, int(120 + 90 * flick), int(20 + 30 * flick))
        p1 = (c + math.cos(a) * r * 0.86, c + math.sin(a) * r * 0.86)
        p2 = (c + math.cos(a + 0.17) * r * 0.86, c + math.sin(a + 0.17) * r * 0.86)
        pygame.draw.line(s, col, p1, p2, max(2, int(r * 0.07)))
    pygame.draw.circle(s, (255, 90, 10), (c, c), r * 0.93, max(1, int(r * 0.03)))
 
    # Llamas detrás del demonio (capas: rojo, naranja, amarillo, blanco caliente)
    base_y = c + r * 0.95
    tongues = [(-0.60, 0.90, 0.20, 0.0), (-0.34, 1.30, 0.25, 1.9), (-0.17, 1.10, 0.20, 3.2),
               (0.00, 1.70, 0.34, 0.5), (0.17, 1.15, 0.20, 1.2), (0.34, 1.25, 0.25, 2.6),
               (0.60, 0.95, 0.20, 4.1)]
    layers = [((150, 20, 4), 1.0, 1.0), ((235, 70, 8), 0.82, 0.78),
              ((255, 150, 20), 0.62, 0.55), ((255, 228, 110), 0.40, 0.30)]
    for color, hm, wm in layers:
        for ox, h0, w0, ph in tongues:
            h = r * h0 * hm * (1 + 0.10 * math.sin(ticks * 0.011 + ph))
            w = r * w0 * wm
            pts = _flame_pts(c + ox * r, base_y, h, w, r * 0.10, ph, ticks)
            pygame.draw.polygon(s, color, pts)
 
    # Cabeza de demonio cornudo a contraluz
    sc = r * 0.42
    hy = c + r * 0.08
 
    def P(poly):
        return [(c + x * sc, hy + y * sc) for x, y in poly]
 
    head = [_FACE, _HORN_L, _HORN_R]
    for p in head:
        pygame.draw.polygon(s, (255, 150, 35), P(p), max(2, int(r * 0.05)))
    for p in head:
        pygame.draw.polygon(s, (12, 3, 5), P(p))
    flick = 0.8 + 0.2 * math.sin(ticks * 0.02)
    eye_col = (255, int(190 + 40 * flick), int(40 + 30 * flick))
    for eye in (_EYE_L, _EYE_R):
        ex = sum(p[0] for p in eye) / 4
        ey = sum(p[1] for p in eye) / 4
        pygame.draw.circle(s, (130, 44, 6), (c + ex * sc, hy + ey * sc), r * 0.11)
        pygame.draw.polygon(s, eye_col, P(eye))
    # colmillos
    for fx in (-0.14, 0.14):
        pygame.draw.polygon(s, (255, 214, 140),
                            P([(fx - 0.05, 0.52), (fx + 0.05, 0.52), (fx, 0.70)]))
 
    # Chispas ascendentes
    span = r * 1.7
    for i in range(16):
        ph = i * 1.73
        x = c + math.sin(ticks * 0.004 + ph) * r * 0.8
        cyc = (ticks * (0.03 + (i % 4) * 0.006) + i * 37) % span
        y = c + r * 0.9 - cyc
        f = 1 - cyc / span
        col = (int(255 * f), int((185 + (i % 2) * 35) * f), int(45 * f))
        pygame.draw.circle(s, col, (x, y), max(1, int(r * 0.035)))
 
    # Recorte circular
    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), r)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(s, s.get_rect(center=(cx, cy)))
 