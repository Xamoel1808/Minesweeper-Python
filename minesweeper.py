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
    def __init__(self, text):
        self.text_surface = font.render(text, True, color)
        self.rect = self.text_surface.get_rect()
        self.text = text
        self.update_position()
    
    def update_position(self):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate vertical spacing between buttons
        button_spacing = 80
        total_height = button_spacing * 3  # for 3 buttons
        start_y = (screen_height - total_height) // 2

        # Center horizontally and position vertically based on button type
        if self.text == "Start":
            self.rect.center = (screen_width // 2, start_y)
        elif self.text == "Option":
            self.rect.center = (screen_width // 2, start_y + button_spacing)
        elif self.text == "Quit":
            self.rect.center = (screen_width // 2, start_y + button_spacing * 2)
        elif self.text == "Back":
            self.rect.center = (screen_width // 2, start_y)

    def draw(self, screen):
        screen.blit(self.text_surface, self.rect)

    def isPressed(self, pos):
        return self.rect.collidepoint(pos)

start_button = Button("Start")
option_button = Button("Option")
quit_button = Button("Quit")

def play():
    while True:
        screen.fill("black")
        back_button = Button("Back")
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.isPressed(event.pos):
                    main_menu()
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position()

        pygame.display.update()
        pygame.display.flip()

def quit():
    pygame.quit()
    sys.exit()

def option():
    while True:
        screen.fill("pink")
        back_button = Button("Back")
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.isPressed(event.pos):
                    main_menu()
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position()

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
            if event.type == pygame.VIDEORESIZE:
                start_button.update_position()
                option_button.update_position()
                quit_button.update_position()

        pygame.display.update()
        pygame.display.flip()

main_menu()