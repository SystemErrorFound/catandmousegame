import pygame
from constants import WHITE, DARK_GREY, GREEN, BLACK, RED, SCREEN_WIDTH

class UIRenderer:
    def __init__(self, game):
        self.game = game
        
    def draw_text(self, text, font, color, x, y, center=True):
        text_surface = font.render(text.upper(), True, color)
        text_rect = text_surface.get_rect()
        if center: 
            text_rect.center = (x, y)
        else: 
            text_rect.topleft = (x, y)
        self.game.screen.blit(text_surface, text_rect)

    def draw_game_ui(self):
        pygame.draw.rect(self.game.screen, DARK_GREY, (0, 0, SCREEN_WIDTH, 60))
        minutes, seconds = divmod(self.game.elapsed_time, 60)
        ui_y = 30
        self.draw_text(f"CHEESE: {self.game.cheese_collected}/3", self.game.small_font, WHITE, 100, ui_y)
        self.draw_text("KING MOUSE!" if self.game.is_king_mouse else "COLLECT CHEESE!", self.game.small_font, WHITE, SCREEN_WIDTH // 2, ui_y)
        self.draw_text(f"TIME: {minutes:02d}:{seconds:02d}", self.game.small_font, WHITE, SCREEN_WIDTH - 100, ui_y)

    def draw_menu(self):
        cx = SCREEN_WIDTH // 2
        self.draw_text("MOUSE ADVENTURE", self.game.title_font, WHITE, cx, 120)
        self.draw_text("COLLECT 3 CHEESE ITEMS TO BECOME KING MOUSE!", self.game.small_font, WHITE, cx, 160)
        self.draw_text("AS KING, CATCH THE CAT TO WIN!", self.game.small_font, WHITE, cx, 180) 
        self.draw_text("USE WASD OR ARROW KEYS TO MOVE", self.game.small_font, WHITE, cx, 200)
        self.draw_text("SELECT CAT AI DIFFICULTY:", self.game.medium_font, WHITE, cx, 240)
        
        bw, bh, gap = 140, 50, 15
        cx = SCREEN_WIDTH // 2
        start_x = cx - (bw * 3 + gap * 2) // 2
        
        self.game.easy_button_rect = pygame.Rect(start_x, 270, bw, bh)
        self.game.medium_button_rect = pygame.Rect(start_x + bw + gap, 270, bw, bh)
        self.game.hard_button_rect = pygame.Rect(start_x + (bw + gap) * 2, 270, bw, bh)
        self.game.start_button_rect = pygame.Rect(cx - 100, 340, 200, 60)
        
        for difficulty, rect in [('easy', self.game.easy_button_rect), ('medium', self.game.medium_button_rect), ('hard', self.game.hard_button_rect)]:
            pygame.draw.rect(self.game.screen, GREEN if self.game.cat_difficulty == difficulty else BLACK, rect)
            pygame.draw.rect(self.game.screen, WHITE, rect, 2)
            self.draw_text(difficulty.upper(), self.game.small_font, WHITE, rect.centerx, rect.centery)
        pygame.draw.rect(self.game.screen, GREEN if self.game.cat_difficulty else BLACK, self.game.start_button_rect)
        pygame.draw.rect(self.game.screen, WHITE, self.game.start_button_rect, 2)
        self.draw_text("START!", self.game.medium_font, WHITE, self.game.start_button_rect.centerx, self.game.start_button_rect.centery)

    def draw_end_screen(self):
        cx = SCREEN_WIDTH // 2
        minutes, seconds = divmod(self.game.elapsed_time, 60)
        self.draw_text(self.game.end_message, self.game.title_font, GREEN if self.game.is_win else RED, cx, 150)
        self.draw_text(self.game.end_details, self.game.small_font, WHITE, cx, 180)
        self.draw_text(f"FINAL TIME: {minutes:02d}:{seconds:02d}", self.game.small_font, WHITE, cx, 200)
        
        bw, bh, gap = 160, 50, 15
        start_x = cx - (bw * 2 + gap) // 2
        self.game.play_again_button_rect = pygame.Rect(start_x, 250, bw, bh)
        self.game.back_to_menu_button_rect = pygame.Rect(start_x + bw + gap, 250, bw, bh)
        
        for color, rect, text in [(GREEN, self.game.play_again_button_rect, "PLAY AGAIN"), (BLACK, self.game.back_to_menu_button_rect, "MENU")]:
            pygame.draw.rect(self.game.screen, color, rect)
            pygame.draw.rect(self.game.screen, WHITE, rect, 2)
            self.draw_text(text, self.game.small_font, WHITE, rect.centerx, rect.centery)