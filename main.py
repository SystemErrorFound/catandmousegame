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
        
        self.gameplay_width = SCREEN_WIDTH
        self.gameplay_height = SCREEN_HEIGHT - 60
        self.board_size = 10
        max_cell_width = self.gameplay_width // self.board_size
        max_cell_height = self.gameplay_height // self.board_size
        self.cell_size = min(max_cell_width, max_cell_height)
        
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.board_x_offset = (SCREEN_WIDTH - self.board_width) // 2
        self.board_y_offset = 60

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mouse Adventure")
        self.clock = pygame.time.Clock()
        
        
        self.title_font = pygame.font.Font(FONT_04B_PATH, 36)   # Titles
        self.medium_font = pygame.font.Font(FONT_04B_PATH, 20)  # Section headers / buttons
        self.small_font = pygame.font.Font(FONT_04B_PATH, 15)   # HUD / small text
        print("04B FONT LOADED SUCCESSFULLY!")


        self.cat_memory = []
        self.memory_size = 5
        self.cat_stuck_counter = 0
        self.last_cat_pos = None
        self.flee_target = None

        self.cat_move_timer = 0
        self.cat_move_delay = 500
        
        # Initialize renderers and AI
        self.ui_renderer = UIRenderer(self)
        self.game_renderer = GameRenderer(self)
        self.cat_ai = CatAI(self)
        
        self.load_assets()

        self.game_state = 'MENU'
        self.cat_difficulty = None
        self.board = []
        self.mouse_pos = {'x': 1, 'y': 1}
        self.cat_pos = {'x': 13, 'y': 13}
        self.cheese_positions = []
        self.cheese_collected = 0
        self.is_king_mouse = False
        
        self.start_time = 0
        self.elapsed_time = 0
        self.player_moved = False 
        
        self.end_message = ""
        self.end_details = ""
        self.is_win = False
        
        # Initialize button rectangles (resized for bigger fonts)
        self.easy_button_rect = pygame.Rect(0, 0, 140, 50)
        self.medium_button_rect = pygame.Rect(0, 0, 140, 50)
        self.hard_button_rect = pygame.Rect(0, 0, 140, 50)

        self.start_button_rect = pygame.Rect(0, 0, 200, 60)

        self.play_again_button_rect = pygame.Rect(0, 0, 160, 50)
        self.back_to_menu_button_rect = pygame.Rect(0, 0, 160, 50)


        
        print(f"SCREEN SIZE: {SCREEN_WIDTH} X {SCREEN_HEIGHT}")
        print(f"BOARD SIZE: {self.board_width} X {self.board_height}")
        print(f"BOARD POSITION: ({self.board_x_offset}, {self.board_y_offset})")
        print(f"BOARD BOUNDARIES: X={self.board_x_offset} TO {self.board_x_offset + self.board_width}, Y={self.board_y_offset} TO {self.board_y_offset + self.board_height}")
        
    def load_assets(self):
        try:
            def load_and_scale(filename):
                path = os.path.join("assets", filename)
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Asset file not found: {path}")
                    
                image = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(image, (self.cell_size, self.cell_size))

            print("LOADING GAME ASSETS...")
            self.mouse_img = load_and_scale("mouse.png")
            self.mouseking_img = load_and_scale("mouseking.png")
            self.cat_img = load_and_scale("cat.png")
            self.cheese_img = load_and_scale("cheese.png")
            self.wall_img = load_and_scale("wall.png")
            
            back_path = os.path.join("assets", "back.png")
            if os.path.exists(back_path):
                self.background_img = pygame.image.load(back_path).convert()
                self.background_img = pygame.transform.scale(self.background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            else:
                self.background_img = None
                print("WARNING: BACK.PNG NOT FOUND, USING DEFAULT BACKGROUND")
            
            print("ASSETS LOADED SUCCESSFULLY!")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"ERROR LOADING ASSET: {e}")
            print("\nCRITICAL ERROR: MAKE SURE YOU HAVE AN 'ASSETS' FOLDER WITH REQUIRED IMAGES.")
            print("REQUIRED: MOUSE.PNG, MOUSEKING.PNG, CAT.PNG, CHEESE.PNG, WALL.PNG; OPTIONAL: BACK.PNG, 04B.TTF")
            print(f"CURRENT WORKING DIRECTORY: {os.getcwd()}")
            sys.exit()

    def initialize_game(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        self.cat_memory, self.cat_stuck_counter, self.last_cat_pos, self.flee_target = [], 0, None, None
        
        self.cat_move_timer = pygame.time.get_ticks()
        self.cat_move_delay = {'easy': 800, 'medium': 600, 'hard': 400}[self.cat_difficulty]
        
        wall_count = {'easy': 20, 'medium': 15, 'hard': 10}[self.cat_difficulty]
        
        walls = []
        while len(walls) < wall_count:
            x, y = random.randint(1, self.board_size - 2), random.randint(1, self.board_size - 2)
            if (x, y) not in walls: walls.append((x, y))
        
        for x, y in walls: self.board[y][x] = 1
                
        while True:
            mouse_x, mouse_y = random.randint(1, 5), random.randint(1, 5)
            cat_x, cat_y = random.randint(self.board_size - 6, self.board_size - 2), random.randint(self.board_size - 6, self.board_size - 2)
            
            mouse_valid = self.board[mouse_y][mouse_x] == 0
            cat_valid = self.board[cat_y][cat_x] == 0
            distance_ok = abs(mouse_x - cat_x) + abs(mouse_y - cat_y) > 10
            
            if mouse_valid and cat_valid and distance_ok:
                break
        
        self.mouse_pos = {'x': mouse_x, 'y': mouse_y}
        self.cat_pos = {'x': cat_x, 'y': cat_y}
        
        self.cheese_positions = []
        while len(self.cheese_positions) < 3:
            cheese_x = random.randint(1, self.board_size - 2)
            cheese_y = random.randint(1, self.board_size - 2)
            pos_tuple = (cheese_x, cheese_y)
            
            is_empty_cell = self.board[cheese_y][cheese_x] == 0
            not_mouse_pos = pos_tuple != (mouse_x, mouse_y)
            not_cat_pos = pos_tuple != (cat_x, cat_y)
            not_duplicate = not any(c['x'] == cheese_x and c['y'] == cheese_y for c in self.cheese_positions)
            
            if is_empty_cell and not_mouse_pos and not_cat_pos and not_duplicate:
                self.cheese_positions.append({'x': cheese_x, 'y': cheese_y})
        
        self.cheese_collected, self.is_king_mouse, self.player_moved = 0, False, False
        self.start_time = pygame.time.get_ticks()

    def move_character(self, pos, dx, dy):
        new_x, new_y = pos['x'] + dx, pos['y'] + dy
        
        in_bounds = 0 <= new_x < self.board_size and 0 <= new_y < self.board_size
        not_wall = self.board[new_y][new_x] != 1 if in_bounds else False
        
        if not (in_bounds and not_wall):
            return False
            
        pos['x'], pos['y'] = new_x, new_y
        return True

    def check_collisions_and_state(self):
        for i, cheese in enumerate(self.cheese_positions):
            if cheese['x'] == self.mouse_pos['x'] and cheese['y'] == self.mouse_pos['y']:
                self.cheese_positions.pop(i)
                self.cheese_collected += 1
                if self.cheese_collected == 3: self.is_king_mouse = True
                break
        if self.mouse_pos['x'] == self.cat_pos['x'] and self.mouse_pos['y'] == self.cat_pos['y']:
            if self.is_king_mouse: self.end_game("THE KING MOUSE DEFEATS THE CAT! YOU WIN!", is_win=True)
            else: self.end_game("THE CAT CAUGHT THE MOUSE!", is_win=False)

    def end_game(self, details, is_win):
        self.game_state = 'GAME_OVER'
        self.end_message = "YOU WIN!" if is_win else "GAME OVER"
        self.end_details = details
        self.is_win = is_win

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if self.game_state == 'MENU' and event.type == pygame.MOUSEBUTTONDOWN:
                    for difficulty, rect in [('easy', self.easy_button_rect), ('medium', self.medium_button_rect), ('hard', self.hard_button_rect)]:
                        if rect.collidepoint(event.pos): self.cat_difficulty = difficulty
                    if self.start_button_rect.collidepoint(event.pos) and self.cat_difficulty:
                        self.initialize_game(); self.game_state = 'PLAYING'
                elif self.game_state == 'PLAYING' and event.type == pygame.KEYDOWN:
                    moves = {pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1), 
                             pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0)}
                    if event.key in moves and self.move_character(self.mouse_pos, *moves[event.key]):
                        self.player_moved = True; self.check_collisions_and_state()
                elif self.game_state == 'GAME_OVER' and event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_again_button_rect.collidepoint(event.pos): self.initialize_game(); self.game_state = 'PLAYING'
                    elif self.back_to_menu_button_rect.collidepoint(event.pos): self.game_state = 'MENU'

            if self.game_state == 'PLAYING':
                self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
                
                if self.cat_ai.should_cat_move():
                    self.cat_ai.cat_ai_move()
                
                if self.player_moved: 
                    self.player_moved = False
            
            if self.game_state == 'MENU': 
                if self.background_img:
                    self.screen.blit(self.background_img, (0, 0))
                else:
                    self.screen.fill(LIGHT_GREY)
                self.ui_renderer.draw_menu()
            elif self.game_state == 'PLAYING': 
                self.screen.fill(GAME_BACKGROUND)
                self.ui_renderer.draw_game_ui()
                self.game_renderer.draw_board()
                self.game_renderer.draw_pieces()
            elif self.game_state == 'GAME_OVER': 
                if self.background_img:
                    self.screen.blit(self.background_img, (0, 0))
                else:
                    self.screen.fill(LIGHT_GREY)
                self.ui_renderer.draw_end_screen()

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = CatMouseGamePygame()
    game.run()