import pygame
from constants import FLOOR_COLOR_LIGHT, FLOOR_COLOR_DARK

class GameRenderer:
    def __init__(self, game):
        self.game = game
        
    def draw_board(self):
        g = self.game
        for y in range(g.board_size):
            for x in range(g.board_size):
                cell_x = g.board_x_offset + x * g.cell_size
                cell_y = g.board_y_offset + y * g.cell_size
                rect = pygame.Rect(cell_x, cell_y, g.cell_size, g.cell_size)
                
                pygame.draw.rect(g.screen, FLOOR_COLOR_LIGHT if (x + y) % 2 == 0 else FLOOR_COLOR_DARK, rect)
                if g.board[y][x] == 1:
                    g.screen.blit(g.wall_img, rect.topleft)

    def draw_pieces(self):
        g = self.game
        for cheese in g.cheese_positions:
            g.screen.blit(g.cheese_img, (g.board_x_offset + cheese['x'] * g.cell_size, g.board_y_offset + cheese['y'] * g.cell_size))
        
        g.screen.blit(g.cat_img, (g.board_x_offset + g.cat_pos['x'] * g.cell_size, g.board_y_offset + g.cat_pos['y'] * g.cell_size))
        g.screen.blit(g.mouseking_img if g.is_king_mouse else g.mouse_img, (g.board_x_offset + g.mouse_pos['x'] * g.cell_size, g.board_y_offset + g.mouse_pos['y'] * g.cell_size))