import sys
import pygame
from Jefes_enemigos import CarniceroBoss
import os



# --- CONFIGURACIÓN DEL ESCENARIO ---
WIDTH, HEIGHT = 1280, 720
# Ajustado para el piso del patio del escenario (evita que los personajes floten o queden bajo el pavimento)
SUELO_Y = 610 

def ejecutar_batalla_carnicero(screen, player):
    clock = pygame.time.Clock()
    FPS = 60

    # 1. Cargar el fondo del escenario en llamas
    # Guarda tu imagen en: assets/fondos/escuela_en_llamas.png
    ruta_fondo = os.path.join("assets", "fondos", "escuela_en_llamas.png")
    
    try:
        fondo_img = pygame.image.load(ruta_fondo).convert()
        fondo_img = pygame.transform.scale(fondo_img, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"No se pudo cargar la imagen del escenario ({e}). Usando fondo alternativo.")
        fondo_img = pygame.Surface((WIDTH, HEIGHT))
        fondo_img.fill((20, 10, 15))

    # 2. Instanciar al Jefe "Carnicero"
    # Se coloca a la derecha del mapa sobre la línea del suelo
    jefe = CarniceroBoss(x=920, y=SUELO_Y - 150)

    # Posicionar al jugador a la izquierda al arrancar el combate
    if hasattr(player, 'rect'):
        player.rect.x = 180
        player.rect.bottom = SUELO_Y

    fuente_jefe = pygame.font.SysFont("Impact", 28)
    fuente_ui = pygame.font.SysFont("Arial", 18, bold=True)
    
    en_batalla = True

    while en_batalla:
        dt = clock.tick(FPS) / 1000.0  # Delta time en segundos

        # --- GESTIÓN DE EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if hasattr(player, "manejar_evento"):
                player.manejar_evento(event)

        # --- ACTUALIZACIÓN DE LÓGICA ---
        keys = pygame.key.get_pressed()
        
        # Actualización de Player y Boss
        player.update(keys, dt)
        jefe.update(player, dt, width=WIDTH)

        # Asegurar límite de suelo para el jugador en este mapa
        if hasattr(player, 'rect') and player.rect.bottom > SUELO_Y:
            player.rect.bottom = SUELO_Y
            if hasattr(player, 'velocity_y'):
                player.velocity_y = 0
            if hasattr(player, 'on_ground'):
                player.on_ground = True

        # --- Detección de Colisiones / Ataques ---
        # Ataque del Carnicero al Jugador
        if jefe.attacking and not jefe.has_hit:
            target_rect = player.rect if hasattr(player, 'rect') else player.hurtbox
            if jefe.hitbox.colliderect(target_rect):
                if hasattr(player, 'take_damage'):
                    player.take_damage(18)
                jefe.has_hit = True

        # Ataque del Jugador al Carnicero
        if getattr(player, 'attacking', False) and not getattr(player, 'has_hit', False):
            player_hitbox = getattr(player, 'hitbox', pygame.Rect(0, 0, 0, 0))
            if player_hitbox.colliderect(jefe.hurtbox):
                jefe.take_damage(10)
                player.has_hit = True

        # --- CONDICIONES DE FINALIZACIÓN ---
        if jefe.muerto_definitivo:
            print("¡Carnicero derrotado!")
            en_batalla = False

        if getattr(player, 'health', 1) <= 0:
            print("Jugador derrotado")
            en_batalla = False

        # --- RENDERIZADO ---
        # Dibujar fondo
        screen.blit(fondo_img, (0, 0))

        # Dibujar entidades
        if hasattr(player, 'draw'):
            player.draw(screen)
        else:
            screen.blit(player.image, player.rect)

        jefe.draw(screen)

        # --- UI / BARRAS DE VIDA (Estilo Fuego/Llamas) ---
        # 1. Barra del Jefe (Superior Central)
        ancho_barra = 550
        alto_barra = 22
        x_jefe_ui = (WIDTH - ancho_barra) // 2
        y_jefe_ui = 40

        # Fondo barra de vida jefe
        pygame.draw.rect(screen, (20, 5, 5), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra + 4, alto_barra + 4))
        
        # Porcentaje de vida del Carnicero
        pct_jefe = max(0, jefe.health / 15)  # 15 es la vida base del Carnicero
        w_restante = int(ancho_barra * pct_jefe)
        
        # Barra con degradado térmico
        pygame.draw.rect(screen, (180, 30, 10), (x_jefe_ui, y_jefe_ui, w_restante, alto_barra))
        pygame.draw.rect(screen, (255, 140, 0), (x_jefe_ui, y_jefe_ui, w_restante, alto_barra // 2)) # Brillo superior
        pygame.draw.rect(screen, (255, 215, 0), (x_jefe_ui - 2, y_jefe_ui - 2, ancho_barra + 4, alto_barra + 4), 2)

        # Texto del Jefe
        lbl_jefe = fuente_jefe.render("EL CARNICERO", True, (255, 200, 50))
        screen.blit(lbl_jefe, (WIDTH // 2 - lbl_jefe.get_width() // 2, 10))

        # 2. Barra de Vida del Jugador (Esquina Superior Izquierda)
        pygame.draw.rect(screen, (10, 10, 10), (28, 28, 204, 24))
        pct_player = max(0, player.health / getattr(player, 'max_health', 100))
        pygame.draw.rect(screen, (40, 180, 70), (30, 30, int(200 * pct_player), 20))
        pygame.draw.rect(screen, (200, 200, 200), (28, 28, 204, 24), 2)
        
        lbl_player = fuente_ui.render("JUGADOR", True, (255, 255, 255))
        screen.blit(lbl_player, (30, 8))

        pygame.display.flip()