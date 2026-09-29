import os
import re
import random
import pygame

try:
    from enemigos import Enemigo
except ImportError:
    class Enemigo(pygame.sprite.Sprite):
        def __init__(self, nombre, vida, x, y):
            super().__init__()
            self.nombre = nombre
            self.health = vida * 50
            self.max_health = self.health
            self.rect = pygame.Rect(x, y, 110, 180)
            self.hurtbox = self.rect.copy()
            self.hitbox = pygame.Rect(0, 0, 0, 0)
            self.attacking = False
            self.has_hit = False
            self.direction = "right"

WIDTH = 1350
SUELO_Y = 590

def extraer_numero(nombre_archivo):
    numeros = re.findall(r'\d+', nombre_archivo)
    return int(numeros[0]) if numeros else 0

def cargar_animacion_carpeta(ruta_carpeta, alto_deseado=260):
    frames = []
    if os.path.exists(ruta_carpeta):
        try:
            archivos = os.listdir(ruta_carpeta)
            archivos.sort(key=extraer_numero)

            for archivo in archivos:
                if archivo.lower().endswith(".png"):
                    path_completo = os.path.join(ruta_carpeta, archivo)
                    img = pygame.image.load(path_completo).convert_alpha()
                    
                    ancho_orig, alto_orig = img.get_size()
                    if alto_orig > 0:
                        ancho_nuevo = int(ancho_orig * (alto_deseado / alto_orig))
                        img = pygame.transform.scale(img, (ancho_nuevo, alto_deseado))
                    
                    frames.append(img)
        except Exception as e:
            print(f"Error cargando {ruta_carpeta}: {e}")
    return frames


# --- CLASES AUXILIARES PARA LA MINI FASE DEL WEREWOLF ---

class BolaFuegoEspecial(pygame.sprite.Sprite):
    def __init__(self, x_inicio, y_inicio, x_destino, y_destino):
        super().__init__()
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 60, 0), (11, 11), 11)
        pygame.draw.circle(self.image, (255, 200, 0), (11, 11), 6)
        pygame.draw.circle(self.image, (255, 255, 255), (11, 11), 3)
        
        self.rect = self.image.get_rect(center=(x_inicio, y_inicio))
        self.x = float(x_inicio)
        self.y = float(y_inicio)
        
        self.x_destino = x_destino
        self.y_destino = y_destino
        self.radio_impacto = 38
        
        dx = x_destino - x_inicio
        dy = y_destino - y_inicio
        distancia = max(1.0, (dx**2 + dy**2)**0.5)
        velocidad = 5.5
        
        self.vx = (dx / distancia) * velocidad
        self.vy = (dy / distancia) * velocidad
        
        self.impactado = False
        self.dano = 12
        self.has_hit = False

    def aplicar_danio_jugador(self, player):
        if self.has_hit:
            return
        if hasattr(player, 'take_damage'):
            player.take_damage(self.dano)
        elif hasattr(player, 'recibir_danio'):
            player.recibir_danio(self.dano)
        elif hasattr(player, 'health'):
            player.health -= self.dano
        self.has_hit = True

    def update(self, player, dt):
        if self.impactado:
            return

        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

        cuerpo_jugador = getattr(player, 'hurtbox', player.rect)

        # Daño directo si la bola de fuego colisiona con el jugador durante el vuelo
        if self.rect.colliderect(cuerpo_jugador):
            self.aplicar_danio_jugador(player)
            self.impactado = True
            return

        # Comprobación de llegada a la zona marcada del suelo
        distancia_al_destino = ((self.x - self.x_destino)**2 + (self.y - self.y_destino)**2)**0.5
        if distancia_al_destino <= 10 or self.y >= self.y_destino:
            self.impactado = True
            
            # Daño en área al llegar al suelo
            distancia_jugador = ((cuerpo_jugador.centerx - self.x_destino)**2 + (cuerpo_jugador.centery - self.y_destino)**2)**0.5
            if distancia_jugador <= self.radio_impacto:
                self.aplicar_danio_jugador(player)

    def draw(self, screen):
        if not self.impactado:
            # Área roja iluminada en la zona objetivo del suelo
            surface_roja = pygame.Surface((self.radio_impacto * 2, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(surface_roja, (255, 0, 0, 140), surface_roja.get_rect())
            pygame.draw.ellipse(surface_roja, (255, 100, 0, 180), surface_roja.get_rect().inflate(-8, -4))
            screen.blit(surface_roja, (self.x_destino - self.radio_impacto, self.y_destino - 8))
            
            screen.blit(self.image, self.rect)


class MiniDemonio:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer_disparo = random.uniform(0.5, 1.2)
        self.intervalo_disparo = 1.8
        self.tiempo_vivo = 0.0

    def update(self, dt, player, lista_proyectiles):
        self.tiempo_vivo += dt
        self.timer_disparo -= dt
        if self.timer_disparo <= 0:
            self.timer_disparo = self.intervalo_disparo
            cuerpo = getattr(player, 'hurtbox', player.rect)
            x_destino = cuerpo.centerx
            y_destino = cuerpo.bottom
            lista_proyectiles.append(BolaFuegoEspecial(self.x, self.y, x_destino, y_destino))

    def draw(self, screen):
        # Flotación leve
        offset_y = int(pygame.time.get_ticks() % 800 < 400) * 3
        pos_y = self.y + offset_y

        # Aura brillante
        aura = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(aura, (255, 30, 0, 60), (25, 25), 22)
        screen.blit(aura, (self.x - 25, pos_y - 25))

        # Cuerpo del demonio
        pygame.draw.polygon(screen, (120, 0, 20), [
            (self.x, pos_y + 18),
            (self.x - 14, pos_y - 6),
            (self.x + 14, pos_y - 6)
        ])
        
        # Cabeza
        pygame.draw.circle(screen, (180, 10, 10), (int(self.x), int(pos_y - 8)), 11)

        # Cuernos
        pygame.draw.polygon(screen, (40, 0, 0), [(self.x - 8, pos_y - 14), (self.x - 14, pos_y - 24), (self.x - 3, pos_y - 17)])
        pygame.draw.polygon(screen, (40, 0, 0), [(self.x + 8, pos_y - 14), (self.x + 14, pos_y - 24), (self.x + 3, pos_y - 17)])

        # Ojos brillantes
        pygame.draw.circle(screen, (255, 230, 0), (int(self.x - 4), int(pos_y - 10)), 3)
        pygame.draw.circle(screen, (255, 230, 0), (int(self.x + 4), int(pos_y - 10)), 3)


# --- JEFES ---

class ImpalerBoss(Enemigo):

    def __init__(self, x=900, y=500):
        super().__init__("Impaler Boss", 10, x, y)

        base_path = os.path.join("assets", "Jefes", "Impaler Boss")

        ALTO_JEFE = 260

        self.animaciones = {
            "idle": cargar_animacion_carpeta(os.path.join(base_path, "idle"), alto_deseado=ALTO_JEFE),
            "correr": cargar_animacion_carpeta(os.path.join(base_path, "walk"), alto_deseado=ALTO_JEFE),
            "saltar": cargar_animacion_carpeta(os.path.join(base_path, "jump"), alto_deseado=ALTO_JEFE),
            "muerte": cargar_animacion_carpeta(os.path.join(base_path, "death"), alto_deseado=ALTO_JEFE),
            "attack1": cargar_animacion_carpeta(os.path.join(base_path, "attack1"), alto_deseado=ALTO_JEFE),
            "attack2": cargar_animacion_carpeta(os.path.join(base_path, "attack2"), alto_deseado=ALTO_JEFE),
            "attack3": cargar_animacion_carpeta(os.path.join(base_path, "attack3"), alto_deseado=ALTO_JEFE),
            "attack4": cargar_animacion_carpeta(os.path.join(base_path, "attack4"), alto_deseado=ALTO_JEFE),
            "attack5": cargar_animacion_carpeta(os.path.join(base_path, "attack5"), alto_deseado=ALTO_JEFE),
            "attack6": cargar_animacion_carpeta(os.path.join(base_path, "attack6"), alto_deseado=ALTO_JEFE),
        }

        self.estado_actual = "idle"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.25 

        self.image = None
        for estado, frames in self.animaciones.items():
            if len(frames) > 0:
                self.image = frames[0]
                self.estado_actual = estado
                break

        if self.image is None:
            self.image = pygame.Surface((120, 200))
            self.image.fill((200, 0, 50))

        self.rect = pygame.Rect(x, y, 110, 180)
        self.hurtbox = self.rect.copy()
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.velocity_y = 0
        self.gravity = 0.6
        self.jump_force = -13
        self.on_ground = True
        self.cooldown_salto = 0.0

        self.direction = "right"
        self.attacking = False
        self.has_hit = False
        
        self.esta_rojo = False
        self.hit_timer = 0.0

        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado and nuevo_estado in self.animaciones:
            if len(self.animaciones[nuevo_estado]) > 0:
                self.estado_actual = nuevo_estado
                self.frame_actual = 0.0

    def seleccionar_ataque_aleatorio(self):
        ataques = ["attack1", "attack2", "attack3", "attack4", "attack5", "attack6"]
        disponibles = [a for a in ataques if len(self.animaciones.get(a, [])) > 0]
        return random.choice(disponibles) if disponibles else "idle"

    def realizar_salto(self):
        if self.on_ground and len(self.animaciones.get("saltar", [])) > 0:
            self.velocity_y = self.jump_force
            self.on_ground = False
            self.cambiar_estado("saltar")

    def actualizar_hitbox_ataque(self):
        if self.attacking:
            ancho_hitbox = 140
            alto_hitbox = 160
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

        self.frame_actual += self.velocidad_animacion

        if self.estado_actual == "muerte":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual == "saltar":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual.startswith("attack"):
            if self.frame_actual >= len(frames):
                self.attacking = False
                self.has_hit = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)
                self.cambiar_estado("idle" if self.on_ground else "saltar")
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        idx = int(self.frame_actual) % len(frames)
        imagen_frame = frames[idx]

        if self.direction == "left":
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
            self.cambiar_estado("muerte")
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True
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

        if abs(distancia) > 120:
            self.direction = "right" if distancia > 0 else "left"
            velocidad = 2.5
            self.rect.x += velocidad if self.direction == "right" else -velocidad
            if self.on_ground and not self.attacking:
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

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        if self.image:
            pos_x = self.rect.centerx - self.image.get_width() // 2
            pos_y = self.rect.bottom - self.image.get_height()
            screen.blit(self.image, (pos_x, pos_y))


class WerewolfBoss(Enemigo):

    def __init__(self, x=900, y=500):
        super().__init__("Werewolf Boss", 12, x, y)

        base_path = os.path.join("assets", "Jefes", "werewolf")
        ALTO_JEFE = 260

        self.animaciones = {
            "idle": cargar_animacion_carpeta(os.path.join(base_path, "idle"), alto_deseado=ALTO_JEFE),
            "correr": cargar_animacion_carpeta(os.path.join(base_path, "walk"), alto_deseado=ALTO_JEFE),
            "muerte": cargar_animacion_carpeta(os.path.join(base_path, "death"), alto_deseado=ALTO_JEFE),
            "attack1": cargar_animacion_carpeta(os.path.join(base_path, "attack 1"), alto_deseado=ALTO_JEFE),
            "attack2": cargar_animacion_carpeta(os.path.join(base_path, "attack 2"), alto_deseado=ALTO_JEFE),
            "attack3": cargar_animacion_carpeta(os.path.join(base_path, "attack 3"), alto_deseado=ALTO_JEFE),
            "attack4": cargar_animacion_carpeta(os.path.join(base_path, "attack 4"), alto_deseado=ALTO_JEFE),
            "attack5": cargar_animacion_carpeta(os.path.join(base_path, "attack 5"), alto_deseado=ALTO_JEFE),
        }

        self.estado_actual = "idle"
        self.frame_actual = 0.0
        self.velocidad_animacion = 0.25

        self.image = None
        for estado, frames in self.animaciones.items():
            if len(frames) > 0:
                self.image = frames[0]
                self.estado_actual = estado
                break

        if self.image is None:
            self.image = pygame.Surface((120, 200))
            self.image.fill((100, 50, 150))

        ANCHO_BASE = 110
        ALTO_BASE = 180
        self.rect = pygame.Rect(x, SUELO_Y - ALTO_BASE, ANCHO_BASE, ALTO_BASE)
        self.hurtbox = self.rect.copy()
        self.hitbox = pygame.Rect(0, 0, 0, 0)

        self.velocity_y = 0
        self.gravity = 0.6
        self.on_ground = True

        self.direction = "right"
        self.attacking = False
        self.has_hit = False
        self.dano_ataque = 15

        self.cooldown_ataque = 0.0

        self.esta_rojo = False
        self.hit_timer = 0.0

        self.desaparecer_timer = 3.0
        self.muerto_definitivo = False

        # Variables de la mini fase especial
        self.en_fase_especial = False
        self.timer_fase_especial = 0.0
        self.cooldown_inicio_fase = 15.0
        self.timer_para_fase = self.cooldown_inicio_fase
        self.invulnerable = False
        
        self.minidemonios = []
        self.proyectiles_fase = []

    def iniciar_fase_especial(self):
        self.en_fase_especial = True
        self.timer_fase_especial = 20.0
        self.invulnerable = True
        self.attacking = False
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        
        self.rect.centerx = WIDTH // 2
        self.rect.centery = SUELO_Y - 260
        self.cambiar_estado("idle")

        self.minidemonios = [
            MiniDemonio(150, 220),
            MiniDemonio(WIDTH - 150, 220)
        ]
        self.proyectiles_fase.clear()

    def finalizar_fase_especial(self):
        self.en_fase_especial = False
        self.invulnerable = False
        self.timer_para_fase = self.cooldown_inicio_fase
        self.minidemonios.clear()
        self.proyectiles_fase.clear()

    def cambiar_estado(self, nuevo_estado):
        if self.estado_actual != nuevo_estado and nuevo_estado in self.animaciones:
            if len(self.animaciones[nuevo_estado]) > 0:
                self.estado_actual = nuevo_estado
                self.frame_actual = 0.0

    def seleccionar_ataque_aleatorio(self):
        ataques = ["attack1", "attack2", "attack3", "attack4", "attack5"]
        disponibles = [a for a in ataques if len(self.animaciones.get(a, [])) > 0]
        return random.choice(disponibles) if disponibles else "idle"

    def actualizar_hitbox_ataque(self):
        if self.attacking and not self.en_fase_especial:
            ancho_hitbox = 150
            alto_hitbox = 170
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

        self.frame_actual += self.velocidad_animacion

        if self.estado_actual == "muerte":
            if self.frame_actual >= len(frames):
                self.frame_actual = len(frames) - 1
        elif self.estado_actual.startswith("attack"):
            if self.frame_actual >= len(frames):
                self.attacking = False
                self.has_hit = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)
                self.cooldown_ataque = 1.0 
                self.cambiar_estado("idle")
        else:
            if self.frame_actual >= len(frames):
                self.frame_actual = 0.0

        idx = int(self.frame_actual) % len(frames)
        imagen_frame = frames[idx]

        if self.direction == "left":
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

        if self.health <= 0:
            self.health = 0
            self.en_fase_especial = False
            self.invulnerable = False
            self.cambiar_estado("muerte")
            self.desaparecer_timer -= dt
            if self.desaparecer_timer <= 0:
                self.muerto_definitivo = True
            self.actualizar_animacion()
            return

        if self.en_fase_especial:
            self.timer_fase_especial -= dt
            
            # Levitación suave mientras vuela
            self.rect.centery = (SUELO_Y - 260) + int(pygame.time.get_ticks() % 1000 < 500) * 4
            
            for demonio in self.minidemonios:
                demonio.update(dt, player, self.proyectiles_fase)
                
            for p in self.proyectiles_fase[:]:
                p.update(player, dt)
                if p.impactado:
                    self.proyectiles_fase.remove(p)

            if self.timer_fase_especial <= 0:
                self.finalizar_fase_especial()

            self.actualizar_animacion()
            return

        if self.timer_para_fase > 0:
            self.timer_para_fase -= dt
        elif not self.attacking and self.on_ground:
            self.iniciar_fase_especial()
            return

        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= dt

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= SUELO_Y:
            self.rect.bottom = SUELO_Y
            self.velocity_y = 0
            self.on_ground = True

        distancia = player.rect.centerx - self.rect.centerx

        if abs(distancia) > 130:
            self.direction = "right" if distancia > 0 else "left"
            velocidad = 3.2
            
            if self.attacking:
                self.rect.x += velocidad * 1.2 if self.direction == "right" else -velocidad * 1.2
            else:
                self.rect.x += velocidad if self.direction == "right" else -velocidad
                if self.on_ground:
                    self.cambiar_estado("correr")
        elif not self.attacking and self.cooldown_ataque <= 0:
            self.direction = "right" if distancia > 0 else "left"
            self.attacking = True
            self.has_hit = False
            ataque = self.seleccionar_ataque_aleatorio()
            self.cambiar_estado(ataque)
        elif not self.attacking:
            self.cambiar_estado("idle")

        self.actualizar_hitbox_ataque()
        self.hurtbox = self.rect.copy()

        if self.attacking and not self.has_hit and self.hitbox.width > 0:
            cuerpo_jugador = getattr(player, 'hurtbox', player.rect)
            if self.hitbox.colliderect(cuerpo_jugador):
                if hasattr(player, 'take_damage'):
                    player.take_damage(self.dano_ataque)
                elif hasattr(player, 'recibir_danio'):
                    player.recibir_danio(self.dano_ataque)
                elif hasattr(player, 'health'):
                    player.health -= self.dano_ataque
                self.has_hit = True

        self.actualizar_animacion()

    def take_damage(self, damage):
        if self.health <= 0 or self.invulnerable:
            return
        self.health = max(0, self.health - damage)
        self.esta_rojo = True
        self.hit_timer = 0.15

    def dibujar_alas(self, screen, cx, cy):
        """Dibuja alas oscuras místicas cuando el jefe está en el aire durante la fase especial."""
        # Ala izquierda
        pts_izq = [(cx - 20, cy - 20), (cx - 110, cy - 80), (cx - 90, cy - 10), (cx - 130, cy + 30), (cx - 60, cy + 20)]
        pygame.draw.polygon(screen, (30, 0, 40), pts_izq)
        pygame.draw.polygon(screen, (120, 10, 40), pts_izq, 3)

        # Ala derecha
        pts_der = [(cx + 20, cy - 20), (cx + 110, cy - 80), (cx + 90, cy - 10), (cx + 130, cy + 30), (cx + 60, cy + 20)]
        pygame.draw.polygon(screen, (30, 0, 40), pts_der)
        pygame.draw.polygon(screen, (120, 10, 40), pts_der, 3)

    def draw(self, screen):
        if self.muerto_definitivo:
            return

        if self.en_fase_especial:
            # Dibujar proyectiles y minidemonios
            for p in self.proyectiles_fase:
                p.draw(screen)
            for demonio in self.minidemonios:
                demonio.draw(screen)

            # Dibujar alas detrás del jefe
            self.dibujar_alas(screen, self.rect.centerx, self.rect.centery)

        if self.image:
            offset_y = 35 

            if self.direction == "left":
                pos_x = self.rect.right - self.image.get_width()
            else:
                pos_x = self.rect.left

            if self.en_fase_especial:
                pos_y = self.rect.centery - (self.image.get_height() // 2)
            else:
                pos_y = (SUELO_Y - self.image.get_height()) + offset_y
            
            screen.blit(self.image, (pos_x, pos_y))