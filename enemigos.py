import pygame
import random

WIDTH = 1350

class Enemigo:
    def __init__(self, name, speed, x, y):
        self.name = name
        self.speed = speed
        self.rect = pygame.Rect(x, y, 60, 90)
        self.health = 120
        self.max_health = 120
        self.direction = "left"
        self.hurtbox = pygame.Rect(x, y, 60, 90)
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.8
        self.has_hit = False
    
    def update(self, player, dt):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
            self.direction = "right"
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed
            self.direction = "left"

        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed

        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(10, min(590 - self.rect.height, self.rect.y))
        
        self.hurtbox.topleft = self.rect.topleft

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        distance_x = abs(self.rect.centerx - player.rect.centerx)
        distance_y = abs(self.rect.centery - player.rect.centery)

        if distance_x < 100 and distance_y < 80:
            if not self.attacking:
                self.attack()

        if self.attacking:
            if self.direction == "right":
                self.hitbox.topleft = (self.rect.right, self.rect.y + 20)
            else:
                self.hitbox.topleft = (self.rect.left - 50, self.rect.y + 20)
            
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attacking = False
                self.has_hit = False
                self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self):
        if self.attack_cooldown > 0:
            return
        self.attacking = True
        self.attack_timer = 0.15
        self.attack_cooldown = self.attack_cooldown_time
        self.has_hit = False
        
        if self.direction == "right":
            self.hitbox = pygame.Rect(self.rect.right, self.rect.y + 20, 50, 50)
        else:
            self.hitbox = pygame.Rect(self.rect.left - 50, self.rect.y + 20, 50, 50)

    def take_damage(self, damage):
        self.health -= damage
        print(f"{self.name} recibió {damage} de daño. Vida restante: {self.health}")

enemy = Enemigo(550, 500)

class OrcoRojo(Enemigo):
    def __init__(self, x, y):
        super().__init__("Orco Rojo", 2, x, y)

class Carnicero(Enemigo):
    def __init__(self, x, y):
        super().__init__("Carnicero", 3, x, y)

class MinotauroNaranja(Enemigo):
    def __init__(self, x, y):
        super().__init__("Minotauro Naranja", 2, x, y)

class Jokai(Enemigo):
    def __init__(self, x, y):
        super().__init__("Jokai", 2, x, y)

class HombreLoboRojo(Enemigo):
    def __init__(self, x, y):
        super().__init__("HombreLoboRojo", 2, x, y)

class Mago(Enemigo):
    def __init__(self, x, y):
        super().__init__("Mago", 3, x, y)

class Cthulhu(Enemigo):
    def __init__(self, x, y):
        super().__init__("Cthulhu", 3, x, y)

class Cerbero(Enemigo):
    def __init__(self, x, y):
        super().__init__("Cerbero", 3, x, y)

class OrcoRojo2(Enemigo):
    def __init__(self, x, y):
        super().__init__("Orco Rojo 2", 3, x, y)

class Demonio(Enemigo):
    def __init__(self, x, y):
        super().__init__("Demonio", 2, x, y)

class CaballeroInfernal(Enemigo):
    def __init__(self, x, y):
        super().__init__("Caballero Infernal", 3, x, y)

class Dragon(Enemigo):
    def __init__(self, x, y):
        super().__init__("Dragon", 2, x, y)


enemigos_normales = [OrcoRojo, MinotauroNaranja, Jokai, HombreLoboRojo, Demonio, Dragon]
enemigos_jefes = [Carnicero, Cthulhu, Cerbero, OrcoRojo2, CaballeroInfernal]

def crear_enemigo_aleatorio(x, y):
    clase_enemigo = random.choice(enemigos_normales)
    nuevo_enemigo = clase_enemigo(x, y) 
    return nuevo_enemigo

