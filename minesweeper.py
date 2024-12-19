import pygame
import sys
import random
import json
import time 
from pygame import KEYDOWN

pygame.init()

background_image = pygame.image.load("assets/background2.png")
background_image_easter_egg = pygame.image.load("assets/background3.png") 

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
    def __init__(self, text, image=None):
        self.text = text
        self.image = image
        if image:
            self.image = pygame.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))
        self.text_surface = font.render(text, True, color) if not image else None
        self.rect = self.text_surface.get_rect() if not image else self.image.get_rect()
        self.update_position(["Start", "Easy", "Option", "Medium", "Score", "Hard", "Quit", "Back"])
    
    def update_position(self, buttons):
        button_spacing = screen.get_height() // 6  
        total_height = button_spacing * len(buttons)
        start_y = (screen.get_height() - total_height) // 2 + button_spacing // 2

        button_index = buttons.index(self.text)
        self.rect.center = (screen.get_width() // 2, start_y + button_index * button_spacing)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
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

# Load images for easter egg mode
start_image = pygame.image.load("assets/start.png")
option_image = pygame.image.load("assets/option.png")
quit_image = pygame.image.load("assets/quit.png")
easy_image = pygame.image.load("assets/easy.png")
medium_image = pygame.image.load("assets/medium.png")
hard_image = pygame.image.load("assets/hard.png")
score_image = pygame.image.load("assets/score.png")
back_image = pygame.image.load("assets/back.png")

def update_buttons_for_easter_egg(easter_egg_active):
    global start_button, option_button, quit_button, easy_button, medium_button, hard_button, score_button, back_button
    if easter_egg_active:
        start_button = Button("Start", start_image)
        option_button = Button("Option", option_image)
        quit_button = Button("Quit", quit_image)
        easy_button = Button("Easy", easy_image)
        medium_button = Button("Medium", medium_image)
        hard_button = Button("Hard", hard_image)
        score_button = Button("Score", score_image)
        back_button = Button("Back", back_image)
    else:
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
        self.print_grid()

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
    try:
        with open("game_results.json", "r") as file:
            game_results = [json.loads(line) for line in file]
    except FileNotFoundError:
        return []
    sorted_results = sorted(game_results, key=lambda x: x['score'])
    return sorted_results

def draw_background(easter_egg=False):
    bg_image = background_image_easter_egg if easter_egg else background_image
    bg_width, bg_height = bg_image.get_size()
    screen_width, screen_height = screen.get_size()
    
    scale = max(screen_width / bg_width, screen_height / bg_height)
    new_width = int(bg_width * scale)
    new_height = int(bg_height * scale)
    
    scaled_background = pygame.transform.scale(bg_image, (new_width, new_height))
    screen.blit(scaled_background, (0, 0))

def play(easter_egg_active):
    update_buttons_for_easter_egg(easter_egg_active)
    buttons = ["Easy", "Medium", "Hard", "Back"]
    while True:
        draw_background(easter_egg_active)
        easy_button.update_position(buttons)
        medium_button.update_position(buttons)
        hard_button.update_position(buttons)
        back_button.update_position(buttons)

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
                    main_menu(easter_egg_active)
                elif easy_button.isPressed(event.pos):
                    start_game(*EASY_DIMS, easter_egg_active)
                elif medium_button.isPressed(event.pos):
                    start_game(*MEDIUM_DIMS, easter_egg_active)
                elif hard_button.isPressed(event.pos):
                    start_game(*HARD_DIMS, easter_egg_active)
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position(buttons)
                easy_button.update_position(buttons)
                medium_button.update_position(buttons)
                hard_button.update_position(buttons)
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    main_menu(easter_egg_active)
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    easter_egg_active = not easter_egg_active

        pygame.display.update()
        pygame.display.flip()

def start_game(width, height, mines, easter_egg_active):
    update_buttons_for_easter_egg(easter_egg_active)
    game = Game(width, height, mines)
    game_screen_width = width * CELL_SIZE
    game_screen_height = height * CELL_SIZE + 40
    
    while True:
        draw_background(easter_egg_active)
        
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
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    easter_egg_active = not easter_egg_active
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

def option(easter_egg_active):
    update_buttons_for_easter_egg(easter_egg_active)
    while True:
        draw_background(easter_egg_active)
        back_button.update_position(["Back"])
        back_button.rect.bottom = screen.get_height() - 10  
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.isPressed(event.pos):
                    main_menu(easter_egg_active)
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position(["Back"])
                back_button.rect.bottom = screen.get_height() - 10  # Move back button to the bottom
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    main_menu(easter_egg_active)
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    easter_egg_active = not easter_egg_active

        pygame.display.update()
        pygame.display.flip()

def play_existing_game(board, first_click, easter_egg_active):
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
        draw_background(easter_egg_active)
        
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    easter_egg_active = not easter_egg_active
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

def score_menu(easter_egg_active):
    update_buttons_for_easter_egg(easter_egg_active)
    sorted_scores = get_sorted_scores()
    font = pygame.font.SysFont("arialblack", 20)
    scroll_y = 0
    scroll_speed = 20
    
    while True:
        draw_background(easter_egg_active)
        back_button.update_position(["Back"])
        back_button.rect.bottom = screen.get_height() - 10 
        back_button.draw(screen)
        
        score_buttons = []  
        
        y_offset = 50 + scroll_y
        if not sorted_scores:
            no_scores_text = font.render("No scores available", True, (0, 0, 0))
            no_scores_rect = no_scores_text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
            screen.blit(no_scores_text, no_scores_rect)
        else:
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
                    main_menu(easter_egg_active)
                for rect, result in score_buttons:
                    if rect.collidepoint(event.pos):
                        play_existing_game(result['board'], result.get('first_click'), easter_egg_active)  
            if event.type == pygame.VIDEORESIZE:
                back_button.update_position(["Back"])
                back_button.rect.bottom = screen.get_height() - 10  # Move back button to the bottom
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    main_menu(easter_egg_active)
                elif event.key == pygame.K_DOWN:
                    scroll_y -= scroll_speed
                elif event.key == pygame.K_UP:
                    scroll_y += scroll_speed
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    easter_egg_active = not easter_egg_active
            if event.type == pygame.MOUSEWHEEL:
                scroll_y += event.y * scroll_speed

        pygame.display.update()
        pygame.display.flip()

def main_menu(easter_egg_active=False):
    update_buttons_for_easter_egg(easter_egg_active)
    buttons = ["Start", "Option", "Score", "Quit"]
    while True:
        draw_background(easter_egg_active)

        start_button.update_position(buttons)
        option_button.update_position(buttons)
        score_button.update_position(buttons)
        quit_button.update_position(buttons)

        start_button.draw(screen)
        option_button.draw(screen)
        score_button.draw(screen)
        quit_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.isPressed(event.pos):
                    play(easter_egg_active)
                if quit_button.isPressed(event.pos):
                    quit()
                if option_button.isPressed(event.pos):
                    option(easter_egg_active)
                if score_button.isPressed(event.pos):
                    score_menu(easter_egg_active)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                start_button.update_position(buttons)
                option_button.update_position(buttons)
                quit_button.update_position(buttons)
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:  
                    easter_egg_active = not easter_egg_active

        pygame.display.update()
        pygame.display.flip()

main_menu()