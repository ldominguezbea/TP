import random

import pygame

from config import BASE_DIR


class Intro:
    FRAMES_PER_CLOUD_STEP = 4
    CLOUD_TILE_SIZE = 128
    EARTH_RADIUS_RATIO = 0.215
    TEXT_DELAY_MS = 2000
    TYPEWRITER_INTERVAL_MS = 65
    TEXT_END_HOLD_MS = 1000
    INTRO_TEXT = "Tierra 30 de Diciembre de 2026"

    def __init__(self, screen):
        self.screen = screen
        image_path = BASE_DIR / "assets" / "fondos" / "Earth_Base.jpg"
        image = pygame.image.load(str(image_path)).convert()

        screen_width, screen_height = screen.get_size()
        image_width, image_height = image.get_size()
        scale = max(screen_width / image_width, screen_height / image_height)
        scaled_size = (round(image_width * scale), round(image_height * scale))
        scaled_image = pygame.transform.smoothscale(image, scaled_size)
        background = pygame.Surface((screen_width, screen_height))
        self.background_rect = scaled_image.get_rect(center=background.get_rect().center)
        background.blit(scaled_image, self.background_rect)
        self.background = background

        radius = round(image_width * scale * self.EARTH_RADIUS_RATIO)
        center = (
            round(image_width * 0.5 * scale + self.background_rect.left),
            round(image_height * 0.5 * scale + self.background_rect.top),
        )
        self.earth_rect = pygame.Rect(
            center[0] - radius, center[1] - radius, radius * 2, radius * 2
        )

        tile_size = self.CLOUD_TILE_SIZE
        cloud_tile = self._make_cloud_tile(tile_size)
        self.cloud_texture = pygame.transform.scale(
            cloud_tile, (self.earth_rect.width, self.earth_rect.height)
        )
        self.cloud_mask = pygame.Surface(self.earth_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(
            self.cloud_mask,
            (255, 255, 255, 255),
            (radius, radius),
            radius - 1,
        )
        self.cloud_layer = pygame.Surface(self.earth_rect.size, pygame.SRCALPHA)
        self.cloud_offset = 0
        self.frame_counter = 0
        self._update_cloud_layer()

        self.elapsed_ms = 0
        self.visible_characters = 0
        self.text_font = pygame.font.SysFont("Consolas", 28, bold=True)
        self.text_color = (100, 235, 255)
        text_width = self.text_font.size(self.INTRO_TEXT)[0]
        self.text_panel = pygame.Surface((text_width + 32, 54), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_panel,
            (3, 14, 28, 205),
            self.text_panel.get_rect(),
            border_radius=5,
        )
        pygame.draw.rect(
            self.text_panel,
            (35, 155, 205, 210),
            self.text_panel.get_rect(),
            width=1,
            border_radius=5,
        )

    @property
    def finished(self):
        intro_duration = (
            self.TEXT_DELAY_MS
            + max(0, len(self.INTRO_TEXT) - 1) * self.TYPEWRITER_INTERVAL_MS
            + self.TEXT_END_HOLD_MS
        )
        return self.elapsed_ms >= intro_duration

    @staticmethod
    def _make_cloud_tile(size):
        tile = pygame.Surface((size, size), pygame.SRCALPHA)
        rng = random.Random(24)

        for _ in range(16):
            center_x = rng.randrange(size)
            center_y = rng.randrange(12, size - 12)
            radius_x = rng.randrange(5, 14)
            radius_y = rng.randrange(2, 6)

            for dx in range(-radius_x, radius_x + 1):
                normalized_x = dx / radius_x
                half_height = round(
                    radius_y * (1 - normalized_x * normalized_x) ** 0.5
                )
                for dy in range(-half_height, half_height + 1):
                    if rng.random() < 0.12:
                        continue
                    if dy > half_height * 0.45:
                        color = (170, 205, 235, rng.randrange(45, 85))
                    else:
                        color = (225, 240, 255, rng.randrange(70, 125))
                    position = ((center_x + dx) % size, center_y + dy)
                    tile.set_at(position, color)

        return tile

    def _update_cloud_layer(self):
        width = self.cloud_layer.get_width()
        self.cloud_layer.fill((0, 0, 0, 0))
        self.cloud_layer.blit(self.cloud_texture, (-self.cloud_offset, 0))
        self.cloud_layer.blit(
            self.cloud_texture, (width - self.cloud_offset, 0)
        )
        self.cloud_layer.blit(
            self.cloud_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )

    def update(self, elapsed_ms):
        self.elapsed_ms += elapsed_ms
        self.frame_counter += 1
        if self.frame_counter >= self.FRAMES_PER_CLOUD_STEP:
            self.frame_counter = 0
            self.cloud_offset = (self.cloud_offset + 1) % self.cloud_layer.get_width()
            self._update_cloud_layer()

        typing_elapsed = self.elapsed_ms - self.TEXT_DELAY_MS
        if typing_elapsed >= 0:
            self.visible_characters = min(
                len(self.INTRO_TEXT),
                int(typing_elapsed / self.TYPEWRITER_INTERVAL_MS) + 1,
            )

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.cloud_layer, self.earth_rect.topleft)
        if self.visible_characters:
            panel_rect = self.text_panel.get_rect(topleft=(28, 24))
            self.screen.blit(self.text_panel, panel_rect)
            text = self.INTRO_TEXT[:self.visible_characters]
            text_surface = self.text_font.render(text, True, self.text_color)
            self.screen.blit(text_surface, (panel_rect.x + 16, panel_rect.y + 10))
