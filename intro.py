import math
import random

import pygame

from config import BASE_DIR, SCREEN_HEIGHT, SCREEN_WIDTH


class Intro:
    TITLE_IMAGE = BASE_DIR / "assets" / "fondos" / "Imagen_titulo.jpg"
    TITLE_TRACK = BASE_DIR / "musica" / "title_music.mp3"
    BROADCAST_AUDIO = (
        BASE_DIR / "musica" / "ElevenLabs_2026-11-08T19_38_54_VEGA_gen_s50_sim75_v4.mp3"
    )
    STUDIO_PHASE_END_MS = 10_000
    ENGINE_PHASE_END_MS = 20_000
    TITLE_PHASE_START_MS = 33_000
    PARTICLE_COUNT = 180
    FADE_DURATION_MS = 2_000
    MUSIC_VOLUME = 0.7
    DUCKED_MUSIC_VOLUME = 0.2
    TITLE_MUSIC_VOLUME = 0.8
    BACKGROUND_COLOR = (0, 0, 0)

    def __init__(self, screen):
        self.screen = screen
        screen_width, screen_height = screen.get_size()
        title_image = pygame.image.load(str(self.TITLE_IMAGE)).convert()
        scale = min(
            screen_width / title_image.get_width(),
            screen_height / title_image.get_height(),
        )
        title_size = (
            round(title_image.get_width() * scale),
            round(title_image.get_height() * scale),
        )
        self.title_image = pygame.transform.smoothscale(title_image, title_size)
        self.title_rect = self.title_image.get_rect(
            center=(screen_width // 2, screen_height // 2)
        )
        self.particle_layer = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        self.studio_font = pygame.font.SysFont("Arial", 34, bold=True)
        self.credit_font = pygame.font.SysFont("Arial", 24, bold=True)

        rng = random.Random(1604)
        self.particles = tuple(
            (
                rng.randrange(screen_width),
                rng.randrange(screen_height),
                rng.uniform(8.0, 28.0),
                rng.random() * math.tau,
                rng.choice((1, 1, 1, 2)),
            )
            for _ in range(self.PARTICLE_COUNT)
        )

        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.broadcast_audio = pygame.mixer.Sound(str(self.BROADCAST_AUDIO))
        pygame.mixer.music.load(str(self.TITLE_TRACK))
        pygame.mixer.music.set_volume(self.MUSIC_VOLUME)
        pygame.mixer.music.play(-1)

        self.elapsed_ms = 0
        self.timeline_ms = 0
        self.phase = "STUDIO"
        self.broadcast_started = False
        self.title_started = False
        self.finished = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.phase == "TITLE":
            pygame.mixer.music.stop()
            self.broadcast_audio.stop()
            self.finished = True

    def update(self, elapsed_ms):
        self.elapsed_ms += max(0, elapsed_ms)
        music_position = pygame.mixer.music.get_pos()
        self.timeline_ms = max(
            self.timeline_ms, self.elapsed_ms, music_position, 0
        )

        if (
            not self.broadcast_started
            and self.timeline_ms >= self.STUDIO_PHASE_END_MS
        ):
            self.broadcast_audio.play()
            pygame.mixer.music.set_volume(self.DUCKED_MUSIC_VOLUME)
            self.broadcast_started = True

        if (
            not self.title_started
            and self.timeline_ms >= self.TITLE_PHASE_START_MS
        ):
            pygame.mixer.music.set_volume(self.TITLE_MUSIC_VOLUME)
            self.title_started = True

        if self.timeline_ms < self.STUDIO_PHASE_END_MS:
            self.phase = "STUDIO"
        elif self.timeline_ms < self.ENGINE_PHASE_END_MS:
            self.phase = "ENGINE"
        elif self.timeline_ms < self.TITLE_PHASE_START_MS:
            self.phase = "ASH"
        else:
            self.phase = "TITLE"

    def _draw_credit(self, lines, phase_elapsed_ms):
        phase_duration_ms = self.ENGINE_PHASE_END_MS - self.STUDIO_PHASE_END_MS
        alpha = min(
            255,
            round(
                255
                * min(
                    phase_elapsed_ms / self.FADE_DURATION_MS,
                    (phase_duration_ms - phase_elapsed_ms)
                    / self.FADE_DURATION_MS,
                    1,
                )
            ),
        )
        center_y = self.screen.get_height() // 2
        for index, (text, font, color) in enumerate(lines):
            rendered = font.render(text, True, color)
            rendered.set_alpha(alpha)
            y = center_y + (index * 46) - ((len(lines) - 1) * 23)
            self.screen.blit(
                rendered,
                (self.screen.get_width() // 2 - rendered.get_width() // 2, y),
            )

    def _draw_particles(self, screen_width, screen_height, intensity, title_mode):
        self.particle_layer.fill((0, 0, 0, 0))
        elapsed_seconds = self.timeline_ms / 1000
        visible_count = round(self.PARTICLE_COUNT * intensity)

        for start_x, start_y, speed, phase, size in self.particles[:visible_count]:
            y = round(
                (start_y - elapsed_seconds * speed) % (screen_height + size)
            ) - size
            x = round(start_x + math.sin(elapsed_seconds * 0.35 + phase) * 5)
            flicker = 0.65 + 0.35 * math.sin(elapsed_seconds * 1.6 + phase)
            if title_mode:
                color = (255, 75 + round(110 * flicker), 18 + round(35 * flicker))
                alpha = round(95 + 140 * flicker)
            else:
                color = (115, 106, 100)
                alpha = round(75 * intensity * flicker)
            pygame.draw.circle(
                self.particle_layer,
                (*color, alpha),
                (x % screen_width, y),
                size,
            )

        self.screen.blit(
            self.particle_layer,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_ADD,
        )

    def draw(self):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(self.BACKGROUND_COLOR)

        if self.phase == "STUDIO":
            self._draw_credit(
                (("IRONBOUND STUDIOS", self.studio_font, (245, 245, 245)),),
                self.timeline_ms,
            )
        elif self.phase == "ENGINE":
            self._draw_credit(
                (("POWERED BY PYGAME-CE", self.credit_font, (245, 245, 245)),),
                self.timeline_ms - self.STUDIO_PHASE_END_MS,
            )
        elif self.phase == "ASH":
            ash_progress = (
                self.timeline_ms - self.ENGINE_PHASE_END_MS
            ) / (self.TITLE_PHASE_START_MS - self.ENGINE_PHASE_END_MS)
            self._draw_particles(
                screen_width, screen_height, ash_progress, title_mode=False
            )
        elif self.phase == "TITLE":
            self.screen.blit(self.title_image, self.title_rect)
            self._draw_particles(
                screen_width, screen_height, 1.0, title_mode=True
            )


def run_intro():
    pygame.init()
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("REQUIEM: El juicio final")
        clock = pygame.time.Clock()
        intro = Intro(screen)
        running = True

        while running and not intro.finished:
            elapsed_ms = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    intro.handle_event(event)

            if running:
                intro.update(elapsed_ms)
                intro.draw()
                pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    run_intro()
