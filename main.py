import pygame
import sys
import random
import os
from constants import *
from ui_renderer import UIRenderer
from game_renderer import GameRenderer
from cat_ai import CatAI

class CatMouseGamePygame:
    def __init__(self):
        pygame.init()
        
        self.board_size = 10
        self.cell_size = min(SCREEN_WIDTH // self.board_size, (SCREEN_HEIGHT - 60) // self.board_size)
        self.board_x_offset = (SCREEN_WIDTH - self.board_size * self.cell_size) // 2
        self.board_y_offset = 60

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mouse Adventure")
        self.clock = pygame.time.Clock()
        
        self.title_font = pygame.font.Font(FONT_04B_PATH, 36)
        self.medium_font = pygame.font.Font(FONT_04B_PATH, 20)
        self.small_font = pygame.font.Font(FONT_04B_PATH, 15)
        
        self.ui_renderer = UIRenderer(self)
        self.game_renderer = GameRenderer(self)
        self.cat_ai = CatAI(self)
        
        self.load_assets()
        
        self.game_state = 'MENU'
        self.cat_difficulty = None
        self.board = []
        self.cheese_positions = []
        self.mouse_pos = {'x': 1, 'y': 1}
        self.cat_pos = {'x': 13, 'y': 13}
        self.cheese_collected = 0
        self.is_king_mouse = False
        self.start_time = 0
        self.elapsed_time = 0
        self.player_moved = False
        self.end_message = ""
        self.end_details = ""
        self.is_win = False
        
        self.easy_button_rect = pygame.Rect(0, 0, 140, 50)
        self.medium_button_rect = pygame.Rect(0, 0, 140, 50)
        self.hard_button_rect = pygame.Rect(0, 0, 140, 50)
        self.start_button_rect = pygame.Rect(0, 0, 200, 60)
        self.play_again_button_rect = pygame.Rect(0, 0, 160, 50)
        self.back_to_menu_button_rect = pygame.Rect(0, 0, 160, 50)
        
    def load_assets(self):
        def load_and_scale(filename):
            image = pygame.image.load(os.path.join("assets", filename)).convert_alpha()
            return pygame.transform.smoothscale(image, (self.cell_size, self.cell_size))

        self.mouse_img = load_and_scale("mouse.png")
        self.mouseking_img = load_and_scale("mouseking.png")
        self.cat_img = load_and_scale("cat.png")
        self.cheese_img = load_and_scale("cheese.png")
        self.wall_img = load_and_scale("wall.png")
        
        background_path = os.path.join("assets", "back.png")
        if os.path.exists(background_path):
            background = pygame.image.load(background_path).convert()
            self.background_img = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.background_img = None

    def initialize_game(self):
        self.board = [[0] * self.board_size for _ in range(self.board_size)]
        
        wall_count = 15
        walls = set()
        while len(walls) < wall_count:
            x = random.randint(1, self.board_size - 2)
            y = random.randint(1, self.board_size - 2)
            walls.add((x, y))
        
        for x, y in walls:
            self.board[y][x] = 1
        
        while True:
            mouse_x = random.randint(1, 5)
            mouse_y = random.randint(1, 5)
            cat_x = random.randint(self.board_size - 6, self.board_size - 2)
            cat_y = random.randint(self.board_size - 6, self.board_size - 2)
            
            mouse_cell_empty = self.board[mouse_y][mouse_x] == 0
            cat_cell_empty = self.board[cat_y][cat_x] == 0
            distance = abs(mouse_x - cat_x) + abs(mouse_y - cat_y)
            
            if mouse_cell_empty and cat_cell_empty and distance > 10:
                break
        
        self.mouse_pos = {'x': mouse_x, 'y': mouse_y}
        self.cat_pos = {'x': cat_x, 'y': cat_y}
        
        self.cheese_positions = []
        while len(self.cheese_positions) < 3:
            cheese_x = random.randint(1, self.board_size - 2)
            cheese_y = random.randint(1, self.board_size - 2)
            
            cell_empty = self.board[cheese_y][cheese_x] == 0
            not_on_mouse = (cheese_x, cheese_y) != (mouse_x, mouse_y)
            not_on_cat = (cheese_x, cheese_y) != (cat_x, cat_y)
            not_duplicate = not any(c['x'] == cheese_x and c['y'] == cheese_y for c in self.cheese_positions)
            
            if cell_empty and not_on_mouse and not_on_cat and not_duplicate:
                self.cheese_positions.append({'x': cheese_x, 'y': cheese_y})
        
        self.cheese_collected = 0
        self.is_king_mouse = False
        self.player_moved = False
        self.start_time = pygame.time.get_ticks()

    def move_character(self, position, delta_x, delta_y):
        new_x = position['x'] + delta_x
        new_y = position['y'] + delta_y
        
        in_bounds = 0 <= new_x < self.board_size and 0 <= new_y < self.board_size
        
        if not in_bounds:
            return False
        
        not_wall = self.board[new_y][new_x] != 1
        
        if not_wall:
            position['x'] = new_x
            position['y'] = new_y
            return True
        return False

    def check_collisions_and_state(self):
        for i, cheese in enumerate(self.cheese_positions):
            if cheese['x'] == self.mouse_pos['x'] and cheese['y'] == self.mouse_pos['y']:
                self.cheese_positions.pop(i)
                self.cheese_collected += 1
                if self.cheese_collected == 3: 
                    self.is_king_mouse = True
                break
        if self.mouse_pos['x'] == self.cat_pos['x'] and self.mouse_pos['y'] == self.cat_pos['y']:
            self.end_game("THE KING MOUSE DEFEATS THE CAT! YOU WIN!" if self.is_king_mouse else "THE CAT CAUGHT THE MOUSE!", self.is_king_mouse)

    def end_game(self, details, is_win):
        self.game_state = 'GAME_OVER'
        self.end_message = "YOU WIN!" if is_win else "GAME OVER"
        self.end_details = details
        self.is_win = is_win

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit(); sys.exit()
                
                if self.game_state == 'MENU' and event.type == pygame.MOUSEBUTTONDOWN:
                    for diff, rect in [('easy', self.easy_button_rect), ('medium', self.medium_button_rect), ('hard', self.hard_button_rect)]:
                        if rect.collidepoint(event.pos): 
                            self.cat_difficulty = diff
                    if self.start_button_rect.collidepoint(event.pos) and self.cat_difficulty:
                        self.initialize_game()
                        self.game_state = 'PLAYING'
                
                elif self.game_state == 'PLAYING' and event.type == pygame.KEYDOWN:
                    moves = {pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1), 
                             pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0)}
                    if event.key in moves and self.move_character(self.mouse_pos, *moves[event.key]):
                        self.player_moved = True
                        self.check_collisions_and_state()
                
                elif self.game_state == 'GAME_OVER' and event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_again_button_rect.collidepoint(event.pos): 
                        self.initialize_game(); self.game_state = 'PLAYING'
                    elif self.back_to_menu_button_rect.collidepoint(event.pos): 
                        self.game_state = 'MENU'

            if self.game_state == 'PLAYING':
                self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
                if self.cat_ai.should_cat_move():
                    self.cat_ai.cat_ai_move()
                if self.player_moved: 
                    self.player_moved = False
            
            if self.game_state == 'PLAYING': 
                self.screen.fill(GAME_BACKGROUND)
                self.ui_renderer.draw_game_ui()
                self.game_renderer.draw_board()
                self.game_renderer.draw_pieces()
            else:
                self.screen.blit(self.background_img, (0, 0)) if self.background_img else self.screen.fill(LIGHT_GREY)
                self.ui_renderer.draw_menu() if self.game_state == 'MENU' else self.ui_renderer.draw_end_screen()

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = CatMouseGamePygame()
    game.run()