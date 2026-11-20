import array
import math
import random
import sys
from pathlib import Path

import pygame

from asset_utils import load_image_or_placeholder


_PAGE_FILES = (
    "Pag_1.png",
    "Pag_2.png",
    "Pag_3.png",
    "Pag_4.png",
    "Pag_5.png",
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
        self.view_rect = pygame.Rect(
            _MARGIN,
            _MARGIN,
            screen_size[0] - _MARGIN * 2,
            screen_size[1] - _MARGIN * 2 - 64,
        )
        self.pages = []
        for filename in _PAGE_FILES:
            path = assets_dir / filename
            image = load_image_or_placeholder(
                path,
                self.view_rect.size,
                alpha=True,
                label=filename,
            )
            scale = min(
                1.0,
                self.view_rect.width / image.get_width(),
                self.view_rect.height / image.get_height(),
            )
            scaled_size = (
                max(1, round(image.get_width() * scale)),
                max(1, round(image.get_height() * scale)),
            )
            self.pages.append(pygame.transform.smoothscale(image, scaled_size))

        self.page_index = 0
        self.scroll_offset = 0.0
        self.scroll_target = 0.0
        self.mode = "page"
        self.transition_from = None
        self.transition_elapsed = 0.0
        self.skip_elapsed = 0.0
        self.pending_action = None
        self.elapsed = 0.0
        self.motes = self._make_motes()
        self.vignette = self._make_vignette()
        self.dust_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.prompt_font = pygame.font.SysFont("Constantia", max(16, screen_size[1] // 44), bold=True)
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

    def _max_scroll(self, page_index=None):
        index = self.page_index if page_index is None else page_index
        return max(0, self.pages[index].get_height() - self.view_rect.height)

    def _render_page(self, scroll_offset=None):
        frame = pygame.Surface(self.screen_size)
        frame.fill((5, 6, 12))
        page = self.pages[self.page_index]
        offset = self.scroll_offset if scroll_offset is None else scroll_offset
        page_rect = page.get_rect(
            center=(
                self.view_rect.centerx,
                self.view_rect.centery - round(offset),
            )
        )
        frame.set_clip(self.view_rect)
        frame.blit(page, page_rect)
        frame.set_clip(None)
        self.image_rect = page_rect
        return frame

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

    def _begin_transition(self):
        self.transition_from = self._render_page()
        self.page_index += 1
        self.scroll_offset = 0.0
        self.scroll_target = 0.0
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
        if self.ambient_channel is not None:
            self.ambient_channel.fadeout(round(_SKIP_FADE_DURATION * 1000))

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self._begin_skip()
            return None
        if self.mode in ("transition", "skipping"):
            return None

        if key in (pygame.K_UP, pygame.K_PAGEUP):
            self.scroll_target = max(
                0.0, self.scroll_target - self.view_rect.height * 0.8
            )
            return None
        if key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
            self.scroll_target = min(
                self._max_scroll(),
                self.scroll_target + self.view_rect.height * 0.8,
            )
            return None

        if key not in (pygame.K_RETURN, pygame.K_SPACE):
            return None

        if self.scroll_offset < self._max_scroll() - 2:
            self.scroll_target = self._max_scroll()
            return None
        if self.page_index < len(self.pages) - 1:
            self._begin_transition()
            return None

        self.stop_audio()
        return "finished"

    def handle_scroll(self, amount):
        if self.mode in ("transition", "skipping"):
            return
        self.scroll_target = max(
            0.0,
            min(
                self._max_scroll(),
                self.scroll_target - amount * self.view_rect.height * 0.18,
            ),
        )

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
            if self.transition_elapsed >= _TRANSITION_DURATION:
                self.mode = "page"
                self.transition_from = None
        elif self.mode == "page":
            progress = min(1.0, elapsed * 8.0)
            self.scroll_offset += (
                self.scroll_target - self.scroll_offset
            ) * progress
            if abs(self.scroll_target - self.scroll_offset) < 0.5:
                self.scroll_offset = self.scroll_target

    def draw(self, surface):
        frame = self._render_page()
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
            prompt_text = (
                "LEER [ENTER / RUEDA]"
                if self.scroll_offset < self._max_scroll() - 2
                else "SIGUIENTE [ENTER]"
            )
            prompt = self.prompt_font.render(
                prompt_text,
                True,
                (round(186 + pulse * 69), round(161 + pulse * 78), round(108 + pulse * 92)),
            )
            prompt_rect = prompt.get_rect(
                bottomright=(surface.get_width() - 24, surface.get_height() - 18)
            )
            backdrop = pygame.Surface(
                (prompt.get_width() + 24, prompt.get_height() + 14),
                pygame.SRCALPHA,
            )
            backdrop.fill((8, 10, 17, 255))
            backdrop_rect = backdrop.get_rect(center=prompt_rect.center)
            surface.blit(backdrop, backdrop_rect)
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
            skip_rect = skip.get_rect(bottomleft=(24, surface.get_height() - 18))
            skip_backdrop_rect = self.skip_backdrop.get_rect(center=skip_rect.center)
            surface.blit(self.skip_backdrop, skip_backdrop_rect)
            surface.blit(skip, skip_rect)
            self.skip_rect = skip_backdrop_rect

            max_scroll = self._max_scroll()
            if max_scroll > 0:
                track = pygame.Rect(
                    self.view_rect.right - 6,
                    self.view_rect.top,
                    4,
                    self.view_rect.height,
                )
                thumb_height = max(
                    22,
                    round(self.view_rect.height ** 2 / self.pages[self.page_index].get_height()),
                )
                thumb_top = self.view_rect.top + round(
                    (self.view_rect.height - thumb_height)
                    * self.scroll_offset
                    / max_scroll
                )
                pygame.draw.rect(surface, (28, 25, 30), track, border_radius=3)
                pygame.draw.rect(
                    surface,
                    (195, 160, 105),
                    (track.x, thumb_top, track.width, thumb_height),
                    border_radius=3,
                )
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
