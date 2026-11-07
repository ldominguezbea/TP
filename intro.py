import math
import random

import pygame

from config import BASE_DIR, SCREEN_HEIGHT, SCREEN_WIDTH


class Intro:
    FRAMES_PER_CLOUD_STEP = 4
    CLOUD_TILE_SIZE = 128
    EARTH_RADIUS_RATIO = 0.215
    TEXT_DELAY_MS = 4500
    TYPEWRITER_INTERVAL_MS = 65
    TEXT_PHASE_PAUSE_MS = 1000
    TEXT_END_HOLD_MS = 2500
    TEXT_PHASES = ("Tierra, ", "30 de Diciembre de ", "2026")
    ZOOM_DURATION_MS = 5500
    CITY_ZOOM_DURATION_MS = 6500
    FINAL_ZOOM = 5.5
    FINAL_CITY_ZOOM = 8.0
    CITY_FOCUS_IMAGE_RATIO = (0.51, 0.52)
    FINAL_TEXT = "Buenos Aires, 2:38 AM"
    BLACK_TEXT_DELAY_MS = 450
    BLACK_TEXT_HOLD_MS = 2500
    PARK_FADE_MS = 1800
    PARK_DURATION_MS = 8000
    PARK_ZOOM_END = 1.60
    PARK_VANISHING_POINT = (0.50, 0.66)
    PARK_SKY_FOCUS = (0.50, 0.28)
    PARK_TREMOR_START_MS = 3500
    PARK_TREMOR_DURATION_MS = 2000
    PARK_TREMOR_RAMP_MS = 150
    PARK_TREMOR_MAX_PX = 5
    PARK_STILL_DURATION_MS = 1000
    PARK_LOOK_UP_START_MS = (
        PARK_TREMOR_START_MS + PARK_TREMOR_DURATION_MS + PARK_STILL_DURATION_MS
    )
    PARK_LOOK_UP_DURATION_MS = 1300
    PARK_RED_FADE_START_MS = PARK_LOOK_UP_START_MS
    PARK_RED_FADE_DURATION_MS = PARK_LOOK_UP_DURATION_MS
    PARK_RED_MAX_ALPHA = 185
    PARK_RED_COLOR = (58, 0, 0)
    PARK_RED_SKY_HEIGHT_RATIO = 0.48
    PARK_RED_FEATHER_RATIO = 0.12
    PARK_SWAY_FREQUENCY_HZ = 0.55
    PARK_VERTICAL_AMPLITUDE_PX = 1.5
    PARK_LATERAL_AMPLITUDE_PX = 1.5
    PARK_SETTLE_MS = 500
    BUENOS_AIRES_IMAGE_POSITION = (640, 525)
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
        self.scene_surface = pygame.Surface((screen_width, screen_height))
        self.buenos_aires_focus = (
            self.BUENOS_AIRES_IMAGE_POSITION[0] * scale + self.background_rect.left,
            self.BUENOS_AIRES_IMAGE_POSITION[1] * scale + self.background_rect.top,
        )

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

        city_path = BASE_DIR / "assets" / "fondos" / "ciudad_buenos_aires.png"
        city_image = pygame.image.load(str(city_path)).convert()
        city_width, city_height = city_image.get_size()
        city_scale = max(screen_width / city_width, screen_height / city_height)
        scaled_city = pygame.transform.smoothscale(
            city_image,
            (round(city_width * city_scale), round(city_height * city_scale)),
        )
        self.city_surface = pygame.Surface((screen_width, screen_height))
        self.city_rect = scaled_city.get_rect(
            center=self.city_surface.get_rect().center
        )
        self.city_surface.blit(scaled_city, self.city_rect)
        self.city_focus = (
            self.CITY_FOCUS_IMAGE_RATIO[0] * city_width * city_scale
            + self.city_rect.left,
            self.CITY_FOCUS_IMAGE_RATIO[1] * city_height * city_scale
            + self.city_rect.top,
        )
        night_tint = pygame.Surface(self.city_surface.get_size())
        night_tint.fill((112, 142, 215))
        self.city_surface.blit(
            night_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT
        )
        city_rng = random.Random(238)
        self.city_lights = []
        for _ in range(150):
            light_x = city_rng.randrange(screen_width)
            light_y = city_rng.randrange(screen_height)
            normalized_x = (light_x - self.city_rect.left) / scaled_city.get_width()
            normalized_y = (light_y - self.city_rect.top) / scaled_city.get_height()
            if 0.32 < normalized_x < 0.68 and 0.40 < normalized_y < 0.62:
                continue
            self.city_lights.append(
                (light_x, light_y, city_rng.random() * math.tau)
            )

        park_path = (
            BASE_DIR / "assets" / "fondos" / "parque_buenos_aires_nocturno.png"
        )
        park_image = pygame.image.load(str(park_path)).convert()
        park_width, park_height = park_image.get_size()
        park_scale = max(screen_width / park_width, screen_height / park_height)
        scaled_park = pygame.transform.smoothscale(
            park_image,
            (round(park_width * park_scale), round(park_height * park_scale)),
        )
        self.park_surface = pygame.Surface((screen_width, screen_height))
        self.park_surface.fill((5, 12, 27))
        self.park_rect = scaled_park.get_rect(
            center=self.park_surface.get_rect().center
        )
        self.park_surface.blit(scaled_park, self.park_rect)
        sky_height = round(screen_height * self.PARK_RED_SKY_HEIGHT_RATIO)
        self.park_sky_layer = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        self.park_sky_layer.blit(
            self.park_surface,
            (0, 0),
            (0, 0, screen_width, sky_height),
        )
        self.park_front_layer = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        self.park_front_layer.blit(
            self.park_surface,
            (0, sky_height),
            (0, sky_height, screen_width, screen_height - sky_height),
        )
        self.park_frame = pygame.Surface((screen_width, screen_height))
        self.park_vanishing_point = (
            self.park_rect.left
            + self.PARK_VANISHING_POINT[0] * park_width * park_scale,
            self.park_rect.top
            + self.PARK_VANISHING_POINT[1] * park_height * park_scale,
        )
        self.park_sky_focus_y = (
            self.park_rect.top + self.PARK_SKY_FOCUS[1] * park_height * park_scale
        )
        self.park_sky_red_overlay = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        feather_start = round(
            sky_height * (1 - self.PARK_RED_FEATHER_RATIO)
        )
        for y in range(sky_height):
            feather_progress = max(
                0.0,
                min(1.0, (y - feather_start) / (sky_height - feather_start)),
            )
            feather_progress = feather_progress * feather_progress * (
                3 - 2 * feather_progress
            )
            alpha = round(255 * (1 - feather_progress))
            pygame.draw.line(
                self.park_sky_red_overlay,
                (*self.PARK_RED_COLOR, alpha),
                (0, y),
                (screen_width - 1, y),
            )
        terror_sound_path = BASE_DIR / "assets" / "sonidos" / "gritos_distantes.wav"
        self.terror_sound = None
        if terror_sound_path.is_file():
            self.terror_sound = pygame.mixer.Sound(str(terror_sound_path))
        else:
            print(f"[INTRO] No se encontró el audio opcional: {terror_sound_path}")
        self.park_black_overlay = pygame.Surface((screen_width, screen_height))
        self.park_black_overlay.fill((0, 0, 0))
        self.park_effects = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        self.park_lamps = tuple(
            (
                round(self.park_rect.left + x * park_scale),
                round(self.park_rect.top + y * park_scale),
                phase,
            )
            for x, y, phase in (
                (47, 207, 0.2),
                (435, 215, 1.4),
                (770, 204, 2.7),
                (815, 275, 3.8),
                (916, 210, 5.1),
            )
        )
        park_rng = random.Random(2382)
        self.foliage = tuple(
            (
                round(self.park_rect.left + x * park_scale),
                round(self.park_rect.top + y * park_scale),
                park_rng.random() * math.tau,
                park_rng.choice(((92, 161, 130), (116, 178, 137), (72, 143, 125))),
            )
            for x, y in (
                (65, 53), (132, 87), (225, 38), (309, 104), (378, 72),
                (845, 63), (938, 105), (1030, 40), (1110, 92), (1170, 53),
            )
        )
        self.park_particles = tuple(
            (
                park_rng.randrange(self.park_rect.left, self.park_rect.right),
                park_rng.randrange(self.park_rect.top, self.park_rect.bottom),
                park_rng.uniform(5, 16),
                park_rng.random() * math.tau,
                park_rng.choice((1, 1, 2)),
            )
            for _ in range(34)
        )
        self.elapsed_ms = 0
        self.visible_text = ""
        self.text_font = pygame.font.SysFont("Consolas", 28, bold=True)
        self.text_color = (80, 255, 140)

    @property
    def text_complete_ms(self):
        return (
            self.TEXT_DELAY_MS
            + sum(
                max(0, len(phase) - 1) * self.TYPEWRITER_INTERVAL_MS
                for phase in self.TEXT_PHASES
            )
            + (len(self.TEXT_PHASES) - 1) * self.TEXT_PHASE_PAUSE_MS
        )

    @property
    def finished(self):
        return self.elapsed_ms >= (
            self.text_complete_ms
            + self.TEXT_END_HOLD_MS
            + self.ZOOM_DURATION_MS
            + self.CITY_ZOOM_DURATION_MS
            + self.BLACK_TEXT_DELAY_MS
            + (len(self.FINAL_TEXT) - 1) * self.TYPEWRITER_INTERVAL_MS
            + self.BLACK_TEXT_HOLD_MS
            + self.PARK_DURATION_MS
        )

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
        previous_elapsed_ms = self.elapsed_ms
        self.elapsed_ms += elapsed_ms
        park_start = (
            self.text_complete_ms
            + self.TEXT_END_HOLD_MS
            + self.ZOOM_DURATION_MS
            + self.CITY_ZOOM_DURATION_MS
            + self.BLACK_TEXT_DELAY_MS
            + (len(self.FINAL_TEXT) - 1) * self.TYPEWRITER_INTERVAL_MS
            + self.BLACK_TEXT_HOLD_MS
        )
        tremor_start = park_start + self.PARK_TREMOR_START_MS
        tremor_end = tremor_start + self.PARK_TREMOR_DURATION_MS
        if previous_elapsed_ms < tremor_start <= self.elapsed_ms:
            if self.terror_sound is not None:
                self.terror_sound.play()
        if previous_elapsed_ms < tremor_end <= self.elapsed_ms:
            if self.terror_sound is not None:
                self.terror_sound.stop()

        self.frame_counter += 1
        if self.frame_counter >= self.FRAMES_PER_CLOUD_STEP:
            self.frame_counter = 0
            self.cloud_offset = (self.cloud_offset + 1) % self.cloud_layer.get_width()
            self._update_cloud_layer()

        typing_elapsed = self.elapsed_ms - self.TEXT_DELAY_MS
        if typing_elapsed < 0:
            return

        self.visible_text = ""
        for index, phase in enumerate(self.TEXT_PHASES):
            phase_duration = max(0, len(phase) - 1) * self.TYPEWRITER_INTERVAL_MS
            if typing_elapsed < phase_duration:
                visible_characters = int(
                    typing_elapsed / self.TYPEWRITER_INTERVAL_MS
                ) + 1
                self.visible_text += phase[:visible_characters]
                return

            self.visible_text += phase
            typing_elapsed -= phase_duration
            if index < len(self.TEXT_PHASES) - 1:
                if typing_elapsed < self.TEXT_PHASE_PAUSE_MS:
                    return
                typing_elapsed -= self.TEXT_PHASE_PAUSE_MS

    def _draw_zoom_transition(self, progress):
        screen_width, screen_height = self.screen.get_size()
        eased_progress = progress * progress * (3 - 2 * progress)
        focus_x = screen_width / 2 + (
            self.buenos_aires_focus[0] - screen_width / 2
        ) * eased_progress
        focus_y = screen_height / 2 + (
            self.buenos_aires_focus[1] - screen_height / 2
        ) * eased_progress
        zoom = 1 + (self.FINAL_ZOOM - 1) * eased_progress

        self.scene_surface.blit(self.background, (0, 0))

        crop_width = max(1, round(screen_width / zoom))
        crop_height = max(1, round(screen_height / zoom))
        crop_x = max(
            0, min(screen_width - crop_width, round(focus_x - crop_width / 2))
        )
        crop_y = max(
            0, min(screen_height - crop_height, round(focus_y - crop_height / 2))
        )
        camera = self.scene_surface.subsurface(
            (crop_x, crop_y, crop_width, crop_height)
        )
        zoomed_scene = pygame.transform.smoothscale(
            camera, (screen_width, screen_height)
        )
        self.screen.blit(zoomed_scene, (0, 0))

        cloud_fade_progress = min(1.0, max(0.0, (progress - 0.08) / 0.68))
        cloud_fade = cloud_fade_progress * cloud_fade_progress * (
            3 - 2 * cloud_fade_progress
        )
        cloud_zoom = zoom * (1 + 1.8 * eased_progress)
        max_cloud_zoom = min(
            screen_width * 2.5 / self.cloud_layer.get_width(),
            screen_height * 2.5 / self.cloud_layer.get_height(),
        )
        cloud_zoom = min(cloud_zoom, max_cloud_zoom)
        cloud_size = (
            max(1, round(self.cloud_layer.get_width() * cloud_zoom)),
            max(1, round(self.cloud_layer.get_height() * cloud_zoom)),
        )
        scaled_clouds = pygame.transform.smoothscale(self.cloud_layer, cloud_size)
        scaled_clouds.set_alpha(round(255 * (1 - cloud_fade)))
        cloud_center = (
            round(
                screen_width / 2
                + (self.earth_rect.centerx - focus_x) * cloud_zoom
            ),
            round(
                screen_height / 2
                + (self.earth_rect.centery - focus_y) * cloud_zoom
            ),
        )
        self.screen.blit(scaled_clouds, scaled_clouds.get_rect(center=cloud_center))

        city_fade = min(1.0, max(0.0, (progress - 0.72) / 0.28))
        if city_fade:
            self.city_surface.set_alpha(round(255 * city_fade))
            self.screen.blit(self.city_surface, (0, 0))
            self.city_surface.set_alpha(255)

    def _draw_zoomed_surface(self, surface, zoom, focus):
        screen_width, screen_height = self.screen.get_size()
        crop_width = max(1, round(screen_width / zoom))
        crop_height = max(1, round(screen_height / zoom))
        crop_x = max(
            0, min(screen_width - crop_width, round(focus[0] - crop_width / 2))
        )
        crop_y = max(
            0, min(screen_height - crop_height, round(focus[1] - crop_height / 2))
        )
        crop = surface.subsurface((crop_x, crop_y, crop_width, crop_height))
        return pygame.transform.smoothscale(crop, (screen_width, screen_height))

    def _draw_city_zoom(self, progress):
        eased_progress = progress * progress * (3 - 2 * progress)
        zoom = 1 + (self.FINAL_CITY_ZOOM - 1) * eased_progress
        city_surface = self.city_surface.copy()
        elapsed_seconds = self.elapsed_ms / 1000
        for x, y, phase in self.city_lights:
            flicker = 0.5 + 0.5 * math.sin(elapsed_seconds * 2.8 + phase)
            if flicker > 0.56:
                color = (116, 158, 220) if flicker < 0.84 else (193, 205, 235)
                pygame.draw.rect(city_surface, color, (x, y, 2, 2))
        city_frame = self._draw_zoomed_surface(
            city_surface, zoom, self.city_focus
        )
        self.screen.blit(city_frame, (0, 0))

    def _draw_final_card(self, elapsed_ms):
        self.screen.fill((0, 0, 0))
        typing_elapsed = elapsed_ms - self.BLACK_TEXT_DELAY_MS
        if typing_elapsed < 0:
            return

        visible_characters = min(
            len(self.FINAL_TEXT),
            int(typing_elapsed / self.TYPEWRITER_INTERVAL_MS) + 1,
        )
        text_surface = self.text_font.render(
            self.FINAL_TEXT[:visible_characters], True, self.text_color
        )
        text_rect = text_surface.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text_surface, text_rect)

    def _park_camera(self, elapsed_ms):
        screen_width, screen_height = self.screen.get_size()
        elapsed_ms = min(max(0, elapsed_ms), self.PARK_DURATION_MS)
        walk_progress = min(1.0, elapsed_ms / self.PARK_TREMOR_START_MS)
        walk_strength = min(
            1.0,
            elapsed_ms / self.PARK_FADE_MS,
            max(
                0.0,
                (self.PARK_TREMOR_START_MS - elapsed_ms) / self.PARK_SETTLE_MS,
            ),
        )
        zoom_progress = walk_progress
        zoom = 1 + (self.PARK_ZOOM_END - 1) * zoom_progress
        phase = math.tau * elapsed_ms / 1000 * self.PARK_SWAY_FREQUENCY_HZ
        vertical_phase = 2 * phase
        vertical_offset = (
            math.sin(vertical_phase)
            * self.PARK_VERTICAL_AMPLITUDE_PX
            * walk_strength
        )
        lateral_sway = (
            math.sin(phase)
            * self.PARK_LATERAL_AMPLITUDE_PX
            * walk_strength
        )
        center_x = screen_width / 2 + (
            self.park_vanishing_point[0] - screen_width / 2
        ) * zoom_progress
        center_y = screen_height / 2 + (
            self.park_vanishing_point[1] - screen_height / 2
        ) * zoom_progress
        look_start = self.PARK_LOOK_UP_START_MS
        look_progress = min(
            1.0,
            max(
                0.0,
                (elapsed_ms - look_start) / self.PARK_LOOK_UP_DURATION_MS,
            ),
        )
        look_progress = look_progress * look_progress * (3 - 2 * look_progress)
        center_y += (self.park_sky_focus_y - center_y) * look_progress
        return (
            zoom,
            center_x + lateral_sway,
            center_y + vertical_offset,
        )

    def _draw_park_scene(self, elapsed_ms):
        self.screen.fill((0, 0, 0))
        fade_progress = min(1.0, elapsed_ms / self.PARK_FADE_MS)
        seconds = elapsed_ms / 1000
        frame = self.park_frame
        frame.fill((5, 12, 27, 255))
        frame.blit(self.park_sky_layer, (0, 0))
        red_progress = min(
            1.0,
            max(
                0.0,
                (elapsed_ms - self.PARK_RED_FADE_START_MS)
                / self.PARK_RED_FADE_DURATION_MS,
            ),
        )
        if red_progress:
            red_alpha = round(self.PARK_RED_MAX_ALPHA * red_progress)
            self.park_sky_red_overlay.set_alpha(red_alpha)
            frame.blit(self.park_sky_red_overlay, (0, 0))
        frame.blit(self.park_front_layer, (0, 0))
        effects = self.park_effects
        effects.fill((0, 0, 0, 0))
        for x, y, phase in self.park_lamps:
            flicker = (0.5 + 0.5 * math.sin(seconds * 2.1 + phase)) * fade_progress
            glow_alpha = round(18 + 24 * flicker)
            pygame.draw.circle(effects, (132, 207, 198, glow_alpha), (x, y), 30)
            pygame.draw.circle(effects, (198, 227, 186, glow_alpha + 18), (x, y), 9)

        for index, (source_x, source_y) in enumerate(
            ((470, 322), (550, 347), (635, 329), (720, 355), (825, 334))
        ):
            puddle_x = round(self.park_rect.left + source_x * (self.park_rect.width / 1200))
            puddle_y = round(self.park_rect.top + source_y * (self.park_rect.width / 1200))
            shimmer = 0.5 + 0.5 * math.sin(seconds * 1.7 + index * 1.9)
            shimmer_alpha = round((8 + shimmer * 23) * fade_progress)
            pygame.draw.ellipse(
                effects,
                (103, 191, 210, shimmer_alpha),
                (puddle_x - 17, puddle_y - 2, 34, 4),
            )

        for x, y, phase, color in self.foliage:
            sway_x = round(math.sin(seconds * 1.2 + phase) * 3)
            sway_y = round(math.sin(seconds * 0.9 + phase) * 2)
            leaf_alpha = round((24 + 14 * math.sin(seconds * 1.1 + phase)) * fade_progress)
            for dx, dy in ((0, 0), (5, -2), (-4, 3)):
                pygame.draw.ellipse(
                    effects,
                    (*color, leaf_alpha),
                    (x + sway_x + dx, y + sway_y + dy, 7, 4),
                )

        for x, y, speed, phase, radius in self.park_particles:
            particle_y = round(
                self.park_rect.top
                + (y - self.park_rect.top + seconds * speed) % self.park_rect.height
            )
            particle_x = round(
                max(
                    self.park_rect.left,
                    min(
                        self.park_rect.right - 1,
                        x + math.sin(seconds * 0.7 + phase) * 8,
                    ),
                )
            )
            brightness = 0.5 + 0.5 * math.sin(seconds * 1.5 + phase)
            alpha = round((35 + brightness * 100) * fade_progress)
            pygame.draw.circle(
                effects,
                (180, 226, 218, alpha),
                (particle_x, particle_y),
                radius,
            )

        frame.blit(effects, (0, 0))

        zoom, center_x, center_y = self._park_camera(elapsed_ms)
        screen_width, screen_height = self.screen.get_size()
        scaled_size = (
            max(1, round(screen_width * zoom)),
            max(1, round(screen_height * zoom)),
        )
        scaled_frame = pygame.transform.smoothscale(frame, scaled_size)
        shake_x = 0
        shake_y = 0
        tremor_elapsed = elapsed_ms - self.PARK_TREMOR_START_MS
        if 0 <= tremor_elapsed < self.PARK_TREMOR_DURATION_MS:
            ramp_in = min(1.0, tremor_elapsed / self.PARK_TREMOR_RAMP_MS)
            ramp_out = min(
                1.0,
                (self.PARK_TREMOR_DURATION_MS - tremor_elapsed)
                / self.PARK_TREMOR_RAMP_MS,
            )
            tremor_progress = min(ramp_in, ramp_out)
            frame_index = round(elapsed_ms * 60 / 1000)
            shake_rng = random.Random(frame_index + 947)
            shake_x = round(
                shake_rng.uniform(-1, 1) * self.PARK_TREMOR_MAX_PX * tremor_progress
            )
            shake_y = round(
                shake_rng.uniform(-1, 1) * self.PARK_TREMOR_MAX_PX * tremor_progress
            )
        dest_rect = scaled_frame.get_rect(
            topleft=(
                round(screen_width / 2 - center_x * zoom) + shake_x,
                round(screen_height / 2 - center_y * zoom) + shake_y,
            )
        )
        self.screen.blit(scaled_frame, dest_rect)
        if fade_progress < 1:
            self.park_black_overlay.set_alpha(round(255 * (1 - fade_progress)))
            self.screen.blit(self.park_black_overlay, (0, 0))

    def draw(self):
        transition_start = self.text_complete_ms + self.TEXT_END_HOLD_MS
        city_start = transition_start + self.ZOOM_DURATION_MS
        black_start = city_start + self.CITY_ZOOM_DURATION_MS
        park_start = (
            black_start
            + self.BLACK_TEXT_DELAY_MS
            + (len(self.FINAL_TEXT) - 1) * self.TYPEWRITER_INTERVAL_MS
            + self.BLACK_TEXT_HOLD_MS
        )
        park_end = park_start + self.PARK_DURATION_MS

        if self.elapsed_ms < transition_start:
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.cloud_layer, self.earth_rect.topleft)
        elif self.elapsed_ms < city_start:
            progress = min(
                1.0,
                (self.elapsed_ms - transition_start) / self.ZOOM_DURATION_MS,
            )
            self._draw_zoom_transition(progress)
        elif self.elapsed_ms < black_start:
            city_elapsed = self.elapsed_ms - city_start
            progress = min(1.0, city_elapsed / self.CITY_ZOOM_DURATION_MS)
            self._draw_city_zoom(progress)
        elif self.elapsed_ms < park_start:
            self._draw_final_card(self.elapsed_ms - black_start)
        elif self.elapsed_ms < park_end:
            self._draw_park_scene(self.elapsed_ms - park_start)
        else:
            self._draw_park_scene(self.PARK_DURATION_MS)

        if self.elapsed_ms < city_start and self.visible_text:
            text_surface = self.text_font.render(
                self.visible_text, True, self.text_color
            )
            fade_progress = min(
                1.0,
                max(
                    0.0,
                    (self.elapsed_ms - transition_start)
                    / (self.ZOOM_DURATION_MS * 0.16),
                ),
            )
            text_surface.set_alpha(round(255 * (1 - fade_progress)))
            self.screen.blit(text_surface, (28, 24))


def run_intro():
    pygame.init()
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("REQUIEM: Introducción")
        clock = pygame.time.Clock()
        intro = Intro(screen)
        running = True

        while running and not intro.finished:
            elapsed_ms = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if running:
                intro.update(elapsed_ms)
                intro.draw()
                pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    run_intro()
