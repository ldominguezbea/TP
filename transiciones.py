"""Escenas de transición de REQUIEM (pygame-ce).

* EscenaCita   : cita bíblica sobre fondo oscuro, ANTES del cómic del prólogo.
* EscenaTitulo : "Cour I - The Invasion" en letras divinas, DESPUÉS del cómic.
* superponer_fundido : velo negro (o de otro color) para fundidos de cualquier escena.

Todas las escenas comparten la misma interfaz:
    escena.handle_event(event)   # cualquier tecla / clic adelanta la escena (tras un margen)
    terminada = escena.update(elapsed_ms)   # True cuando acabó por completo
    escena.draw(surface)
"""
import math
import random

import pygame

from fuentes_requiem import (
    FUENTES_GOTICAS, FUENTES_TEXTO,
    cargar_fuente, envolver_texto, halo_de_texto,
)


# ============================================================
# AUXILIARES
# ============================================================

_velos = {}


def superponer_fundido(destino, opacidad, color=(0, 0, 0)):
    """Dibuja sobre `destino` un velo de `color` con opacidad 0..1."""
    a = int(255 * max(0.0, min(1.0, opacidad)))
    if a <= 0:
        return
    tam = destino.get_size()
    velo = _velos.get(tam)
    if velo is None:
        velo = pygame.Surface(tam)
        _velos[tam] = velo
    velo.fill(color)
    velo.set_alpha(a)
    destino.blit(velo, (0, 0))


def _suave(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _dt(ms):
    return min(max(ms, 0) / 1000.0, 0.05)


def _sprite_radial(tam, color, intensidad, exponente=1.8):
    n = 40
    peq = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            d = math.hypot((x - c) / c, (y - c) / c)
            a = max(0.0, 1.0 - d) ** exponente * intensidad
            peq.set_at((x, y), (*color, int(255 * min(1.0, a))))
    return pygame.transform.smoothscale(peq, (max(2, int(tam[0])), max(2, int(tam[1]))))


class _EscenaFundida:
    """Máquina de estados común: espera -> entrada -> mantener -> salida -> negro -> fin.

    `nivel` (0..1) es la visibilidad del contenido. Pulsar tecla/clic tras
    `margen_salto` segundos adelanta la escena: de entrada/mantener pasa a salida
    (desde el nivel actual, sin saltos bruscos) y, si ya estaba saliendo, la termina.
    """
    T_ESPERA = 0.6
    T_ENTRADA = 1.8
    T_MANTENER = 4.0
    T_SALIDA = 1.4
    T_NEGRO = 0.4
    MARGEN_SALTO = 0.9

    def __init__(self):
        self.fase = "espera"
        self.t = 0.0            # tiempo total
        self.t_fase = 0.0
        self.nivel = 0.0
        self.terminada = False

    def handle_event(self, event):
        if self.terminada or self.t < self.MARGEN_SALTO:
            return
        pulsado = (event.type == pygame.KEYDOWN or
                   (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1))
        if not pulsado:
            return
        if self.fase in ("espera", "entrada", "mantener"):
            self._ir("salida")
        elif self.fase == "salida":
            self.nivel = 0.0
            self._ir("negro")

    def _ir(self, fase):
        self.fase = fase
        self.t_fase = 0.0

    def _avanzar(self, dt):
        self.t += dt
        self.t_fase += dt
        if self.fase == "espera":
            if self.t_fase >= self.T_ESPERA:
                self._ir("entrada")
        elif self.fase == "entrada":
            self.nivel = min(1.0, self.nivel + dt / self.T_ENTRADA)
            if self.nivel >= 1.0:
                self._ir("mantener")
        elif self.fase == "mantener":
            if self.t_fase >= self.T_MANTENER:
                self._ir("salida")
        elif self.fase == "salida":
            self.nivel = max(0.0, self.nivel - dt / self.T_SALIDA)
            if self.nivel <= 0.0:
                self._ir("negro")
        elif self.fase == "negro":
            if self.t_fase >= self.T_NEGRO:
                self.fase = "fin"
                self.terminada = True
        return self.terminada


# ============================================================
# 1) CITA BÍBLICA (antes del cómic)
# ============================================================

class EscenaCita(_EscenaFundida):
    TEXTO = ("¡Ay de los moradores de la tierra y del mar!, porque el diablo "
             "ha descendido a vosotros, teniendo gran ira.")
    REFERENCIA = "Apocalipsis 12:12"

    def __init__(self, tam, texto=None, referencia=None):
        super().__init__()
        self.W, self.H = tam
        s = self.H / 720.0
        self.s = s
        rng = random.Random(666)

        f_cita = cargar_fuente(FUENTES_TEXTO, 36 * s, italic=True)
        f_ref = cargar_fuente(FUENTES_GOTICAS, 26 * s)
        lineas = envolver_texto(texto or self.TEXTO, f_cita, int(self.W * 0.62))

        alto_linea = f_cita.get_linesize() + int(6 * s)
        ancho = max(f_cita.size(l)[0] for l in lineas) + int(20 * s)
        alto = alto_linea * len(lineas) + int(70 * s)
        self.texto_surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        for i, linea in enumerate(lineas):
            y = i * alto_linea
            sombra = f_cita.render(linea, True, (60, 8, 10))
            marca = f_cita.render(linea, True, (226, 216, 200))
            cx = ancho // 2
            self.texto_surf.blit(sombra, sombra.get_rect(midtop=(cx + int(2 * s), y + int(2 * s))))
            self.texto_surf.blit(marca, marca.get_rect(midtop=(cx, y)))
        y_ref = alto_linea * len(lineas) + int(26 * s)
        linea_y = y_ref - int(12 * s)
        pygame.draw.line(self.texto_surf, (120, 30, 30), (ancho // 2 - int(40 * s), linea_y),
                         (ancho // 2 + int(40 * s), linea_y), 1)
        ref = f_ref.render("— " + (referencia or self.REFERENCIA), True, (196, 150, 70))
        self.texto_surf.blit(ref, ref.get_rect(midtop=(ancho // 2, y_ref)))

        # Resplandor apagado y brasas muy tenues
        self.resplandor = _sprite_radial((int(self.W * 0.9), int(self.H * 0.7)), (130, 22, 22), 0.28)
        self.brasas = [[rng.uniform(0, self.W), rng.uniform(0, self.H), rng.uniform(8, 24) * s,
                        rng.random() * math.tau, max(1, round(rng.choice((1, 1, 2)) * s))]
                       for _ in range(55)]
        self.capa = pygame.Surface((self.W, self.H))

    def update(self, elapsed_ms):
        return self._avanzar(_dt(elapsed_ms))

    def draw(self, destino):
        destino.fill((4, 3, 6))
        n = _suave(self.nivel)
        t = self.t

        pulso = 0.8 + 0.2 * math.sin(t * 0.9)
        self.resplandor.set_alpha(int(255 * (0.25 + 0.75 * n) * pulso))
        destino.blit(self.resplandor, self.resplandor.get_rect(center=(self.W // 2, int(self.H * 0.52))))

        capa = self.capa
        capa.fill((0, 0, 0))
        for x0, y0, vel, fase, tam in self.brasas:
            y = (y0 - t * vel) % (self.H + 20) - 10
            x = (x0 + math.sin(t * 0.4 + fase) * 10 * self.s) % self.W
            fl = 0.5 + 0.5 * math.sin(t * 1.5 + fase * 3)
            k = (0.18 + 0.30 * fl) * (0.4 + 0.6 * n)
            pygame.draw.circle(capa, (int(200 * k), int(60 * k), int(25 * k)), (int(x), int(y)), tam)
        destino.blit(capa, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        if n > 0.003:
            self.texto_surf.set_alpha(int(255 * n))
            destino.blit(self.texto_surf, self.texto_surf.get_rect(center=(self.W // 2, int(self.H * 0.5))))


# ============================================================
# 2) "Cour I - The Invasion" (después del cómic)
# ============================================================

class EscenaTitulo(_EscenaFundida):
    TEXTO = "Cour I - The Invasion"
    T_ESPERA = 0.8
    T_ENTRADA = 2.6
    T_MANTENER = 3.4
    T_SALIDA = 1.5
    T_NEGRO = 0.45
    MARGEN_SALTO = 1.6

    def __init__(self, tam, texto=None):
        super().__init__()
        self.W, self.H = tam
        s = self.H / 720.0
        self.s = s
        texto = texto or self.TEXTO
        rng = random.Random(1212)

        # Letra más ornamental disponible, reducida hasta que quepa en el 82 % del ancho
        tam_fuente = 92
        while True:
            fuente = cargar_fuente(FUENTES_GOTICAS, tam_fuente * s)
            if fuente.size(texto)[0] <= self.W * 0.82 or tam_fuente <= 36:
                break
            tam_fuente -= 4
        self.texto_base = fuente.render(texto, True, (255, 247, 224))
        self.texto_dorado = fuente.render(texto, True, (255, 214, 120))
        self.halo_ancho = halo_de_texto(fuente, texto, (255, 196, 84), int(46 * s))
        self.halo_cerca = halo_de_texto(fuente, texto, (255, 226, 150), int(16 * s))

        # Luz divina: resplandor dorado y haces de luz
        self.luz = _sprite_radial((int(self.W * 1.15), int(self.H * 0.62)), (255, 214, 130), 0.42, 1.5)
        self.haces = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        cx, cy = self.W // 2, int(self.H * 0.5)
        largo = max(self.W, self.H)
        for k in range(18):
            ang = k * math.tau / 18 + 0.1
            ancho_ang = 0.035 + 0.02 * ((k * 7) % 3)
            pts = [(cx, cy),
                   (cx + math.cos(ang - ancho_ang) * largo, cy + math.sin(ang - ancho_ang) * largo),
                   (cx + math.cos(ang + ancho_ang) * largo, cy + math.sin(ang + ancho_ang) * largo)]
            pygame.draw.polygon(self.haces, (255, 226, 150, 15), pts)

        # Divisor sagrado: línea que se difumina en los extremos con rombo central
        ancho_d = int(self.W * 0.46)
        self.divisor = pygame.Surface((ancho_d, int(18 * s)), pygame.SRCALPHA)
        yc = self.divisor.get_height() // 2
        for x in range(ancho_d):
            u = abs(x - ancho_d / 2) / (ancho_d / 2)
            a = int(255 * (1 - u) ** 1.3)
            self.divisor.set_at((x, yc), (255, 226, 150, a))
            self.divisor.set_at((x, yc + 1), (255, 200, 110, a // 2))
        d = int(7 * s)
        pygame.draw.polygon(self.divisor, (255, 240, 200),
                            [(ancho_d // 2, yc - d), (ancho_d // 2 + d, yc),
                             (ancho_d // 2, yc + d), (ancho_d // 2 - d, yc)])

        # Chispas doradas que ascienden
        self.motas = [[rng.uniform(0, self.W), rng.uniform(0, self.H), rng.uniform(10, 30) * s,
                       rng.random() * math.tau, max(1, round(rng.choice((1, 1, 2)) * s))]
                      for _ in range(60)]

    def update(self, elapsed_ms):
        return self._avanzar(_dt(elapsed_ms))

    def draw(self, destino):
        destino.fill((0, 0, 0))
        W, H, s, t = self.W, self.H, self.s, self.t
        n = _suave(self.nivel)
        pulso = 0.5 + 0.5 * math.sin(t * 1.7)           # 0..1, lento y solemne
        centro = (W // 2, int(H * 0.5))

        if n > 0.003:
            self.luz.set_alpha(int(255 * n * (0.8 + 0.2 * pulso)))
            destino.blit(self.luz, self.luz.get_rect(center=centro))
            self.haces.set_alpha(int(255 * n * (0.65 + 0.35 * pulso)))
            destino.blit(self.haces, (0, 0))

            for x0, y0, vel, fase, tam in self.motas:
                y = (y0 - t * vel) % (H + 20) - 10
                x = (x0 + math.sin(t * 0.5 + fase) * 12 * s) % W
                k = n * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2 + fase * 2)))
                pygame.draw.circle(destino, (int(255 * k), int(224 * k), int(150 * k)), (int(x), int(y)), tam)

            # Expansión muy sutil: arranca un 4 % más pequeño y respira un ±1 %
            escala = 0.96 + 0.04 * n + 0.010 * math.sin(t * 1.7)
            self._blit_escalado(destino, self.halo_ancho, centro, escala, int(255 * n * (0.55 + 0.45 * pulso)))
            self._blit_escalado(destino, self.halo_cerca, centro, escala, int(255 * n * (0.6 + 0.4 * pulso)))
            self._blit_escalado(destino, self.texto_dorado, centro, escala, int(255 * n))
            self._blit_escalado(destino, self.texto_base, centro, escala, int(255 * n * (0.85 + 0.15 * pulso)))

            y_div = centro[1] + self.texto_base.get_height() // 2 + int(24 * s)
            self.divisor.set_alpha(int(255 * _suave((self.nivel - 0.25) / 0.75)))
            destino.blit(self.divisor, self.divisor.get_rect(center=(W // 2, y_div)))

    @staticmethod
    def _blit_escalado(destino, sup, centro, escala, alfa):
        if alfa <= 0:
            return
        w, h = sup.get_size()
        if abs(escala - 1.0) > 0.002:
            sup = pygame.transform.smoothscale(sup, (max(1, int(w * escala)), max(1, int(h * escala))))
        sup.set_alpha(max(0, min(255, alfa)))
        destino.blit(sup, sup.get_rect(center=centro))