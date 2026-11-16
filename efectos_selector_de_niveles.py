import math

import pygame


def _lerp(a, b, t):
    return a + (b - a) * t


class SwirlCursor:
    """Marcador estable para el nodo seleccionado, sin estela ni partículas."""

    def __init__(self, screen_size):
        self.x = None
        self.y = None
        self.strength = 0.0

    def snap(self, x, y):
        self.x, self.y = x, y

    def update(self, tx, ty, strength, dt):
        if self.x is None:
            self.snap(tx, ty)
        dt = max(1, dt)
        k = 1 - math.exp(-dt * 0.011)
        self.x += (tx - self.x) * k
        self.y += (ty - self.y) * k
        self.strength += (strength - self.strength) * 0.2

    def draw(self, screen, node_r, ticks):
        if self.x is None or self.strength <= 0.02:
            return
        pulse = 0.5 + 0.5 * math.sin(ticks * 0.006)
        radius = max(2, round(node_r * (0.72 + pulse * 0.12)))
        color = (215, 187, 120)
        center = round(self.x), round(self.y)
        pygame.draw.circle(screen, color, center, radius, 2)
        pygame.draw.circle(
            screen,
            (255, 225, 160),
            center,
            max(2, round(radius * 0.68)),
            1,
        )


# ----------------------------------------------------------------------------
# Icono del Nivel 4: portal infernal con demonio cornudo
# ----------------------------------------------------------------------------
def _flame_pts(x0, base_y, h, w, sway, phase, ticks, n=9):
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        half = (
            w
            * ((1 - t) ** 0.75)
            * (0.85 + 0.15 * math.sin(t * 5 + phase + ticks * 0.012))
        )
        off = sway * (t**1.6) * math.sin(ticks * 0.008 + phase + t * 2.2)
        y = base_y - h * t
        left.append((x0 + off - half, y))
        right.append((x0 + off + half, y))
    return left + right[::-1]


_FACE = [
    (-0.45, -0.35),
    (0.45, -0.35),
    (0.55, 0.05),
    (0.35, 0.55),
    (0.12, 0.88),
    (-0.12, 0.88),
    (-0.35, 0.55),
    (-0.55, 0.05),
]
_HORN_L = [
    (-0.40, -0.28),
    (-0.78, -0.40),
    (-1.05, -0.70),
    (-1.12, -1.22),
    (-0.80, -0.92),
    (-0.50, -0.78),
    (-0.30, -0.55),
]
_HORN_R = [(-x, y) for x, y in _HORN_L]
_EYE_L = [(-0.40, -0.06), (-0.12, 0.02), (-0.15, 0.11), (-0.42, 0.00)]
_EYE_R = [(-x, y) for x, y in _EYE_L]


def _fire_border(screen, cx, cy, r, ticks):
    n = 26
    layers = (((190, 24, 2), 1.0), ((255, 110, 12), 0.68), ((255, 215, 80), 0.38))
    for layer, (color, frac) in enumerate(layers):
        for k in range(n):
            ang = k * math.tau / n + ticks * 0.0004
            ln = (
                0.30
                + 0.18 * math.sin(ticks * 0.012 + k * 1.9)
                + 0.10 * math.sin(ticks * 0.021 + k * 3.1)
            ) * r * frac
            sway = 0.14 * math.sin(ticks * 0.009 + k)
            hw = (math.pi / n) * 1.2 * (1 - layer * 0.2)
            b1 = (
                cx + math.cos(ang - hw) * r * 0.98,
                cy + math.sin(ang - hw) * r * 0.98,
            )
            b2 = (
                cx + math.cos(ang + hw) * r * 0.98,
                cy + math.sin(ang + hw) * r * 0.98,
            )
            tip = (
                cx + math.cos(ang + sway) * (r + 2 + ln),
                cy + math.sin(ang + sway) * (r + 2 + ln),
            )
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
        e = t**1.5
        col = (
            int(_lerp(18, 150 + 40 * pulse, e)),
            int(_lerp(2, 28, e)),
            int(_lerp(6, 8, t)),
        )
        pygame.draw.circle(s, col, (c, c), rad)

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

    for j in range(16):
        a = -rot * 1.6 + j * math.tau / 16
        flick = 0.6 + 0.4 * math.sin(ticks * 0.01 + j * 1.7)
        col = (255, int(120 + 90 * flick), int(20 + 30 * flick))
        p1 = (c + math.cos(a) * r * 0.86, c + math.sin(a) * r * 0.86)
        p2 = (
            c + math.cos(a + 0.17) * r * 0.86,
            c + math.sin(a + 0.17) * r * 0.86,
        )
        pygame.draw.line(s, col, p1, p2, max(2, int(r * 0.07)))
    pygame.draw.circle(s, (255, 90, 10), (c, c), r * 0.93, max(1, int(r * 0.03)))

    base_y = c + r * 0.95
    tongues = [
        (-0.60, 0.90, 0.20, 0.0),
        (-0.34, 1.30, 0.25, 1.9),
        (-0.17, 1.10, 0.20, 3.2),
        (0.00, 1.70, 0.34, 0.5),
        (0.17, 1.15, 0.20, 1.2),
        (0.34, 1.25, 0.25, 2.6),
        (0.60, 0.95, 0.20, 4.1),
    ]
    layers = [
        ((150, 20, 4), 1.0, 1.0),
        ((235, 70, 8), 0.82, 0.78),
        ((255, 150, 20), 0.62, 0.55),
        ((255, 228, 110), 0.40, 0.30),
    ]
    for color, hm, wm in layers:
        for ox, h0, w0, ph in tongues:
            h = r * h0 * hm * (1 + 0.10 * math.sin(ticks * 0.011 + ph))
            w = r * w0 * wm
            pts = _flame_pts(c + ox * r, base_y, h, w, r * 0.10, ph, ticks)
            pygame.draw.polygon(s, color, pts)

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
        pygame.draw.circle(
            s, (130, 44, 6), (c + ex * sc, hy + ey * sc), r * 0.11
        )
        pygame.draw.polygon(s, eye_col, P(eye))
    for fx in (-0.14, 0.14):
        pygame.draw.polygon(
            s,
            (255, 214, 140),
            P([(fx - 0.05, 0.52), (fx + 0.05, 0.52), (fx, 0.70)]),
        )

    span = r * 1.7
    for i in range(16):
        ph = i * 1.73
        x = c + math.sin(ticks * 0.004 + ph) * r * 0.8
        cyc = (ticks * (0.03 + (i % 4) * 0.006) + i * 37) % span
        y = c + r * 0.9 - cyc
        f = 1 - cyc / span
        col = (
            int(255 * f),
            int((185 + (i % 2) * 35) * f),
            int(45 * f),
        )
        pygame.draw.circle(s, col, (x, y), max(1, int(r * 0.035)))

    mask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), r)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(s, s.get_rect(center=(cx, cy)))