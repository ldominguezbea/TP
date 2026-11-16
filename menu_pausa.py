import math

import pygame


RETURN_TO_MENU_EXIT_CODE = 10
EXIT_GAME_EXIT_CODE = 11

_OPTIONS = ("Resume", "Return to menu", "Exit game")


def pausar_juego(screen, devolver_accion=False):
    """Muestra el menú de pausa; las salidas se comunican al lanzador del juego."""
    snapshot = screen.copy()
    width, height = screen.get_size()
    clock = pygame.time.Clock()
    selected = 0
    started_at = pygame.time.get_ticks()
    action = None
    music_was_playing = False

    if pygame.mixer.get_init():
        music_was_playing = pygame.mixer.music.get_busy()
        if music_was_playing:
            pygame.mixer.music.pause()

    veil = pygame.Surface((width, height), pygame.SRCALPHA)
    veil.fill((8, 3, 10, 218))
    atmosphere = pygame.Surface((width, height), pygame.SRCALPHA)
    for index in range(7):
        radius = int(min(width, height) * (0.18 + index * 0.055))
        color = (90, 15 + index * 2, 22, max(8, 28 - index * 2))
        pygame.draw.circle(
            atmosphere,
            color,
            (width // 2, height // 2),
            radius,
            max(1, height // 360),
        )

    panel_width = min(660, int(width * 0.84))
    panel_height = min(540, int(height * 0.86))
    panel = pygame.Rect(
        (width - panel_width) // 2,
        (height - panel_height) // 2,
        panel_width,
        panel_height,
    )
    button_width = min(440, panel_width - 72)
    button_height = 62
    button_gap = 14
    buttons_top = panel.centery - 38
    button_rects = [
        pygame.Rect(
            panel.centerx - button_width // 2,
            buttons_top + index * (button_height + button_gap),
            button_width,
            button_height,
        )
        for index in range(len(_OPTIONS))
    ]

    title_font = pygame.font.SysFont("Georgia", max(36, min(52, height // 13)), bold=True)
    subtitle_font = pygame.font.SysFont("Arial", max(15, height // 39), bold=True)
    option_font = pygame.font.SysFont("Georgia", max(22, height // 28), bold=True)
    footer_font = pygame.font.SysFont("Arial", max(12, height // 54), bold=True)

    def center_text(text, font, color, y):
        rendered = font.render(text, True, color)
        screen.blit(rendered, rendered.get_rect(center=(panel.centerx, y)))

    try:
        while action is None:
            clock.tick(60)
            elapsed = (pygame.time.get_ticks() - started_at) / 1000.0
            pulse = 0.5 + 0.5 * math.sin(elapsed * 2.4)

            screen.blit(snapshot, (0, 0))
            screen.blit(veil, (0, 0))
            screen.blit(atmosphere, (0, 0))

            ember_color = (190, 31, 24)
            for index in range(28):
                x = (index * 173 + int(elapsed * (18 + index % 4) * 9)) % width
                y = (index * 97 + int(elapsed * (13 + index % 3) * 6)) % height
                radius = 1 + index % 3
                pygame.draw.circle(screen, ember_color, (x, y), radius)

            shadow = panel.move(0, 12)
            pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=8)
            pygame.draw.rect(screen, (15, 9, 15), panel, border_radius=8)
            pygame.draw.rect(screen, (114, 28, 26), panel, 2, border_radius=8)
            pygame.draw.rect(screen, (197, 142, 73), panel.inflate(-12, -12), 1, border_radius=6)

            spike = max(18, min(28, width // 48))
            for side in (-1, 1):
                x = panel.centerx + side * (panel_width // 2 - 22)
                pygame.draw.polygon(
                    screen,
                    (120, 27, 24),
                    ((x, panel.top + 44), (x + side * spike, panel.top + 74), (x, panel.top + 104)),
                )
                pygame.draw.polygon(
                    screen,
                    (120, 27, 24),
                    ((x, panel.bottom - 104), (x + side * spike, panel.bottom - 74), (x, panel.bottom - 44)),
                )

            crest_y = panel.top + 52
            crest_radius = max(15, min(22, height // 32))
            pygame.draw.circle(screen, (91, 13, 19), (panel.centerx, crest_y), crest_radius + 5)
            pygame.draw.circle(screen, (190, 51, 35), (panel.centerx, crest_y), crest_radius, 2)
            pygame.draw.polygon(
                screen,
                (203, 157, 83),
                (
                    (panel.centerx, crest_y - crest_radius + 5),
                    (panel.centerx + crest_radius - 5, crest_y),
                    (panel.centerx, crest_y + crest_radius - 5),
                    (panel.centerx - crest_radius + 5, crest_y),
                ),
                2,
            )
            center_text("PAUSED", title_font, (238, 215, 184), panel.top + 112)
            center_text(
                "THE INVASION WAITS FOR NO ONE",
                subtitle_font,
                (179, 84, 68),
                panel.top + 157,
            )
            pygame.draw.line(
                screen,
                (103, 44, 37),
                (panel.left + 72, panel.top + 183),
                (panel.right - 72, panel.top + 183),
                1,
            )

            for index, (label, rect) in enumerate(zip(_OPTIONS, button_rects)):
                active = index == selected
                fill = (71, 20, 23) if active else (27, 18, 22)
                border = (
                    (int(205 + pulse * 45), int(135 + pulse * 24), 74)
                    if active
                    else (101, 57, 48)
                )
                pygame.draw.rect(screen, fill, rect, border_radius=5)
                pygame.draw.rect(screen, border, rect, 2 if active else 1, border_radius=5)
                if active:
                    accent_x = rect.left + 17
                    pygame.draw.polygon(
                        screen,
                        (225, 163, 76),
                        (
                            (accent_x, rect.centery),
                            (accent_x + 11, rect.centery - 8),
                            (accent_x + 11, rect.centery + 8),
                        ),
                    )
                text_color = (255, 227, 183) if active else (177, 165, 157)
                label_surface = option_font.render(label, True, text_color)
                screen.blit(label_surface, label_surface.get_rect(center=rect.center))

            center_text(
                "SELECT   ↑  /  ↓        CONFIRM   ENTER",
                footer_font,
                (145, 117, 101),
                panel.bottom - 27,
            )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    action = "exit"
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        action = "resume"
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        selected = (selected - 1) % len(_OPTIONS)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected = (selected + 1) % len(_OPTIONS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        action = ("resume", "menu", "exit")[selected]
                elif event.type == pygame.MOUSEMOTION:
                    for index, rect in enumerate(button_rects):
                        if rect.collidepoint(event.pos):
                            selected = index
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for index, rect in enumerate(button_rects):
                        if rect.collidepoint(event.pos):
                            action = ("resume", "menu", "exit")[index]
                            break
    finally:
        if music_was_playing and pygame.mixer.get_init():
            pygame.mixer.music.unpause()

    if devolver_accion:
        return action
    if action == "menu":
        raise SystemExit(RETURN_TO_MENU_EXIT_CODE)
    if action == "exit":
        raise SystemExit(EXIT_GAME_EXIT_CODE)
