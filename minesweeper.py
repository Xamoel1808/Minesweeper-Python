import pygame
import sys

from pygame import KEYDOWN

pygame.init()

BACKGROUND_COLOR = (255, 105, 180)

width=500
height=600
screen = pygame.display.set_mode((width,height), pygame.RESIZABLE)
pygame.display.set_caption("Minesweeper")

font = pygame.font.SysFont("arialblack", 40)

color = (255, 255, 255)

def draw_text (text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

class Button():
    def __init__(self, x, y, text):
        self.text_surface = font.render(text, True, color)  # Crée une surface pour le texte
        self.rect = self.text_surface.get_rect(topleft=(x, y))
    def draw(self, screen):
        screen.blit(self.text_surface, self.rect)
    def isPressed(self, pos):
        return self.rect.collidepoint(pos)



start_button = Button(height/2, width/2, "Start")
option_button = Button(50, 150, "Option")
quit_button = Button(50, 250, "Quit")


def play():
    while True:
        screen.fill("black")
        back_button = Button(50, 150, "Back")
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.isPressed(event.pos):
                    main_menu()

        pygame.display.update()
        pygame.display.flip()

def quit():
    pygame.quit()
    sys.exit()

def option():
    while True:
        screen.fill("pink")
        back_button = Button(50, 150, "Back")
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.isPressed(event.pos):
                    main_menu()

        pygame.display.update()
        pygame.display.flip()

def main_menu():
    while True:
        screen.fill(BACKGROUND_COLOR)

        start_button.draw(screen)
        option_button.draw(screen)
        quit_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.isPressed(event.pos):
                    play()
                if quit_button.isPressed(event.pos):
                    quit()
                if option_button.isPressed(event.pos):
                    option()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        pygame.display.flip()

main_menu()