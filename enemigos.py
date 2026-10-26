import pygame, random


class Enemigo():
    def __init__(self, nombre, vida):
        self.nombre = nombre
        self.vida = vida


class OrcoRojo(Enemigo):
    def __init__(self):
        super().__init__("Orco Rojo", 100)


class esqueletoNegro(Enemigo):
    def __init__(self):
        super().__init__("Esqueleto Negro", 100)


orco = OrcoRojo()
esqueleto_negro= esqueletoNegro()

enemigos = [OrcoRojo, esqueletoNegro]

def crear_enemigos():
    enemigo = random.choice(enemigos)
    v_ataque = 5
    while enemigo.vida != 0:
        pygame.time.set_timer()
        pass
crear_enemigos()

def hola():
    print("Hola")
    
