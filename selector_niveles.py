import math
import pygame

from efectos_selector_de_niveles import SwirlCursor, draw_fire_icon


class LevelSelector:
    def __init__(self, screen, audio):
        self.screen = screen
        self.audio = audio
        width, height = screen.get_size()

        # Posición central para el planeta gigante enfocado
        self.center_pos = (width // 2, int(height * 0.48))
        self.selected_index = 0
        self.confirmed_level = None
        self.total_levels = 4

        # El cursor de remolino se posiciona en el centro
        self.cursor = SwirlCursor(screen.get_size())
        self.cursor.snap(*self.center_pos)

        # Fuentes
        self.title_font = pygame.font.SysFont("Impact", 56)
        self.level_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.detail_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.help_font = pygame.font.SysFont("Arial", 18, bold=True)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            direction = -1 if event.key == pygame.K_LEFT else 1
            prev_index = self.selected_index
            self.selected_index = (self.selected_index + direction) % self.total_levels

            if prev_index != self.selected_index:
                self.confirmed_level = None
                self.audio.travel()
                # Transición de audio si cambia entre Tierra (0..2) y Gehena (3)
                if (prev_index == 3) != (self.selected_index == 3):
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
        environment = 1.0 if self.selected_index == 3 else 0.0
        self.cursor.update(*self.center_pos, 1.0, elapsed_ms)
        self.audio.update_ambient(environment)

    def draw_earth_planet_3d(self, screen, cx, cy, radius, ticks):
        """Renderiza la Tierra con efecto de esfera 3D, continentes proyectados y sombra difusa."""
        # 1. Base del océano
        pygame.draw.circle(screen, (15, 80, 155), (cx, cy), radius)

        # 2. Continentes en rotación lateral (Proyección esférica 3D básica)
        planet_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        angle = ticks * 0.0015

        # Continentes moviéndose en eje X para simular rotación planetaria
        for i in range(3):
            shift = ((angle + i * 2.1) % math.tau) - math.pi
            # Factor 3D: los continentes se comprimen cerca de los bordes (cos)
            px = radius + math.sin(shift) * (radius * 0.7)
            py = radius + math.cos(i * 1.5) * (radius * 0.35) - 10
            scale_w = int((radius * 0.6) * abs(math.cos(shift)))
            scale_h = int(radius * 0.4)

            if scale_w > 4:
                pygame.draw.ellipse(
                    planet_surf,
                    (45, 165, 80),
                    (int(px - scale_w // 2), int(py - scale_h // 2), scale_w, scale_h),
                )

        # Máscara circular para mantener los continentes dentro del cuerpo celeste
        mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255), (radius, radius), radius)
        planet_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(planet_surf, (cx - radius, cy - radius))

        # 3. Sombra de volumen 3D (Luz desde arriba a la izquierda)
        shadow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Sombra en degradado proyectada a la derecha e inferior
        pygame.draw.circle(
            shadow_surf, (5, 10, 25, 160), (radius + 18, radius + 15), radius - 5
        )
        shadow_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(shadow_surf, (cx - radius, cy - radius))

        # 4. Resplandor / Atmósfera exterior brillante
        pygame.draw.circle(screen, (130, 215, 255), (cx, cy), radius, 5)

    def draw(self, ticks):
        screen = self.screen
        width, height = screen.get_size()
        cx, cy = self.center_pos
        radius = 120  # Planeta gigante central

        # --- Título ---
        title = self.title_font.render("SELECCIONA UN NIVEL", True, (245, 235, 220))
        screen.blit(title, title.get_rect(center=(width // 2, int(height * 0.12))))

        # --- Flechas de navegación 3D a los lados del planeta ---
        pulse = math.sin(ticks * 0.006) * 8
        arrow_l = self.title_font.render("<", True, (235, 185, 40))
        arrow_r = self.title_font.render(">", True, (235, 185, 40))

        screen.blit(
            arrow_l,
            arrow_l.get_rect(center=(cx - radius - 80 - int(pulse), cy)),
        )
        screen.blit(
            arrow_r,
            arrow_r.get_rect(center=(cx + radius + 80 + int(pulse), cy)),
        )

        # --- Sombra proyectada por el planeta sobre el suelo ---
        pygame.draw.ellipse(
            screen, (10, 5, 10, 180), (cx - radius, cy + radius + 10, radius * 2, 35)
        )

        # --- Dibujado del planeta seleccionado ---
        if self.selected_index == 3:
            # Planeta 4: Gehena (fuego/demonio gigante)
            draw_fire_icon(screen, cx, cy, radius, ticks)
        else:
            # Planetas 1, 2, 3: Tierra 3D
            self.draw_earth_planet_3d(screen, cx, cy, radius, ticks)

        # Remolino de luz / Efecto del cursor sobre el planeta
        self.cursor.draw(screen, radius, ticks)

        # --- Información del nivel (Número y Mundo) ---
        world_name = "GEHENA" if self.selected_index == 3 else "TIERRA"
        color = (245, 110, 45) if self.selected_index == 3 else (90, 190, 255)

        lbl_level = self.level_font.render(
            f"NIVEL {self.selected_index + 1}", True, (255, 255, 255)
        )
        lbl_rect = lbl_level.get_rect(center=(cx, cy + radius + 65))
        screen.blit(lbl_level, lbl_rect)

        lbl_world = self.detail_font.render(world_name, True, color)
        screen.blit(lbl_world, lbl_world.get_rect(center=(cx, cy + radius + 100)))

        # --- Menú inferior de ayuda ---
        if self.confirmed_level is None:
            help_text = "[← / →] CAMBIAR PLANETA   |   [ENTER] ELEGIR   |   [M] SILENCIO   |   [ESC] VOLVER"
        else:
            help_text = f"¡NIVEL {self.confirmed_level} SELECCIONADO!"

        help_surface = self.help_font.render(help_text, True, (245, 205, 90))
        screen.blit(
            help_surface,
            help_surface.get_rect(center=(width // 2, int(height * 0.90))),
        )