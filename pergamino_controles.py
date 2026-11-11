from pathlib import Path

import pygame


class ControlsBook:
    """Draws the static two-page controls book and its key mappings."""

    def __init__(self, screen_size, assets_dir: Path):
        self.screen_size = screen_size
        self.book = pygame.image.load(str(assets_dir / "LIbro.png")).convert_alpha()
        book_width, book_height = self.book.get_size()
        self.scale = min(
            screen_size[0] * 0.94 / book_width, screen_size[1] * 0.92 / book_height
        )
        self.book_size = (
            round(book_width * self.scale),
            round(book_height * self.scale),
        )
        self.book_image = pygame.transform.smoothscale(self.book, self.book_size)
        self.book_rect = self.book_image.get_rect(
            center=(screen_size[0] // 2, screen_size[1] // 2)
        )

        self.page = self.book.copy()
        self.header_font = pygame.font.SysFont("Georgia", 28, bold=True)
        self.key_font = pygame.font.SysFont("Georgia", 19, bold=True)
        self.action_font = pygame.font.SysFont("Georgia", 17, bold=True)
        self.footer_font = pygame.font.SysFont("Georgia", 18, bold=True)
        self._draw_contents()
        self.book_image = pygame.transform.smoothscale(self.page, self.book_size)

    def draw(self, surface):
        surface.blit(self.book_image, self.book_rect)

    def _draw_contents(self):
        image_width, image_height = self.page.get_size()
        ink = (79, 45, 22)
        arrow_ink = (133, 83, 37)

        for label, center_x in (("[ MOVIMIENTO ]", 280), ("[ COMBATE ]", 780)):
            title = self.header_font.render(label, True, ink)
            self.page.blit(title, title.get_rect(center=(center_x, 145)))

        left_rows = (
            ("[ A / D ]", "MOVIMIENTO", 230),
            ("[ W ]", "SALTO", 305),
            ("[ S ]", "BAJAR (PLATAFORMA)", 380),
            ("[ Q ]", "RODAR", 455),
        )
        right_rows = (
            ("[ E ]", "ATAQUE ESPECIAL", 255),
            ("[ CLICK IZQ ]", "ATAQUE", 345),
            ("[ CLICK DER ]", "BLOQUEO", 435),
            ("[ ESC ]", "VOLVER AL MENÚ", 525),
        )

        for key, action, row_y in left_rows:
            self._draw_mapping(
                key,
                action,
                row_y,
                key_x=75,
                action_x=245,
                page_right=493,
                key_font=self.key_font,
                action_font=self.action_font,
                ink=ink,
                arrow_ink=arrow_ink,
            )
        for row_index, (key, action, row_y) in enumerate(right_rows):
            self._draw_mapping(
                key,
                action,
                row_y,
                key_x=570,
                action_x=745,
                page_right=986,
                key_font=self.footer_font if row_index == 3 else self.key_font,
                action_font=self.footer_font if row_index == 3 else self.action_font,
                ink=ink,
                arrow_ink=arrow_ink,
            )

    def _draw_mapping(
        self,
        key,
        action,
        row_y,
        key_x,
        action_x,
        page_right,
        key_font,
        action_font,
        ink,
        arrow_ink,
    ):
        key_surface = key_font.render(key, True, ink)
        action_surface = action_font.render(action, True, ink)
        if action_x + action_surface.get_width() > page_right:
            action_font = pygame.font.SysFont(
                "Georgia", max(13, action_font.get_height() - 3), bold=True
            )
            action_surface = action_font.render(action, True, ink)

        self.page.blit(key_surface, (key_x, row_y - key_surface.get_height() // 2))
        arrow_start = key_x + key_surface.get_width() + 8
        arrow_end = action_x - 10
        if arrow_end > arrow_start + 6:
            pygame.draw.line(
                self.page, arrow_ink, (arrow_start, row_y), (arrow_end, row_y), 2
            )
            pygame.draw.polygon(
                self.page,
                arrow_ink,
                (
                    (arrow_end, row_y),
                    (arrow_end - 7, row_y - 4),
                    (arrow_end - 7, row_y + 4),
                ),
            )
        self.page.blit(
            action_surface, (action_x, row_y - action_surface.get_height() // 2)
        )
