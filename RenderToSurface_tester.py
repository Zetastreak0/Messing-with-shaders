import pygame
from RenderToSurface_pipeline import *
from pygame.locals import *
from OpenGL.GL import *
import sys
import time

BLACK = (0,0,0)
WHITE = (255,255,255)

pygame.init()

size = [900, 720]
FRAMERATE = 60

screen = pygame.display.set_mode(size, DOUBLEBUF | OPENGL)

clock = pygame.time.Clock()

done = False


init_shaders()
change_active("blackHoleSoloAngledTrue")
set_viewport(size[0], size[1])
tex_id = None

overlay = pygame.Surface(size, pygame.SRCALPHA)
OVRect = overlay.get_rect()
overlay.fill((0,0,0,0))
overlay.set_alpha()

player = pygame.Surface((50, 50))
playerrect = player.get_rect()
player.fill(WHITE)
movement = [0,0]

check()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                movement[1] = -5
            if event.key == pygame.K_a:
                movement[0] = -5
            if event.key == pygame.K_s:
                movement[1] = 5
            if event.key == pygame.K_d:
                movement[0] = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                movement[1] = 0
            if event.key == pygame.K_a:
                movement[0] = 0
            if event.key == pygame.K_s:
                movement[1] = 0
            if event.key == pygame.K_d:
                movement[0] = 0

    playerrect.x += movement[0]
    playerrect.y += movement[1]

    overlay.fill((0,0,0,0))
    overlay.blit(player, playerrect.topleft)

    update_shaders(size[0], size[1], True)
    tex_id = update_layers(overlay, tex_id)
    
    pygame.display.flip()
    clock.tick(FRAMERATE)

pygame.quit()
