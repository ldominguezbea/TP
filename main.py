import pygame
from enemigos import Enemigo, crear_enemigo_aleatorio 
from jugadores import Player
pygame.init()

WIDTH = 1350
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plataformero")

clock = pygame.time.Clock()


fondo = pygame.image.load("assets/fondos/fondo_mvp.png")
fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))


player = Player(200, 200)


enemy = crear_enemigo_aleatorio(800, 300) 

player_damage = 20
enemy_damage = 12

running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player.attack()

    player.update(dt)
    enemy.update(player, dt)

    if player.attacking and not player.has_hit:
        if player.hitbox.colliderect(enemy.hurtbox):
            enemy.take_damage(player_damage)
            player.has_hit = True

    if enemy.attacking and not enemy.has_hit:
        if enemy.hitbox.colliderect(player.hurtbox):
            player.take_damage(enemy_damage)
            enemy.has_hit = True


    cargar_imagen = pygame.image.load("fondo.png").convert()
    fondo_ = pygame.transform.scale(cargar_imagen, (WIDTH, HEIGHT))

    player.draw()
    pygame.draw.rect(screen, (255, 50, 50), enemy.rect) 
    pygame.draw.rect(screen, (0, 255, 0), enemy.hurtbox, 2) 
    if enemy.attacking:
        pygame.draw.rect(screen, (255, 150, 0), enemy.hitbox, 2)

    pygame.display.flip()

pygame.quit()


