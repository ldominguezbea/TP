import array
import math
import random
import sys
from pathlib import Path

import pygame


RETURN_TO_MENU_EXIT_CODE = 10
EXIT_GAME_EXIT_CODE = 11

_OPTIONS = ("Reanudar", "Volver al menú", "Salir del juego")
_RUNE_ASSETS = (
    Path(__file__).resolve().parent
    / "assets"
    / "sprites"
    / "fondos"
    / "06_ember_forge_wheel"
    / "128x128"
)
_ENTRY_DURATION = 0.55
_UI_FADE_DURATION = 0.36
_EXIT_DURATION = 0.7
_OVERLAY_ALPHA = 208
def _font(family, size, bold=False):
    font_path = pygame.font.match_font(family)
    if font_path:
        font = pygame.font.Font(font_path, size)
        font.set_bold(bold)
        return font
    return pygame.font.SysFont("Georgia", size, bold=bold)


def _draw_rune_symbol(surface, center, size, color, variant):
    cx, cy = center
    half = max(3, size // 2)
    pygame.draw.line(surface, color, (cx, cy - half), (cx, cy + half), 1)
    if variant % 4 == 0:
        pygame.draw.line(surface, color, (cx, cy - half // 2), (cx + half, cy - half), 1)
        pygame.draw.line(surface, color, (cx, cy), (cx - half, cy + half // 2), 1)
    elif variant % 4 == 1:
        pygame.draw.line(surface, color, (cx, cy - half // 2), (cx + half, cy + half // 2), 1)
        pygame.draw.line(surface, color, (cx - half, cy), (cx, cy + half), 1)
    elif variant % 4 == 2:
        pygame.draw.line(surface, color, (cx - half, cy - half // 2), (cx + half, cy - half // 2), 1)
        pygame.draw.line(surface, color, (cx - half, cy + half // 2), (cx + half, cy + half // 2), 1)
    else:
        pygame.draw.line(surface, color, (cx - half, cy - half), (cx + half, cy + half), 1)
        pygame.draw.line(surface, color, (cx + half, cy - half), (cx - half, cy + half), 1)


def _make_fire_sound():
    mixer_settings = pygame.mixer.get_init()
    if mixer_settings is None:
        return None

    sample_rate, sample_format, channels = mixer_settings
    if sample_format != -16:
        print("[PAUSA] El sonido de los botones requiere audio PCM firmado de 16 bits.")
        return None

    duration = 0.16
    sample_count = int(sample_rate * duration)
    rng = random.Random(731)
    samples = array.array("h")
    for index in range(sample_count):
        progress = index / max(1, sample_count - 1)
        envelope = math.sin(math.pi * progress) ** 1.4
        crackle = rng.uniform(-1.0, 1.0) * (0.32 if rng.random() < 0.28 else 0.08)
        tone = math.sin(2 * math.pi * (620 - 390 * progress) * progress * duration) * 0.2
        sample = round(max(-1.0, min(1.0, (crackle + tone) * envelope)) * 32767)
        for _ in range(channels):
            samples.append(sample)

    if sys.byteorder != "little":
        samples.byteswap()
    try:
        sound = pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error as error:
        print(f"[PAUSA] No se pudo crear el sonido de selección: {error}")
        return None
    sound.set_volume(0.13)
    return sound


def _load_strip(path, frame_size=128):
    strip = pygame.image.load(str(path)).convert_alpha()
    if strip.get_width() % frame_size:
        raise ValueError(f"El ancho de la tira de animación no es válido: {path}")
    return [
        strip.subsurface(
            pygame.Rect(x, 0, frame_size, frame_size)
        ).copy()
        for x in range(0, strip.get_width(), frame_size)
    ]


def _prepare_rune_frames(path, rune_size):
    frames = _load_strip(path)
    prepared = []
    for frame in frames:
        scaled = pygame.transform.smoothscale(frame, (rune_size, rune_size))
        halo_size = round(rune_size * 1.18)
        halo = pygame.transform.smoothscale(frame, (halo_size, halo_size))
        prepared.append((scaled, halo))
    return prepared


def _draw_rune(screen, frame_pair, alpha):
    if alpha <= 0:
        return
    frame, halo = frame_pair
    halo.set_alpha(round(alpha * 0.34))
    screen.blit(halo, halo.get_rect(center=screen.get_rect().center))
    frame.set_alpha(round(alpha))
    screen.blit(frame, frame.get_rect(center=screen.get_rect().center))


def _ease(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def _draw_pause_ui(surface, panel, selected, pulse, fonts, rune_pair):
    _width, height = surface.get_size()
    button_width = min(440, panel.width - 72)
    button_height = 62
    button_gap = 14
    buttons_top = panel.centery - 38
    button_rects = [
        pygame.Rect(
            panel.centerx - button_width // 2,
            buttons_top + index * (button_height + button_gap),
            button_width,
            button_height,
        )
        for index in range(len(_OPTIONS))
    ]

    title_font, subtitle_font, option_font, footer_font = fonts[:4]

    def center_text(text, font, color, y):
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(center=(panel.centerx, y)))

    shadow = panel.move(0, 12)
    pygame.draw.rect(surface, (0, 0, 0, 210), shadow, border_radius=8)
    pygame.draw.rect(surface, (25, 17, 26, 255), panel, border_radius=8)
    for y in range(panel.top + 14, panel.bottom - 14, 12):
        color = (37, 25, 35, 255) if (y // 12) % 2 else (30, 21, 31, 255)
        pygame.draw.line(surface, color, (panel.left + 12, y), (panel.right - 12, y), 1)
    pygame.draw.rect(surface, (114, 28, 26), panel, 2, border_radius=8)
    pygame.draw.rect(
        surface,
        (197, 142, 73, 255),
        panel.inflate(-12, -12),
        1,
        border_radius=6,
    )

    rune_colors = (
        (219, 112, 62),
        (213, 176, 88),
        (94, 183, 162),
        (174, 105, 204),
    )
    rune_size = max(12, height // 46)
    for index, x in enumerate(range(panel.left + 30, panel.right - 24, 28)):
        _draw_rune_symbol(
            surface,
            (x, panel.top + 21),
            rune_size,
            rune_colors[index % len(rune_colors)],
            index,
        )
    for y in range(panel.top + 48, panel.bottom - 48, 62):
        variant = y // 62
        _draw_rune_symbol(
            surface,
            (panel.left + 22, y),
            12,
            rune_colors[variant % 4],
            variant,
        )
        _draw_rune_symbol(
            surface,
            (panel.right - 22, y),
            12,
            rune_colors[(variant + 1) % 4],
            variant + 1,
        )
    rune_frame, rune_halo = rune_pair
    pattern_size = min(panel.width // 2, panel.height // 2)
    pattern_rect = pygame.Rect(0, 0, pattern_size, pattern_size)
    pattern_rect.center = (panel.centerx, panel.centery)
    pattern = pygame.transform.smoothscale(rune_frame, pattern_rect.size)
    pattern.set_alpha(35)
    surface.blit(pattern, pattern_rect)
    halo = pygame.transform.smoothscale(rune_halo, (pattern_size + 30, pattern_size + 30))
    halo.set_alpha(18)
    surface.blit(halo, halo.get_rect(center=panel.center))

    crest_y = panel.top + 52
    crest_radius = max(15, min(22, height // 32))
    pygame.draw.circle(surface, (91, 13, 19), (panel.centerx, crest_y), crest_radius + 5)
    pygame.draw.circle(surface, (190, 51, 35), (panel.centerx, crest_y), crest_radius, 2)
    pygame.draw.polygon(
        surface,
        (203, 157, 83),
        (
            (panel.centerx, crest_y - crest_radius + 5),
            (panel.centerx + crest_radius - 5, crest_y),
            (panel.centerx, crest_y + crest_radius - 5),
            (panel.centerx - crest_radius + 5, crest_y),
        ),
        2,
    )
    center_text("PAUSADO", title_font, (238, 215, 184), panel.top + 112)
    center_text(
        "LA INVASIÓN NO ESPERA A NADIE",
        subtitle_font,
        (179, 84, 68),
        panel.top + 157,
    )
    pygame.draw.line(
        surface,
        (103, 44, 37),
        (panel.left + 72, panel.top + 183),
        (panel.right - 72, panel.top + 183),
        1,
    )

    hover_strengths = fonts[-1]
    for index, (label, rect) in enumerate(zip(_OPTIONS, button_rects)):
        strength = hover_strengths[index]
        active = index == selected
        fill = (
            (int(60 + 28 * strength), int(30 + 12 * strength), int(31 + 10 * strength))
            if active
            else (33, 24, 31)
        )
        border = (
            (int(174 + 72 * strength + pulse * 8), int(112 + 65 * strength), int(62 + 18 * strength))
            if active
            else (101, 57, 48)
        )
        pygame.draw.rect(surface, fill, rect, border_radius=5)
        pygame.draw.rect(surface, border, rect, 2 if active else 1, border_radius=5)
        text_color = (
            (int(192 + 63 * strength), int(162 + 69 * strength), int(116 + 67 * strength))
            if active
            else (177, 165, 157)
        )
        label_surface = option_font.render(label, True, text_color)
        if strength > 0.01:
            label_size = (
                round(label_surface.get_width() * (1.0 + 0.08 * strength)),
                round(label_surface.get_height() * (1.0 + 0.08 * strength)),
            )
            label_surface = pygame.transform.smoothscale(label_surface, label_size)
        if strength > 0.05:
            glow_surface = option_font.render(label, True, (255, 119, 43))
            glow_surface.set_alpha(round(55 * strength))
            surface.blit(glow_surface, glow_surface.get_rect(center=rect.center).move(0, 1))
        surface.blit(label_surface, label_surface.get_rect(center=rect.center))

    center_text(
        "NAVEGAR  W / S        CONFIRMAR  ENTER",
        footer_font,
        (145, 117, 101),
        panel.bottom - 27,
    )
    return button_rects


def _load_pause_sound(filename, volume):
    if not pygame.mixer.get_init():
        return None
    path = Path(__file__).resolve().parent / "musica" / filename
    try:
        sound = pygame.mixer.Sound(str(path))
    except (pygame.error, OSError) as error:
        print(f"[PAUSA] No se pudo cargar {filename}: {error}")
        return None
    sound.set_volume(volume)
    return sound


def pausar_juego(screen, devolver_accion=False):
    """Congela el nivel hasta completar la entrada y salida de la pausa."""
    snapshot = screen.copy()
    width, height = screen.get_size()
    clock = pygame.time.Clock()
    selected = 0
    elapsed = 0.0
    exiting_elapsed = None
    requested_action = None
    result = None
    music_was_playing = False
    ambient_channel = None
    hover_strengths = [0.0] * len(_OPTIONS)
    fire_sound = _make_fire_sound()
    previous_selected = selected

    rune_size = max(128, round(min(width, height) * 0.38))
    entry_frames = _prepare_rune_frames(
        _RUNE_ASSETS / "ember_forge_wheel_128x128_activate_strip.png",
        rune_size,
    )
    idle_frames = _prepare_rune_frames(
        _RUNE_ASSETS / "ember_forge_wheel_128x128_idle_strip.png",
        rune_size,
    )
    exit_frames = _prepare_rune_frames(
        _RUNE_ASSETS / "ember_forge_wheel_128x128_dissipate_strip.png",
        rune_size,
    )
    bell = _load_pause_sound("Bell1.mp3", 0.7)
    drone = _load_pause_sound("Bell2.mp3", 0.18)

    panel_width = min(660, int(width * 0.84))
    panel_height = min(540, int(height * 0.86))
    panel = pygame.Rect(
        (width - panel_width) // 2,
        (height - panel_height) // 2,
        panel_width,
        panel_height,
    )
    ui_fonts = (
        _font("Constantia", max(36, min(52, height // 13)), bold=True),
        _font("Constantia", max(15, height // 39), bold=True),
        _font("Constantia", max(22, height // 28), bold=True),
        _font("Constantia", max(12, height // 54), bold=True),
        hover_strengths,
    )
    veil = pygame.Surface((width, height), pygame.SRCALPHA)
    ui_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    if pygame.mixer.get_init():
        music_was_playing = pygame.mixer.music.get_busy()
        if music_was_playing:
            pygame.mixer.music.pause()
    if bell is not None:
        bell.play()

    try:
        while result is None:
            dt = clock.tick(60) / 1000.0
            if exiting_elapsed is None:
                elapsed += dt
            else:
                exiting_elapsed += dt

            screen.blit(snapshot, (0, 0))
            if exiting_elapsed is None:
                entry_progress = _ease(elapsed / _ENTRY_DURATION)
                overlay_alpha = round(_OVERLAY_ALPHA * entry_progress)
                if elapsed < _ENTRY_DURATION:
                    frame_progress = min(1.0, elapsed / _ENTRY_DURATION)
                    frame_index = min(
                        len(entry_frames) - 1,
                        int(frame_progress * len(entry_frames)),
                    )
                    rune_pair = entry_frames[frame_index]
                    rune_alpha = round(255 * entry_progress)
                else:
                    idle_elapsed = elapsed - _ENTRY_DURATION
                    frame_index = int(idle_elapsed / 0.09) % len(idle_frames)
                    rune_pair = idle_frames[frame_index]
                    rune_alpha = 255

                if elapsed >= _ENTRY_DURATION and ambient_channel is None and drone:
                    ambient_channel = drone.play(loops=-1)

                ui_progress = _ease((elapsed - _ENTRY_DURATION) / _UI_FADE_DURATION)
            else:
                exit_progress = _ease(exiting_elapsed / _EXIT_DURATION)
                overlay_alpha = round(_OVERLAY_ALPHA * (1.0 - exit_progress))
                frame_index = min(
                    len(exit_frames) - 1,
                    int(exiting_elapsed / _EXIT_DURATION * len(exit_frames)),
                )
                rune_pair = exit_frames[frame_index]
                rune_alpha = round(255 * (1.0 - exit_progress))
                ui_progress = _ease(
                    max(0.0, (elapsed - _ENTRY_DURATION) / _UI_FADE_DURATION)
                ) * (1.0 - exit_progress)

            veil.fill((8, 3, 10, overlay_alpha))
            screen.blit(veil, (0, 0))
            _draw_rune(screen, rune_pair, rune_alpha)

            ui_surface.fill((0, 0, 0, 0))
            pulse = 0.5 + 0.5 * math.sin(elapsed * 2.4)
            for index in range(len(hover_strengths)):
                target = 1.0 if index == selected else 0.0
                hover_strengths[index] += (target - hover_strengths[index]) * min(1.0, dt * 9.0)
            button_rects = _draw_pause_ui(
                ui_surface,
                panel,
                selected,
                pulse,
                ui_fonts,
                rune_pair,
            )
            ui_surface.set_alpha(round(ui_progress * 255))
            screen.blit(ui_surface, (0, 0))
            pygame.display.flip()

            if exiting_elapsed is None and elapsed >= (
                _ENTRY_DURATION + _UI_FADE_DURATION
            ):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        requested_action = "exit"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            requested_action = "resume"
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            selected = (selected - 1) % len(_OPTIONS)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            selected = (selected + 1) % len(_OPTIONS)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            requested_action = ("resume", "menu", "exit")[selected]
                    elif event.type == pygame.MOUSEMOTION:
                        for index, rect in enumerate(button_rects):
                            if rect.collidepoint(event.pos):
                                selected = index
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for index, rect in enumerate(button_rects):
                            if rect.collidepoint(event.pos):
                                selected = index
                                requested_action = ("resume", "menu", "exit")[index]
                                break
            elif exiting_elapsed is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        requested_action = "exit"

            if selected != previous_selected:
                if fire_sound is not None:
                    fire_sound.play()
                previous_selected = selected

            if requested_action is not None and exiting_elapsed is None:
                exiting_elapsed = 0.0
                if ambient_channel is not None:
                    ambient_channel.stop()
                    ambient_channel = None
                if bell is not None:
                    bell.play()

            if exiting_elapsed is not None and exiting_elapsed >= _EXIT_DURATION:
                result = requested_action
    finally:
        if ambient_channel is not None:
            ambient_channel.stop()
        if music_was_playing and pygame.mixer.get_init():
            pygame.mixer.music.unpause()

    if devolver_accion:
        return result
    if result == "menu":
        raise SystemExit(RETURN_TO_MENU_EXIT_CODE)
    if result == "exit":
        raise SystemExit(EXIT_GAME_EXIT_CODE)
