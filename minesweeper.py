import pygame
import sys

pygame.init()

BACKGROUND_COLOR = (255, 105, 180)  

screen = pygame.display.set_mode((800,600), pygame.RESIZABLE)
pygame.display.set_caption("Minesweeper")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)
    pygame.display.flip()


pygame.quit()
sys.exit()