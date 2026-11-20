import os
import math
import random

import pygame


def _colisiona_mascara(mask, rect, objetivo):
    mascara_objetivo = pygame.mask.Mask(
        (objetivo.width, objetivo.height), fill=True
    )
    offset = (objetivo.left - rect.left, objetivo.top - rect.top)
    return mask.overlap(mascara_objetivo, offset) is not None


class ProyectilCorte:
    def __init__(self, imagen, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        angle = -math.degrees(math.atan2(self.vy, self.vx)) + 180
        corte = pygame.transform.scale(imagen, (330, 200))
        self.surface = pygame.transform.rotate(corte, angle)
        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect(center=(round(self.x), round(self.y)))
        self.dano = 12
        self.esquivado = False

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (round(self.x), round(self.y))

    def alcanza(self, rect):
        return _colisiona_mascara(self.mask, self.rect, rect)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)


class AtaqueX:
    def __init__(self, imagen_corte, center, angle_hacia_jugador):
        imagen_base = pygame.transform.scale(imagen_corte, (250, 150))
        self.cortes = []
        for offset in (-45, 45):
            angle = angle_hacia_jugador + 180 + offset
            surface = pygame.transform.rotate(imagen_base, angle)
            rect = surface.get_rect(center=center)
            self.cortes.append((surface, pygame.mask.from_surface(surface), rect))
        self.rect = self.cortes[0][2].union(self.cortes[1][2])
        self.warning = 0.62
        self.active = 0.20
        self.hit = False

    @property
    def esta_activo(self):
        return self.warning <= 0 and self.active > 0

    @property
    def terminado(self):
        return self.warning <= 0 and self.active <= 0

    def update(self, dt):
        if self.warning > 0:
            self.warning = max(0.0, self.warning - dt)
        else:
            self.active = max(0.0, self.active - dt)

    def alcanza(self, rect):
        if not self.esta_activo:
            return False
        return any(
            _colisiona_mascara(mask, slash_rect, rect)
            for _, mask, slash_rect in self.cortes
        )

    def draw(self, screen):
        if self.warning > 0:
            alpha = 90 + round(70 * math.sin((0.62 - self.warning) * 18) ** 2)
            for surface, _, slash_rect in self.cortes:
                aviso = surface.copy()
                aviso.fill(
                    (255, 75, 75, 255),
                    special_flags=pygame.BLEND_RGBA_MULT,
                )
                aviso.set_alpha(alpha)
                screen.blit(aviso, slash_rect)
        elif self.active > 0:
            for surface, _, slash_rect in self.cortes:
                screen.blit(surface, slash_rect)


class ProyectilX:
    def __init__(self, imagen_corte, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        imagen_base = pygame.transform.scale(imagen_corte, (230, 140))
        angle_hacia_jugador = -math.degrees(math.atan2(self.vy, self.vx))
        self.cortes = []
        for offset in (-45, 45):
            angle = angle_hacia_jugador + 180 + offset
            surface = pygame.transform.rotate(imagen_base, angle)
            rect = surface.get_rect(center=(round(x), round(y)))
            self.cortes.append((surface, pygame.mask.from_surface(surface), rect))
        self.rect = self.cortes[0][2].union(self.cortes[1][2])
        self.dano = 25
        self.esquivado = False

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        for _, _, rect in self.cortes:
            rect.center = (round(self.x), round(self.y))
        self.rect.center = (round(self.x), round(self.y))

    def alcanza(self, rect):
        return any(
            _colisiona_mascara(mask, slash_rect, rect)
            for _, mask, slash_rect in self.cortes
        )

    def draw(self, screen):
        for surface, _, slash_rect in self.cortes:
            screen.blit(surface, slash_rect)


class CiclopeCombatController:
    FASE_2_LIMITE = 0.75
    FASE_3_LIMITE = 0.35
    DANIO_MAXIMO_POR_MAREO = 55

    def __init__(self, jefe, ancho, suelo):
        self.jefe = jefe
        self.ancho = ancho
        self.suelo = suelo
        ruta_corte = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "Jefes",
            "Ciclope",
            "sombra.png",
        )
        self.imagen_corte = pygame.image.load(ruta_corte).convert_alpha()
        self.fase = 1
        self.estado = "combate"
        self.temporizador = 0.7
        self.transicion = 0.0
        self.duracion_transicion = 1.5
        self.proyectiles = []
        self.corte_x = None
        self.direccion_disparo = pygame.Vector2()
        self.objetivo_telegráfico = None
        self.especial_fase2 = random.uniform(6.5, 8.5)
        self.cortes_restantes = 0
        self.posiciones_fase3 = []
        self.indice_posicion_fase3 = 0
        self.disparos_posicion_fase3 = 0
        self.timer_muerte = 0.0
        self.efecto_teletransporte = 0.0
        self.origen_teletransporte = pygame.Vector2(jefe.rect.center)
        self.destino_teletransporte = pygame.Vector2(jefe.rect.center)
        self.jefe.fase_actual = 1
        self.jefe.vulnerable = False
        self.jefe.transicionando = False
        self.jefe.dano_en_vulnerabilidad = 0
        self.jefe.rect.bottom = suelo
        self.jefe.hurtbox = self.jefe.rect.copy()

    def _cambiar_fase_si_corresponde(self):
        porcentaje = self.jefe.health / self.jefe.max_health
        fase_objetivo = 1 if porcentaje > self.FASE_2_LIMITE else 2
        if porcentaje <= self.FASE_3_LIMITE:
            fase_objetivo = 3
        if fase_objetivo <= self.fase:
            return

        self.fase = fase_objetivo
        self.jefe.fase_actual = fase_objetivo
        if fase_objetivo == 2:
            self.especial_fase2 = random.uniform(6.5, 8.5)
        self.jefe.vulnerable = False
        self.jefe.transicionando = True
        self.jefe.attacking = False
        self.jefe.hitbox = pygame.Rect(0, 0, 0, 0)
        self.jefe.health = max(
            self.jefe.health,
            round(self.jefe.max_health * (
                self.FASE_2_LIMITE if fase_objetivo == 2 else self.FASE_3_LIMITE
            )),
        )
        self.proyectiles.clear()
        self.corte_x = None
        self.estado = "transicion"
        self.transicion = self.duracion_transicion

    def _teletransportar(self, center):
        self.origen_teletransporte.update(self.jefe.rect.center)
        self.destino_teletransporte.update(center)
        self.jefe.rect.center = (round(center[0]), round(center[1]))
        self.jefe.hurtbox = self.jefe.rect.copy()
        self.efecto_teletransporte = 0.42

    def _orientar(self, player):
        dx = player.hurtbox.centerx - self.jefe.rect.centerx
        self.jefe.direction = "right" if dx >= 0 else "left"
        self.jefe.attacking = False

    def _animar_jefe(self, estado, dt, velocidad=12, repetir=True):
        if estado not in self.jefe.animaciones or not self.jefe.animaciones[estado]:
            estado = "idle"
        if self.jefe.estado_actual != estado:
            self.jefe.cambiar_estado(estado)

        frames = self.jefe.animaciones[estado]
        self.jefe.frame_actual += dt * velocidad
        if repetir:
            self.jefe.frame_actual %= len(frames)
        else:
            self.jefe.frame_actual = min(self.jefe.frame_actual, len(frames) - 1)

        frame = frames[int(self.jefe.frame_actual)]
        espejar = self.jefe.direction == "left"
        if getattr(self.jefe, "invertir_orientacion_sprite", False):
            espejar = not espejar
        self.jefe.image = pygame.transform.flip(frame, True, False) if espejar else frame

    def _empezar_ataque_cuerpo(self, player):
        self._orientar(player)
        self.estado = "cuerpo_preparacion"
        self.temporizador = 0.58
        self.jefe.hitbox = pygame.Rect(0, 0, 0, 0)

    def _empezar_ataque_distancia(self, player):
        self._orientar(player)
        if self.jefe.estado_actual == "attack1":
            self.jefe.cambiar_estado("idle")
        self._actualizar_objetivo_disparo(player)
        self.estado = "distancia_preparacion"
        self.jefe.hitbox = pygame.Rect(0, 0, 0, 0)

    def _actualizar_objetivo_disparo(self, player):
        origen = pygame.Vector2(self.jefe.rect.center)
        self.objetivo_telegráfico = pygame.Vector2(player.hurtbox.center)
        direccion = self.objetivo_telegráfico - origen
        if direccion.length_squared() == 0:
            direccion.update(1 if self.jefe.direction == "right" else -1, 0)
        self.direccion_disparo = direccion.normalize()

    def _disparar_corte(self):
        origen_x = self.jefe.rect.centerx
        origen_y = self.jefe.rect.centery - 18
        velocidad = 345
        self.proyectiles.append(
            ProyectilCorte(
                self.imagen_corte,
                origen_x, origen_y,
                self.direccion_disparo.x * velocidad,
                self.direccion_disparo.y * velocidad,
            )
        )
        self.estado = "distancia_recuperacion"
        self.temporizador = 1.05

    def _empezar_especial_fase2(self, player):
        self._orientar(player)
        lado = random.choice(("izquierda", "derecha"))
        esquina_x = 135 if lado == "izquierda" else self.ancho - 135
        self._teletransportar((esquina_x, self.suelo - self.jefe.rect.height // 2))
        self.estado = "fase2_teletransporte"
        self.temporizador = 0.55
        self.cortes_restantes = 3

    def _crear_corte_fase2(self, player):
        direccion = pygame.Vector2(player.hurtbox.center) - pygame.Vector2(
            self.jefe.rect.center
        )
        angle_hacia_jugador = (
            -math.degrees(math.atan2(direccion.y, direccion.x))
            if direccion.length_squared()
            else 0
        )
        self.corte_x = AtaqueX(
            self.imagen_corte, player.hurtbox.center, angle_hacia_jugador
        )
        self.estado = "fase2_cortes"

    def _empezar_fase3(self):
        self.jefe.vulnerable = False
        self.jefe.dano_en_vulnerabilidad = 0
        self.posiciones_fase3 = [
            (self.ancho // 2, 170),
            (125, 350),
            (self.ancho - 125, 350),
        ]
        random.shuffle(self.posiciones_fase3)
        self.indice_posicion_fase3 = 0
        self._teletransportar(self.posiciones_fase3[0])
        self.estado = "fase3_teletransporte"
        self.temporizador = 0.4
        self.disparos_posicion_fase3 = 3

    def _entrar_en_mareo(self):
        center = (self.ancho // 2, self.suelo - self.jefe.rect.height // 2)
        self._teletransportar(center)
        self.jefe.vulnerable = True
        self.jefe.dano_en_vulnerabilidad = 0
        self.estado = "mareo"
        self.temporizador = 5.2

    def _disparar_x(self):
        origen = pygame.Vector2(self.jefe.rect.center)
        angulo = {3: -0.10, 2: 0.0, 1: 0.10}[self.disparos_posicion_fase3]
        direccion = self.direccion_disparo.rotate_rad(angulo)
        velocidad = 350
        self.proyectiles.append(
            ProyectilX(
                self.imagen_corte,
                origen.x, origen.y,
                direccion.x * velocidad, direccion.y * velocidad,
            )
        )
        self.disparos_posicion_fase3 -= 1
        self.estado = "fase3_rafaga"
        self.temporizador = 0.08 if not self.disparos_posicion_fase3 else 0.52

    def _actualizar_ataque_cuerpo(self, dt, player):
        self.temporizador -= dt
        hitbox = pygame.Rect(0, 0, 165, 135)
        hitbox.bottom = self.jefe.rect.bottom
        if self.jefe.direction == "right":
            hitbox.left = self.jefe.rect.right - 12
        else:
            hitbox.right = self.jefe.rect.left + 12

        if self.estado == "cuerpo_preparacion":
            self._animar_jefe("attack1", dt, 10)
            if self.temporizador <= 0:
                self.estado = "cuerpo_activo"
                self.temporizador = 0.22
                self.jefe.has_hit = False
        else:
            self._animar_jefe("attack1", dt, 10)
            self.jefe.hitbox = hitbox
            if not self.jefe.has_hit and hitbox.colliderect(player.hurtbox):
                player.take_damage(18, attacker=hitbox)
                self.jefe.has_hit = True
            if self.temporizador <= 0:
                self.jefe.hitbox = pygame.Rect(0, 0, 0, 0)
                self.estado = "recuperacion"
                self.temporizador = 0.65

    def _actualizar_ataques(self, dt, player):
        distancia = abs(player.hurtbox.centerx - self.jefe.rect.centerx)

        if self.estado == "combate":
            self._orientar(player)
            if self.fase == 2:
                self.especial_fase2 -= dt
                if self.especial_fase2 <= 0:
                    self._empezar_especial_fase2(player)
                    return

            if self.fase == 3:
                self._empezar_fase3()
                return

            if distancia <= 210:
                self._empezar_ataque_cuerpo(player)
            elif distancia > 370 and self.fase == 1:
                self._empezar_ataque_distancia(player)
            else:
                self.jefe.rect.x += (
                    145 * dt if self.jefe.direction == "right" else -145 * dt
                )
                self.jefe.rect.x = max(55, min(self.ancho - 55 - self.jefe.rect.width, self.jefe.rect.x))
                self.jefe.hurtbox = self.jefe.rect.copy()
                self._animar_jefe("correr", dt)
            return

        if self.estado in ("cuerpo_preparacion", "cuerpo_activo"):
            self._actualizar_ataque_cuerpo(dt, player)
            return

        if self.estado == "distancia_preparacion":
            self._actualizar_objetivo_disparo(player)
            self._animar_jefe("attack1", dt, 10, repetir=False)
            if self.jefe.frame_actual >= 4:
                self._disparar_corte()
            return

        if self.estado == "distancia_recuperacion":
            self.temporizador -= dt
            self._animar_jefe("attack1", dt, 10, repetir=False)
            if self.temporizador <= 0:
                self.estado = "combate"
            return

        if self.estado == "recuperacion":
            self.temporizador -= dt
            self._animar_jefe("idle", dt)
            if self.temporizador <= 0:
                self.estado = "combate"
            return

        if self.estado == "fase2_teletransporte":
            self.temporizador -= dt
            self._animar_jefe("cast", dt)
            if self.temporizador <= 0:
                self._orientar(player)
                self.estado = "fase2_golpe"
                self.temporizador = len(self.jefe.animaciones["attack1"]) / 10
            return

        if self.estado == "fase2_golpe":
            self._orientar(player)
            self._animar_jefe("attack1", dt, 10, repetir=False)
            self.temporizador -= dt
            if self.temporizador <= 0:
                self._crear_corte_fase2(player)
            return

        if self.estado == "fase2_cortes":
            self.corte_x.update(dt)
            if (
                self.corte_x.esta_activo
                and not self.corte_x.hit
                and self.corte_x.alcanza(player.hurtbox)
            ):
                player.take_damage(16, attacker=self.corte_x)
                self.corte_x.hit = True
            if self.corte_x.terminado:
                self.cortes_restantes -= 1
                if self.cortes_restantes:
                    self._crear_corte_fase2(player)
                else:
                    self.corte_x = None
                    self.estado = "recuperacion"
                    self.temporizador = 0.65
                    self.especial_fase2 = random.uniform(8.0, 10.0)
            self._animar_jefe("cast", dt)
            return

        if self.estado == "fase3_teletransporte":
            self.temporizador -= dt
            self._animar_jefe("cast", dt)
            if self.temporizador <= 0:
                self.estado = "fase3_apuntar"
                self.temporizador = 0.0
                self.objetivo_telegráfico = pygame.Vector2(player.hurtbox.center)
                direccion = self.objetivo_telegráfico - pygame.Vector2(
                    self.jefe.rect.center
                )
                if direccion.length_squared() == 0:
                    direccion.update(1, 0)
                self.direccion_disparo = direccion.normalize()
            return

        if self.estado == "fase3_apuntar":
            self._actualizar_objetivo_disparo(player)
            self._animar_jefe("attack1", dt, 10, repetir=False)
            if self.jefe.frame_actual >= 4:
                self._disparar_x()
            return

        if self.estado == "fase3_rafaga":
            self.temporizador -= dt
            self._animar_jefe("cast", dt)
            if self.temporizador <= 0:
                if self.disparos_posicion_fase3:
                    self.estado = "fase3_apuntar"
                    self.temporizador = 0.0
                else:
                    self.indice_posicion_fase3 += 1
                    if self.indice_posicion_fase3 >= len(self.posiciones_fase3):
                        self._entrar_en_mareo()
                    else:
                        self._teletransportar(
                            self.posiciones_fase3[self.indice_posicion_fase3]
                        )
                        self.estado = "fase3_teletransporte"
                        self.temporizador = 0.12
                        self.disparos_posicion_fase3 = 3
            return

        if self.estado == "mareo":
            self.temporizador -= dt
            self._animar_jefe("idle", dt, 7)
            if self.temporizador <= 0 or (
                self.jefe.dano_en_vulnerabilidad
                >= self.DANIO_MAXIMO_POR_MAREO
            ):
                self.jefe.vulnerable = False
                self.estado = "combate"
            return

        if self.estado == "derrota":
            self.timer_muerte += dt
            self._animar_jefe("muerte", dt, 8, repetir=False)
            if self.timer_muerte >= 1.5:
                self.jefe.muerto_definitivo = True

    def update(self, dt, player, screen):
        self._cambiar_fase_si_corresponde()
        self.efecto_teletransporte = max(0.0, self.efecto_teletransporte - dt)

        if self.jefe.esta_rojo:
            self.jefe.hit_timer = max(0.0, self.jefe.hit_timer - dt)
            if self.jefe.hit_timer == 0:
                self.jefe.esta_rojo = False

        if self.jefe.health <= 0 and self.estado != "derrota":
            self.jefe.health = 0
            self.jefe.vulnerable = False
            self.jefe.transicionando = False
            self.jefe.attacking = False
            self.proyectiles.clear()
            self.corte_x = None
            self.estado = "derrota"
            self.timer_muerte = 0.0

        if self.jefe.muerto_definitivo:
            return

        if self.estado == "transicion":
            self.transicion -= dt
            self._animar_jefe("cast", dt)
            if self.transicion <= 0:
                self.jefe.transicionando = False
                if self.fase == 3:
                    self._empezar_fase3()
                else:
                    self.estado = "combate"
                    self.temporizador = 0.0
            return

        if self.estado == "derrota":
            self._actualizar_ataques(dt, player)
            return

        if self.fase == 3 and self.estado == "combate":
            self._empezar_fase3()
            return

        self._actualizar_ataques(dt, player)

        for proyectil in self.proyectiles[:]:
            proyectil.update(dt)
            if proyectil.alcanza(player.hurtbox) and not proyectil.esquivado:
                if player.rodando:
                    proyectil.esquivado = True
                else:
                    player.take_damage(proyectil.dano, attacker=proyectil)
                    self.proyectiles.remove(proyectil)
            if (
                proyectil in self.proyectiles
                and not screen.get_rect().inflate(100, 100).colliderect(proyectil.rect)
            ):
                self.proyectiles.remove(proyectil)

        if self.estado in ("distancia_preparacion", "fase3_apuntar"):
            self._orientar(player)

    def draw(self, screen, tiempo):
        if self.efecto_teletransporte > 0:
            progreso = 1 - self.efecto_teletransporte / 0.42
            for center, alpha_base in (
                (self.origen_teletransporte, 115),
                (self.destino_teletransporte, 190),
            ):
                radio = 18 + round(progreso * 55)
                color = (195, 55, 255, max(0, round(alpha_base * (1 - progreso))))
                aura = pygame.Surface((radio * 2 + 4, radio * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(aura, color, (radio + 2, radio + 2), radio, 4)
                screen.blit(aura, (round(center.x - radio - 2), round(center.y - radio - 2)))

        if self.estado in ("distancia_preparacion", "fase3_apuntar"):
            destino = self.objetivo_telegráfico
            if destino is not None:
                pygame.draw.line(
                    screen, (175, 85, 255), self.jefe.rect.center, destino, 2,
                )
                pygame.draw.circle(screen, (195, 115, 255), destino, 13, 2)

        if self.corte_x is not None:
            self.corte_x.draw(screen)
        for proyectil in self.proyectiles:
            proyectil.draw(screen)

        if self.estado == "mareo":
            center_x = self.jefe.rect.centerx
            head_y = self.jefe.rect.top + 20
            for index in range(3):
                angle = tiempo * 4 + index * math.tau / 3
                x = round(center_x + math.cos(angle) * 52)
                y = round(head_y + math.sin(angle) * 16)
                pygame.draw.line(screen, (255, 235, 120), (x, y + 8), (x + 5, y - 5), 3)
                pygame.draw.line(screen, (255, 235, 120), (x + 5, y - 5), (x + 10, y + 8), 3)
