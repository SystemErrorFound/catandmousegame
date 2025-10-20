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

        self.cat_memory, self.memory_size, self.cat_stuck_counter, self.last_cat_pos, self.flee_target, self.cat_move_timer = [], 5, 0, None, None, 0
        
        self.ui_renderer = UIRenderer(self)
        self.game_renderer = GameRenderer(self)
        self.cat_ai = CatAI(self)
        
        self.load_assets()
        self.game_state, self.cat_difficulty = 'MENU', None
        self.board, self.cheese_positions = [], []
        self.mouse_pos = {'x': 1, 'y': 1}
        self.cat_pos = {'x': 13, 'y': 13}
        self.cheese_collected, self.is_king_mouse, self.start_time, self.elapsed_time, self.player_moved = 0, False, 0, 0, False
        self.end_message, self.end_details, self.is_win = "", "", False
        
        self.easy_button_rect = self.medium_button_rect = self.hard_button_rect = pygame.Rect(0, 0, 140, 50)
        self.start_button_rect = pygame.Rect(0, 0, 200, 60)
        self.play_again_button_rect = self.back_to_menu_button_rect = pygame.Rect(0, 0, 160, 50)
        
    def load_assets(self):
        load_scale = lambda f: pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", f)).convert_alpha(), (self.cell_size, self.cell_size))

        self.mouse_img, self.mouseking_img, self.cat_img, self.cheese_img, self.wall_img = (
            load_scale("mouse.png"), load_scale("mouseking.png"), load_scale("cat.png"), 
            load_scale("cheese.png"), load_scale("wall.png"))
        
        back_path = os.path.join("assets", "back.png")
        self.background_img = pygame.transform.scale(pygame.image.load(back_path).convert(), 
                              (SCREEN_WIDTH, SCREEN_HEIGHT)) if os.path.exists(back_path) else None

    def initialize_game(self):
        self.board = [[0] * self.board_size for _ in range(self.board_size)]
        self.cat_memory, self.cat_stuck_counter, self.last_cat_pos, self.flee_target = [], 0, None, None
        
        self.cat_move_timer, self.cat_move_delay = pygame.time.get_ticks(), {'easy': 450, 'medium': 350, 'hard': 250}[self.cat_difficulty]
        
        wall_count = {'easy': 20, 'medium': 15, 'hard': 10}[self.cat_difficulty]
        walls = set()
        while len(walls) < wall_count:
            walls.add((random.randint(1, self.board_size - 2), random.randint(1, self.board_size - 2)))
        for x, y in walls: 
            self.board[y][x] = 1
                
        while True:
            mx, my = random.randint(1, 5), random.randint(1, 5)
            cx, cy = random.randint(self.board_size - 6, self.board_size - 2), random.randint(self.board_size - 6, self.board_size - 2)
            if self.board[my][mx] == 0 and self.board[cy][cx] == 0 and abs(mx - cx) + abs(my - cy) > 10:
                break
        self.mouse_pos, self.cat_pos = {'x': mx, 'y': my}, {'x': cx, 'y': cy}
        
        self.cheese_positions = []
        while len(self.cheese_positions) < 3:
            cx, cy = random.randint(1, self.board_size - 2), random.randint(1, self.board_size - 2)
            if (self.board[cy][cx] == 0 and (cx, cy) != (mx, my) and (cx, cy) != (self.cat_pos['x'], self.cat_pos['y']) 
                and not any(c['x'] == cx and c['y'] == cy for c in self.cheese_positions)):
                self.cheese_positions.append({'x': cx, 'y': cy})
        self.cheese_collected, self.is_king_mouse, self.player_moved, self.start_time = 0, False, False, pygame.time.get_ticks()

    def move_character(self, pos, dx, dy):
        nx, ny = pos['x'] + dx, pos['y'] + dy
        if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[ny][nx] != 1:
            pos['x'], pos['y'] = nx, ny
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