import pygame
import sys
import random
import json
import time 
from pygame import KEYDOWN

pygame.init()

background_image = pygame.image.load("assets/background2.png")

flag_image = pygame.image.load("assets/flag.png")
bomb_image = pygame.image.load("assets/bomb.png")

width=1000
height=600
screen = pygame.display.set_mode((width,height), pygame.RESIZABLE)
pygame.display.set_caption("Minesweeper")
pygame.display.set_icon(bomb_image)

font = pygame.font.SysFont("arialblack", 40)

screen_width = screen.get_width()
screen_height = screen.get_height()

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
        button_spacing = 80
        total_height = button_spacing * 4
        start_y = (screen.get_height() - total_height) // 2

        if self.text == "Start":
            self.rect.center = (screen.get_width() // 2, start_y)
        elif self.text == "Easy":
            self.rect.center = (screen.get_width() // 2, start_y)
        elif self.text == "Option":
            self.rect.center = (screen.get_width() // 2, start_y + button_spacing)
        elif self.text == "Medium":
            self.rect.center = (screen.get_width() // 2, start_y + button_spacing)
        elif self.text == "Score":
            self.rect.center = (screen.get_width() // 2, start_y + button_spacing * 2)
        elif self.text == "Hard":
            self.rect.center = (screen.get_width() // 2, start_y + button_spacing * 2)
        elif self.text == "Quit":
            self.rect.center = (screen.get_width() // 2, start_y + button_spacing * 3)
        elif self.text == "Back":
            self.rect.center = (screen.get_width() // 2, start_y + button_spacing * 3)

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
score_button = Button("Score")
back_button = Button("Back")

explosion_sound = pygame.mixer.Sound("assets/explosion.mp3")

class Game:
    def __init__(self, width, height, mines, first_click=None):
        self.width = width
        self.height = height
        self.mines = mines
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flagged = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.flags_left = mines
        self.victory = False
        self.score = 0
        self.start_time = time.time()
        self.end_time = None  
        self.mines_placed = False
        self.first_click = first_click  
        
        self.COLORS = {
            1: (0, 0, 255),
            2: (0, 255, 0),
            3: (255, 0, 0),
            4: (0, 0, 128),
            5: (128, 0, 0),
            6: (0, 128, 128),
            7: (0, 0, 0),
            8: (128, 128, 128)
        }

    def place_mines(self, first_click_x=None, first_click_y=None):
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        if first_click_x is not None and first_click_y is not None:
            safe_zone = [(first_click_x + dx, first_click_y + dy) 
                         for dx in range(-1, 2) for dy in range(-1, 2)
                         if 0 <= first_click_x + dx < self.width and 0 <= first_click_y + dy < self.height]
            for pos in safe_zone:
                if pos in positions:
                    positions.remove(pos)
        mine_positions = random.sample(positions, self.mines)
        
        for x, y in mine_positions:
            self.board[y][x] = -1
        self.mines_placed = True
    
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

    def draw_grid(self, screen):
        cell_font = pygame.font.SysFont("arialblack", 20)
        
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if not self.revealed[y][x]:
                    pygame.draw.rect(screen, (192, 192, 192), rect)
                    pygame.draw.rect(screen, (128, 128, 128), rect, 1)
                    
                    if self.flagged[y][x]:
                        flag_rect = flag_image.get_rect(center=rect.center)
                        screen.blit(flag_image, flag_rect)
                else:
                    pygame.draw.rect(screen, (220, 220, 220), rect)
                    pygame.draw.rect(screen, (128, 128, 128), rect, 1)
                    
                    if self.board[y][x] > 0:
                        number = str(self.board[y][x])
                        color = self.COLORS.get(self.board[y][x], (0, 0, 0))
                        text = cell_font.render(number, True, color)
                        text_rect = text.get_rect(center=rect.center)
                        screen.blit(text, text_rect)
                    elif self.board[y][x] == -1:
                        bomb_rect = bomb_image.get_rect(center=rect.center)
                        screen.blit(bomb_image, bomb_rect)

    def toggle_flag(self, x, y):
        if not self.revealed[y][x]:
            if not self.flagged[y][x] and self.flags_left > 0:
                self.flagged[y][x] = True
                self.flags_left -= 1
            elif self.flagged[y][x]:
                self.flagged[y][x] = False
                self.flags_left += 1

    def check_victory(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != -1 and not self.revealed[y][x]:
                    return False
        return True

    def calculate_score(self):
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        self.score = int(elapsed_time)

    def reveal_cell(self, x, y):
        if not self.mines_placed:  
            self.place_mines(x, y)
            self.calculate_numbers()
            self.first_click = (x, y) 
        if self.flagged[y][x]:
            return
        if self.revealed[y][x] or self.flagged[y][x]:
            return
        self.revealed[y][x] = True
        if self.board[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    new_y, new_x = y + dy, x + dx
                    if (0 <= new_y < self.height and 0 <= new_x < self.width):
                        self.reveal_cell(new_x, new_y)
        elif self.board[y][x] == -1:
            self.game_over = True
            self.end_time = time.time()
            explosion_sound.play()  
        if self.check_victory():
            self.game_over = True
            self.victory = True
            self.calculate_score() 

    def get_elapsed_time(self):
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

class Score:
    def __init__(self, name, score, mode, board):
        self.name = name
        self.score = score
        self.mode = mode
        self.board = board

def save_game(name, score, mode, board, first_click):
    game_data = {
        "name": name,
        "score": score,
        "mode": mode,
        "board": board,
        "first_click": first_click  
    }
    with open("game_results.json", "a") as file:
        json.dump(game_data, file)
        file.write("\n")

def get_player_name():
    name = ""
    input_active = True
    font = pygame.font.SysFont("arialblack", 20)
    while input_active:
        screen.fill((0, 0, 0))
        prompt_text = font.render("Enter your name: " + name, True, (255, 255, 255))
        screen.blit(prompt_text, (50, screen.get_height() // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
    return name

def get_sorted_scores():
    with open("game_results.json", "r") as file:
        game_results = [json.loads(line) for line in file]
    
    sorted_results = sorted(game_results, key=lambda x: x['score'])
    return sorted_results

def draw_background():
    bg_width, bg_height = background_image.get_size()
    screen_width, screen_height = screen.get_size()
    
    scale = max(screen_width / bg_width, screen_height / bg_height)
    new_width = int(bg_width * scale)
    new_height = int(bg_height * scale)
    
    scaled_background = pygame.transform.scale(background_image, (new_width, new_height))
    screen.blit(scaled_background, (0, 0))

def play():
    while True:
        draw_background()
        easy_button.update_position()
        medium_button.update_position()
        hard_button.update_position()
        back_button.update_position()

        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    main_menu()

        pygame.display.update()
        pygame.display.flip()

def start_game(width, height, mines):
    game = Game(width, height, mines)
    game_screen_width = width * CELL_SIZE
    game_screen_height = height * CELL_SIZE + 40
    
    while True:
        draw_background()
        
        flag_font = pygame.font.SysFont("arialblack", 20)
        flag_text = flag_font.render(f"Flags: {game.flags_left}", True, (0, 0, 0))
        screen.blit(flag_text, (10, 10))
        
        elapsed_time = game.get_elapsed_time()
        time_text = flag_font.render(f"Time: {int(elapsed_time)}s", True, (0, 0, 0))
        screen.blit(time_text, (game_screen_width - 150, 10)) 
        
        game_surface = pygame.Surface((game_screen_width, height * CELL_SIZE))
        game_surface.fill((192, 192, 192))
        game.draw_grid(game_surface)
        
        grid_x = (screen.get_width() - game_screen_width) // 2
        grid_y = (screen.get_height() - game_screen_height) // 2 + 40
        screen.blit(game_surface, (grid_x, grid_y))

        if game.game_over:
            message_width = 200
            message_height = 100
            rect = pygame.Rect(
                (screen.get_width() - message_width) // 2,
                (screen.get_height() - message_height) // 2,
                message_width,
                message_height
            )
            pygame.draw.rect(screen, (255, 0, 0) if not game.victory else (0, 255, 0), rect)
            
            game_over_font = pygame.font.SysFont("arialblack", 20)
            text = game_over_font.render("GAME OVER!" if not game.victory else "YOU WIN!", True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
            
            if game.victory:
                player_name = get_player_name()
                save_game(player_name, game.score, f"{width}x{height}", game.board, game.first_click)
                return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                x, y = event.pos
                y -= grid_y
                x -= grid_x
                if y >= 0 and x >= 0:
                    grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                    if 0 <= grid_x < width and 0 <= grid_y < height:
                        if event.button == 1:
                            game.reveal_cell(grid_x, grid_y)
                        elif event.button == 3:
                            game.toggle_flag(grid_x, grid_y)

        pygame.display.update()

def quit():
    pygame.quit()
    sys.exit()

def option():
    while True:
        draw_background()
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.isPressed(event.pos):
                    main_menu()
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position()
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    main_menu()

        pygame.display.update()
        pygame.display.flip()

def play_existing_game(board, first_click):
    height = len(board)
    width = len(board[0])
    mines = sum(row.count(-1) for row in board)
    game = Game(width, height, mines, first_click)
    game.board = board
    game.mines_placed = True 
    game.calculate_numbers()
    if first_click:
        game.reveal_cell(*first_click)  
    game_screen_width = width * CELL_SIZE
    game_screen_height = height * CELL_SIZE + 40
    
    while True:
        draw_background()
        
        flag_font = pygame.font.SysFont("arialblack", 20)
        flag_text = flag_font.render(f"Flags: {game.flags_left}", True, (0, 0, 0))
        screen.blit(flag_text, (10, 10))
        
        elapsed_time = game.get_elapsed_time()
        time_text = flag_font.render(f"Time: {int(elapsed_time)}s", True, (0, 0, 0))
        screen.blit(time_text, (game_screen_width - 150, 10)) 
        
        game_surface = pygame.Surface((game_screen_width, height * CELL_SIZE))
        game_surface.fill((192, 192, 192))
        game.draw_grid(game_surface)
        
        grid_x = (screen.get_width() - game_screen_width) // 2
        grid_y = (screen.get_height() - game_screen_height) // 2 + 40
        screen.blit(game_surface, (grid_x, grid_y))

        if game.game_over:
            message_width = 200
            message_height = 100
            rect = pygame.Rect(
                (screen.get_width() - message_width) // 2,
                (screen.get_height() - message_height) // 2,
                message_width,
                message_height
            )
            pygame.draw.rect(screen, (255, 0, 0) if not game.victory else (0, 255, 0), rect)
            
            game_over_font = pygame.font.SysFont("arialblack", 20)
            text = game_over_font.render("GAME OVER!" if not game.victory else "YOU WIN!", True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
            
            if game.victory:
                player_name = get_player_name()
                save_game(player_name, game.score, f"{width}x{height}", game.board, game.first_click)
                return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                x, y = event.pos
                y -= grid_y
                x -= grid_x
                if y >= 0 and x >= 0:
                    grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                    if 0 <= grid_x < width and 0 <= grid_y < height:
                        if event.button == 1:
                            game.reveal_cell(grid_x, grid_y)
                        elif event.button == 3:
                            game.toggle_flag(grid_x, grid_y)

        pygame.display.update()

def score_menu():
    sorted_scores = get_sorted_scores()
    font = pygame.font.SysFont("arialblack", 20)
    scroll_y = 0
    scroll_speed = 20
    
    while True:
        draw_background()
        back_button.draw(screen)
        
        score_buttons = []  
        
        y_offset = 50 + scroll_y
        for result in sorted_scores:
            score_text = f"{result['name']} = {result['score']} in {result['mode']}"
            text_surface = font.render(score_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(screen.get_width() / 2, y_offset))
            screen.blit(text_surface, text_rect)
            score_buttons.append((text_rect, result))
            y_offset += 30

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                if back_button.isPressed(event.pos):
                    main_menu()
                for rect, result in score_buttons:
                    if rect.collidepoint(event.pos):
                        play_existing_game(result['board'], result.get('first_click'))  
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position()
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                elif event.key == pygame.K_DOWN:
                    scroll_y -= scroll_speed
                elif event.key == pygame.K_UP:
                    scroll_y += scroll_speed
            if event.type == pygame.MOUSEWHEEL:
                scroll_y += event.y * scroll_speed

        pygame.display.update()
        pygame.display.flip()

def main_menu():
    while True:
        draw_background()

        start_button.update_position()
        option_button.update_position()
        score_button.update_position()
        quit_button.update_position()

        start_button.draw(screen)
        option_button.draw(screen)
        score_button.draw(screen)
        quit_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.isPressed(event.pos):
                    play()
                if quit_button.isPressed(event.pos):
                    quit()
                if option_button.isPressed(event.pos):
                    option()
                if score_button.isPressed(event.pos):
                    score_menu()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                start_button.update_position()
                option_button.update_position()
                quit_button.update_position()
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        pygame.display.flip()

main_menu()