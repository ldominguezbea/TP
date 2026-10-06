import os
import sys
import re
import pygame

WIDTH, HEIGHT = 1280, 720
SUELO_Y = 610


def cargar_animacion_con_altura_maxima(folder_path, altura_max):
    frames = []
    if os.path.exists(folder_path):
        archivos = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
        archivos.sort(key=lambda f: int(re.search(r'\d+', f).group()) if re.search(r'\d+', f) else f)
        
        for archivo in archivos:
            ruta = os.path.join(folder_path, archivo)
            img = pygame.image.load(ruta).convert_alpha()
            proporcion = img.get_width() / img.get_height()
            nuevo_ancho = int(altura_max * proporcion)
            img = pygame.transform.scale(img, (nuevo_ancho, altura_max))
            frames.append(img)
    return frames


class Proyectil:
    def __init__(self, x, y, vx, vy, radio=8, color=(255, 100, 0), rebota=False, duracion=5.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radio = radio
        self.color = color
        self.rebota = rebota
        self.duracion = duracion
        self.rect = pygame.Rect(int(x - radio), int(y - radio), radio * 2, radio * 2)

    def update(self, dt, width=WIDTH, suelo_y=SUELO_Y):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.duracion -= dt

        if self.rebota:
            if self.x - self.radio <= 0 or self.x + self.radio >= width:
                self.vx = -self.vx
                self.x = max(self.radio, min(width - self.radio, self.x))
            if self.y - self.radio <= 0 or self.y + self.radio >= suelo_y:
                self.vy = -self.vy
                self.y = max(self.radio, min(suelo_y - self.radio, self.y))

        self.rect.center = (int(self.x), int(self.y))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(screen, (255, 240, 180), (int(self.x), int(self.y)), max(2, self.radio // 2))


class Enemigo:
    def __init__(self, nombre, vida, x, y):
        self.nombre = nombre
        self.health = vida
        self.max_health = vida


def ejecutar_batalla_carnicero(screen, player):
    from Jefes_enemigos import CarniceroBoss

    clock = pygame.time.Clock()
    FPS = 60

    # Cargar fondo
    rutas_posibles = [
        "Escenario_batalla_nivel_1.png",
        os.path.join("assets", "imagenes","Nivel1" "Nivel1_imagen3.png"),
    
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

    # Cargar imagen de cierre de nivel
    rutas_cierre = [
        "Cierre_nivel_1.png",
        os.path.join("assets", "Cierre_nivel_1.png"),
        os.path.join("assets", "fondos", "Cierre_nivel_1.png"),
        os.path.join("assets", "UI", "Cierre_nivel_1.png")
    ]
    img_cierre = None
    for r in rutas_cierre:
        if os.path.exists(r):
            try:
                img_cierre = pygame.image.load(r).convert_alpha()
                img_cierre = pygame.transform.scale(img_cierre, (WIDTH, HEIGHT))
                break
            except Exception as e:
                print(f"Error al cargar {r}: {e}")

    jefe = CarniceroBoss(x=920, y=SUELO_Y - 300)

    if hasattr(player, 'rect'):
        player.rect.x = 180
        player.rect.bottom = SUELO_Y

    fuente_jefe = pygame.font.SysFont("Impact", 24)
    fuente_ui = pygame.font.SysFont("Arial", 16, bold=True)
    
    en_batalla = True
    timer_muerte_jefe = 0.0
    mostrar_cierre = False

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
        jefe.update(player, dt, width=WIDTH, suelo_y=SUELO_Y)

        # Control del temporizador tras la muerte del jefe
        if jefe.muerto_definitivo:
            timer_muerte_jefe += dt
            if timer_muerte_jefe >= 5.0:
                mostrar_cierre = True

        if hasattr(player, 'rect') and player.rect.bottom > SUELO_Y:
            player.rect.bottom = SUELO_Y
            if hasattr(player, 'velocity_y'):
                player.velocity_y = 0
            if hasattr(player, 'on_ground'):
                player.on_ground = True

        target_player_rect = player.rect if hasattr(player, 'rect') else player.hurtbox

        # Daño por proyectiles
        for proj in jefe.proyectiles[:]:
            if proj.rect.colliderect(target_player_rect):
                if hasattr(player, 'take_damage'):
                    player.take_damage(6)
                if proj in jefe.proyectiles:
                    jefe.proyectiles.remove(proj)

        # Daño por machete
        if jefe.attacking and not jefe.has_hit:
            if jefe.hitbox.width > 0 and jefe.hitbox.colliderect(target_player_rect):
                if hasattr(player, 'take_damage'):
                    player.take_damage(18)
                jefe.has_hit = True

        # Daño del jugador al jefe
        if not jefe.muerto_definitivo and getattr(player, 'attacking', False) and not getattr(player, 'has_hit', False):
            player_hitbox = getattr(player, 'hitbox', pygame.Rect(0, 0, 0, 0))
            if player_hitbox.colliderect(jefe.hurtbox):
                jefe.take_damage(8)
                player.has_hit = True

        if getattr(player, 'health', 1) <= 0:
            player.health = 0

        screen.blit(fondo_img, (0, 0))

        if hasattr(player, 'draw'):
            player.draw(screen)
        else:
            screen.blit(player.image, player.rect)

        jefe.draw(screen)

        # UI del Jefe (se dibuja solo si no ha desaparecido por completo)
        if not jefe.muerto_definitivo:
            ancho_barra_jefe = 500
            alto_barra_jefe = 20
            x_jefe_ui = (WIDTH - ancho_barra_jefe) // 2
            y_jefe_ui = 45

            pygame.draw.rect(screen, (20, 5, 5), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra_jefe + 4, alto_barra_jefe + 4))
            
            max_v_jefe = getattr(jefe, 'max_health', 100)
            pct_jefe = max(0.0, min(1.0, jefe.health / max_v_jefe if max_v_jefe > 0 else 0))
            w_restante = int(ancho_barra_jefe * pct_jefe)
            
            if w_restante > 0:
                color_fase = (180, 30, 10) if jefe.fase_actual == 1 else ((255, 100, 0) if jefe.fase_actual == 2 else (255, 200, 0))
                pygame.draw.rect(screen, color_fase, (x_jefe_ui, y_jefe_ui, w_restante, alto_barra_jefe))
                pygame.draw.rect(screen, (255, 220, 100), (x_jefe_ui, y_jefe_ui, w_restante, alto_barra_jefe // 2))
            
            pygame.draw.rect(screen, (255, 215, 0), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra_jefe + 4, alto_barra_jefe + 4), 2)

            lbl_jefe = fuente_jefe.render("Athros :The bloodred", True, (255, 200, 50))
            screen.blit(lbl_jefe, (WIDTH // 2 - lbl_jefe.get_width() // 2, 15))

        # UI del Jugador
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

        # Dibujar pantalla de cierre al cumplirse los 7 segundos
        if mostrar_cierre:
            if img_cierre:
                screen.blit(img_cierre, (0, 0))
            else:
                # Fondo oscuro de reemplazo si no se encuentra la imagen
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(220)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                fuente_cierre = pygame.font.SysFont("Impact", 48)
                lbl_cierre = fuente_cierre.render("NIVEL 1 COMPLETADO", True, (255, 215, 0))
                screen.blit(lbl_cierre, (WIDTH // 2 - lbl_cierre.get_width() // 2, HEIGHT // 2 - 24))

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
                self.rect.x -= 320 * dt
                self.direction = "left"
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.rect.x += 320 * dt
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
                ancho_hitbox = 90
                
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