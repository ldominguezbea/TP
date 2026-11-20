import math
import random
from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent
MUSICA_FINAL = BASE_DIR / "musica" / "Rip y Tear.mp3"
DURACION_MINIMA_FIN_MS = 4500


def iniciar_musica_epica():
    if not MUSICA_FINAL.is_file():
        raise FileNotFoundError(f"No se encontró la música del final: {MUSICA_FINAL}")
    if pygame.mixer.get_init() is None:
        print("[AUDIO] El mezclador no está disponible; el final continúa sin música.")
        return False
    try:
        pygame.mixer.music.load(str(MUSICA_FINAL))
        pygame.mixer.music.set_volume(0.62)
        pygame.mixer.music.play(-1)
    except pygame.error as error:
        print(f"[AUDIO] No se pudo iniciar la música del final: {error}")
        return False
    return True


def detener_musica_epica():
    if pygame.mixer.get_init() is None:
        return
    try:
        pygame.mixer.music.fadeout(900)
    except pygame.error as error:
        print(f"[AUDIO] No se pudo atenuar la música del final: {error}")


class PantallaFinalEpica:
    def __init__(self, screen, background, subtitle):
        self.screen = screen
        self.background = background
        self.subtitle = subtitle
        self.started_at = pygame.time.get_ticks()
        self.width, self.height = screen.get_size()
        self.center = (self.width // 2, self.height // 2)
        self.font_title = pygame.font.SysFont("Georgia", 112, bold=True)
        self.font_subtitle = pygame.font.SysFont("Georgia", 23, bold=True)
        self.font_hint = pygame.font.SysFont("Arial", 18, bold=True)
        self.title_letters = [
            (
                self.font_title.render(letter, True, (255, 232, 170)),
                self.font_title.render(letter, True, (255, 95, 22)),
            )
            for letter in "FIN"
        ]
        gap = 22
        total_width = sum(normal.get_width() for normal, _ in self.title_letters)
        total_width += gap * (len(self.title_letters) - 1)
        left = self.center[0] - total_width // 2
        self.letter_centers = []
        for normal, _ in self.title_letters:
            self.letter_centers.append(left + normal.get_width() // 2)
            left += normal.get_width() + gap
        self.dim_layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.dim_layer.fill((3, 5, 15, 155))
        self.effect_layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        rng = random.Random(731)
        self.embers = [
            (
                rng.uniform(0, self.width),
                rng.uniform(0, self.height + 40),
                rng.uniform(18, 68),
                rng.randint(1, 3),
                rng.uniform(0, math.tau),
            )
            for _ in range(58)
        ]

    def draw(self):
        elapsed_ms = pygame.time.get_ticks() - self.started_at
        elapsed = elapsed_ms / 1000.0
        self.screen.fill((0, 0, 0))
        self.screen.blit(
            self.background,
            self.background.get_rect(center=self.center),
        )
        self.screen.blit(self.dim_layer, (0, 0))

        self.effect_layer.fill((0, 0, 0, 0))
        center_x, center_y = self.center
        ring_progress = min(1.0, elapsed_ms / 1800.0)
        ring_alpha = int(75 * (1.0 - ring_progress * 0.35))
        ring_radius = int(88 + ring_progress * 58 + math.sin(elapsed * 2.2) * 5)
        pygame.draw.circle(
            self.effect_layer,
            (255, 185, 75, ring_alpha),
            (center_x, center_y - 26),
            ring_radius,
            2,
        )
        pygame.draw.circle(
            self.effect_layer,
            (255, 95, 30, ring_alpha // 2),
            (center_x, center_y - 26),
            ring_radius + 12,
            1,
        )
        for index in range(14):
            angle = math.tau * index / 14 + elapsed * 0.09
            start = (
                center_x + math.cos(angle) * (ring_radius + 10),
                center_y - 26 + math.sin(angle) * (ring_radius + 10),
            )
            end = (
                center_x + math.cos(angle) * (ring_radius + 24),
                center_y - 26 + math.sin(angle) * (ring_radius + 24),
            )
            pygame.draw.line(
                self.effect_layer,
                (255, 185, 75, ring_alpha),
                start,
                end,
                2,
            )

        for x, y, speed, radius, phase in self.embers:
            ember_y = (self.height + 25 - (y + elapsed * speed)) % (self.height + 50)
            ember_x = x + math.sin(elapsed * 1.4 + phase) * 16
            alpha = int(90 + 100 * (0.5 + 0.5 * math.sin(elapsed * 2 + phase)))
            pygame.draw.circle(
                self.effect_layer,
                (255, 115 + int(55 * math.sin(phase)), 28, alpha // 3),
                (round(ember_x), round(ember_y)),
                radius + 3,
            )
            pygame.draw.circle(
                self.effect_layer,
                (255, 185, 75, alpha),
                (round(ember_x), round(ember_y)),
                radius,
            )
        self.screen.blit(self.effect_layer, (0, 0))

        for index, (normal, glow) in enumerate(self.title_letters):
            progress = max(
                0.0,
                min(1.0, (elapsed_ms - (350 + index * 650)) / 500.0),
            )
            if progress <= 0:
                continue
            pulse = 1.0 + 0.025 * math.sin(elapsed * 3.2 + index)
            scale = (0.78 + 0.22 * progress) * pulse
            size = (
                max(1, round(normal.get_width() * scale)),
                max(1, round(normal.get_height() * scale)),
            )
            letter = pygame.transform.smoothscale(normal, size)
            letter_glow = pygame.transform.smoothscale(glow, size)
            alpha = int(255 * progress)
            letter.set_alpha(alpha)
            letter_glow.set_alpha(int(alpha * 0.45))
            y = center_y - 34 + round((1.0 - progress) * 24)
            rect = letter.get_rect(center=(self.letter_centers[index], y))
            self.screen.blit(letter_glow, (rect.x - 3, rect.y + 3))
            self.screen.blit(letter, rect)

        subtitle_alpha = int(
            255 * max(0.0, min(1.0, (elapsed_ms - 2100) / 900.0))
        )
        if subtitle_alpha:
            subtitle = self.font_subtitle.render(
                self.subtitle,
                True,
                (255, 224, 172),
            )
            subtitle.set_alpha(subtitle_alpha)
            subtitle_rect = subtitle.get_rect(
                center=(center_x, center_y + 88)
            )
            self.screen.blit(subtitle, subtitle_rect)
            line_width = int(
                min(self.width * 0.34, (self.width * 0.34) * subtitle_alpha / 255)
            )
            line_y = subtitle_rect.bottom + 15
            pygame.draw.line(
                self.screen,
                (210, 145, 58),
                (center_x - line_width // 2, line_y),
                (center_x + line_width // 2, line_y),
                2,
            )

        if elapsed_ms >= DURACION_MINIMA_FIN_MS - 300:
            hint = self.font_hint.render(
                "PRESIONA ENTER PARA CONTINUAR",
                True,
                (245, 225, 190),
            )
            hint.set_alpha(
                int(175 + 80 * (0.5 + 0.5 * math.sin(elapsed * 3.0)))
            )
            self.screen.blit(
                hint,
                hint.get_rect(center=(center_x, self.height - 44)),
            )
