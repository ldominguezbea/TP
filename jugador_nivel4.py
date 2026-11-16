import pygame

from personajes import crear_jugador


class JugadorSeleccionadoNivel4:
    def __init__(
        self,
        x,
        suelo_y,
        ancho_pantalla,
        vida_maxima=150,
    ):
        self.personaje = crear_jugador(
            x,
            suelo_y,
            suelo_y,
            ancho_pantalla,
            ancho_pantalla,
        )
        self.personaje.vida_maxima = vida_maxima
        self.personaje.vida = vida_maxima
        self.personaje.plataformas = []
        self._rect = self.personaje.hurtbox.copy()
        self._imagen_cache = {}
        self._actualizar_rect()

    @property
    def rect(self):
        return self._rect

    @property
    def hurtbox(self):
        return self._rect

    @property
    def hitbox(self):
        return self.personaje.hitbox

    @property
    def health(self):
        return self.personaje.health

    @health.setter
    def health(self, value):
        self.personaje.health = value

    @property
    def max_health(self):
        return self.personaje.max_health

    @max_health.setter
    def max_health(self, value):
        self.personaje.max_health = value

    @property
    def attacking(self):
        return self.personaje.atacando

    @property
    def has_hit(self):
        return self.personaje.has_hit

    @has_hit.setter
    def has_hit(self, value):
        self.personaje.has_hit = value

    @property
    def pos_x(self):
        return self.personaje.pos_x

    @property
    def velocity_y(self):
        return self.personaje.velocidad_y

    @velocity_y.setter
    def velocity_y(self, value):
        self.personaje.velocidad_y = value

    @property
    def on_ground(self):
        return self.personaje.en_suelo

    @on_ground.setter
    def on_ground(self, value):
        self.personaje.en_suelo = value

    def _actualizar_rect(self):
        self._rect.center = self.personaje.hurtbox.center

    def procesar_evento(self, evento):
        self.personaje.procesar_evento(evento)

    def attack(self):
        evento = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": pygame.BUTTON_LEFT, "pos": self._rect.center},
        )
        self.procesar_evento(evento)

    def update(self, dt, platform=None):
        if dt <= 0:
            return
        self.personaje.plataformas = [platform] if platform is not None else []
        self.personaje.update(0, transicion_realizada=True)
        self._actualizar_rect()

    def take_damage(self, damage):
        self.personaje.take_damage(damage)

    def set_position(self, x, suelo_y):
        self.personaje.posicion_suelo = suelo_y
        self.personaje.pos_x = float(x)
        self.personaje.rect.midbottom = (round(x), suelo_y)
        self.personaje.velocidad_x = 0
        self.personaje.velocidad_y = 0
        self.personaje.en_suelo = True
        self.personaje.actualizar_hitboxes()
        self._actualizar_rect()

    def _imagen_visible(self):
        imagen = self.personaje.image
        clave = (
            self.personaje.estado,
            int(self.personaje.frame_index),
            self.personaje.mirando_derecha,
        )
        if clave not in self._imagen_cache:
            limites = imagen.get_bounding_rect()
            if limites.width == 0 or limites.height == 0:
                raise ValueError(
                    "El personaje seleccionado tiene un fotograma vacío."
                )
            recorte = imagen.subsurface(limites).copy()
            escala = min(90 / recorte.get_width(), 110 / recorte.get_height())
            tamano = (
                max(1, round(recorte.get_width() * escala)),
                max(1, round(recorte.get_height() * escala)),
            )
            self._imagen_cache[clave] = pygame.transform.scale(recorte, tamano)
        return self._imagen_cache[clave]

    def draw(self, screen):
        imagen = self._imagen_visible()
        screen.blit(
            imagen,
            imagen.get_rect(midbottom=self.personaje.rect.midbottom),
        )
