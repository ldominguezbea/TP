import array
import math
import random
import re
import sys
from pathlib import Path

import pygame


class ControlsBook:
    FRAME_DURATION = 0.095

    def __init__(self, screen_size, heroes_dir: Path):
        self.screen_size = screen_size
        self.scale = min(screen_size[0] / 1350, screen_size[1] / 720)
        self.animation_elapsed = 0.0
        self.closing = False
        self.font_title = pygame.font.SysFont("Constantia", self._px(29), bold=True)
        self.font_small = pygame.font.SysFont("Constantia", self._px(12), bold=True)
        self.font_controls = pygame.font.SysFont("Constantia", self._px(15), bold=True)
        self.sounds = self._make_sounds()
        self.animations = self._load_animations(heroes_dir)

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
        self.background = self._make_background()

    def _px(self, value):
        return max(1, round(value * self.scale))

    def _load_animations(self, assets_dir):
        hero_directories = {
            "VIENTO": assets_dir / "P_viento",
            "TIERRA": assets_dir / "P_tierra",
            "PLANTA": assets_dir / "P_planta",
            "FUEGO": assets_dir / "p_fuego" / "p_fuego",
        }
        action_directories = {
            "run": ("run",),
            "jump": ("j_up", "jump_full", "jump_down", "j_down", "03_jump", "03_jump_down"),
            "roll": ("roll",),
            "attack": ("1_atk",),
            "special": ("sp_atk",),
            "defend": ("defend",),
        }
        animations = {}

        def fallback_frames():
            surface = pygame.Surface((48, 62), pygame.SRCALPHA)
            center = (surface.get_width() // 2, surface.get_height() // 2)
            pygame.draw.circle(surface, (91, 128, 116), center, 15, 1)
            pygame.draw.polygon(
                surface,
                (177, 143, 79),
                (
                    (center[0], center[1] - 10),
                    (center[0] + 8, center[1]),
                    (center[0], center[1] + 10),
                    (center[0] - 8, center[1]),
                ),
                1,
            )
            return [surface]

        def frame_order(path):
            match = re.search(r"(\d+)(?=\.png$)", path.name)
            return (int(match.group(1)) if match else 0, path.name.casefold())

        for hero, hero_dir in hero_directories.items():
            for action, directories in action_directories.items():
                frames = []
                for directory in directories:
                    directory_path = hero_dir / directory
                    frame_paths = sorted(directory_path.glob("*.png"), key=frame_order)
                    for frame_path in frame_paths:
                        try:
                            image = pygame.image.load(str(frame_path)).convert_alpha()
                        except (pygame.error, OSError) as error:
                            print(
                                f"[CONTROLES] No se pudo cargar el fotograma "
                                f"{frame_path}: {error}"
                            )
                            continue
                        bounds = image.get_bounding_rect(min_alpha=1)
                        if bounds.width and bounds.height:
                            frames.append(image.subsurface(bounds).copy())

                if not frames:
                    frames = fallback_frames()

                max_size = (self._px(48), self._px(62))
                largest_width = max(frame.get_width() for frame in frames)
                largest_height = max(frame.get_height() for frame in frames)
                frame_scale = min(
                    max_size[0] / largest_width,
                    max_size[1] / largest_height,
                )
                scaled_frames = []
                for frame in frames:
                    scaled_frames.append(
                        pygame.transform.scale(
                            frame,
                            (
                                max(1, round(frame.get_width() * frame_scale)),
                                max(1, round(frame.get_height() * frame_scale)),
                            ),
                        )
                    )
                animations[(hero, action)] = scaled_frames

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
        background.fill((13, 15, 18))

        board_height = self._px(82)
        for y in range(0, height, board_height):
            shade = (y // board_height) % 2
            color = (22 + shade * 3, 25 + shade * 2, 29 + shade * 2)
            pygame.draw.rect(background, color, (0, y, width, board_height))
            pygame.draw.line(
                background,
                (10, 12, 15),
                (0, y),
                (width, y),
                self._px(3),
            )
            for x in range(self._px(40), width, self._px(180)):
                offset = (x + y) % max(1, width // 3)
                pygame.draw.arc(
                    background,
                    (30, 39, 39),
                    (offset, y + self._px(18), self._px(100), self._px(34)),
                    math.pi,
                    math.tau,
                    self._px(1),
                )

        border = self._px(24)
        pygame.draw.rect(
            background,
            (9, 12, 15),
            (border, border, width - border * 2, height - border * 2),
            self._px(2),
        )
        self._draw_table_runes(background)
        return background

    def _draw_table_runes(self, surface):
        width, height = self.screen_size
        gold = (133, 105, 61)
        glow = (49, 89, 82)
        margin = self._px(46)
        spacing = self._px(88)
        radius = self._px(10)

        safe_book_area = self.book_rect.inflate(self._px(36), self._px(36))
        footer_area = pygame.Rect(0, height - self._px(48), width, self._px(48))
        placed_runes = []

        def draw_rune(x, y, diagonal=True):
            bounds = pygame.Rect(
                x - radius - self._px(4),
                y - radius - self._px(4),
                (radius + self._px(4)) * 2,
                (radius + self._px(4)) * 2,
            )
            if (
                bounds.colliderect(safe_book_area)
                or bounds.colliderect(footer_area)
                or any(bounds.colliderect(existing) for existing in placed_runes)
            ):
                return
            placed_runes.append(bounds)

            pygame.draw.circle(
                surface, glow, (x, y), radius + self._px(4), self._px(1)
            )
            pygame.draw.circle(surface, gold, (x, y), radius, self._px(1))
            if diagonal:
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
            else:
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

        for x in range(margin, width - margin, spacing):
            for y in (margin, height - margin):
                if y == height - margin and abs(x - width // 2) < self._px(240):
                    continue
                draw_rune(x, y)
        for y in range(margin + spacing, height - margin, spacing):
            for x in (margin, width - margin):
                draw_rune(x, y, diagonal=False)

    def reset(self):
        self.animation_elapsed = 0.0
        self.closing = False
        self._play_sound("open")

    def handle_key(self, key):
        if (
            key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)
            and not self.closing
        ):
            self.closing = True
            self.animation_elapsed = 0.0
            self._play_sound("close")
            return True
        return False

    def update(self, elapsed_seconds):
        self.animation_elapsed += max(0.0, elapsed_seconds)
        return self.closing and self.animation_elapsed >= self.FRAME_DURATION * 8

    def draw(self, surface):
        screen_width, screen_height = self.screen_size
        surface.blit(self.background, (0, 0))
        pygame.draw.rect(
            surface,
            (13, 18, 19),
            self.book_rect,
            border_radius=self._px(18),
        )
        pygame.draw.rect(
            surface,
            (105, 89, 60),
            self.book_rect,
            self._px(2),
            border_radius=self._px(18),
        )

        pages = (self.left_page_rect, self.right_page_rect)
        for page in pages:
            pygame.draw.rect(surface, (28, 34, 35), page, border_radius=8)
            pygame.draw.rect(
                surface,
                (105, 89, 60),
                page,
                self._px(2),
                border_radius=8,
            )
            inner_page = page.inflate(-self._px(12), -self._px(12))
            pygame.draw.rect(
                surface,
                (49, 58, 55),
                inner_page,
                self._px(1),
                border_radius=6,
            )

        sections = (
            (
                self.left_page_rect,
                "MOVIMIENTO",
                (("A / D", "CAMINAR", "run"), ("W", "SALTAR", "jump"), ("Q", "ESQUIVAR", "roll")),
            ),
            (
                self.right_page_rect,
                "COMBATE",
                (
                    ("CLIC IZQ.", "ATACAR", "attack"),
                    ("CLIC DER.", "DEFENDER", "defend"),
                    ("E", "HABILIDAD ESPECIAL", "special"),
                ),
            ),
        )
        heroes = ("VIENTO", "TIERRA", "PLANTA", "FUEGO")

        for page, title, rows in sections:
            title_shadow = self.font_title.render(title, True, (8, 14, 14))
            title_image = self.font_title.render(title, True, (192, 159, 91))
            surface.blit(
                title_shadow,
                title_shadow.get_rect(
                    center=(page.centerx + self._px(1), page.top + self._px(51))
                ),
            )
            surface.blit(
                title_image,
                title_image.get_rect(center=(page.centerx, page.top + self._px(49))),
            )
            pygame.draw.line(
                surface,
                (119, 103, 70),
                (page.left + self._px(28), page.top + self._px(82)),
                (page.right - self._px(28), page.top + self._px(82)),
                self._px(2),
            )
            ornament_y = page.top + self._px(82)
            for ornament_x in (page.left + self._px(20), page.right - self._px(20)):
                diamond = (
                    (ornament_x, ornament_y - self._px(6)),
                    (ornament_x + self._px(6), ornament_y),
                    (ornament_x, ornament_y + self._px(6)),
                    (ornament_x - self._px(6), ornament_y),
                )
                pygame.draw.polygon(surface, (159, 133, 79), diamond, self._px(1))

            header_height = self._px(94)
            bottom_padding = self._px(18)
            row_height = (
                page.height - header_height - bottom_padding
            ) // len(rows)
            first_row_top = page.top + header_height
            for row_index, (key, description, action) in enumerate(rows):
                row_top = first_row_top + row_index * row_height
                label_image = self.font_controls.render(
                    f"{key}  /  {description}", True, (216, 207, 183)
                )
                surface.blit(
                    label_image,
                    label_image.get_rect(
                        center=(page.centerx, row_top + self._px(14))
                    ),
                )

                for hero_index, hero in enumerate(heroes):
                    frames = self.animations[(hero, action)]
                    frame_index = int(
                        self.animation_elapsed / self.FRAME_DURATION
                    ) % len(frames)
                    frame = frames[frame_index]
                    center_x = page.left + round(
                        (hero_index + 0.5) * page.width / len(heroes)
                    )
                    surface.blit(
                        frame,
                        frame.get_rect(
                            midbottom=(
                                center_x,
                                row_top + row_height - self._px(25),
                            )
                        ),
                    )
                    hero_label = self.font_small.render(
                        hero, True, (143, 171, 155)
                    )
                    surface.blit(
                        hero_label,
                        hero_label.get_rect(
                            center=(
                                center_x,
                                row_top + row_height - self._px(9),
                            )
                        ),
                    )

                if row_index < len(rows) - 1:
                    pygame.draw.line(
                        surface,
                        (67, 82, 77),
                        (page.left + self._px(34), row_top + row_height),
                        (page.right - self._px(34), row_top + row_height),
                        self._px(1),
                    )

        hint = self.font_small.render(
            "ESC / ENTER / ESPACIO: volver",
            True,
            (179, 167, 139),
        )
        hint_backing = hint.get_rect(
            center=(screen_width // 2, screen_height - self._px(24))
        ).inflate(self._px(20), self._px(8))
        pygame.draw.rect(
            surface, (15, 19, 21), hint_backing, border_radius=self._px(8)
        )
        pygame.draw.rect(
            surface,
            (69, 79, 70),
            hint_backing,
            self._px(1),
            border_radius=self._px(8),
        )
        surface.blit(
            hint,
            hint.get_rect(center=hint_backing.center),
        )
