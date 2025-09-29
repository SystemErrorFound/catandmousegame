import pygame
from constants import WHITE, DARK_GREY, GREEN, BLACK, RED, SCREEN_WIDTH

class UIRenderer:
    def __init__(self, game):
        self.game = game
        
    def draw_text(self, text, font, color, x, y, center=True):
        # Convert all text to uppercase for 04b font
        text_surface = font.render(text.upper(), True, color)
        text_rect = text_surface.get_rect()
        if center: text_rect.center = (x, y)
        else: text_rect.topleft = (x, y)
        self.game.screen.blit(text_surface, text_rect)

    def draw_game_ui(self):
        ui_height = 60
        pygame.draw.rect(self.game.screen, DARK_GREY, (0, 0, SCREEN_WIDTH, ui_height))
        ui_y = ui_height // 2
        
        minutes, seconds = divmod(self.game.elapsed_time, 60)
        # Center-aligned UI elements
        self.draw_text(f"CHEESE: {self.game.cheese_collected}/3", self.game.small_font, WHITE, 100, ui_y, center=True)
        self.draw_text("KING MOUSE!" if self.game.is_king_mouse else "COLLECT CHEESE!", self.game.small_font, WHITE, SCREEN_WIDTH // 2, ui_y, center=True)
        self.draw_text(f"TIME: {minutes:02d}:{seconds:02d}", self.game.small_font, WHITE, SCREEN_WIDTH - 100, ui_y, center=True)

    def draw_menu(self):
        # Center-aligned menu text
        center_x = SCREEN_WIDTH // 2
        self.draw_text("MOUSE ADVENTURE", self.game.title_font, WHITE, center_x, 120, center=True)
        self.draw_text("COLLECT 3 CHEESE ITEMS TO BECOME KING MOUSE!", self.game.small_font, WHITE, center_x, 160, center=True)
        self.draw_text("AS KING, CATCH THE CAT TO WIN!", self.game.small_font, WHITE, center_x, 180, center=True) 
        self.draw_text("USE WASD OR ARROW KEYS TO MOVE", self.game.small_font, WHITE, center_x, 200, center=True)
        self.draw_text("SELECT CAT AI DIFFICULTY:", self.game.medium_font, WHITE, center_x, 240, center=True)
        
        # Larger buttons, center-aligned
        btn_width, btn_height, btn_gap = 140, 50, 15
        center_x = SCREEN_WIDTH // 2
        total_btn_width = btn_width * 3 + btn_gap * 2
        start_x = center_x - total_btn_width // 2
        
        self.game.easy_button_rect = pygame.Rect(start_x, 270, btn_width, btn_height)
        self.game.medium_button_rect = pygame.Rect(start_x + btn_width + btn_gap, 270, btn_width, btn_height)
        self.game.hard_button_rect = pygame.Rect(start_x + (btn_width + btn_gap) * 2, 270, btn_width, btn_height)
        
        start_btn_width = 200
        start_btn_height = 60
        start_btn_y = 340
        self.game.start_button_rect = pygame.Rect(center_x - start_btn_width // 2, start_btn_y, start_btn_width, start_btn_height)
        
        for difficulty, rect in [('easy', self.game.easy_button_rect), ('medium', self.game.medium_button_rect), ('hard', self.game.hard_button_rect)]:
            pygame.draw.rect(self.game.screen, GREEN if self.game.cat_difficulty==difficulty else BLACK, rect)
            pygame.draw.rect(self.game.screen, WHITE, rect, 2)
            # Center-align button text
            self.draw_text(difficulty.upper(), self.game.small_font, WHITE, rect.centerx, rect.centery, center=True)
        
        start_color = GREEN if self.game.cat_difficulty else BLACK
        pygame.draw.rect(self.game.screen, start_color, self.game.start_button_rect)
        pygame.draw.rect(self.game.screen, WHITE, self.game.start_button_rect, 2)
        # Center-align start button text
        self.draw_text("START!", self.game.medium_font, WHITE, self.game.start_button_rect.centerx, self.game.start_button_rect.centery, center=True)

    def draw_end_screen(self):
        # Center-aligned end screen text
        center_x = SCREEN_WIDTH // 2
        minutes, seconds = divmod(self.game.elapsed_time, 60)
        self.draw_text(self.game.end_message, self.game.title_font, GREEN if self.game.is_win else RED, center_x, 150, center=True)
        self.draw_text(self.game.end_details, self.game.small_font, WHITE, center_x, 180, center=True)
        self.draw_text(f"FINAL TIME: {minutes:02d}:{seconds:02d}", self.game.small_font, WHITE, center_x, 200, center=True)
        
        # Larger end screen buttons, center-aligned
        btn_width, btn_height, btn_gap = 160, 50, 15
        center_x = SCREEN_WIDTH // 2
        total_btn_width = btn_width * 2 + btn_gap
        start_x = center_x - total_btn_width // 2
        
        self.game.play_again_button_rect = pygame.Rect(start_x, 250, btn_width, btn_height)
        self.game.back_to_menu_button_rect = pygame.Rect(start_x + btn_width + btn_gap, 250, btn_width, btn_height)
        
        for color, rect, text in [(GREEN, self.game.play_again_button_rect, "PLAY AGAIN"), (BLACK, self.game.back_to_menu_button_rect, "MENU")]:
            pygame.draw.rect(self.game.screen, color, rect)
            pygame.draw.rect(self.game.screen, WHITE, rect, 2)
            # Center-align button text
            self.draw_text(text, self.game.small_font, WHITE, rect.centerx, rect.centery, center=True)