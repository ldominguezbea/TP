import pygame

from efectos_selector_de_niveles import SwirlCursor, draw_fire_icon


class LevelSelector:
    def __init__(self, screen, audio):
        self.screen = screen
        self.audio = audio
        width, height = screen.get_size()
        self.positions = [
            (int(width * fraction), int(height * row))
            for fraction, row in (
                (0.16, 0.52),
                (0.39, 0.62),
                (0.62, 0.52),
                (0.85, 0.62),
            )
        ]
        self.selected_index = 0
        self.confirmed_level = None
        self.cursor = SwirlCursor(screen.get_size())
        self.cursor.snap(*self.positions[self.selected_index])
        self.title_font = pygame.font.SysFont("Impact", 54)
        self.level_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.detail_font = pygame.font.SysFont("Arial", 17, bold=True)
        self.help_font = pygame.font.SysFont("Arial", 18, bold=True)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            direction = -1 if event.key == pygame.K_LEFT else 1
            next_index = (self.selected_index + direction) % len(self.positions)
            if next_index != self.selected_index:
                changed_world = (self.selected_index == 3) != (next_index == 3)
                self.selected_index = next_index
                self.confirmed_level = None
                self.audio.travel()
                if changed_world:
                    self.audio.planet_switch()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.confirmed_level = self.selected_index + 1
            self.audio.confirm()
            return self.confirmed_level
        elif event.key == pygame.K_ESCAPE:
            return "back"
        elif event.key == pygame.K_m:
            self.audio.toggle_mute()

        return None

    def update(self, elapsed_ms):
        target = self.positions[self.selected_index]
        environment = 1.0 if self.selected_index == 3 else 0.0
        self.cursor.update(*target, 1.0, elapsed_ms)
        self.audio.update_ambient(environment)

    def draw(self, ticks):
        screen = self.screen
        width, height = screen.get_size()
        title = self.title_font.render("SELECCIONA UN NIVEL", True, (245, 235, 220))
        screen.blit(title, title.get_rect(center=(width // 2, height * 0.19)))

        for index in range(len(self.positions) - 1):
            pygame.draw.line(
                screen,
                (125, 105, 95),
                self.positions[index],
                self.positions[index + 1],
                5,
            )

        for index, (x, y) in enumerate(self.positions):
            selected = index == self.selected_index
            radius = 48 if selected else 40
            color = (90, 185, 255) if index < 3 else (235, 90, 35)

            if index == 3:
                draw_fire_icon(screen, x, y, radius, ticks)
            else:
                pygame.draw.circle(screen, (14, 20, 32), (x, y), radius + 7)
                pygame.draw.circle(screen, color, (x, y), radius, 5 if selected else 3)
                pygame.draw.circle(screen, (35, 55, 75), (x, y), radius - 8)
                number = self.level_font.render(str(index + 1), True, (245, 245, 250))
                screen.blit(number, number.get_rect(center=(x, y)))

            label = self.level_font.render(f"NIVEL {index + 1}", True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=(x, y + radius + 35)))
            world_name = "GEHENA" if index == 3 else "TIERRA"
            detail = self.detail_font.render(world_name, True, color)
            screen.blit(detail, detail.get_rect(center=(x, y + radius + 60)))

        self.cursor.draw(screen, 42, ticks)

        if self.confirmed_level is None:
            help_text = "[←/→] MOVER   [ENTER] ELEGIR   [M] SILENCIO   [ESC] VOLVER"
        else:
            help_text = f"NIVEL {self.confirmed_level} SELECCIONADO"
        help_surface = self.help_font.render(help_text, True, (245, 205, 90))
        screen.blit(help_surface, help_surface.get_rect(center=(width // 2, height - 48)))
