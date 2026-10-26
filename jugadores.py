import pygame
from config import BASE_DIR, GAME_WIDTH, GAME_HEIGHT, abrir_archivo

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 90)
        self.speed = 5
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -12
        self.on_ground = False
        self.health = 150
        self.max_health = 150
        self.direction = "right"

        self.animacion_correr = []
        assets_dir = BASE_DIR / "assets" / "Heroes" / "p_fuego" / "fire_knight"
        
        for i in range(1, 9):
            path_frame = assets_dir / f"run_{i}.txt"
            abrir_archivo(path_frame)
            
            # Superficies dinámicas de respaldo
            surface_frame = pygame.Surface((60, 90), pygame.SRCALPHA)
            pygame.draw.rect(surface_frame, (255, 100, 30), (0, 0, 60, 90), border_radius=4)
            self.animacion_correr.append(surface_frame)

        self.frame_correr = 0
        self.timer_correr = 0
        self.velocidad_animacion = 0.08
        self.imagen = self.animacion_correr[0]

        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.3
        self.has_hit = False

        self.hurtbox = pygame.Rect(x, y, 60, 90)
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        moviendo = False

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
            moviendo = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
            moviendo = True

        if moviendo:
            self.timer_correr += dt
            if self.timer_correr >= self.velocidad_animacion:
                self.frame_correr = (self.frame_correr + 1) % 8
                self.timer_correr = 0
        else:
            self.frame_correr = 0
            self.timer_correr = 0

        self.imagen = self.animacion_correr[self.frame_correr]
        if self.direction == "left":
            self.imagen = pygame.transform.flip(self.imagen, True, False)

        if keys[pygame.K_w] and self.on_ground:
            self.velocity_y = self.jump_force
            self.on_ground = False

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        suelo_y = 590
        if self.rect.bottom >= suelo_y:
            self.rect.bottom = suelo_y
            self.velocity_y = 0
            self.on_ground = True

        self.rect.x = max(0, min(GAME_WIDTH - self.rect.width, self.rect.x))
        self.hurtbox.topleft = self.rect.topleft

    def draw(self, surface):
        surface.blit(self.imagen, self.rect)
