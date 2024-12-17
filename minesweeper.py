import pygame
import sys
import random
from pygame import KEYDOWN

pygame.init()

BACKGROUND_COLOR = (255, 105, 180)

width=500
height=600
screen = pygame.display.set_mode((width,height), pygame.RESIZABLE)
pygame.display.set_caption("Minesweeper")

font = pygame.font.SysFont("arialblack", 40)

color = (255, 255, 255)

EASY_DIMS = (9, 9, 10)      
MEDIUM_DIMS = (16, 16, 40)
HARD_DIMS = (30, 16, 99)
CELL_SIZE = 30

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
        
        button_spacing = 80
        total_height = button_spacing * 3  
        start_y = (screen_height - total_height) // 2

        if self.text == "Start":
            self.rect.center = (screen_width // 2, start_y)
        elif self.text == "Easy":
            self.rect.center = (screen_width // 2, start_y)
        elif self.text == "Option":
            self.rect.center = (screen_width // 2, start_y + button_spacing)
        elif self.text == "Medium":
            self.rect.center = (screen_width // 2, start_y + button_spacing)
        elif self.text == "Quit":
            self.rect.center = (screen_width // 2, start_y + button_spacing * 2)
        elif self.text == "Hard":
            self.rect.center = (screen_width // 2, start_y + button_spacing * 2)
        elif self.text == "Back":
            self.rect.center = (screen_width // 2, start_y + button_spacing * 3)

    def draw(self, screen):
        screen.blit(self.text_surface, self.rect)

    def isPressed(self, pos):
        return self.rect.collidepoint(pos)

start_button = Button("Start")
option_button = Button("Option")
quit_button = Button("Quit")
easy_button = Button("Easy")
medium_button = Button("Medium")
hard_button = Button("Hard")

class Game:
    def __init__(self, width, height, mines):
        self.width = width
        self.height = height
        self.mines = mines
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flagged = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.place_mines()
        self.calculate_numbers()
        
    def place_mines(self):
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        mine_positions = random.sample(positions, self.mines)
        
        for x, y in mine_positions:
            self.board[y][x] = -1
    
    def calculate_numbers(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != -1:
                    mine_count = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0:
                                continue
                            new_y, new_x = y + dy, x + dx
                            if (0 <= new_y < self.height and 
                                0 <= new_x < self.width and 
                                self.board[new_y][new_x] == -1):
                                mine_count += 1
                    self.board[y][x] = mine_count

    def print_grid(self):
        for row in self.board:
            print(' '.join(str(cell) if cell != -1 else 'M' for cell in row))

def play():
    while True:
        screen.fill("black")
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
        back_button = Button("Back")
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.isPressed(event.pos):
                    main_menu()
                elif easy_button.isPressed(event.pos):
                    start_game(*EASY_DIMS)
                elif medium_button.isPressed(event.pos):
                    start_game(*MEDIUM_DIMS)
                elif hard_button.isPressed(event.pos):
                    start_game(*HARD_DIMS)
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position()
                easy_button.update_position()
                medium_button.update_position()
                hard_button.update_position()

        pygame.display.update()
        pygame.display.flip()

def start_game(width, height, mines):
    game = Game(width, height, mines)
    game.print_grid()
    game_screen_width = width * CELL_SIZE
    game_screen_height = height * CELL_SIZE
    screen = pygame.display.set_mode((game_screen_width, game_screen_height))
    
    while True:
        screen.fill("gray")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        pygame.display.update()

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