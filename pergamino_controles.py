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
        for animation, directories in frame_directories.items():
            frames = []
            for directory in directories:
                frame_paths = list((assets_dir / directory).glob("*.png"))
                frame_paths.sort(
                    key=lambda path: int(re.search(r"(\d+)\.png$", path.name).group(1))
                )
                if not frame_paths:
                    raise FileNotFoundError(
                        f"No hay fotogramas para {animation}: {assets_dir / directory}"
                    )
                for frame_path in frame_paths:
                    image = pygame.image.load(str(frame_path)).convert_alpha()
                    bounds = image.get_bounding_rect(min_alpha=1)
                    if bounds.width and bounds.height:
                        frames.append(image.subsurface(bounds).copy())
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

    def update(self, dt):
        self.animation_elapsed += max(0.0, dt)

    def _draw_leaf(self, surface, rect, right=False):
        shadow = rect.move(self._px(4), self._px(5))
        pygame.draw.rect(surface, (28, 17, 13), shadow, border_radius=self._px(5))
        pygame.draw.rect(surface, (91, 56, 32), rect.inflate(self._px(7), self._px(7)), border_radius=self._px(5))
        pygame.draw.rect(surface, (228, 202, 151), rect)
        pygame.draw.rect(surface, (193, 157, 103), rect, self._px(2))
        inset = rect.inflate(-self._px(22), -self._px(22))
        pygame.draw.rect(surface, (171, 130, 77), inset, self._px(1))
        seam_x = rect.left + self._px(14) if right else rect.right - self._px(14)
        pygame.draw.line(
            surface,
            (184, 145, 95),
            (seam_x, rect.top + self._px(5)),
            (seam_x, rect.bottom - self._px(5)),
            self._px(2),
        )

    def _current_frame(self, page):
        animation = self.animations["movement" if page == 0 else "combat"]
        index = int(self.animation_elapsed / self.FRAME_DURATION) % len(animation)
        return animation[index]

    def _draw_control_page(self, surface, rect, page):
        page_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        self._draw_leaf(page_surface, page_surface.get_rect(), right=page == 1)
        title_text = "[ MOVIMIENTO ]" if page == 0 else "[ ARTES DE COMBATE ]"
        title = self.font_title.render(title_text, True, (91, 48, 34))
        page_surface.blit(
            title,
            title.get_rect(center=(rect.width // 2, self._px(52))),
        )
        pygame.draw.line(
            page_surface,
            (154, 111, 58),
            (self._px(44), self._px(83)),
            (rect.width - self._px(44), self._px(83)),
            self._px(2),
        )

        controls = (
            (
                "[ A / D ]  ──► MOVIMIENTO",
                "[ W ]      ──► SALTO",
                "[ S ]      ──► BAJAR (PLATAFORMA)",
                "[ Q ]      ──► RODAR",
            )
            if page == 0
            else (
                "[ E ]         ──► ATAQUE ESPECIAL",
                "[ CLICK IZQ ] ──► ATAQUE BÁSICO",
                "[ CLICK DER ] ──► BLOQUEO",
            )
        )
        row_start = self._px(105)
        row_step = self._px(40)
        for index, text in enumerate(controls):
            rendered = self.font_controls.render(text, True, (69, 47, 33))
            page_surface.blit(
                rendered,
                rendered.get_rect(center=(rect.width // 2, row_start + index * row_step)),
            )

        sprite = self._current_frame(page)
        available_height = self._px(138)
        available_width = self._px(185)
        scale = min(
            available_width / sprite.get_width(),
            available_height / sprite.get_height(),
        )
        sprite_size = (
            max(1, round(sprite.get_width() * scale)),
            max(1, round(sprite.get_height() * scale)),
        )
        sprite = pygame.transform.scale(sprite, sprite_size)
        sprite_y = row_start + len(controls) * row_step + self._px(12)
        page_surface.blit(
            sprite,
            sprite.get_rect(center=(rect.width // 2, sprite_y + available_height // 2)),
        )

        surface.blit(page_surface, rect)

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        pygame.draw.rect(
            surface,
            (37, 24, 18),
            self.book_rect.inflate(self._px(22), self._px(18)),
            border_radius=self._px(12),
        )
        pygame.draw.rect(
            surface,
            (132, 83, 43),
            self.book_rect.inflate(self._px(12), self._px(8)),
            self._px(3),
            border_radius=self._px(10),
        )
        self._draw_control_page(surface, self.left_page_rect, 0)
        self._draw_control_page(surface, self.right_page_rect, 1)

        center_x = self.book_rect.centerx
        pygame.draw.line(
            surface,
            (80, 46, 28),
            (center_x, self.book_rect.top + self._px(12)),
            (center_x, self.book_rect.bottom - self._px(12)),
            self._px(8),
        )
        title = self.font_title.render(
            "[ ARTES DEL GUERRERO ]",
            True,
            (236, 199, 116),
        )
        surface.blit(title, title.get_rect(center=(self.screen_size[0] // 2, self._px(35))))

        hint = self.font_small.render("ESC  CERRAR", True, (224, 193, 130))
        surface.blit(
            hint,
            hint.get_rect(center=(self.screen_size[0] // 2, self.book_rect.bottom + self._px(31))),
        )
