import pygame
import math


SCREEN_WIDTH = 1360
SCREEN_HEIGHT = 720
GAME_WIDTH = 320
GAME_HEIGHT = 180

def draw_cool_indicator_demon(surface, x, y, time):
    pulse = abs(math.sin(time * 6))
    glow_surf = pygame.Surface((18, 18), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (255, 30, 0, int(60 + pulse * 80)), (9, 9), 8)
    surface.blit(glow_surf, (x - 2, y - 2))
    
    pygame.draw.polygon(surface, (180, 10, 10), [
        (x + 3, y + 3), (x + 11, y + 3), (x + 13, y + 7), (x + 7, y + 13), (x + 1, y + 7)
    ])
    pygame.draw.polygon(surface, (255, 50, 0), [(x + 2, y + 3), (x - 1, y - 3), (x + 4, y + 1)])
    pygame.draw.polygon(surface, (255, 50, 0), [(x + 12, y + 3), (x + 15, y - 3), (x + 10, y + 1)])
    surface.set_at((x - 1, y - 3), (255, 200, 0))
    surface.set_at((x + 15, y - 3), (255, 200, 0))
    
    pygame.draw.line(surface, (255, 255, 100), (x + 3, y + 6), (x + 5, y + 7), 1)
    pygame.draw.line(surface, (255, 255, 100), (x + 11, y + 6), (x + 9, y + 7), 1)
    
    pygame.draw.line(surface, (20, 0, 0), (x + 4, y + 10), (x + 10, y + 10), 1)
    surface.set_at((x + 5, y + 11), (255, 255, 255))
    surface.set_at((x + 9, y + 11), (255, 255, 255))

def draw_detailed_civilian(surface, x, y, direction, time):
    leg_swing = math.sin(time * 16) * 4 * direction
    arm_swing = math.sin(time * 16 + math.pi) * 3 * direction
    ix, iy = int(x), int(y)
    
    pygame.draw.ellipse(surface, (5, 2, 2), (ix - 3, iy + 7, 10, 4))
    pygame.draw.line(surface, (25, 25, 35), (ix + 2, iy + 4), (ix + 1 + int(leg_swing), iy + 8), 2)
    pygame.draw.line(surface, (25, 25, 35), (ix + 3, iy + 4), (ix + 4 - int(leg_swing), iy + 8), 2)
    surface.set_at((ix + 1 + int(leg_swing), iy + 8), (200, 200, 200))
    surface.set_at((ix + 4 - int(leg_swing), iy + 8), (200, 200, 200))
    
    pygame.draw.rect(surface, (30, 80, 170), (ix, iy - 1, 5, 5))
    pygame.draw.rect(surface, (30, 110, 40), (ix, iy + 2, 5, 2))
    
    pygame.draw.line(surface, (215, 160, 125), (ix + 1, iy), (ix - int(arm_swing), iy + 3), 1)
    pygame.draw.line(surface, (215, 160, 125), (ix + 4, iy), (ix + 4 + int(arm_swing), iy + 3), 1)
    pygame.draw.rect(surface, (215, 160, 125), (ix + 1, iy - 5, 4, 4))

    eye_x = ix + 1 if direction < 0 else ix + 3
    surface.set_at((eye_x, iy - 3), (0, 0, 0))

def draw_cool_demon(surface, x, y, direction, time):
    leg_swing = math.sin(time * 12) * 4 * direction
    wing_flap = math.sin(time * 8) * 3
    ix, iy = int(x), int(y)
    
    pygame.draw.ellipse(surface, (5, 2, 2), (ix - 5, iy + 9, 14, 3))
    
    w_off = int(wing_flap)
    wing_pts_l = [(ix + 2, iy - 2), (ix - 10 * direction, iy - 10 + w_off), (ix - 4 * direction, iy + 3)]
    wing_pts_r = [(ix + 4, iy - 2), (ix + 12 * direction, iy - 10 + w_off), (ix + 6 * direction, iy + 3)]
    pygame.draw.polygon(surface, (80, 0, 0), wing_pts_l)
    pygame.draw.polygon(surface, (140, 10, 10), wing_pts_l, 1)
    pygame.draw.polygon(surface, (80, 0, 0), wing_pts_r)
    pygame.draw.polygon(surface, (140, 10, 10), wing_pts_r, 1)
    
    pygame.draw.line(surface, (120, 10, 10), (ix + 2, iy + 4), (ix + int(leg_swing), iy + 9), 2)
    pygame.draw.line(surface, (120, 10, 10), (ix + 5, iy + 4), (ix + 6 - int(leg_swing), iy + 9), 2)
    
    pygame.draw.polygon(surface, (180, 20, 20), [(ix, iy - 4), (ix + 7, iy - 4), (ix + 5, iy + 5), (ix + 2, iy + 5)])
    pygame.draw.polygon(surface, (110, 10, 10), [(ix + 2, iy - 2), (ix + 5, iy - 2), (ix + 4, iy + 4), (ix + 3, iy + 4)])
    
    pygame.draw.line(surface, (230, 30, 30), (ix + 1, iy - 2), (ix - 2 * direction, iy + 2), 1)
    
    pygame.draw.rect(surface, (200, 25, 25), (ix + 1, iy - 8, 5, 5))
    pygame.draw.polygon(surface, (255, 80, 0), [(ix + 1, iy - 7), (ix - 3 * direction, iy - 13), (ix + 2, iy - 7)])
    pygame.draw.polygon(surface, (255, 80, 0), [(ix + 5, iy - 7), (ix + 8 * direction, iy - 13), (ix + 4, iy - 7)])
    
    eye_x = ix + 1 if direction < 0 else ix + 4
    surface.set_at((eye_x, iy - 6), (255, 230, 0))
    surface.set_at((eye_x + direction, iy - 6), (255, 100, 0))

def draw_flying_demon(surface, x, y, direction, time, offset):
    wing_flap = math.sin(time * 10 + offset) * 5
    float_y = math.sin(time * 3 + offset) * 2
    ix, iy = int(x), int(y + float_y)
    
    w_off = int(wing_flap)
    
    wing_l = [(ix + 1, iy), (ix - 12 * direction, iy - 8 + w_off), (ix - 5 * direction, iy + 4)]
    wing_r = [(ix + 3, iy), (ix + 14 * direction, iy - 8 + w_off), (ix + 7 * direction, iy + 4)]
    
    pygame.draw.polygon(surface, (100, 0, 0), wing_l)
    pygame.draw.polygon(surface, (180, 20, 20), wing_l, 1)
    pygame.draw.polygon(surface, (100, 0, 0), wing_r)
    pygame.draw.polygon(surface, (180, 20, 20), wing_r, 1)
    
    pygame.draw.ellipse(surface, (160, 15, 15), (ix - 1, iy - 2, 6, 4))
    pygame.draw.line(surface, (120, 10, 10), (ix + 2, iy + 2), (ix - 4 * direction, iy + 6), 1)
    
    eye_x = ix if direction < 0 else ix + 3
    surface.set_at((eye_x, iy - 1), (255, 255, 0))

def draw_giant_demon(surface, time):
    float_y = math.sin(time * 1.5) * 2
    gx = 118
    gy = int(-2 + float_y)

    giant_surf = pygame.Surface((100, 140), pygame.SRCALPHA)
    pygame.draw.polygon(giant_surf, (20, 3, 3), [(25, 50), (55, 50), (75, 140), (5, 140)])
    pygame.draw.polygon(giant_surf, (15, 2, 2), [(35, 50), (45, 50), (50, 140), (30, 140)])

    pygame.draw.polygon(giant_surf, (30, 5, 5), [(10, 25), (-5, -5), (20, 15)])
    pygame.draw.polygon(giant_surf, (30, 5, 5), [(70, 25), (85, -5), (60, 15)])

    pygame.draw.polygon(giant_surf, (25, 4, 4), [(15, 10), (65, 10), (55, 50), (25, 50)])

    pygame.draw.rect(giant_surf, (255, 230, 0), (24, 20, 10, 6))
    pygame.draw.rect(giant_surf, (255, 230, 0), (46, 20, 10, 6))
    pygame.draw.rect(giant_surf, (200, 0, 0), (28, 20, 2, 6))
    pygame.draw.rect(giant_surf, (200, 0, 0), (50, 20, 2, 6))

    pygame.draw.polygon(giant_surf, (0, 0, 0), [(22, 34), (58, 34), (50, 48), (30, 48)])

    for tx in range(24, 56, 4):
        pygame.draw.polygon(giant_surf, (255, 255, 255), [(tx, 34), (tx + 2, 34), (tx + 1, 38)])
    for tx in range(28, 50, 4):
        pygame.draw.polygon(giant_surf, (255, 255, 255), [(tx, 48), (tx + 2, 48), (tx + 1, 44)])

    surface.blit(giant_surf, (gx, gy))

def draw_scenery(surface, time):
    surface.fill((10, 2, 2))
    glow = pygame.Surface((GAME_WIDTH, 90), pygame.SRCALPHA)
    pygame.draw.rect(glow, (140, 25, 0, 45), (0, 0, GAME_WIDTH, 90))
    surface.blit(glow, (0, GAME_HEIGHT - 90))

    draw_giant_demon(surface, time)

    buildings = [
        {"x": 60, "y": 40, "w": 45, "h": 100, "antenna": True},
        {"x": 110, "y": 25, "w": 55, "h": 115, "antenna": False},
        {"x": 170, "y": 50, "w": 40, "h": 90, "antenna": True},
        {"x": 215, "y": 30, "w": 50, "h": 110, "antenna": False},
        {"x": 270, "y": 60, "w": 50, "h": 80, "antenna": True}
    ]

    for b in buildings:
        bx, by, bw, bh = b["x"], b["y"], b["w"], b["h"]
        pygame.draw.rect(surface, (18, 6, 6), (bx, by, bw, bh))
        pygame.draw.rect(surface, (45, 12, 12), (bx, by, bw, bh), 1)
        pygame.draw.rect(surface, (30, 8, 8), (bx - 2, by - 2, bw + 4, 3))
        pygame.draw.rect(surface, (55, 15, 15), (bx - 2, by - 2, bw + 4, 3), 1)

        if b["antenna"]:
            pygame.draw.line(surface, (60, 20, 20), (bx + bw // 2, by - 2), (bx + bw // 2, by - 12), 1)
            surface.set_at((bx + bw // 2, by - 12), (255, 60, 0))

        for wx in range(bx + 4, bx + bw - 6, 8):
            for wy in range(by + 8, by + bh - 10, 10):
                if (wx * 7 + wy * 3) % 5 == 0:
                    pygame.draw.rect(surface, (230, 100, 0), (wx, wy, 4, 5))
                    pygame.draw.rect(surface, (255, 200, 50), (wx + 1, wy + 1, 2, 3))
                else:
                    pygame.draw.rect(surface, (10, 3, 3), (wx, wy, 4, 5))

    pygame.draw.rect(surface, (15, 12, 12), (0, 140, GAME_WIDTH, GAME_HEIGHT - 140))
    pygame.draw.rect(surface, (22, 18, 18), (0, 152, GAME_WIDTH, GAME_HEIGHT - 152))
    pygame.draw.line(surface, (45, 35, 35), (0, 140), (GAME_WIDTH, 140), 1)
    pygame.draw.line(surface, (38, 28, 28), (0, 152), (GAME_WIDTH, 152), 1)

    pygame.draw.line(surface, (255, 60, 0), (30, 165), (55, 168), 1)
    pygame.draw.line(surface, (255, 60, 0), (140, 146), (160, 148), 1)
    pygame.draw.line(surface, (255, 60, 0), (230, 160), (255, 163), 1)

    for fx in range(0, GAME_WIDTH, 8):
        fh = int(abs(math.sin(fx * 0.3 + time * 4) * 5) + abs(math.cos(fx * 0.1 + time * 3) * 3))
        if fh > 1:
            pygame.draw.rect(surface, (255, 40, 0), (fx, 140 - fh, 3, fh))
            pygame.draw.rect(surface, (255, 180, 0), (fx + 1, 140 - fh + 2, 1, fh - 2))