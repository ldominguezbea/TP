import random

import pygame

from config import BASE_DIR


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
    URBAN_DURATION_MS = 6500
    CITY_HOLD_MS = 0
    FINAL_ZOOM = 5.5
    FINAL_STREET_ZOOM = 8.0
    CITY_SIZE = (450, 240)
    PLAZA_MAYO_CENTER = (225, 120)
    STREET_PEDESTRIAN_HEAD = (94, 151)
    FINAL_TEXT = "Buenos Aires, 3:04 PM"
    BLACK_TEXT_DELAY_MS = 450
    BLACK_TEXT_INTERVAL_MS = 115
    BLACK_TEXT_HOLD_MS = 1400
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

        city_surface = self._make_plaza_mayo_surface()
        self.city_surface = pygame.transform.scale(
            city_surface, (screen_width, screen_height)
        )
        street_surface = self._make_street_level_surface()
        self.street_surface = pygame.transform.scale(
            street_surface, (screen_width, screen_height)
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
            + self.URBAN_DURATION_MS
            + self.CITY_HOLD_MS
            + self.BLACK_TEXT_DELAY_MS
            + (len(self.FINAL_TEXT) - 1) * self.BLACK_TEXT_INTERVAL_MS
            + self.BLACK_TEXT_HOLD_MS
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

    @classmethod
    def _make_plaza_mayo_surface(cls):
        width, height = cls.CITY_SIZE
        city = pygame.Surface(cls.CITY_SIZE)
        city.fill((48, 51, 49))
        rng = random.Random(25)
        plaza = pygame.Rect(160, 91, 130, 58)
        landmarks = (
            plaza.inflate(7, 7),
            pygame.Rect(124, 94, 34, 53),
            pygame.Rect(170, 67, 55, 26),
            pygame.Rect(268, 91, 57, 58),
        )

        for road_x in range(0, width, 47):
            pygame.draw.rect(city, (68, 70, 67), (road_x, 0, 6, height))
            pygame.draw.line(
                city,
                (79, 80, 74),
                (road_x + 1, 0),
                (road_x + 1, height),
            )
        for road_y in range(0, height, 39):
            pygame.draw.rect(city, (68, 70, 67), (0, road_y, width, 5))
            pygame.draw.line(
                city,
                (79, 80, 74),
                (0, road_y + 1),
                (width, road_y + 1),
            )

        roof_colors = (
            (165, 151, 128),
            (186, 171, 146),
            (132, 139, 137),
            (198, 185, 157),
            (146, 132, 116),
            (119, 128, 127),
        )
        for block_x in range(7, width - 38, 47):
            for block_y in range(7, height - 30, 39):
                block = pygame.Rect(block_x, block_y, 39, 31)
                if any(block.colliderect(area) for area in landmarks):
                    continue
                pygame.draw.rect(city, (105, 99, 84), block)
                pygame.draw.rect(city, (139, 130, 108), block.inflate(-2, -2))

                courtyard = pygame.Rect(
                    block.left + rng.randrange(12, 17),
                    block.top + rng.randrange(9, 13),
                    rng.randrange(7, 12),
                    rng.randrange(5, 8),
                )
                pygame.draw.rect(city, (67, 82, 60), courtyard.inflate(2, 2))
                pygame.draw.rect(city, (111, 126, 79), courtyard)
                pygame.draw.rect(
                    city,
                    (49, 65, 52),
                    (courtyard.centerx - 1, courtyard.centery - 1, 3, 3),
                )

                for _ in range(rng.randrange(5, 9)):
                    building_width = rng.randrange(5, 11)
                    building_height = rng.randrange(4, 9)
                    building = pygame.Rect(
                        rng.randrange(
                            block.left + 2, block.right - building_width - 1
                        ),
                        rng.randrange(
                            block.top + 2, block.bottom - building_height - 1
                        ),
                        building_width,
                        building_height,
                    )
                    if building.colliderect(courtyard):
                        continue
                    roof = rng.choice(roof_colors)
                    pygame.draw.rect(city, (77, 73, 63), building.move(1, 1))
                    pygame.draw.rect(city, roof, building)
                    pygame.draw.line(
                        city,
                        tuple(min(255, channel + 22) for channel in roof),
                        building.topleft,
                        (building.right - 1, building.top),
                    )
                    if building.width > 6 and building.height > 5:
                        city.set_at(building.center, (111, 115, 106))

                for _ in range(3):
                    vent = (
                        rng.randrange(block.left + 3, block.right - 3),
                        rng.randrange(block.top + 3, block.bottom - 3),
                    )
                    city.set_at(vent, (219, 204, 170))

        for road_x in (120, 335):
            pygame.draw.rect(city, (90, 83, 69), (road_x, 0, 11, height))
            pygame.draw.line(
                city,
                (177, 152, 112),
                (road_x + 1, 0),
                (road_x + 1, height),
            )
            for dash_y in range(4, height, 16):
                pygame.draw.rect(city, (209, 187, 142), (road_x + 6, dash_y, 1, 7))
        for road_y in (69, 158):
            pygame.draw.rect(city, (90, 83, 69), (0, road_y, width, 10))
            pygame.draw.line(
                city, (177, 152, 112), (0, road_y + 1), (width, road_y + 1)
            )
            for dash_x in range(4, width, 18):
                pygame.draw.rect(city, (209, 187, 142), (dash_x, road_y + 5, 8, 1))

        pygame.draw.rect(city, (135, 120, 94), plaza.inflate(4, 4))
        pygame.draw.rect(city, (187, 164, 125), plaza)
        pygame.draw.rect(city, (224, 205, 163), plaza.inflate(-3, -3), 1)

        for garden in (
            pygame.Rect(166, 97, 34, 46),
            pygame.Rect(207, 97, 37, 46),
            pygame.Rect(251, 97, 33, 46),
        ):
            pygame.draw.rect(city, (111, 79, 58), garden)
            pygame.draw.rect(city, (62, 103, 58), garden.inflate(-3, -3))
            pygame.draw.rect(city, (79, 126, 67), garden.inflate(-7, -7), 1)
            pygame.draw.line(
                city,
                (215, 191, 148),
                (garden.centerx, garden.top + 3),
                (garden.centerx, garden.bottom - 4),
            )
            pygame.draw.line(
                city,
                (215, 191, 148),
                (garden.left + 3, garden.centery),
                (garden.right - 4, garden.centery),
            )
            for tree_x, tree_y in (
                (garden.left + 5, garden.top + 5),
                (garden.right - 7, garden.top + 5),
                (garden.left + 5, garden.bottom - 7),
                (garden.right - 7, garden.bottom - 7),
            ):
                pygame.draw.rect(city, (43, 74, 47), (tree_x, tree_y, 4, 4))
                pygame.draw.rect(
                    city, (106, 143, 75), (tree_x + 1, tree_y + 1, 2, 2)
                )

        pygame.draw.rect(city, (91, 71, 55), (218, 112, 15, 17))
        pygame.draw.rect(city, (231, 218, 185), (217, 111, 15, 16))
        pygame.draw.polygon(
            city,
            (205, 198, 179),
            ((224, 112), (219, 121), (229, 121)),
        )
        pygame.draw.line(city, (255, 246, 219), (224, 112), (224, 121))
        pygame.draw.rect(city, (130, 119, 98), (220, 122, 9, 2))

        cabildo = pygame.Rect(128, 102, 27, 35)
        pygame.draw.rect(city, (87, 79, 66), cabildo.move(2, 2))
        pygame.draw.rect(city, (218, 207, 178), cabildo)
        pygame.draw.rect(
            city, (169, 157, 133), (cabildo.x + 2, cabildo.y + 3, 23, 29)
        )
        pygame.draw.rect(
            city, (226, 216, 191), (cabildo.x + 7, cabildo.y + 7, 13, 20)
        )
        pygame.draw.rect(
            city, (195, 183, 157), (cabildo.centerx - 3, cabildo.y - 7, 7, 8)
        )
        pygame.draw.rect(
            city, (228, 219, 194), (cabildo.centerx - 2, cabildo.y - 5, 4, 4)
        )
        for window_y in (cabildo.y + 10, cabildo.y + 17, cabildo.y + 24):
            for window_x in (cabildo.x + 4, cabildo.x + 20):
                pygame.draw.rect(city, (71, 88, 91), (window_x, window_y, 2, 3))

        cathedral = pygame.Rect(176, 75, 43, 13)
        pygame.draw.rect(city, (91, 81, 67), cathedral.move(1, 2))
        pygame.draw.rect(city, (211, 203, 184), cathedral)
        pygame.draw.rect(
            city, (239, 230, 209), (cathedral.x + 4, cathedral.y + 3, 35, 7)
        )
        pygame.draw.rect(
            city, (185, 175, 153), (cathedral.x + 17, cathedral.y + 4, 9, 6)
        )
        for tower_x in (cathedral.x + 4, cathedral.right - 9):
            pygame.draw.rect(
                city, (201, 188, 163), (tower_x, cathedral.y - 4, 6, 6)
            )
            pygame.draw.rect(
                city, (230, 219, 191), (tower_x + 2, cathedral.y - 3, 2, 3)
            )
        for column_x in range(cathedral.x + 7, cathedral.right - 7, 5):
            pygame.draw.line(
                city,
                (153, 145, 128),
                (column_x, cathedral.y + 4),
                (column_x, cathedral.y + 9),
            )

        casa = pygame.Rect(272, 98, 49, 48)
        pygame.draw.rect(city, (78, 64, 57), casa.move(2, 2))
        pygame.draw.rect(city, (191, 124, 105), casa)
        pygame.draw.rect(city, (222, 164, 143), (casa.x + 3, casa.y + 3, 43, 40))
        pygame.draw.rect(city, (237, 191, 163), (casa.x + 5, casa.y + 5, 39, 7))
        pygame.draw.rect(city, (176, 110, 97), (casa.x + 7, casa.y + 15, 35, 26))
        pygame.draw.rect(city, (234, 224, 199), (casa.x + 13, casa.y + 20, 23, 15))
        pygame.draw.rect(city, (190, 144, 117), (casa.x + 16, casa.y + 23, 17, 9))
        for wing_x in (casa.x + 4, casa.right - 9):
            pygame.draw.rect(city, (220, 151, 130), (wing_x, casa.y + 14, 5, 27))
            for window_y in (casa.y + 17, casa.y + 24, casa.y + 31):
                pygame.draw.rect(city, (92, 83, 76), (wing_x + 1, window_y, 2, 3))
        pygame.draw.rect(city, (230, 177, 146), (casa.x + 19, casa.y + 8, 11, 5))
        pygame.draw.rect(city, (242, 207, 171), (casa.x + 22, casa.y + 6, 5, 3))
        pygame.draw.line(
            city,
            (244, 202, 170),
            (casa.x + 6, casa.y + 12),
            (casa.right - 5, casa.y + 12),
        )

        for car_x, car_y, color, vertical in (
            (51, 73, (187, 65, 49), True),
            (91, 74, (222, 210, 177), True),
            (353, 74, (67, 111, 151), True),
            (386, 159, (205, 184, 137), True),
            (52, 181, (74, 117, 153), True),
            (111, 159, (181, 77, 53), True),
            (29, 174, (205, 193, 166), False),
            (367, 67, (210, 201, 171), False),
            (341, 168, (181, 76, 51), False),
        ):
            vehicle = pygame.Surface((3, 6) if vertical else (6, 3))
            vehicle.fill(color)
            window_rect = (1, 1, 1, 3) if vertical else (1, 1, 3, 1)
            pygame.draw.rect(vehicle, (69, 88, 94), window_rect)
            city.blit(vehicle, (car_x, car_y))

        for person_x, person_y, color in (
            (160, 88, (228, 218, 188)),
            (205, 151, (172, 65, 51)),
            (240, 87, (225, 210, 176)),
            (292, 152, (71, 104, 139)),
            (116, 105, (221, 214, 194)),
            (333, 129, (191, 74, 58)),
            (72, 152, (230, 219, 185)),
            (388, 112, (205, 193, 167)),
        ):
            city.set_at((person_x, person_y), (42, 37, 32))
            city.set_at((person_x, person_y - 1), color)

        return city

    @classmethod
    def _make_street_level_surface(cls):
        width, height = cls.CITY_SIZE
        street = pygame.Surface(cls.CITY_SIZE)
        street.fill((91, 137, 158))
        rng = random.Random(38)
        pygame.draw.rect(street, (118, 112, 96), (0, 90, width, height - 90))

        for x, y, building_width, building_height, color in (
            (12, 12, 72, 81, (126, 111, 91)),
            (91, 4, 67, 94, (169, 147, 116)),
            (307, 10, 59, 87, (146, 132, 115)),
            (370, 0, 68, 96, (178, 157, 127)),
        ):
            facade = pygame.Rect(x, y, building_width, building_height)
            pygame.draw.rect(street, (72, 69, 63), facade.move(3, 3))
            pygame.draw.rect(street, color, facade)
            pygame.draw.rect(
                street,
                tuple(min(255, channel + 22) for channel in color),
                (facade.x, facade.y, facade.width, 4),
            )
            for window_y in range(facade.y + 10, facade.bottom - 8, 15):
                for window_x in range(facade.x + 7, facade.right - 7, 14):
                    window_color = rng.choice(
                        ((62, 88, 98), (83, 106, 111), (193, 169, 128))
                    )
                    pygame.draw.rect(
                        street, (82, 75, 64), (window_x - 2, window_y - 2, 9, 11)
                    )
                    pygame.draw.rect(
                        street, window_color, (window_x, window_y, 5, 7)
                    )
                    pygame.draw.line(
                        street,
                        (205, 190, 160),
                        (window_x + 2, window_y),
                        (window_x + 2, window_y + 6),
                    )
            for balcony_y in range(facade.y + 19, facade.bottom - 12, 30):
                pygame.draw.rect(
                    street,
                    (84, 76, 65),
                    (facade.x + 4, balcony_y + 8, facade.width - 8, 2),
                )
                for rail_x in range(facade.x + 7, facade.right - 5, 7):
                    street.set_at((rail_x, balcony_y + 6), (199, 183, 151))

        pygame.draw.polygon(
            street,
            (172, 142, 108),
            ((0, 91), (201, 88), (165, 133), (91, height), (0, height)),
        )
        pygame.draw.polygon(
            street,
            (185, 153, 113),
            ((250, 88), (width, 92), (width, height), (355, height), (284, 133)),
        )
        pygame.draw.polygon(
            street,
            (57, 62, 63),
            ((201, 88), (250, 88), (355, height), (91, height)),
        )
        pygame.draw.polygon(
            street,
            (81, 83, 79),
            ((205, 94), (210, 94), (132, height), (120, height)),
        )
        pygame.draw.polygon(
            street,
            (81, 83, 79),
            ((244, 94), (249, 94), (326, height), (314, height)),
        )

        for index in range(6):
            stripe_width = 1 + index
            stripe_y = 178 + index * 8
            stripe_x = 226 - stripe_width // 2
            pygame.draw.rect(
                street,
                (218, 210, 184),
                (stripe_x, stripe_y, stripe_width, 3 + index // 2),
            )

        for canopy_x, canopy_y, radius in (
            (24, 119, 18),
            (56, 111, 17),
            (383, 119, 18),
            (419, 109, 20),
        ):
            pygame.draw.rect(
                street,
                (57, 84, 56),
                (canopy_x - radius, canopy_y - radius, radius * 2, radius * 2),
            )
            for leaf_x, leaf_y, leaf_color in (
                (-10, -5, (81, 119, 68)),
                (-3, -11, (104, 139, 75)),
                (5, -4, (73, 111, 63)),
                (10, 4, (96, 130, 69)),
                (-7, 7, (69, 102, 59)),
                (2, 6, (116, 145, 78)),
            ):
                pygame.draw.rect(
                    street,
                    leaf_color,
                    (canopy_x + leaf_x, canopy_y + leaf_y, 8, 7),
                )

        for car_x, car_y, color, car_width, car_height in (
            (178, 171, (151, 53, 43), 15, 24),
            (251, 184, (57, 96, 129), 18, 29),
            (196, 209, (192, 176, 142), 23, 31),
        ):
            car = pygame.Rect(car_x, car_y, car_width, car_height)
            pygame.draw.rect(street, (37, 39, 38), car.inflate(3, 2))
            pygame.draw.rect(street, color, car)
            pygame.draw.rect(
                street,
                (73, 95, 101),
                (car.x + 3, car.y + 5, car.width - 6, car.height // 3),
            )
            pygame.draw.rect(
                street,
                (188, 193, 177),
                (car.x + 2, car.y + 2, car.width - 4, 2),
            )
            pygame.draw.rect(
                street,
                (224, 202, 144),
                (car.x + 2, car.bottom - 4, 3, 2),
            )
            pygame.draw.rect(
                street,
                (224, 202, 144),
                (car.right - 5, car.bottom - 4, 3, 2),
            )

        pedestrian_x, pedestrian_y = cls.STREET_PEDESTRIAN_HEAD
        pygame.draw.ellipse(
            street,
            (61, 52, 45),
            (pedestrian_x - 8, pedestrian_y + 20, 17, 5),
        )
        pygame.draw.rect(
            street,
            (42, 40, 37),
            (pedestrian_x - 5, pedestrian_y + 13, 4, 12),
        )
        pygame.draw.rect(
            street,
            (42, 40, 37),
            (pedestrian_x + 1, pedestrian_y + 13, 4, 12),
        )
        pygame.draw.rect(
            street,
            (49, 73, 92),
            (pedestrian_x - 7, pedestrian_y + 4, 14, 12),
        )
        pygame.draw.rect(
            street,
            (80, 105, 121),
            (pedestrian_x - 5, pedestrian_y + 5, 10, 4),
        )
        pygame.draw.rect(
            street,
            (197, 151, 111),
            (pedestrian_x - 5, pedestrian_y - 7, 10, 11),
        )
        pygame.draw.rect(
            street,
            (48, 41, 37),
            (pedestrian_x - 6, pedestrian_y - 9, 12, 5),
        )
        pygame.draw.rect(
            street,
            (228, 185, 132),
            (pedestrian_x - 3, pedestrian_y - 3, 2, 2),
        )
        pygame.draw.rect(
            street,
            (59, 48, 41),
            (pedestrian_x + 2, pedestrian_y - 3, 1, 1),
        )

        return street

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
        return pygame.transform.scale(crop, (screen_width, screen_height))

    def _draw_urban_descent(self, progress):
        screen_width, screen_height = self.screen.get_size()
        zoom = 1 + (self.FINAL_STREET_ZOOM - 1) * progress
        plaza_focus = (
            self.PLAZA_MAYO_CENTER[0] / self.CITY_SIZE[0] * screen_width,
            self.PLAZA_MAYO_CENTER[1] / self.CITY_SIZE[1] * screen_height,
        )
        street_focus = (
            self.STREET_PEDESTRIAN_HEAD[0] / self.CITY_SIZE[0] * screen_width,
            self.STREET_PEDESTRIAN_HEAD[1] / self.CITY_SIZE[1] * screen_height,
        )

        aerial_frame = self._draw_zoomed_surface(
            self.city_surface, zoom, plaza_focus
        )
        street_frame = self._draw_zoomed_surface(
            self.street_surface, zoom, street_focus
        )
        self.screen.blit(aerial_frame, (0, 0))

        blend_progress = min(1.0, max(0.0, (progress - 0.18) / 0.42))
        blend = blend_progress * blend_progress * (3 - 2 * blend_progress)
        if blend:
            street_frame.set_alpha(round(255 * blend))
            self.screen.blit(street_frame, (0, 0))

    def _draw_final_card(self, elapsed_ms):
        self.screen.fill((0, 0, 0))
        typing_elapsed = elapsed_ms - self.BLACK_TEXT_DELAY_MS
        if typing_elapsed < 0:
            return

        visible_characters = min(
            len(self.FINAL_TEXT),
            int(typing_elapsed / self.BLACK_TEXT_INTERVAL_MS) + 1,
        )
        text_surface = self.text_font.render(
            self.FINAL_TEXT[:visible_characters], True, self.text_color
        )
        text_rect = text_surface.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        transition_start = self.text_complete_ms + self.TEXT_END_HOLD_MS
        urban_start = transition_start + self.ZOOM_DURATION_MS
        black_start = urban_start + self.URBAN_DURATION_MS + self.CITY_HOLD_MS

        if self.elapsed_ms < transition_start:
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.cloud_layer, self.earth_rect.topleft)
        elif self.elapsed_ms < urban_start:
            progress = min(
                1.0,
                (self.elapsed_ms - transition_start) / self.ZOOM_DURATION_MS,
            )
            self._draw_zoom_transition(progress)
        elif self.elapsed_ms < black_start:
            urban_elapsed = self.elapsed_ms - urban_start
            progress = min(1.0, urban_elapsed / self.URBAN_DURATION_MS)
            self._draw_urban_descent(progress)
        else:
            self._draw_final_card(self.elapsed_ms - black_start)

        if self.elapsed_ms < urban_start and self.visible_text:
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
