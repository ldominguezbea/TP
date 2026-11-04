from enum import Enum, auto
from pathlib import Path

import pygame


class ScrollState(Enum):
    CLOSED = auto()
    OPENING = auto()
    OPEN = auto()
    CLOSING = auto()


class ControlsScroll:
    """Controla el spritesheet y la interacción del pergamino de controles."""

    COLUMNS = 4
    ROWS = 2
    FRAME_DURATION = 0.075

    def __init__(self, screen_size, assets_dir: Path):
        self.screen_size = screen_size
        self.state = ScrollState.CLOSED
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frames = []
        self.frame_offsets = []

        # Carga los recursos y separa el spritesheet en celdas ordenadas por filas.
        sheet = pygame.image.load(
            str(assets_dir / "Sprite de pergaminos antiguos.png")
        ).convert_alpha()
        frame_width = sheet.get_width() // self.COLUMNS
        frame_height = sheet.get_height() // self.ROWS
        self.frame_size = (frame_width, frame_height)
        if (
            sheet.get_width() % self.COLUMNS
            or sheet.get_height() % self.ROWS
        ):
            raise ValueError("El spritesheet del pergamino no tiene una cuadrícula válida.")

        for row in range(self.ROWS):
            for column in range(self.COLUMNS):
                cell = sheet.subsurface(
                    (
                        column * frame_width,
                        row * frame_height,
                        frame_width,
                        frame_height,
                    )
                ).copy()
                if row == 0 and column == self.COLUMNS - 1:
                    # El cuarto fotograma incluye parte del pergamino de la fila inferior.
                    cell = cell.subsurface((0, 0, frame_width, 420)).copy()
                bounds = cell.get_bounding_rect(min_alpha=1)
                if bounds.width == 0 or bounds.height == 0:
                    raise ValueError("El spritesheet contiene un fotograma vacío.")
                self.frames.append(cell.subsurface(bounds).copy())
                self.frame_offsets.append((bounds.x, bounds.y))

    def reset(self):
        """Vuelve al pergamino cerrado al entrar de nuevo en Controls."""
        self.state = ScrollState.CLOSED
        self.frame_index = 0
        self.frame_timer = 0.0

    def handle_enter(self):
        # Solo acepta ENTER en estados estables para evitar interrupciones.
        if self.state == ScrollState.CLOSED:
            self.state = ScrollState.OPENING
            self.frame_index = 0
            self.frame_timer = 0.0
        elif self.state == ScrollState.OPEN:
            self.state = ScrollState.CLOSING
            self.frame_index = len(self.frames) - 1
            self.frame_timer = 0.0

    def update(self, dt):
        """Avanza los fotogramas usando segundos y reporta el fin del cierre."""
        if self.state not in (ScrollState.OPENING, ScrollState.CLOSING):
            return False

        self.frame_timer += max(0.0, dt)
        while self.frame_timer >= self.FRAME_DURATION:
            self.frame_timer -= self.FRAME_DURATION

            if self.state == ScrollState.OPENING:
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
                else:
                    self.state = ScrollState.OPEN
                    self.frame_timer = 0.0
                    break
            else:
                if self.frame_index > 0:
                    self.frame_index -= 1
                else:
                    self.state = ScrollState.CLOSED
                    self.frame_timer = 0.0
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
