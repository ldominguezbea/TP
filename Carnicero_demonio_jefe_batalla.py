import os
import sys
import re
import pygame

WIDTH, HEIGHT = 1280, 720
SUELO_Y = 610

# Directorio base absoluto donde se encuentra este archivo .py
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))

# Carga de la textura sun_spirit.png desde la carpeta assets/barras de vida
rutas_sun_spirit = [
    os.path.join(DIRECTORIO_BASE, "assets", "barras de vida", "sun_spirit.png"),
    os.path.join("assets", "barras de vida", "sun_spirit.png"),
    os.path.join(DIRECTORIO_BASE, "sun_spirit.png"),
    "sun_spirit.png"
]

IMG_SUN_SPIRIT = None
for r in rutas_sun_spirit:
    if os.path.exists(r):
        try:
            IMG_SUN_SPIRIT = pygame.image.load(r).convert_alpha()
            print(f"✅ Textura 'sun_spirit.png' cargada con éxito desde: {r}")
            break
        except Exception as e:
            print(f"❌ Error al cargar {r}: {e}")

if IMG_SUN_SPIRIT is None:
    print("⚠️ ADVERTENCIA: No se encontró 'sun_spirit.png' en 'assets/barras de vida/'.")


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


def ejecutar_batalla_carnicero(screen, player, img_bar=None):
    from Jefes_enemigos import CarniceroBoss

    clock = pygame.time.Clock()
    FPS = 60

    # Cargar fondo
    rutas_posibles = [
        os.path.join(DIRECTORIO_BASE, "Escenario_batalla_nivel_1.png"),
        os.path.join(DIRECTORIO_BASE, "assets", "imagenes", "Nivel1", "Nivel1_imagen3.png"),
        os.path.join(DIRECTORIO_BASE, "imagenes", "Nivel1", "Nivel1_imagen3.png"),
        "Escenario_batalla_nivel_1.png"
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
        os.path.join(DIRECTORIO_BASE, "Cierre_nivel_1.png"),
        os.path.join(DIRECTORIO_BASE, "assets", "Cierre_nivel_1.png"),
        os.path.join(DIRECTORIO_BASE, "assets", "fondos", "Cierre_nivel_1.png"),
        os.path.join(DIRECTORIO_BASE, "assets", "UI", "Cierre_nivel_1.png"),
        "Cierre_nivel_1.png"
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

    # Determinar qué imagen de barra usar
    textura_barra = img_bar if img_bar is not None else IMG_SUN_SPIRIT

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
        if getattr(jefe, 'muerto_definitivo', False):
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
        if getattr(jefe, 'attacking', False) and not getattr(jefe, 'has_hit', False):
            if hasattr(jefe, 'hitbox') and jefe.hitbox.width > 0 and jefe.hitbox.colliderect(target_player_rect):
                if hasattr(player, 'take_damage'):
                    player.take_damage(18)
                jefe.has_hit = True

        # Daño del jugador al jefe
        if not getattr(jefe, 'muerto_definitivo', False) and getattr(player, 'attacking', False) and not getattr(player, 'has_hit', False):
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

        # ----------------------------------------------------
        # UI DEL JEFE (Con la textura sun_spirit.png)
        # ----------------------------------------------------
        if not getattr(jefe, 'muerto_definitivo', False):
            max_v_jefe = getattr(jefe, 'max_health', 100)
            pct_jefe = max(0.0, min(1.0, jefe.health / max_v_jefe if max_v_jefe > 0 else 0))

            if textura_barra is not None:
                # 1. Ajuste de dimensiones de sun_spirit.png
                ancho_b_jefe = 600
                escala = ancho_b_jefe / textura_barra.get_width()
                alto_b_jefe = int(textura_barra.get_height() * escala)
                bar_scaled = pygame.transform.scale(textura_barra, (ancho_b_jefe, alto_b_jefe))

                x_jefe_ui = (WIDTH - ancho_b_jefe) // 2
                y_jefe_ui = 30

                # 2. Zona de relleno de vida (Detrás de la imagen)
                x_fill = x_jefe_ui + int(ancho_b_jefe * 0.12)
                y_fill = y_jefe_ui + int(alto_b_jefe * 0.25)
                w_max_fill = int(ancho_b_jefe * 0.76)
                h_fill = int(alto_b_jefe * 0.50)

                w_restante = int(w_max_fill * pct_jefe)

                # Fondo barra vacía
                pygame.draw.rect(screen, (25, 5, 5), (x_fill, y_fill, w_max_fill, h_fill))

                # Relleno de vida activa según fase
                if w_restante > 0:
                    fase = getattr(jefe, 'fase_actual', 1)
                    color_fase = (180, 30, 10) if fase == 1 else ((255, 100, 0) if fase == 2 else (255, 200, 0))
                    pygame.draw.rect(screen, color_fase, (x_fill, y_fill, w_restante, h_fill))
                    pygame.draw.rect(screen, (255, 220, 100), (x_fill, y_fill, w_restante, max(1, h_fill // 3)))

                # 3. Superposición de la imagen ornamental sun_spirit.png
                screen.blit(bar_scaled, (x_jefe_ui, y_jefe_ui))

                # 4. Nombre del Jefe
                lbl_sombra = fuente_jefe.render("Athros : The Bloodred", True, (0, 0, 0))
                lbl_jefe = fuente_jefe.render("Athros : The Bloodred", True, (255, 215, 0))
                rect_lbl = lbl_jefe.get_rect(center=(WIDTH // 2, y_jefe_ui - 12))
                screen.blit(lbl_sombra, (rect_lbl.x + 2, rect_lbl.y + 2))
                screen.blit(lbl_jefe, rect_lbl)

            else:
                # Respaldo simple por si la imagen falla
                ancho_barra_jefe = 500
                alto_barra_jefe = 20
                x_jefe_ui = (WIDTH - ancho_barra_jefe) // 2
                y_jefe_ui = 45

                pygame.draw.rect(screen, (20, 5, 5), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra_jefe + 4, alto_barra_jefe + 4))
                w_restante = int(ancho_barra_jefe * pct_jefe)

                if w_restante > 0:
                    fase = getattr(jefe, 'fase_actual', 1)
                    color_fase = (180, 30, 10) if fase == 1 else ((255, 100, 0) if fase == 2 else (255, 200, 0))
                    pygame.draw.rect(screen, color_fase, (x_jefe_ui, y_jefe_ui, w_restante, alto_barra_jefe))
                    pygame.draw.rect(screen, (255, 220, 100), (x_jefe_ui, y_jefe_ui, w_restante, alto_barra_jefe // 2))

                pygame.draw.rect(screen, (255, 215, 0), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra_jefe + 4, alto_barra_jefe + 4), 2)
                lbl_jefe = fuente_jefe.render("Athros : The Bloodred", True, (255, 200, 50))
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

        # Dibujar pantalla de cierre
        if mostrar_cierre:
            if img_cierre:
                screen.blit(img_cierre, (0, 0))
            else:
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
    pygame.display.set_caption("Batalla de Jefe - Athros : The Bloodred")

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