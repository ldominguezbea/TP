import array
import math
import random
import re
import sys
from pathlib import Path

import pygame


class ControlsBook:
    FRAME_DURATION = 0.095

    def __init__(self, screen_size, hero_assets_dir: Path):
        self.screen_size = screen_size
        self.scale = min(screen_size[0] / 1350, screen_size[1] / 720)
        self.animation_elapsed = 0.0
        self.background = self._make_background()
        self.font_title = pygame.font.SysFont("Georgia", self._px(29), bold=True)
        self.font_body = pygame.font.SysFont("Georgia", self._px(19), bold=True)
        self.font_small = pygame.font.SysFont("Georgia", self._px(15))
        self.font_controls = pygame.font.SysFont("Arial", self._px(16), bold=True)
        self.sounds = self._make_sounds()
        self.animations = self._load_animations(hero_assets_dir)

        width, height = screen_size
        self.book_rect = pygame.Rect(
            round(width * 0.115),
            round(height * 0.105),
            round(width * 0.77),
            round(height * 0.79),
        )
        self.page_gap = self._px(16)
        self.page_width = (
            self.book_rect.width - self._px(34) - self.page_gap
        ) // 2
        self.page_height = self.book_rect.height - self._px(34)
        self.left_page_rect = pygame.Rect(
            self.book_rect.left + self._px(17),
            self.book_rect.top + self._px(17),
            self.page_width,
            self.page_height,
        )
        self.right_page_rect = pygame.Rect(
            self.left_page_rect.right + self.page_gap,
            self.left_page_rect.top,
            self.page_width,
            self.page_height,
        )

    def _px(self, value):
        return max(1, round(value * self.scale))

    def _load_animations(self, assets_dir):
        frame_directories = {
            "run": ("02_run",),
            "jump": ("03_jump_up", "03_jump", "03_jump_down"),
            "roll": ("04_roll",),
            "attack": ("05_1_atk",),
            "special": ("08_sp_atk",),
            "defend": ("09_defend",),
        }
        animations = {}

        def fallback_frames(color=(143, 101, 61), size=(92, 120)):
            surface = pygame.Surface(size, pygame.SRCALPHA)
            rect = surface.get_rect().inflate(-16, -18)
            pygame.draw.rect(surface, color, rect, border_radius=16)
            pygame.draw.line(surface, (228, 199, 120), (rect.centerx, rect.top), (rect.centerx, rect.bottom), 3)
            pygame.draw.line(surface, (228, 199, 120), (rect.left + 12, rect.centery), (rect.right - 12, rect.centery), 2)
            return [surface]

        for animation, directories in frame_directories.items():
            frames = []
            for directory in directories:
                directory_path = assets_dir / directory
                if not directory_path.exists():
                    continue
                frame_paths = list(directory_path.glob("*.png"))
                if not frame_paths:
                    continue
                frame_paths.sort(
                    key=lambda path: int(re.search(r"(\d+)\.png$", path.name).group(1))
                )
                for frame_path in frame_paths:
                    try:
                        image = pygame.image.load(str(frame_path)).convert_alpha()
                    except pygame.error:
                        continue
                    bounds = image.get_bounding_rect(min_alpha=1)
                    if bounds.width and bounds.height:
                        frames.append(image.subsurface(bounds).copy())
            if not frames:
                frames = fallback_frames()
            animations[animation] = frames

        animations["movement"] = (
            animations["run"] + animations["jump"] + animations["roll"]
        )
        animations["combat"] = animations["attack"] + animations["special"] + animations["defend"]
        return animations

    def _make_sounds(self):
        if not pygame.mixer.get_init():
            print("[CONTROLES] Audio no disponible; el libro funcionará sin sonido.")
            return {}

        sample_rate, sample_format, channels = pygame.mixer.get_init()
        if sample_format != -16:
            print(
                "[CONTROLES] Formato de audio no compatible; "
                "el libro funcionará sin sonido."
            )
            return {}

        def create_sound(kind):
            duration = {"open": 0.48, "close": 0.36}[kind]
            sample_count = int(sample_rate * duration)
            samples = array.array("h")
            rng = random.Random({"open": 11, "close": 17}[kind])
            for index in range(sample_count):
                position = index / sample_rate
                progress = index / max(1, sample_count - 1)
                if kind == "open":
                    envelope = math.sin(math.pi * progress) ** 1.4
                    frequency = 180 + 500 * progress
                    noise_amount = 0.24
                else:
                    envelope = math.exp(-position * 8) * min(1.0, progress * 35)
                    frequency = 120 - 45 * progress
                    noise_amount = 0.08

                tone = math.sin(2 * math.pi * frequency * position) * 0.35
                sample = int(
                    max(-1.0, min(1.0, envelope * (tone + rng.uniform(-1, 1) * noise_amount)))
                    * 32767
                )
                for _ in range(channels):
                    samples.append(sample)

            if sys.byteorder != "little":
                samples.byteswap()
            return pygame.mixer.Sound(buffer=samples.tobytes())

        try:
            sounds = {kind: create_sound(kind) for kind in ("open", "close")}
        except pygame.error as error:
            print(f"[CONTROLES] No se pudieron crear los sonidos del libro: {error}")
            return {}
        for sound in sounds.values():
            sound.set_volume(0.55)
        return sounds

    def _play_sound(self, name):
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def _make_background(self):
        width, height = self.screen_size
        background = pygame.Surface(self.screen_size)
        background.fill((34, 20, 15))

        board_height = self._px(82)
        for y in range(0, height, board_height):
            shade = (y // board_height) % 2
            color = (69 + shade * 5, 39 + shade * 3, 25 + shade * 2)
            pygame.draw.rect(background, color, (0, y, width, board_height))
            pygame.draw.line(
                background,
                (30, 18, 14),
                (0, y),
                (width, y),
                self._px(3),
            )
            for x in range(self._px(40), width, self._px(180)):
                offset = (x + y) % max(1, width // 3)
                pygame.draw.arc(
                    background,
                    (82, 49, 31),
                    (offset, y + self._px(18), self._px(100), self._px(34)),
                    math.pi,
                    math.tau,
                    self._px(1),
                )

        border = self._px(24)
        pygame.draw.rect(
            background,
            (24, 17, 15),
            (border, border, width - border * 2, height - border * 2),
            self._px(2),
        )
        self._draw_table_runes(background)
        return background

    def _draw_table_runes(self, surface):
        width, height = self.screen_size
        gold = (159, 118, 56)
        glow = (69, 124, 112)
        margin = self._px(46)
        spacing = self._px(78)
        radius = self._px(13)
        for x in range(margin, width - margin, spacing):
            for y in (margin, height - margin):
                if y == height - margin and abs(x - width // 2) < self._px(240):
                    continue
                pygame.draw.circle(surface, glow, (x, y), radius + self._px(4), self._px(1))
                pygame.draw.circle(surface, gold, (x, y), radius, self._px(1))
                pygame.draw.line(
                    surface,
                    glow,
                    (x - radius // 2, y + radius // 2),
                    (x + radius // 2, y - radius // 2),
                    self._px(2),
                )
                pygame.draw.line(
                    surface,
                    gold,
                    (x - radius // 2, y - radius // 2),
                    (x + radius // 2, y + radius // 2),
                    self._px(1),
                )
        for y in range(margin + spacing, height - margin, spacing):
            for x in (margin, width - margin):
                pygame.draw.circle(surface, glow, (x, y), radius + self._px(4), self._px(1))
                pygame.draw.polygon(
                    surface,
                    gold,
                    (
                        (x, y - radius),
                        (x + radius, y),
                        (x, y + radius),
                        (x - radius, y),
                    ),
                    self._px(1),
                )

    def reset(self):
        self.animation_elapsed = 0.0
        self._play_sound("open")

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self._play_sound("close")
            return True
        return False

    def draw(self, surface):
        # CLOSED usa el fotograma 1 y OPEN el fotograma 8 del spritesheet.
        screen_width, screen_height = self.screen_size
        # Todos los fotogramas comparten escala y ancla; solo cambia el dibujo del sprite.
        frame_width, frame_height = self.frame_size
        scale = min(
            screen_width * 0.78 / frame_width,
            screen_height * 0.88 / frame_height,
        )
        frame = self.frames[
            0 if self.state == ScrollState.CLOSED else self.frame_index
        ]
        offset_x, offset_y = self.frame_offsets[
            0 if self.state == ScrollState.CLOSED else self.frame_index
        ]
        image = pygame.transform.smoothscale(
            frame,
            (
                max(1, round(frame.get_width() * scale)),
                max(1, round(frame.get_height() * scale)),
            ),
        )
        image_rect = image.get_rect(
            topleft=(
                round(screen_width / 2 + (offset_x - frame_width / 2) * scale),
                round(screen_height / 2 + (offset_y - frame_height / 2) * scale),
            )
        )
        surface.blit(image, image_rect)
