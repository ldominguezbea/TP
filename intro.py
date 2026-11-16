import math
import random

import pygame

from config import BASE_DIR, SCREEN_HEIGHT, SCREEN_WIDTH


class Intro:
    TITLE_IMAGE = BASE_DIR / "assets" / "fondos" / "Imagen_titulo.jpg"
    LOGO_IMAGE = BASE_DIR / "assets" / "barras de vida" / "LOGO.png"
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
    SUBTITLE_CUES = (
        (0, 1_600, "Advertencia."),
        (1_600, 4_100, "Red de defensa global fuera de línea."),
        (4_100, 6_900, "Más del 60 % de la población ha perecido."),
        (
            6_900,
            10_600,
            "Las fuerzas militares se desmoronan\n"
            "ante interminables hordas demoníacas.",
        ),
        (10_600, 11_900, "Estamos desbordados."),
        (11_900, 12_750, "Mayday."),
        (12_750, 15_700, "Baliza de socorro automática activada."),
        (15_700, 17_700, "¿Alguien me escucha?"),
        (17_700, 19_600, "¿Alguien puede leerme?"),
        (19_600, 21_200, "¿Hay alguien ahí fuera?"),
        (21_200, 22_439, "Que Dios nos ayude."),
    )

    def __init__(self, screen, audio_enabled=True):
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
        logo = pygame.image.load(str(self.LOGO_IMAGE)).convert_alpha()
        self.studio_logo = pygame.transform.scale(logo, (210, 226))
        self.particle_layer = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        self.studio_font = pygame.font.SysFont("Georgia", 36, bold=True)
        self.credit_font = pygame.font.SysFont("Georgia", 24, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.instruction_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.instruction = self.instruction_font.render(
            'press "esc" to continue', True, (255, 255, 255)
        )
        self.instruction_background = pygame.Surface(
            (self.instruction.get_width() + 28, self.instruction.get_height() + 20),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            self.instruction_background,
            (0, 0, 0, 175),
            self.instruction_background.get_rect(),
            border_radius=6,
        )
        self.instruction_rect = self.instruction_background.get_rect(topleft=(24, 24))
        self.subtitle = None

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

        self.audio_enabled = audio_enabled
        self.broadcast_audio = None
        self.broadcast_channel = None
        self.broadcast_started_ticks = None
        if self.audio_enabled:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                self.broadcast_audio = pygame.mixer.Sound(str(self.BROADCAST_AUDIO))
                pygame.mixer.music.load(str(self.TITLE_TRACK))
                pygame.mixer.music.set_volume(self.MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
            except (pygame.error, OSError) as error:
                print(f"[AUDIO] No se pudo iniciar el audio de la intro: {error}")
                self.audio_enabled = False

        self.elapsed_ms = 0
        self.timeline_ms = 0
        self.phase = "STUDIO"
        self.broadcast_started = False
        self.title_started = False
        self.finished = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.audio_enabled:
                pygame.mixer.music.stop()
                self.broadcast_audio.stop()
            self.finished = True

    def update(self, elapsed_ms):
        self.elapsed_ms += max(0, elapsed_ms)
        music_position = pygame.mixer.music.get_pos() if self.audio_enabled else -1
        self.timeline_ms = max(
            self.timeline_ms, self.elapsed_ms, music_position, 0
        )

        if (
            self.audio_enabled
            and not self.broadcast_started
            and self.timeline_ms >= self.STUDIO_PHASE_END_MS
        ):
            self.broadcast_channel = self.broadcast_audio.play()
            self.broadcast_started_ticks = pygame.time.get_ticks()
            pygame.mixer.music.set_volume(self.DUCKED_MUSIC_VOLUME)
            self.broadcast_started = True

        if (
            self.audio_enabled
            and not self.title_started
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

        self.subtitle = None
        if (
            self.broadcast_channel is not None
            and self.broadcast_started_ticks is not None
            and self.broadcast_channel.get_busy()
        ):
            audio_position_ms = (
                pygame.time.get_ticks() - self.broadcast_started_ticks
            )
            self.subtitle = next(
                (
                    text
                    for start_ms, end_ms, text in self.SUBTITLE_CUES
                    if start_ms <= audio_position_ms < end_ms
                ),
                None,
            )

    def _draw_subtitle(self):
        if self.subtitle is None:
            return

        lines = self.subtitle.splitlines()
        rendered_lines = [
            self.subtitle_font.render(line, True, (255, 255, 255))
            for line in lines
        ]
        padding_x = 28
        padding_y = 14
        line_spacing = 4
        box_width = max(line.get_width() for line in rendered_lines) + padding_x * 2
        box_height = (
            sum(line.get_height() for line in rendered_lines)
            + line_spacing * (len(rendered_lines) - 1)
            + padding_y * 2
        )
        box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(
            box,
            (0, 0, 0, 190),
            box.get_rect(),
            border_radius=8,
        )
        box_rect = box.get_rect(
            midbottom=(self.screen.get_width() // 2, self.screen.get_height() - 28)
        )
        self.screen.blit(box, box_rect)

        y = box_rect.top + padding_y
        for line in rendered_lines:
            self.screen.blit(line, line.get_rect(midtop=(box_rect.centerx, y)))
            y += line.get_height() + line_spacing

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

    def _draw_studio_credit(self):
        phase_duration_ms = self.STUDIO_PHASE_END_MS
        alpha = min(
            255,
            round(
                255
                * min(
                    self.timeline_ms / self.FADE_DURATION_MS,
                    (phase_duration_ms - self.timeline_ms)
                    / self.FADE_DURATION_MS,
                    1,
                )
            ),
        )
        rendered = self.studio_font.render("IRONBOUND STUDIOS", True, (245, 245, 245))
        rendered.set_alpha(alpha)
        self.studio_logo.set_alpha(alpha)

        group_height = self.studio_logo.get_height() + 18 + rendered.get_height()
        top = (self.screen.get_height() - group_height) // 2
        center_x = self.screen.get_width() // 2
        self.screen.blit(
            self.studio_logo,
            self.studio_logo.get_rect(midtop=(center_x, top)),
        )
        self.screen.blit(
            rendered,
            (center_x - rendered.get_width() // 2, top + self.studio_logo.get_height() + 18),
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
            self._draw_studio_credit()
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

        self._draw_subtitle()
        self.screen.blit(self.instruction_background, self.instruction_rect)
        self.screen.blit(
            self.instruction,
            (self.instruction_rect.x + 14, self.instruction_rect.y + 10),
        )


def run_intro(screen=None, audio_enabled=True):
    owns_display = screen is None
    if owns_display:
        pygame.init()
    try:
        if owns_display:
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("REQUIEM: El juicio final")
        clock = pygame.time.Clock()
        intro = Intro(screen, audio_enabled=audio_enabled)
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
        if owns_display:
            pygame.quit()
    return running


if __name__ == "__main__":
    run_intro()
