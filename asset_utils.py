import pygame


def load_image_or_placeholder(
    path,
    fallback_size,
    *,
    alpha=False,
    label=None,
):
    try:
        image = pygame.image.load(str(path))
        return image.convert_alpha() if alpha else image.convert()
    except (pygame.error, OSError) as error:
        print(f"[ASSETS] No se pudo cargar {path}; se usará una imagen de respaldo: {error}")

    flags = pygame.SRCALPHA if alpha else 0
    placeholder = pygame.Surface(fallback_size, flags)
    color = (18, 15, 24, 255) if alpha else (18, 15, 24)
    placeholder.fill(color)

    if label and pygame.font.get_init():
        font_size = max(14, min(28, fallback_size[1] // 12))
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        text = font.render(label, True, (220, 215, 205))
        placeholder.blit(text, text.get_rect(center=placeholder.get_rect().center))

    return placeholder
