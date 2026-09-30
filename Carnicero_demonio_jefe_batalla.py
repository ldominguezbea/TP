import os
import sys
import random
import re
import pygame

WIDTH, HEIGHT = 1280, 720
SUELO_Y = 610 

def cargar_animacion_con_altura_maxima(folder_path, altura_max):
    frames = []
    if os.path.exists(folder_path):
        archivos = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
        # Ordenamiento numérico natural para evitar el salto entre frames (ej. 1, 2, 3... 10, 11... 22)
        archivos.sort(key=lambda f: int(re.search(r'\d+', f).group()) if re.search(r'\d+', f) else f)
        
        for archivo in archivos:
            ruta = os.path.join(folder_path, archivo)
            img = pygame.image.load(ruta).convert_alpha()
            proporcion = img.get_width() / img.get_height()
            nuevo_ancho = int(altura_max * proporcion)
            img = pygame.transform.scale(img, (nuevo_ancho, altura_max))
            frames.append(img)
    return frames

class Enemigo:
    def __init__(self, nombre, vida, x, y):
        self.nombre = nombre
        self.health = vida
        self.max_health = vida

class CarniceroBoss(Enemigo):
    def __init__(self, x=920, y=SUELO_Y - 400):
        ALTURA_MAX = 400
        super().__init__("Athros :The bloodred", 15, x, y)

        base_path = os.path.join("assets", "Jefes", "Carnicero")

        self.animaciones = {
            "idle": cargar_animacion_con_altura_maxima(os.path.join(base_path, "01_demon_idle"), ALTURA_MAX),
            "correr": cargar_animacion_con_altura_maxima(os.path.join(base_path, "02_demon_walk"), ALTURA_MAX),
            "attack1": cargar_animacion_con_altura_maxima(os.path.join(base_path, "03_demon_cleave"), ALTURA_MAX),
            "take_hit": cargar_animacion_con_altura_maxima(os.path.join(base_path, "04_demon_take_hit"), ALTURA_MAX),
            "muerte": cargar_animacion_con_altura_maxima(os.path.join(base_path, "05_demon_death"), ALTURA_MAX),
        }

        self.estado_actual = "idle"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.20 

        self.image = None
        for estado, frames in self.animaciones.items():
            if len(frames) > 0:
                self.image = frames[0]
                self.estado_actual = estado
                break

        if self.image is None:
            self.image = pygame.Surface((260, ALTURA_MAX))
            self.image.fill((200, 0, 50))

        self.rect = pygame.Rect(x, y, 260, ALTURA_MAX)
        self.hurtbox = self.rect.copy()
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.velocity_y = 0
        self.gravity = 0.6
        self.jump_force = -13
        self.on_ground = True
        self.cooldown_salto = 0.0

        self.direction = "left"
        self.attacking = False
        self.has_hit = False
        
        self.esta_rojo = False
        self.hit_timer = 0.0

        self.muerte_completada = False
        self.muerto_definitivo = False

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado and nuevo_estado in self.animaciones:
            if len(self.animaciones[nuevo_estado]) > 0:
                self.estado_actual = nuevo_estado
                self.frame_actual = 0.0

    def seleccionar_ataque_aleatorio(self):
        ataques = ["attack1"]
        disponibles = [a for a in ataques if len(self.animaciones.get(a, [])) > 0]
        return random.choice(disponibles) if disponibles else "idle"

    def realizar_salto(self):
        if self.on_ground:
            self.velocity_y = self.jump_force
            self.on_ground = False

    def actualizar_hitbox_ataque(self):
        if self.attacking:
            ancho_hitbox = 280
            alto_hitbox = 320
            if self.direction == "left":
                self.hitbox = pygame.Rect(self.rect.left - ancho_hitbox, self.rect.y, ancho_hitbox, alto_hitbox)
            else:
                self.hitbox = pygame.Rect(self.rect.right, self.rect.y, ancho_hitbox, alto_hitbox)
        else:
            self.hitbox = pygame.Rect(0, 0, 0, 0)

    def actualizar_animacion(self):
        frames = self.animaciones.get(self.estado_actual, [])
        if not frames:
            return

        if self.estado_actual == "muerte":
            self.frame_actual += self.velocidad_animacion
            if self.frame_actual >= len(frames) - 1:
                self.frame_actual = float(len(frames) - 1)
                self.muerte_completada = True
            
            idx = min(int(self.frame_actual), len(frames) - 1)
        else:
            self.frame_actual += self.velocidad_animacion
            if self.estado_actual == "take_hit":
                if self.frame_actual >= len(frames):
                    self.cambiar_estado("idle")
            elif self.estado_actual.startswith("attack"):
                if self.frame_actual >= len(frames):
                    self.attacking = False
                    self.has_hit = False
                    self.hitbox = pygame.Rect(0, 0, 0, 0)
                    self.cambiar_estado("idle")
            else:
                if self.frame_actual >= len(frames):
                    self.frame_actual = 0.0

            idx = int(self.frame_actual) % len(frames)

        imagen_frame = frames[idx]

        if self.direction == "right":
            imagen_frame = pygame.transform.flip(imagen_frame, True, False)

        if self.esta_rojo:
            imagen_frame = imagen_frame.copy()
            imagen_frame.fill((255, 60, 60), special_flags=pygame.BLEND_RGB_MULT)

        self.image = imagen_frame

    def update(self, player, dt, width=WIDTH):
        if self.muerto_definitivo:
            return

        if self.esta_rojo:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.esta_rojo = False

        if self.cooldown_salto > 0:
            self.cooldown_salto -= dt

        if self.health <= 0:
            self.health = 0
            
            if self.estado_actual != "muerte":
                self.cambiar_estado("muerte")

            if self.muerte_completada:
                self.muerto_definitivo = True
                return

            self.actualizar_animacion()
            return

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= SUELO_Y:
            self.rect.bottom = SUELO_Y
            self.velocity_y = 0
            self.on_ground = True

        distancia = player.rect.centerx - self.rect.centerx

        if self.on_ground and self.cooldown_salto <= 0 and not self.attacking:
            if player.rect.y < self.rect.y - 50 or random.random() < 0.02:
                self.realizar_salto()
                self.cooldown_salto = 3.0

        if abs(distancia) > 180 and not self.attacking:
            self.direction = "right" if distancia > 0 else "left"
            velocidad = 2.5
            self.rect.x += velocidad if self.direction == "right" else -velocidad
            if self.on_ground:
                self.cambiar_estado("correr")
        elif not self.attacking:
            self.direction = "right" if distancia > 0 else "left"
            self.attacking = True
            self.has_hit = False
            ataque = self.seleccionar_ataque_aleatorio()
            self.cambiar_estado(ataque)

        self.actualizar_hitbox_ataque()
        self.hurtbox = self.rect.copy()
        self.actualizar_animacion()

    def take_damage(self, damage):
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        self.esta_rojo = True
        self.hit_timer = 0.15
        if not self.attacking and self.health > 0:
            self.cambiar_estado("take_hit")

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))


def ejecutar_batalla_carnicero(screen, player):
    clock = pygame.time.Clock()
    FPS = 60

    rutas_posibles = [
        "Escenario_batalla_nivel_1.png",
        os.path.join("assets", "fondos", "Escenario_batalla_nivel_1.png"),
        os.path.join("assets", "fondos", "escuela_en_llamas.png"),
        os.path.join("assets", "fondos", "escuela_en_llamas.jpg")
    ]
    
    fondo_img = None
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            try:
                fondo_img = pygame.image.load(ruta).convert()
                fondo_img = pygame.transform.scale(fondo_img, (WIDTH, HEIGHT))
                break
            except Exception as e:
                print(f"Error al cargar {ruta}: {e}")

    if fondo_img is None:
        fondo_img = pygame.Surface((WIDTH, HEIGHT))
        fondo_img.fill((20, 10, 15))

    jefe = CarniceroBoss(x=920, y=SUELO_Y - 400)

    if hasattr(player, 'rect'):
        player.rect.x = 180
        player.rect.bottom = SUELO_Y

    fuente_jefe = pygame.font.SysFont("Impact", 24)
    fuente_ui = pygame.font.SysFont("Arial", 16, bold=True)
    
    en_batalla = True

    while en_batalla:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if hasattr(player, "manejar_evento"):
                player.manejar_evento(event)

        keys = pygame.key.get_pressed()
        player.update(keys, dt)
        jefe.update(player, dt, width=WIDTH)

        if hasattr(player, 'rect') and player.rect.bottom > SUELO_Y:
            player.rect.bottom = SUELO_Y
            if hasattr(player, 'velocity_y'):
                player.velocity_y = 0
            if hasattr(player, 'on_ground'):
                player.on_ground = True

        if jefe.attacking and not jefe.has_hit:
            target_rect = player.rect if hasattr(player, 'rect') else player.hurtbox
            if jefe.hitbox.colliderect(target_rect):
                if hasattr(player, 'take_damage'):
                    player.take_damage(18)
                jefe.has_hit = True

        if not jefe.muerto_definitivo and getattr(player, 'attacking', False) and not getattr(player, 'has_hit', False):
            player_hitbox = getattr(player, 'hitbox', pygame.Rect(0, 0, 0, 0))
            if player_hitbox.colliderect(jefe.hurtbox):
                jefe.take_damage(10)
                player.has_hit = True

        if getattr(player, 'health', 1) <= 0:
            player.health = 0

        screen.blit(fondo_img, (0, 0))

        if hasattr(player, 'draw'):
            player.draw(screen)
        else:
            screen.blit(player.image, player.rect)

        jefe.draw(screen)

        # Barra de vida del Jefe
        ancho_barra_jefe = 500
        alto_barra_jefe = 20
        x_jefe_ui = (WIDTH - ancho_barra_jefe) // 2
        y_jefe_ui = 45

        pygame.draw.rect(screen, (20, 5, 5), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra_jefe + 4, alto_barra_jefe + 4))
        
        max_v_jefe = getattr(jefe, 'max_health', 15)
        pct_jefe = max(0.0, min(1.0, jefe.health / max_v_jefe if max_v_jefe > 0 else 0))
        w_restante = int(ancho_barra_jefe * pct_jefe)
        
        if w_restante > 0:
            pygame.draw.rect(screen, (180, 30, 10), (x_jefe_ui, y_jefe_ui, w_restante, alto_barra_jefe))
            pygame.draw.rect(screen, (255, 140, 0), (x_jefe_ui, y_jefe_ui, w_restante, alto_barra_jefe // 2))
        
        pygame.draw.rect(screen, (255, 215, 0), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra_jefe + 4, alto_barra_jefe + 4), 2)

        lbl_jefe = fuente_jefe.render("Athros :The bloodred", True, (255, 200, 50))
        screen.blit(lbl_jefe, (WIDTH // 2 - lbl_jefe.get_width() // 2, 15))

        # Barra de vida del Jugador
        ancho_barra_player = 180
        alto_barra_player = 18
        x_player_ui = 30
        y_player_ui = 30

        pygame.draw.rect(screen, (10, 10, 10), (x_player_ui - 2, y_player_ui - 2, ancho_barra_player + 4, alto_barra_player + 4))
        max_v_player = getattr(player, 'max_health', 100)
        pct_player = max(0.0, min(1.0, player.health / max_v_player if max_v_player > 0 else 0))
        
        if pct_player > 0:
            pygame.draw.rect(screen, (40, 180, 70), (x_player_ui, y_player_ui, int(ancho_barra_player * pct_player), alto_barra_player))
        
        pygame.draw.rect(screen, (200, 200, 200), (x_player_ui - 2, y_player_ui - 2, ancho_barra_player + 4, alto_barra_player + 4), 2)
        
        lbl_player = fuente_ui.render("JUGADOR", True, (255, 255, 255))
        screen.blit(lbl_player, (x_player_ui, 8))

        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Batalla de Jefe - Athros :The bloodred")

    class JugadorPrueba:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x, y, 60, 110)
            self.hurtbox = self.rect
            self.image = pygame.Surface((60, 110))
            self.image.fill((0, 150, 255))
            self.health = 100
            self.max_health = 100
            self.attacking = False
            self.has_hit = False
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            self.velocity_y = 0
            self.on_ground = True
            self.direction = "right"

        def update(self, keys, dt):
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.rect.x -= 300 * dt
                self.direction = "left"
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.rect.x += 300 * dt
                self.direction = "right"

            if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
                self.velocity_y = -13
                self.on_ground = False

            self.velocity_y += 0.6
            self.rect.y += self.velocity_y

            tecla_ataque = keys[pygame.K_f] or keys[pygame.K_SPACE]
            if tecla_ataque and not self.attacking:
                self.attacking = True
                self.has_hit = False
                ancho_hitbox = 80
                
                if self.direction == "right":
                    self.hitbox = pygame.Rect(self.rect.right, self.rect.y, ancho_hitbox, 110)
                else:
                    self.hitbox = pygame.Rect(self.rect.left - ancho_hitbox, self.rect.y, ancho_hitbox, 110)
            elif not tecla_ataque:
                self.attacking = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)

        def take_damage(self, damage):
            self.health = max(0, self.health - damage)

        def draw(self, surface):
            surface.blit(self.image, self.rect)

    jugador_test = JugadorPrueba(180, SUELO_Y - 110)
    ejecutar_batalla_carnicero(screen, jugador_test)