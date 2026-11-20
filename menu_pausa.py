"""Menú de pausa cinemático de REQUIEM (compatible con pygame-ce).

API pública (sin cambios respecto a la versión anterior):

    pausar_juego(screen, devolver_accion=False)
        - devolver_accion=True  -> devuelve "resume" | "menu" | "exit"
        - devolver_accion=False -> "resume" devuelve None; "menu" y "exit"
                                   lanzan SystemExit con los códigos de abajo.

    menu_muerte_juego(screen, devolver_accion=False)
        - devolver_accion=True  -> devuelve "retry" | "menu" | "exit"
        - devolver_accion=False -> lanza SystemExit con el código de la acción.

    RETURN_TO_MENU_EXIT_CODE, EXIT_GAME_EXIT_CODE, RETRY_LEVEL_EXIT_CODE,
    NivelIntegradoFinalizado

Recursos opcionales (se buscan por nombre dentro de la carpeta del proyecto,
hasta 5 niveles de profundidad):
    runaintro.gif, runaidle.gif       -> animación de la runa (requiere Pillow)
    Bell2.mp3 (bucle de pausa), Bell1.mp3 (apertura/selección/salida)

Si falta algún recurso (o Pillow), el menú sigue funcionando con una runa
procedural y sin esos sonidos: nunca debe romper el juego.
"""

import array
import math
import os
import random
from pathlib import Path

import pygame


RETURN_TO_MENU_EXIT_CODE = 10
EXIT_GAME_EXIT_CODE = 11
RETRY_LEVEL_EXIT_CODE = 12

_OPTIONS = ("Resume", "Return to menu", "Exit game")
_ACCIONES = ("resume", "menu", "exit")
# Color de acento por opción: dorado (reanudar), ámbar (menú), rojo (salir).
_ACENTOS = ((232, 184, 96), (222, 140, 78), (232, 70, 56))

# ----------------------------------------------------------------------------
# Ajustes rápidos
# ----------------------------------------------------------------------------
ARCHIVO_RUNA_ENTRADA = "runaintro.gif"
ARCHIVO_RUNA_IDLE = "runaidle.gif"
ARCHIVO_SONIDO_SELECCION = "Bell1.mp3"
ARCHIVO_SONIDO_PAUSA = "Bell2.mp3"
VOLUMEN_CAMPANAS = 0.85
VOLUMEN_SFX = 0.45
VOLUMEN_MUSICA_EN_PAUSA = 0.28   # la música baja a este % mientras dura la pausa
DURACION_ENTRADA_MS = 1150
DURACION_SALIDA_REANUDAR_MS = 700
DURACION_SALIDA_DEFINITIVA_MS = 1100


class NivelIntegradoFinalizado(Exception):
    def __init__(self, completed=False, action=None):
        self.completed = completed
        self.action = action


# ----------------------------------------------------------------------------
# Utilidades matemáticas
# ----------------------------------------------------------------------------
def _clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def _lerp(a, b, t):
    return a + (b - a) * t


def _suave(t):
    t = _clamp(t)
    return t * t * (3.0 - 2.0 * t)


def _ease_out(t):
    t = _clamp(t)
    return 1.0 - (1.0 - t) ** 3


def _ease_in(t):
    t = _clamp(t)
    return t ** 3


def _ease_out_back(t, s=1.70158):
    t = _clamp(t) - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0


def _mezcla(c1, c2, t):
    return tuple(int(_lerp(a, b, t)) for a, b in zip(c1, c2))


def _escalar_color(color, f):
    f = _clamp(f)
    return tuple(int(c * f) for c in color)


# ----------------------------------------------------------------------------
# Búsqueda y carga de recursos
# ----------------------------------------------------------------------------
_RUTAS_CACHE = {}
_FUENTES = {}


def _carpetas_base():
    bases = [Path(__file__).resolve().parent, Path.cwd()]
    try:
        from config import BASE_DIR  # type: ignore

        bases.insert(0, Path(BASE_DIR))
    except Exception:
        pass
    vistos = []
    for base in bases:
        if base not in vistos and base.is_dir():
            vistos.append(base)
    return vistos


def _buscar_recurso(nombre):
    clave = nombre.lower()
    if clave in _RUTAS_CACHE:
        return _RUTAS_CACHE[clave]

    encontrado = None
    ignorar = {"__pycache__", "venv", ".venv", "node_modules", ".git"}
    for base in _carpetas_base():
        for raiz, carpetas, archivos in os.walk(base):
            profundidad = len(Path(raiz).relative_to(base).parts)
            carpetas[:] = [
                c for c in carpetas if c not in ignorar and not c.startswith(".")
            ] if profundidad < 5 else []
            for archivo in archivos:
                if archivo.lower() == clave:
                    encontrado = Path(raiz) / archivo
                    break
            if encontrado:
                break
        if encontrado:
            break

    _RUTAS_CACHE[clave] = encontrado
    return encontrado


def _fuente(nombre, tam, negrita=True):
    clave = (nombre, tam, negrita)
    if clave not in _FUENTES:
        _FUENTES[clave] = pygame.font.SysFont(nombre, tam, bold=negrita)
    return _FUENTES[clave]


def _cargar_gif(nombre):
    """Devuelve (frames, duraciones_ms). Usa Pillow; si falla, listas vacías."""
    ruta = _buscar_recurso(nombre)
    if ruta is None:
        print(f"[PAUSA] No se encontró {nombre}; se usa una runa procedural.")
        return [], []
    try:
        from PIL import Image, ImageSequence
    except ImportError:
        print("[PAUSA] Falta Pillow (pip install pillow); se usa una runa procedural.")
        return [], []

    frames, duraciones = [], []
    try:
        with Image.open(ruta) as gif:
            predeterminada = int(gif.info.get("duration", 80) or 80)
            for cuadro in ImageSequence.Iterator(gif):
                rgba = cuadro.convert("RGBA")
                datos = rgba.tobytes()
                superficie = pygame.image.frombuffer(datos, rgba.size, "RGBA")
                frames.append(superficie.convert_alpha())
                duraciones.append(int(cuadro.info.get("duration", predeterminada) or predeterminada))
    except Exception as error:  # noqa: BLE001 - el menú nunca debe romper el juego
        print(f"[PAUSA] No se pudo leer {nombre}: {error}")
        return [], []
    return frames, duraciones


def _runa_procedural(cantidad=16, tam=128):
    frames = []
    c = tam // 2
    for f in range(cantidad):
        s = pygame.Surface((tam, tam), pygame.SRCALPHA)
        giro = f / cantidad * math.tau / 9
        for radio, color in ((c - 2, (205, 80, 34)), (c - 11, (160, 46, 30)), (c - 24, (225, 130, 56))):
            pygame.draw.circle(s, color, (c, c), radio, 1)
        for paso, color in ((4, (232, 112, 40)), (2, (200, 70, 30))):
            puntos = [
                (c + math.cos(giro + i * math.tau * paso / 9) * (c - 13),
                 c + math.sin(giro + i * math.tau * paso / 9) * (c - 13))
                for i in range(9)
            ]
            pygame.draw.polygon(s, color, puntos, 1)
        pygame.draw.circle(s, (255, 214, 150), (c, c), 3)
        frames.append(s)
    return frames


def _sintetizar_tono(frecuencia, duracion_ms, volumen, caida=3.0, bajada=0.0):
    ajustes = pygame.mixer.get_init()
    if ajustes is None:
        return None
    tasa, formato, canales = ajustes
    if formato != -16:
        return None
    muestras = array.array("h")
    total = max(1, int(tasa * duracion_ms / 1000))
    fase = 0.0
    for i in range(total):
        p = i / total
        fase += math.tau * frecuencia * (1.0 - bajada * p) / tasa
        envolvente = min(1.0, i / (tasa * 0.003)) * (1.0 - p) ** caida
        valor = int(32767 * volumen * envolvente * math.sin(fase))
        muestras.extend([valor] * canales)
    try:
        return pygame.mixer.Sound(buffer=muestras.tobytes())
    except pygame.error:
        return None


def _cargar_sonido(nombre, volumen):
    if pygame.mixer.get_init() is None:
        return None
    ruta = _buscar_recurso(nombre)
    if ruta is None:
        print(f"[PAUSA] No se encontró {nombre}.")
        return None
    try:
        sonido = pygame.mixer.Sound(str(ruta))
        sonido.set_volume(volumen)
        return sonido
    except pygame.error as error:
        print(f"[PAUSA] No se pudo cargar {nombre}: {error}")
        return None


def _crear_glifos(rng, cantidad=10, ancho=26, alto=44, color=(176, 54, 40)):
    """Pseudo-runas (astas con ramas) para las columnas decorativas."""
    glifos = []
    for _ in range(cantidad):
        s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        x = ancho // 2
        pygame.draw.line(s, color, (x, 3), (x, alto - 3), 2)
        for _ in range(rng.randint(1, 3)):
            y = rng.randint(6, alto - 20)
            lado = rng.choice((-1, 1))
            largo = rng.randint(7, 11)
            tipo = rng.choice((0, 1, 2))
            if tipo == 0:
                pygame.draw.line(s, color, (x, y), (x + lado * largo, y + largo), 2)
            elif tipo == 1:
                pygame.draw.line(s, color, (x, y + largo), (x + lado * largo, y), 2)
            else:
                pygame.draw.line(s, color, (x, y), (x + lado * largo, y + largo // 2), 2)
                pygame.draw.line(s, color, (x + lado * largo, y + largo // 2), (x, y + largo), 2)
        glifos.append(s)
    return glifos


class _Recursos:
    """Se carga una sola vez por proceso y se reutiliza en cada pausa."""

    def __init__(self):
        entrada, dur_entrada = _cargar_gif(ARCHIVO_RUNA_ENTRADA)
        idle, dur_idle = _cargar_gif(ARCHIVO_RUNA_IDLE)

        self.runa_entrada = entrada
        self.runa_salida = list(reversed(entrada))

        if idle:
            self.runa_idle = idle
        elif entrada:
            self.runa_idle = [entrada[-1]]
        else:
            self.runa_idle = _runa_procedural()
        referencia = dur_idle or dur_entrada
        self.frame_ms = max(30, int(referencia[0])) if referencia else 80

        self.sonido_seleccion = _cargar_sonido(ARCHIVO_SONIDO_SELECCION, VOLUMEN_CAMPANAS)
        self.sonido_pausa = _cargar_sonido(ARCHIVO_SONIDO_PAUSA, VOLUMEN_CAMPANAS)
        self.tick = _sintetizar_tono(1180, 55, VOLUMEN_SFX * 0.55, caida=2.2)
        self.glifos = _crear_glifos(random.Random(1604))


_RECURSOS = None


def _obtener_recursos():
    global _RECURSOS
    if _RECURSOS is None:
        _RECURSOS = _Recursos()
    return _RECURSOS


def _tocar(sonido, loops=0):
    if sonido is None or pygame.mixer.get_init() is None:
        return None
    try:
        canal = sonido.play(loops=loops)
        if canal is None:
            canal = pygame.mixer.find_channel(True)
            if canal is not None:
                canal.play(sonido, loops=loops)
        return canal
    except pygame.error:
        return None


# ----------------------------------------------------------------------------
# Superficies auxiliares (gradientes, viñeta, desenfoque, runa escalada)
# ----------------------------------------------------------------------------
def _desenfocar(superficie):
    w, h = superficie.get_size()
    pequena = pygame.transform.smoothscale(superficie, (max(1, w // 16), max(1, h // 16)))
    return pygame.transform.smoothscale(pequena, (w, h))


def _gradiente_radial_alfa(tam, color, alfa_max, potencia):
    base = 32
    s = pygame.Surface((base, base), pygame.SRCALPHA)
    c = (base - 1) / 2
    for y in range(base):
        for x in range(base):
            d = math.hypot(x - c, y - c) / c
            f = max(0.0, 1.0 - d) ** potencia
            s.set_at((x, y), (*color, int(alfa_max * f)))
    return pygame.transform.smoothscale(s, (tam, tam))


def _vineta(ancho, alto):
    pw, ph = 48, 27
    s = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for y in range(ph):
        for x in range(pw):
            dx = (x / (pw - 1) - 0.5) * 2.0
            dy = (y / (ph - 1) - 0.5) * 2.0
            d = math.hypot(dx, dy) / 1.414
            a = _clamp((d - 0.38) / 0.62) ** 1.7
            s.set_at((x, y), (5, 0, 7, int(235 * a)))
    return pygame.transform.smoothscale(s, (ancho, alto))


def _escalar_frame(frame, tam):
    k = max(1, math.ceil(tam / frame.get_width()))
    grande = pygame.transform.scale(frame, (frame.get_width() * k, frame.get_height() * k))
    if grande.get_width() == tam:
        return grande
    return pygame.transform.smoothscale(grande, (tam, tam))


def _brillo_de_frame(frame, tam):
    """Versión borrosa y muy luminosa del frame para el resplandor aditivo."""
    base = pygame.Surface(frame.get_size())
    base.fill((0, 0, 0))
    base.blit(frame, (0, 0))
    pequena = pygame.transform.smoothscale(base, (max(4, tam // 12), max(4, tam // 12)))
    for _ in range(3):
        copia = pequena.copy()
        pequena.blit(copia, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    lado = int(tam * 1.55)
    return pygame.transform.smoothscale(pequena, (lado, lado))


def _crear_calavera():
    tam = 360
    icono = pygame.Surface((tam, tam), pygame.SRCALPHA)
    contorno = (39, 25, 26, 255)
    hueso = (211, 195, 169, 255)
    sombra_hueso = (153, 125, 102, 255)
    luz_hueso = (244, 229, 200, 255)

    silueta = (
        (180, 25), (218, 31), (250, 49), (274, 77), (289, 111),
        (290, 139), (279, 164), (260, 183), (253, 207), (248, 229),
        (231, 251), (208, 267), (180, 278), (152, 267), (129, 251),
        (112, 229), (107, 207), (100, 183), (81, 164), (70, 139),
        (71, 111), (86, 77), (110, 49), (142, 31),
    )
    pygame.draw.polygon(icono, contorno, silueta)
    pygame.draw.polygon(
        icono,
        hueso,
        (
            (180, 34), (215, 40), (245, 58), (266, 84), (279, 114),
            (279, 137), (268, 158), (250, 175), (242, 198), (239, 218),
            (227, 239), (211, 254), (195, 264), (180, 269), (165, 264),
            (149, 254), (133, 239), (121, 218), (118, 198), (110, 175),
            (92, 158), (81, 137), (81, 114), (94, 84), (115, 58),
            (145, 40),
        ),
    )

    pygame.draw.polygon(
        icono,
        (164, 136, 110, 255),
        ((94, 87), (117, 59), (146, 41), (158, 53), (145, 107),
         (133, 169), (121, 211), (110, 176), (91, 158), (81, 137)),
    )
    pygame.draw.ellipse(icono, (230, 215, 187, 255), (137, 48, 90, 34))
    pygame.draw.line(icono, (249, 235, 211, 185), (143, 58), (169, 48), 4)
    pygame.draw.line(icono, (135, 105, 83, 150), (219, 61), (247, 91), 3)

    for reflejar in (False, True):
        espejo = lambda puntos: [
            (tam - x if reflejar else x, y) for x, y in puntos
        ]
        ceja = espejo(
            ((98, 120), (112, 99), (138, 92), (160, 102), (169, 116),
             (157, 125), (132, 119), (111, 135))
        )
        pygame.draw.polygon(icono, sombra_hueso, ceja)
        pygame.draw.lines(
            icono, luz_hueso, False,
            espejo(((101, 117), (117, 102), (140, 99), (158, 108))),
            5,
        )
        cuenca = espejo(
            ((105, 125), (119, 111), (141, 108), (158, 118), (162, 137),
             (151, 154), (131, 160), (113, 151), (102, 138))
        )
        pygame.draw.polygon(icono, contorno, cuenca)
        pygame.draw.ellipse(
            icono,
            (20, 12, 16, 255),
            pygame.Rect(114 if not reflejar else 204, 120, 35, 29),
        )
        pómulo = espejo(
            ((101, 155), (119, 163), (143, 166), (158, 178), (142, 188),
             (119, 181), (105, 171))
        )
        pygame.draw.polygon(icono, sombra_hueso, pómulo)
        pygame.draw.lines(
            icono, luz_hueso, False,
            espejo(((103, 158), (123, 166), (145, 169))), 4,
        )

    pygame.draw.polygon(
        icono,
        (34, 20, 22, 255),
        ((180, 154), (163, 187), (169, 201), (191, 201), (197, 187)),
    )
    pygame.draw.line(icono, (119, 88, 70, 255), (178, 160), (171, 188), 3)
    pygame.draw.line(icono, (244, 229, 200, 190), (177, 86), (178, 120), 3)

    mandibula = (
        (113, 180), (247, 180), (247, 209), (237, 236), (219, 254),
        (199, 266), (180, 272), (161, 266), (141, 254), (123, 236),
        (113, 209),
    )
    pygame.draw.polygon(icono, contorno, mandibula)
    pygame.draw.polygon(
        icono,
        (190, 170, 143, 255),
        ((120, 187), (240, 187), (239, 209), (230, 233), (214, 249),
         (197, 260), (180, 265), (163, 260), (146, 249), (130, 233),
         (121, 209)),
    )
    pygame.draw.polygon(
        icono,
        (38, 21, 22, 255),
        ((132, 194), (228, 194), (225, 228), (210, 239), (150, 239),
         (135, 228)),
    )

    for indice, x in enumerate(range(139, 218, 13)):
        altura = 23 if indice in (1, 5) else 27
        diente = ((x, 197), (x + 10, 197), (x + 9, 197 + altura), (x + 2, 197 + altura))
        pygame.draw.polygon(icono, (239, 225, 198, 255), diente)
        pygame.draw.lines(icono, (110, 82, 68, 230), False, diente, 2)

    for indice, x in enumerate(range(146, 210, 16)):
        altura = 13 if indice in (0, 3) else 16
        diente = ((x, 238), (x + 11, 238), (x + 10, 238 - altura), (x + 1, 238 - altura))
        pygame.draw.polygon(icono, (207, 190, 163, 255), diente)
        pygame.draw.lines(icono, (92, 67, 57, 220), False, diente, 2)

    pygame.draw.line(icono, (92, 66, 57, 255), (126, 226), (145, 244), 3)
    pygame.draw.line(icono, (92, 66, 57, 255), (234, 226), (215, 244), 3)
    pygame.draw.lines(
        icono, (125, 91, 72, 220), False,
        ((139, 68), (128, 83), (134, 92), (125, 103)), 3,
    )
    pygame.draw.lines(
        icono, (125, 91, 72, 190), False,
        ((239, 106), (229, 115), (235, 124)), 3,
    )
    for x, y, radio in ((116, 188, 3), (126, 194, 2), (237, 188, 3), (228, 194, 2)):
        pygame.draw.circle(icono, (115, 83, 67, 255), (x, y), radio)

    return icono


# ----------------------------------------------------------------------------
# Menú de pausa
# ----------------------------------------------------------------------------
class _MenuPausa:
    def __init__(self, screen, menu_muerte=False):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.rec = _obtener_recursos()
        self.rng = random.Random()
        self.menu_muerte = menu_muerte
        self.opciones = (
            ("Retry", "Return to menu", "Exit game")
            if menu_muerte
            else _OPTIONS
        )
        self.acciones = ("retry", "menu", "exit") if menu_muerte else _ACCIONES
        self.acentos = (
            ((232, 70, 56), (222, 140, 78), (178, 62, 54))
            if menu_muerte
            else _ACENTOS
        )

        # Estado
        self.fase = "entrada"        # entrada -> reposo -> salida -> fin
        self.t_fase = 0.0
        self.t_total = 0.0
        self.k = 0.0                 # visibilidad del fondo (veladura, blur, viñeta)
        self.k_out = 1.0             # visibilidad de la interfaz al salir
        self.k0 = 1.0
        self.seleccion = 0
        self.hover = [1.0, 0.0, 0.0]
        self.accion = None
        self.definitiva = False
        self.salida_ms = DURACION_SALIDA_REANUDAR_MS
        self.flash = 0.0
        self.sacudida = 7.0
        self.brasas = []
        self.ondas = [{"t": 0.0}, {"t": -430.0}]
        self.glitch_hasta = 0.0
        self.proximo_glitch = 3200.0

        # Audio / teclado
        self.audio = pygame.mixer.get_init() is not None
        self.musica = False
        self.vol_musica = 1.0
        self.canal_sonido_pausa = None
        self.teclas_previas = self._teclas_presionadas()

        # Fondo
        self.snapshot = screen.copy()
        self.fondo_borroso = _desenfocar(self.snapshot)
        self.velo = pygame.Surface((self.W, self.H))
        self.velo.fill((8, 3, 10))
        self.negro = pygame.Surface((self.W, self.H))
        self.negro.fill((0, 0, 0))
        self.destello = pygame.Surface((self.W, self.H))
        self.destello.fill((255, 226, 190))
        self.vineta = _vineta(self.W, self.H)
        self.capa_aditiva = pygame.Surface((self.W, self.H))

        self._calcular_layout()
        self._preparar_runa()
        self._preparar_textos()

    # ------------------------------------------------------------------ layout
    def _calcular_layout(self):
        W, H = self.W, self.H
        self.cx = W // 2
        self.btn_h = int(_clamp(H * 0.07, 40, 60))
        self.btn_gap = 10 if H < 600 else 12
        self.btn_w = int(_clamp(W * 0.34, 300, 470))
        total = 3 * self.btn_h + 2 * self.btn_gap
        pie = 40
        self.btn_top = H - pie - total
        self.rects = [
            pygame.Rect(
                self.cx - self.btn_w // 2,
                self.btn_top + i * (self.btn_h + self.btn_gap),
                self.btn_w,
                self.btn_h,
            )
            for i in range(3)
        ]
        self.titulo_y = int(H * 0.085)
        self.subtitulo_y = int(H * 0.14)
        runa_top = int(H * 0.185)
        self.runa_tam = max(120, int(min(H * 0.46, W * 0.5, self.btn_top - 12 - runa_top)))
        self.runa_centro = (self.cx, runa_top + self.runa_tam // 2)

    def _preparar_runa(self):
        tam = self.runa_tam

        def escalar(frames):
            pares = []
            for original in frames:
                frame = _escalar_frame(original, tam)
                pares.append((frame, _brillo_de_frame(frame, tam)))
            return pares

        self.runa_idle = escalar(self.rec.runa_idle)
        self.runa_entrada = escalar(self.rec.runa_entrada)
        self.runa_salida = escalar(self.rec.runa_salida)
        self.calavera = _crear_calavera()
        lado = int(tam * 2.7)
        self.resplandor_fondo = _gradiente_radial_alfa(lado, (170, 30, 20), 150, 1.7)

    def _preparar_textos(self):
        fuente_titulo = _fuente("Georgia", max(36, min(54, self.H // 13)))
        self.letras = []
        texto = "YOU DIED" if self.menu_muerte else "PAUSED"
        sep = max(6, fuente_titulo.size("A")[0] // 5)
        anchos = [fuente_titulo.size(c)[0] for c in texto]
        total = sum(anchos) + sep * (len(texto) - 1)
        x = self.cx - total // 2
        for letra, ancho in zip(texto, anchos):
            self.letras.append(
                (
                    fuente_titulo.render(letra, True, (240, 218, 186)),
                    fuente_titulo.render(letra, True, (128, 26, 22)),
                    x,
                )
            )
            x += ancho + sep
        fuente_sub = _fuente("Arial", max(14, self.H // 42))
        texto_subtitulo = (
            "THE END IS ONLY THE BEGINNING"
            if self.menu_muerte
            else "THE INVASION WAITS FOR NO ONE"
        )
        self.subtitulo = fuente_sub.render(
            texto_subtitulo, True, (184, 88, 70)
        )
        self.fuente_opcion = _fuente("Georgia", max(21, self.H // 29))
        fuente_pie = _fuente("Arial", max(12, self.H // 56))
        self.pie = fuente_pie.render(
            (
                "SELECT   \u2191  /  \u2193        CONFIRM   ENTER"
                if self.menu_muerte
                else "SELECT   \u2191  /  \u2193        CONFIRM   ENTER        RESUME   ESC"
            ),
            True,
            (150, 120, 104),
        )

    # ------------------------------------------------------------------- audio
    @staticmethod
    def _teclas_presionadas():
        presionadas = []
        try:
            estado = pygame.key.get_pressed()
            for nombre, valor in vars(pygame).items():
                if nombre.startswith("K_") and isinstance(valor, int):
                    try:
                        if estado[valor]:
                            presionadas.append(valor)
                    except (IndexError, KeyError, TypeError, pygame.error):
                        continue
        except pygame.error:
            pass
        return presionadas

    def _iniciar_audio(self):
        if not self.audio:
            return
        try:
            self.musica = pygame.mixer.music.get_busy()
            self.vol_musica = pygame.mixer.music.get_volume()
            pygame.mixer.pause()          # congela los sfx del nivel
        except pygame.error:
            self.audio = False
            return
        _tocar(self.rec.sonido_seleccion)
        self.canal_sonido_pausa = _tocar(self.rec.sonido_pausa, loops=-1)

    def _aplicar_volumen_musica(self):
        if not (self.audio and self.musica):
            return
        try:
            if self.fase == "salida" and self.definitiva:
                p = _clamp(self.t_fase / self.salida_ms)
                factor = VOLUMEN_MUSICA_EN_PAUSA * (1.0 - _suave(p))
            else:
                factor = 1.0 - (1.0 - VOLUMEN_MUSICA_EN_PAUSA) * self.k
            pygame.mixer.music.set_volume(_clamp(self.vol_musica * factor))
        except pygame.error:
            pass

    def liberar(self):
        """Deja audio y eventos limpios, tanto al reanudar como al salir."""
        saliendo = self.accion in ("menu", "exit", "retry")
        if self.audio:
            try:
                if saliendo:
                    pygame.mixer.stop()
                    if self.musica:
                        pygame.mixer.music.stop()
                else:
                    pygame.mixer.unpause()
                if self.musica:
                    pygame.mixer.music.set_volume(self.vol_musica)
            except pygame.error:
                pass
        if not saliendo:
            self._reponer_teclas()

    def _reponer_teclas(self):
        """Los KEYUP ocurridos durante la pausa se pierden: los reponemos."""
        try:
            ahora = pygame.key.get_pressed()
            for tecla in self.teclas_previas:
                if not ahora[tecla]:
                    pygame.event.post(
                        pygame.event.Event(pygame.KEYUP, key=tecla, mod=0, unicode="", scancode=0)
                    )
        except (IndexError, KeyError, TypeError, pygame.error):
            pass

    # ----------------------------------------------------------------- entrada
    def _seleccionar(self, indice):
        if indice != self.seleccion:
            self.seleccion = indice
            _tocar(self.rec.tick)

    def _pedir(self, accion, indice=None):
        if self.fase == "salida":
            if accion == "exit" and not self.definitiva:
                self.accion = "exit"
                self.definitiva = True
                self.salida_ms = DURACION_SALIDA_DEFINITIVA_MS
            return
        if indice is not None:
            self.seleccion = indice
        self.accion = accion
        self.definitiva = accion in ("menu", "exit") or (
            self.menu_muerte and accion == "retry"
        )
        self.salida_ms = (
            DURACION_SALIDA_DEFINITIVA_MS if self.definitiva else DURACION_SALIDA_REANUDAR_MS
        )
        self.k0 = self.k
        self.fase = "salida"
        self.t_fase = 0.0
        self.flash = 1.0
        self.sacudida = 4.0
        self.ondas.append({"t": 0.0})
        if self.audio:
            if self.canal_sonido_pausa is not None:
                try:
                    self.canal_sonido_pausa.stop()
                except pygame.error:
                    pass
                self.canal_sonido_pausa = None
            _tocar(self.rec.sonido_seleccion)
        self._rafaga(36, self.runa_centro, 90, 380)

    def _procesar_eventos(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self._pedir("exit")
                continue
            if self.fase == "salida":
                continue
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if self.menu_muerte:
                        self._pedir("menu", 1)
                    else:
                        self._pedir("resume", 0)
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    self._seleccionar((self.seleccion - 1) % len(self.opciones))
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self._seleccionar((self.seleccion + 1) % len(self.opciones))
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self._pedir(self.acciones[self.seleccion], self.seleccion)
            elif ev.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self.rects):
                    if rect.collidepoint(ev.pos):
                        self._seleccionar(i)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, rect in enumerate(self.rects):
                    if rect.collidepoint(ev.pos):
                        self._pedir(self.acciones[i], i)
                        break

    # -------------------------------------------------------------- simulación
    def _rafaga(self, cantidad, centro, vmin, vmax):
        for _ in range(cantidad):
            ang = self.rng.random() * math.tau
            vel = self.rng.uniform(vmin, vmax)
            vida = self.rng.uniform(0.6, 1.5)
            self.brasas.append(
                [centro[0], centro[1], math.cos(ang) * vel, math.sin(ang) * vel,
                 self.rng.choice((1, 2, 2, 3)), vida, vida, self.rng.random() * math.tau, True]
            )

    def _actualizar_brasas(self, dt):
        s = dt / 1000.0
        if len(self.brasas) < 80 and self.rng.random() < 0.7 * max(self.k, 0.2):
            vida = self.rng.uniform(4.0, 9.0)
            self.brasas.append(
                [self.rng.uniform(0, self.W), self.H + 4, self.rng.uniform(-8, 8),
                 -self.rng.uniform(22, 70), self.rng.choice((1, 1, 2, 3)), vida, vida,
                 self.rng.random() * math.tau, False]
            )
        vivas = []
        for p in self.brasas:
            if p[8]:  # chispas de ráfaga: frenan
                p[2] *= 1.0 - min(1.0, 2.2 * s)
                p[3] *= 1.0 - min(1.0, 2.2 * s)
            else:
                p[2] += math.sin(self.t_total / 700.0 + p[7]) * 6 * s
            p[0] += p[2] * s
            p[1] += p[3] * s
            p[5] -= s
            if p[5] > 0 and -12 < p[1] < self.H + 12:
                vivas.append(p)
        self.brasas = vivas

    def _actualizar(self, dt):
        self.t_total += dt
        self.t_fase += dt
        self.sacudida = max(0.0, self.sacudida - dt * 0.03)
        self.flash = max(0.0, self.flash - dt / 380.0)
        objetivo = lambda i: 1.0 if i == self.seleccion else 0.0  # noqa: E731
        for i in range(3):
            self.hover[i] += (objetivo(i) - self.hover[i]) * min(1.0, dt / 85.0)

        if self.fase == "entrada":
            self.k = _ease_out(self.t_fase / DURACION_ENTRADA_MS)
            self.k_out = 1.0
            if self.t_fase >= DURACION_ENTRADA_MS:
                self.fase, self.t_fase, self.k = "reposo", 0.0, 1.0
        elif self.fase == "reposo":
            self.k = self.k_out = 1.0
            if self.t_total >= self.proximo_glitch:
                self.glitch_hasta = self.t_total + 110
                self.proximo_glitch = self.t_total + self.rng.uniform(2800, 5200)
        elif self.fase == "salida":
            p = _clamp(self.t_fase / self.salida_ms)
            self.k = self.k0 if self.definitiva else self.k0 * (1.0 - _suave(p))
            self.k_out = 1.0 - _suave(_clamp(p * 1.25))
            if p >= 1.0:
                self.fase = "fin"

        for onda in self.ondas:
            onda["t"] += dt
        self.ondas = [o for o in self.ondas if o["t"] < 1500]
        self._actualizar_brasas(dt)
        self._aplicar_volumen_musica()

    # ------------------------------------------------------------------ dibujo
    def _estado_runa(self, ts):
        """Devuelve (frame, brillo_surf, escala, alfa, intensidad_brillo)."""
        ms = self.rec.frame_ms
        if self.fase == "entrada":
            t = self.t_fase
            if self.runa_entrada:
                indice = int(_clamp(t / DURACION_ENTRADA_MS) * len(self.runa_entrada))
                par = self.runa_entrada[min(len(self.runa_entrada) - 1, indice)]
            else:
                par = self.runa_idle[0]
            escala = _lerp(0.62, 1.0, _ease_out_back(t / DURACION_ENTRADA_MS))
            return par, escala, int(255 * _clamp(t / 260.0)), 0.55 + 0.45 * self.k
        if self.fase == "salida":
            p = _clamp(self.t_fase / self.salida_ms)
            if self.runa_salida:
                indice = int(p * len(self.runa_salida))
                par = self.runa_salida[min(len(self.runa_salida) - 1, indice)]
            else:
                par = self.runa_idle[int(self.t_total / ms) % len(self.runa_idle)]
            if self.definitiva:
                escala = 1.0 - 0.22 * _ease_in(p)
            else:
                escala = 1.0 + 0.14 * _ease_out(p)
            return par, escala, int(255 * (1.0 - _suave(p))), 1.0 + self.flash * 0.8
        par = self.runa_idle[int(self.t_fase / ms) % len(self.runa_idle)]
        escala = 1.0 + 0.012 * math.sin(ts * 1.9)
        return par, escala, 255, 0.72 + 0.28 * math.sin(ts * 2.2) + self.flash * 0.8

    def _dibujar_fondo(self):
        s = self.screen
        ox = oy = 0
        if self.sacudida > 0.5:
            a = int(self.sacudida)
            ox, oy = self.rng.randint(-a, a), self.rng.randint(-a, a)
        s.fill((0, 0, 0))
        s.blit(self.snapshot, (ox, oy))
        if self.k > 0.003:
            self.fondo_borroso.set_alpha(int(255 * _clamp(self.k * 1.5)))
            s.blit(self.fondo_borroso, (ox, oy))
            self.velo.set_alpha(int(212 * self.k))
            s.blit(self.velo, (0, 0))
            self.vineta.set_alpha(int(255 * self.k))
            s.blit(self.vineta, (0, 0))

    def _dibujar_columnas(self, ts):
        if self.W < 900 or self.k <= 0.01:
            return
        glifos = self.rec.glifos
        paso = 58
        aparece = _suave((self.t_total - 300) / 700.0) * self.k_out
        for lado, xf, vel in ((0, 0.085, 13.0), (1, 0.915, -13.0), (2, 0.155, -7.0), (3, 0.845, 7.0)):
            x = int(self.W * xf)
            desplaz = ts * vel
            base_j = int(math.floor(desplaz / paso))
            resto = desplaz - base_j * paso
            tenue = 0.55 if lado >= 2 else 1.0
            for j in range(self.H // paso + 3):
                y = int(j * paso + resto - paso)
                env = math.sin(math.pi * _clamp(y / self.H)) ** 1.5
                parpadeo = 0.6 + 0.4 * math.sin(ts * 1.7 + j * 1.3 + lado * 2.1)
                alfa = int(150 * env * parpadeo * aparece * tenue)
                if alfa <= 4:
                    continue
                glifo = glifos[(j - base_j + lado * 3) % len(glifos)]
                glifo.set_alpha(alfa)
                self.screen.blit(glifo, (x - glifo.get_width() // 2, y))

    def _dibujar_brasas(self):
        for p in self.brasas:
            f = _clamp(p[5] / p[6])
            if p[8]:
                color = (255, int(150 + 100 * f), int(60 + 90 * f))
            else:
                color = (int(120 + 70 * f), int(20 + 40 * f), int(14 + 12 * f))
            color = _escalar_color(color, (0.35 + 0.65 * f) * self.k_out)
            pygame.draw.circle(self.screen, color, (int(p[0]), int(p[1])), p[4])

    def _dibujar_ondas(self):
        if not self.ondas:
            return
        capa = self.capa_aditiva
        capa.fill((0, 0, 0))
        cx, cy = self.runa_centro
        maximo = max(self.W, self.H) * 0.62
        dibujada = False
        for onda in self.ondas:
            if onda["t"] <= 0:
                continue
            p = onda["t"] / 1100.0
            if p >= 1.0:
                continue
            radio = int(_lerp(self.runa_tam * 0.25, maximo, _ease_out(p)))
            color = _escalar_color((255, 120, 62), (1.0 - p) ** 1.6)
            pygame.draw.circle(capa, color, (cx, cy), radio, max(1, int(7 * (1.0 - p))))
            dibujada = True
        if dibujada:
            self.screen.blit(capa, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _dibujar_halos(self, ts, vis):
        cx, cy = self.runa_centro
        r = self.runa_tam / 2
        for radio_f, vel, marcas, color in (
            (1.12, 0.35, 48, (150, 42, 32)),
            (1.23, -0.22, 72, (112, 34, 30)),
            (1.35, 0.12, 28, (84, 26, 26)),
        ):
            radio = int(r * radio_f * (0.92 + 0.08 * vis))
            col = _escalar_color(color, vis)
            pygame.draw.circle(self.screen, col, (cx, cy), radio, 1)
            base = ts * vel
            for m in range(marcas):
                ang = base + m * math.tau / marcas
                largo = 9 if m % 6 == 0 else 3
                ca, sa = math.cos(ang), math.sin(ang)
                pygame.draw.line(
                    self.screen,
                    col,
                    (cx + ca * radio, cy + sa * radio),
                    (cx + ca * (radio + largo), cy + sa * (radio + largo)),
                    1,
                )
        # arcos brillantes que orbitan
        pulso = 0.6 + 0.4 * math.sin(ts * 2.6)
        col_arco = _escalar_color((236, 150, 78), vis * pulso)
        radio = int(r * 1.12 * (0.92 + 0.08 * vis))
        caja = pygame.Rect(0, 0, radio * 2, radio * 2)
        caja.center = (cx, cy)
        for desfase in (0.0, math.pi):
            ini = ts * 0.9 + desfase
            pygame.draw.arc(self.screen, col_arco, caja, ini, ini + 0.7, 2)

    def _dibujar_runa(self, ts):
        par, escala, alfa, brillo = self._estado_runa(ts)
        frame, resplandor = par
        cx, cy = self.runa_centro
        vis = _clamp(alfa / 255.0)
        if vis <= 0.01:
            return

        # resplandor rojizo de fondo
        self.resplandor_fondo.set_alpha(int(255 * vis * _clamp(0.55 + 0.45 * brillo, 0, 1)))
        self.screen.blit(self.resplandor_fondo, self.resplandor_fondo.get_rect(center=(cx, cy)))

        self._dibujar_halos(ts, vis)

        if self.menu_muerte:
            tam = max(72, int(self.runa_tam * escala * 0.72))
            pulso = 0.5 + 0.5 * math.sin(ts * 3.4)
            icono = self.calavera.copy()
            brillo_ojos = pygame.Surface(icono.get_size(), pygame.SRCALPHA)
            alpha_ojos = int(35 + 55 * pulso)
            pygame.draw.ellipse(
                brillo_ojos, (255, 73, 39, alpha_ojos), (126, 132, 20, 12)
            )
            pygame.draw.ellipse(
                brillo_ojos, (255, 73, 39, alpha_ojos), (214, 132, 20, 12)
            )
            pygame.draw.circle(
                brillo_ojos, (255, 174, 105, min(190, alpha_ojos + 75)), (136, 138), 3
            )
            pygame.draw.circle(
                brillo_ojos, (255, 174, 105, min(190, alpha_ojos + 75)), (224, 138), 3
            )
            icono.blit(brillo_ojos, (0, 0))
            icono = pygame.transform.smoothscale(icono, (tam, tam))
            icono.set_alpha(alfa)
            self.screen.blit(icono, icono.get_rect(center=(cx, cy)))
            return

        # brillo aditivo del propio frame
        intensidad = _clamp(brillo * 0.55 * vis, 0.0, 1.0)
        g = resplandor
        if abs(escala - 1.0) > 0.004:
            lado = max(8, int(g.get_width() * escala))
            g = pygame.transform.smoothscale(g, (lado, lado))
        v = int(255 * intensidad)
        g = g.copy()
        g.fill((v, int(v * 0.72), int(v * 0.52)), special_flags=pygame.BLEND_RGB_MULT)
        self.screen.blit(g, g.get_rect(center=(cx, cy)), special_flags=pygame.BLEND_RGB_ADD)

        # frame de la runa
        if abs(escala - 1.0) > 0.004:
            lado = max(8, int(self.runa_tam * escala))
            frame = pygame.transform.smoothscale(frame, (lado, lado))
        else:
            frame = frame.copy()
        frame.set_alpha(alfa)
        self.screen.blit(frame, frame.get_rect(center=(cx, cy)))

    def _dibujar_titulo(self, ts):
        k = self.k_out
        glitch = self.t_total < self.glitch_hasta
        for i, (letra, sombra, x) in enumerate(self.letras):
            p = _ease_out((self.t_total - (350 + i * 75)) / 380.0)
            if p <= 0.0 or k <= 0.0:
                continue
            alfa = int(255 * p * k)
            y = self.titulo_y - letra.get_height() // 2 + int((1.0 - p) * 18)
            jx = self.rng.randint(-3, 3) if glitch else 0
            sombra.set_alpha(int(alfa * 0.85))
            letra.set_alpha(alfa)
            if glitch:
                self.screen.blit(sombra, (x + jx + 3, y))
            self.screen.blit(sombra, (x + jx, y + 3))
            self.screen.blit(letra, (x + jx, y))

        p = _ease_out((self.t_total - 800) / 500.0)
        if p > 0.0 and k > 0.0:
            self.subtitulo.set_alpha(int(255 * p * k))
            self.screen.blit(
                self.subtitulo, self.subtitulo.get_rect(center=(self.cx, self.subtitulo_y))
            )
        p = _ease_out((self.t_total - 950) / 600.0)
        if p > 0.0 and k > 0.0:
            semiancho = int(min(self.W * 0.26, 300) * p)
            y = self.subtitulo_y + 22
            color = _escalar_color((150, 62, 46), k)
            pygame.draw.line(self.screen, color, (self.cx - semiancho, y), (self.cx - 8, y), 1)
            pygame.draw.line(self.screen, color, (self.cx + 8, y), (self.cx + semiancho, y), 1)
            pygame.draw.polygon(
                self.screen,
                _escalar_color((214, 164, 88), k),
                ((self.cx, y - 5), (self.cx + 5, y), (self.cx, y + 5), (self.cx - 5, y)),
                1,
            )

    def _dibujar_boton(self, i, ts):
        rect = self.rects[i]
        p_in = _clamp((self.t_total - (380 + i * 120)) / 520.0)
        if p_in <= 0.0 or self.k_out <= 0.0:
            return
        lado = -1 if i % 2 == 0 else 1
        e = _ease_out_back(p_in)
        desplaz = int(lado * (1.0 - e) * self.W * 0.22 + lado * (1.0 - self.k_out) * self.W * 0.10)
        alfa_total = _clamp(p_in * 1.4) * self.k_out
        hover = self.hover[i]
        acento = self.acentos[i]

        pad = 14
        w, h = rect.w, rect.h
        surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        r = pygame.Rect(pad, pad, w, h)

        pygame.draw.rect(surf, (0, 0, 0, 120), r.move(0, 5), border_radius=6)
        base = _mezcla((24, 16, 21), _mezcla((66, 19, 23), (80, 22, 20), 0.5 if i == 2 else 0.0), hover)
        pygame.draw.rect(surf, (*base, 238), r, border_radius=6)

        if hover > 0.03:
            franja = pygame.Surface((w, h), pygame.SRCALPHA)
            x0 = int(((ts * 0.55 + i * 0.3) % 1.0) * (w + h * 2)) - h
            pygame.draw.polygon(
                franja,
                (255, 224, 176, int(44 * hover)),
                ((x0, 0), (x0 + 26, 0), (x0 + 26 - h // 2, h), (x0 - h // 2, h)),
            )
            surf.blit(franja, r.topleft)

        pulso = 0.5 + 0.5 * math.sin(ts * 3.2 + i)
        borde = _mezcla((104, 58, 50), _mezcla(acento, (255, 236, 200), pulso * 0.45), hover)
        pygame.draw.rect(surf, (*borde, 255), r, 2 if hover > 0.5 else 1, border_radius=6)
        if hover > 0.03:
            pygame.draw.rect(
                surf, (*_mezcla(base, (197, 142, 73), 0.55 * hover), 238), r.inflate(-9, -9), 1, border_radius=4
            )
            # esquinas ornamentales
            l = int(10 + 4 * pulso)
            col = (*_mezcla(base, acento, hover), 255)
            for sx, sy in ((r.left, r.top), (r.right - 1, r.top), (r.left, r.bottom - 1), (r.right - 1, r.bottom - 1)):
                dx = 1 if sx == r.left else -1
                dy = 1 if sy == r.top else -1
                pygame.draw.line(surf, col, (sx, sy), (sx + dx * l, sy), 2)
                pygame.draw.line(surf, col, (sx, sy), (sx, sy + dy * l), 2)

            # marcadores animados
            ax = r.left + 20 + int(3 * math.sin(ts * 5.0))
            tam = 8 * hover
            pygame.draw.polygon(
                surf,
                (*acento, 255),
                ((ax, r.centery), (ax + tam * 1.4, r.centery - tam), (ax + tam * 1.4, r.centery + tam)),
            )
            bx = r.right - 22 - int(3 * math.sin(ts * 5.0))
            pygame.draw.polygon(
                surf,
                (*acento, 255),
                ((bx - 7 * hover, r.centery), (bx, r.centery - 7 * hover),
                 (bx + 7 * hover, r.centery), (bx, r.centery + 7 * hover)),
                1,
            )

        color_texto = _mezcla((176, 164, 156), (255, 228, 186), hover)
        if i == 2:
            color_texto = _mezcla((176, 164, 156), (255, 190, 170), hover)
        etiqueta = self.fuente_opcion.render(self.opciones[i], True, color_texto)
        pos = etiqueta.get_rect(center=(r.centerx + int(6 * hover), r.centery))
        if hover > 0.05:
            parpadeo = 0.65 + 0.35 * math.sin(ts * 31.0)
            brillo = self.fuente_opcion.render(
                self.opciones[i], True, (255, 44, 30)
            )
            brillo.set_alpha(int(110 * hover * parpadeo))
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                surf.blit(brillo, pos.move(dx, dy))
        surf.blit(etiqueta, pos)

        if self.flash > 0.0 and i == self.seleccion:
            velo_flash = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(
                velo_flash, (255, 240, 210, int(210 * self.flash)), velo_flash.get_rect(), border_radius=6
            )
            surf.blit(velo_flash, r.topleft)
            desplaz += int(self.rng.randint(-3, 3) * self.flash)

        surf.set_alpha(int(255 * alfa_total))
        self.screen.blit(surf, (rect.x - pad + desplaz, rect.y - pad))

    def _dibujar(self):
        ts = self.t_total / 1000.0
        self._dibujar_fondo()
        self._dibujar_columnas(ts)
        self._dibujar_brasas()
        self._dibujar_ondas()
        self._dibujar_runa(ts)
        self._dibujar_titulo(ts)
        for i in range(3):
            self._dibujar_boton(i, ts)

        p = _suave((self.t_total - 1000) / 500.0) * self.k_out
        if p > 0.01:
            self.pie.set_alpha(int(255 * p))
            self.screen.blit(self.pie, self.pie.get_rect(center=(self.cx, self.H - 22)))

        if self.flash > 0.0:
            self.destello.set_alpha(int(70 * self.flash))
            self.screen.blit(self.destello, (0, 0))
        if self.fase == "salida" and self.definitiva:
            p = _clamp(self.t_fase / self.salida_ms)
            self.negro.set_alpha(int(255 * _ease_in(p)))
            self.screen.blit(self.negro, (0, 0))

    # -------------------------------------------------------------------- bucle
    def ejecutar(self):
        reloj = pygame.time.Clock()
        self._iniciar_audio()
        self._rafaga(26, self.runa_centro, 120, 420)
        while self.fase != "fin":
            dt = min(50, reloj.tick(60))
            self._procesar_eventos()
            self._actualizar(dt)
            self._dibujar()
            pygame.display.flip()
        return self.accion


def precargar_recursos_pausa():
    """Opcional: carga gifs y campanas al arrancar para que la 1.ª pausa no tenga tirón."""
    try:
        _obtener_recursos()
    except Exception as error:  # noqa: BLE001
        print(f"[PAUSA] No se pudieron precargar los recursos: {error}")


def pausar_juego(screen, devolver_accion=False):
    """Muestra el menú de pausa; las salidas se comunican al lanzador del juego."""
    try:
        menu = _MenuPausa(screen)
    except Exception as error:  # noqa: BLE001 - un fallo visual no debe tumbar el juego
        import traceback

        traceback.print_exc()
        print(f"[PAUSA] No se pudo crear el menú de pausa: {error}")
        return "resume" if devolver_accion else None

    try:
        accion = menu.ejecutar()
    finally:
        menu.liberar()

    if devolver_accion:
        return accion
    if accion == "menu":
        raise SystemExit(RETURN_TO_MENU_EXIT_CODE)
    if accion == "exit":
        raise SystemExit(EXIT_GAME_EXIT_CODE)
    return None


def menu_muerte_juego(screen, devolver_accion=False):
    """Muestra el menú de derrota con la misma presentación que el de pausa."""
    menu = _MenuPausa(screen, menu_muerte=True)
    try:
        accion = menu.ejecutar()
    finally:
        menu.liberar()

    if devolver_accion:
        return accion
    if accion == "retry":
        raise SystemExit(RETRY_LEVEL_EXIT_CODE)
    if accion == "menu":
        raise SystemExit(RETURN_TO_MENU_EXIT_CODE)
    if accion == "exit":
        raise SystemExit(EXIT_GAME_EXIT_CODE)
    return None