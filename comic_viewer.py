import array
import math
import random
import sys
from pathlib import Path

import pygame


_PAGE_FILES = (
    ("Pag_1.png", 0.81, 0.91),
    ("Pag_2.png", 0.88, 0.94),
    ("Pag_3.png", 0.94, 0.96),
    ("Pag_4.png", 0.83, 0.96),
    ("Pag_5.png", 0.70, 0.98),
)
_TRANSITION_DURATION = 0.4
_SKIP_FADE_DURATION = 0.36
_MARGIN = 28


def _smoothstep(progress):
    progress = max(0.0, min(1.0, progress))
    return progress * progress * (3.0 - 2.0 * progress)


def _make_pcm_sound(duration, sample_rate, channels, sample_function):
    sample_count = round(sample_rate * duration)
    samples = array.array("h")
    for index in range(sample_count):
        value = round(max(-1.0, min(1.0, sample_function(index / sample_rate))) * 32767)
        for _ in range(channels):
            samples.append(value)
    if sys.byteorder != "little":
        samples.byteswap()
    return pygame.mixer.Sound(buffer=samples.tobytes())


class ComicViewer:
    def __init__(self, screen_size, assets_dir: Path):
        self.screen_size = screen_size
        self.pages = []
        self.prompt_positions = []
        for filename, grid_bottom, prompt_position in _PAGE_FILES:
            path = assets_dir / filename
            if not path.is_file():
                raise FileNotFoundError(f"No se encontró una página del prólogo: {path}")
            image = pygame.image.load(str(path)).convert_alpha()
            panels = (
                self._make_irregular_panels(image)
                if filename == "Pag_5.png"
                else self._make_panels(image, grid_bottom)
            )
            self.pages.append((image, panels))
            self.prompt_positions.append(prompt_position)

        self.page_index = 0
        self.panel_index = 0
        self.mode = "panel"
        self.camera_rect = self.pages[0][1][0]
        self.transition_from = None
        self.transition_start = None
        self.transition_target = None
        self.transition_target_mode = None
        self.transition_elapsed = 0.0
        self.skip_elapsed = 0.0
        self.pending_action = None
        self.elapsed = 0.0
        self.motes = self._make_motes()
        self.vignette = self._make_vignette()
        self.dust_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.prompt_font = pygame.font.SysFont("Constantia", max(16, screen_size[1] // 44), bold=True)
        prompt = self.prompt_font.render("CONTINUAR [ENTER]", True, (255, 255, 255))
        self.prompt_backdrop = pygame.Surface(
            (prompt.get_width() + 24, prompt.get_height() + 14),
            pygame.SRCALPHA,
        )
        self.prompt_backdrop.fill((8, 10, 17, 255))
        skip_prompt = self.prompt_font.render("SALTAR [ESC / CLICK]", True, (255, 255, 255))
        self.skip_backdrop = pygame.Surface(
            (skip_prompt.get_width() + 24, skip_prompt.get_height() + 14),
            pygame.SRCALPHA,
        )
        self.skip_backdrop.fill((8, 10, 17, 255))
        self.skip_rect = None
        self.fade_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.ambient_sound, _ = self._make_audio()
        self.ambient_channel = (
            self.ambient_sound.play(loops=-1) if self.ambient_sound is not None else None
        )
        self.rng = random.Random()
        self.flip_sounds = self._load_flip_sounds()

    @staticmethod
    def _make_panels(image, grid_bottom):
        width, height = image.get_size()
        cell_width = width / 3
        cell_height = height * grid_bottom / 3
        panels = []
        for row in range(3):
            for column in range(3):
                overlap_x = round(cell_width * 0.035)
                overlap_y = round(cell_height * 0.035)
                left = max(0, round(column * cell_width) - overlap_x)
                top = max(0, round(row * cell_height) - overlap_y)
                right = min(width, round((column + 1) * cell_width) + overlap_x)
                bottom = min(
                    round(height * grid_bottom),
                    round((row + 1) * cell_height) + overlap_y,
                )
                panels.append(
                    (
                        float(left),
                        float(top),
                        float(max(1, right - left)),
                        float(max(1, bottom - top)),
                    )
                )
        return panels

    @staticmethod
    def _make_irregular_panels(image):
        width, height = image.get_size()
        grid_bottom = 0.70
        row_edges = (0.0, 0.23, 0.47, grid_bottom)
        rows = (
            ((0.0, 0.62), (0.62, 1.0)),
            ((0.0, 0.38), (0.38, 0.73), (0.73, 1.0)),
            ((0.0, 0.42), (0.42, 0.73), (0.73, 1.0)),
        )
        panels = []
        for row, columns in enumerate(rows):
            top = max(0, round(height * row_edges[row]) - round(height * 0.012))
            bottom = min(
                round(height * grid_bottom),
                round(height * row_edges[row + 1]) + round(height * 0.012),
            )
            for left_fraction, right_fraction in columns:
                left = max(0, round(width * left_fraction) - round(width * 0.012))
                right = min(width, round(width * right_fraction) + round(width * 0.012))
                panels.append(
                    (float(left), float(top), float(right - left), float(bottom - top))
                )
        return panels

    def _make_vignette(self):
        width, height = self.screen_size
        low_size = max(1, width // 8), max(1, height // 8)
        mask = pygame.Surface(low_size, pygame.SRCALPHA)
        center_x, center_y = low_size[0] / 2, low_size[1] / 2
        max_distance = math.hypot(center_x, center_y)
        for x in range(low_size[0]):
            for y in range(low_size[1]):
                distance = math.hypot((x - center_x) * 1.08, y - center_y) / max_distance
                alpha = round(max(0.0, min(128.0, (distance - 0.52) * 270)))
                if alpha:
                    mask.set_at((x, y), (0, 0, 0, alpha))
        return pygame.transform.smoothscale(mask, self.screen_size)

    def _make_motes(self):
        rng = random.Random(4201)
        width, height = self.screen_size
        return [
            [
                rng.uniform(0, width),
                rng.uniform(0, height),
                rng.uniform(-5, 5),
                rng.uniform(-9, -2),
                rng.choice((1, 1, 2)),
                rng.randint(20, 52),
            ]
            for _ in range(24)
        ]

    def _load_flip_sounds(self):
        if not pygame.mixer.get_init():
            return []
        music_dir = Path(__file__).resolve().parent / "musica"
        sounds = []
        for filename in ("page flip.mp3", "page flip-2.mp3"):
            path = music_dir / filename
            try:
                sound = pygame.mixer.Sound(str(path))
            except (pygame.error, OSError) as error:
                print(f"[PRÓLOGO] No se pudo cargar {filename}: {error}")
                continue
            sound.set_volume(0.32)
            sounds.append(sound)
        if not sounds:
            print("[PRÓLOGO] No hay efectos de paso de página disponibles.")
        return sounds

    @staticmethod
    def _make_audio():
        mixer_settings = pygame.mixer.get_init()
        if mixer_settings is None:
            return None, None
        sample_rate, sample_format, channels = mixer_settings
        if sample_format != -16:
            print("[PRÓLOGO] Audio PCM de 16 bits no disponible; se omitirá el audio ambiental.")
            return None, None
        try:
            ambient = _make_pcm_sound(
                2.4,
                sample_rate,
                channels,
                lambda time: (
                    math.sin(2 * math.pi * 52 * time) * 0.035
                    + math.sin(2 * math.pi * 77 * time) * 0.019
                    + math.sin(2 * math.pi * 103 * time) * 0.008
                ),
            )
            ambient.set_volume(0.28)

            return ambient, None
        except pygame.error as error:
            print(f"[PRÓLOGO] No se pudieron preparar los sonidos: {error}")
            return None, None

    def _make_camera_surface(self, rect):
        image, _ = self.pages[self.page_index]
        x, y, width, height = rect
        crop = image.subsurface(
            pygame.Rect(
                round(x),
                round(y),
                max(1, round(width)),
                max(1, round(height)),
            )
        )
        target_width = max(1, self.screen_size[0] - _MARGIN * 2)
        target_height = max(1, self.screen_size[1] - _MARGIN * 2)
        scale = min(target_width / crop.get_width(), target_height / crop.get_height())
        size = (
            max(1, round(crop.get_width() * scale)),
            max(1, round(crop.get_height() * scale)),
        )
        scaled = pygame.transform.smoothscale(crop, size)
        frame = pygame.Surface(self.screen_size)
        frame.fill((5, 6, 12))
        self.image_rect = scaled.get_rect(center=frame.get_rect().center)
        frame.blit(scaled, self.image_rect)
        return frame

    def _begin_transition(self, target, target_mode, next_page=False):
        self.transition_from = self._make_camera_surface(self.camera_rect)
        if next_page:
            self.page_index += 1
            self.panel_index = 0
            image = self.pages[self.page_index][0]
            self.camera_rect = (0.0, 0.0, float(image.get_width()), float(image.get_height()))
        self.transition_start = self.camera_rect
        self.transition_target = target
        self.transition_target_mode = target_mode
        self.transition_elapsed = 0.0
        self.mode = "transition"
        if self.flip_sounds:
            self.rng.choice(self.flip_sounds).play()

    def _begin_skip(self):
        if self.mode == "skipping" or self.pending_action is not None:
            return
        self.mode = "skipping"
        self.skip_elapsed = 0.0
        self.transition_from = None
        self.transition_target = None
        if self.ambient_channel is not None:
            self.ambient_channel.fadeout(round(_SKIP_FADE_DURATION * 1000))

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self._begin_skip()
            return None
        if key not in (pygame.K_RETURN, pygame.K_SPACE) or self.mode == "transition":
            return None

        panels = self.pages[self.page_index][1]
        if self.mode == "panel":
            if self.panel_index < len(panels) - 1:
                self.panel_index += 1
                self._begin_transition(panels[self.panel_index], "panel")
            else:
                image = self.pages[self.page_index][0]
                full_page = (0.0, 0.0, float(image.get_width()), float(image.get_height()))
                self._begin_transition(full_page, "full")
            return None

        if self.page_index < len(self.pages) - 1:
            first_panel = self.pages[self.page_index + 1][1][0]
            self._begin_transition(first_panel, "panel", next_page=True)
            return None

        self.stop_audio()
        return "finished"

    def handle_click(self, position):
        if self.mode != "skipping" and self.skip_rect is not None:
            if self.skip_rect.collidepoint(position):
                self._begin_skip()

    def consume_action(self):
        action = self.pending_action
        self.pending_action = None
        return action

    def update(self, dt):
        elapsed = max(0.0, dt)
        self.elapsed += elapsed
        width, height = self.screen_size
        for mote in self.motes:
            mote[0] = (mote[0] + mote[2] * elapsed) % width
            mote[1] += mote[3] * elapsed
            if mote[1] < 0:
                mote[1] = float(height)

        if self.mode == "skipping":
            self.skip_elapsed += elapsed
            if self.skip_elapsed >= _SKIP_FADE_DURATION:
                self.mode = "done"
                self.stop_audio()
                self.pending_action = "skip"
            return

        if self.mode == "transition":
            self.transition_elapsed += elapsed
            progress = _smoothstep(self.transition_elapsed / _TRANSITION_DURATION)
            target = self.transition_target
            self.camera_rect = tuple(
                current + (destination - current) * progress
                for current, destination in zip(self.transition_start, target)
            )
            if self.transition_elapsed >= _TRANSITION_DURATION:
                self.camera_rect = self.transition_target
                self.mode = self.transition_target_mode
                self.transition_from = None
                self.transition_target = None

    def draw(self, surface):
        frame = self._make_camera_surface(self.camera_rect)
        surface.blit(frame, (0, 0))
        if self.transition_from is not None:
            progress = _smoothstep(self.transition_elapsed / _TRANSITION_DURATION)
            previous = self.transition_from.copy()
            previous.set_alpha(round(255 * (1.0 - progress)))
            surface.blit(previous, (0, 0))

        surface.blit(self.vignette, (0, 0))
        self.dust_surface.fill((0, 0, 0, 0))
        for x, y, _vx, _vy, radius, alpha in self.motes:
            pygame.draw.circle(
                self.dust_surface,
                (221, 193, 139, alpha),
                (round(x), round(y)),
                radius,
            )
        surface.blit(self.dust_surface, (0, 0))

        if self.mode != "skipping":
            pulse = 0.5 + 0.5 * math.sin(self.elapsed * 2.8)
            prompt = self.prompt_font.render(
                "CONTINUAR [ENTER]",
                True,
                (round(186 + pulse * 69), round(161 + pulse * 78), round(108 + pulse * 92)),
            )
            if self.mode == "full":
                prompt_rect = prompt.get_rect(
                    bottomright=(
                        self.image_rect.right - 12,
                        self.image_rect.top
                        + round(self.image_rect.height * self.prompt_positions[self.page_index]),
                    )
                )
            else:
                prompt_rect = prompt.get_rect(
                    bottomright=(surface.get_width() - 24, surface.get_height() - 20)
                )
            backdrop_rect = self.prompt_backdrop.get_rect(center=prompt_rect.center)
            surface.blit(self.prompt_backdrop, backdrop_rect)
            surface.blit(prompt, prompt_rect)

            skip = self.prompt_font.render(
                "SALTAR [ESC / CLICK]",
                True,
                (
                    round(188 + pulse * 48),
                    round(144 + pulse * 50),
                    round(109 + pulse * 38),
                ),
            )
            skip_rect = skip.get_rect(bottomleft=(24, surface.get_height() - 20))
            skip_backdrop_rect = self.skip_backdrop.get_rect(center=skip_rect.center)
            surface.blit(self.skip_backdrop, skip_backdrop_rect)
            surface.blit(skip, skip_rect)
            self.skip_rect = skip_backdrop_rect
        else:
            self.skip_rect = None

        if self.mode == "skipping":
            self.fade_surface.fill(
                (
                    0,
                    0,
                    0,
                    round(255 * _smoothstep(self.skip_elapsed / _SKIP_FADE_DURATION)),
                )
            )
            surface.blit(self.fade_surface, (0, 0))

    def stop_audio(self):
        if self.ambient_channel is not None:
            self.ambient_channel.stop()
            self.ambient_channel = None
