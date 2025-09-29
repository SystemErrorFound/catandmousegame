import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_COLOR_LIGHT, FLOOR_COLOR_DARK

class GameRenderer:
    def __init__(self, game):
        self.game = game
        
    def draw_board(self):
        for y in range(self.game.board_size):
            for x in range(self.game.board_size):
                cell_x = self.game.board_x_offset + x * self.game.cell_size
                cell_y = self.game.board_y_offset + y * self.game.cell_size
                
                rect = pygame.Rect(cell_x, cell_y, self.game.cell_size, self.game.cell_size)
                color = FLOOR_COLOR_LIGHT if (x + y) % 2 == 0 else FLOOR_COLOR_DARK
                pygame.draw.rect(self.game.screen, color, rect)
                
                if self.game.board[y][x] == 1:
                    self.game.screen.blit(self.game.wall_img, rect.topleft)

    def draw_pieces(self):
        for cheese in self.game.cheese_positions:
            x = self.game.board_x_offset + cheese['x'] * self.game.cell_size
            y = self.game.board_y_offset + cheese['y'] * self.game.cell_size
            self.game.screen.blit(self.game.cheese_img, (x, y))
        
        for pos, img in [(self.game.cat_pos, self.game.cat_img), 
                        (self.game.mouse_pos, self.game.mouseking_img if self.game.is_king_mouse else self.game.mouse_img)]:
            x = self.game.board_x_offset + pos['x'] * self.game.cell_size
            y = self.game.board_y_offset + pos['y'] * self.game.cell_size
            self.game.screen.blit(img, (x, y))