import pygame
from constants import WHITE, DARK_GREY, GREEN, BLACK, RED, SCREEN_WIDTH

class UIRenderer:
    def __init__(self, game):
        self.game = game
        
    def draw_text(self, text, font, color, x, y, center=True):
        surf = font.render(text.upper(), True, color)
        rect = surf.get_rect()
        rect.center = (x, y) if center else rect.update(x, y, rect.w, rect.h) or (x, y)
        self.game.screen.blit(surf, rect)

    def draw_game_ui(self):
        g = self.game
        pygame.draw.rect(g.screen, DARK_GREY, (0, 0, SCREEN_WIDTH, 60))
        m, s = divmod(g.elapsed_time, 60)
        self.draw_text(f"CHEESE: {g.cheese_collected}/3", g.small_font, WHITE, 100, 30)
        self.draw_text("KING MOUSE!" if g.is_king_mouse else "COLLECT CHEESE!", g.small_font, WHITE, SCREEN_WIDTH // 2, 30)
        self.draw_text(f"TIME: {m:02d}:{s:02d}", g.small_font, WHITE, SCREEN_WIDTH - 100, 30)

    def draw_menu(self):
        g, cx = self.game, SCREEN_WIDTH // 2
        self.draw_text("MOUSE ADVENTURE", g.title_font, WHITE, cx, 120)
        self.draw_text("COLLECT 3 CHEESE ITEMS TO BECOME KING MOUSE!", g.small_font, WHITE, cx, 160)
        self.draw_text("AS KING, CATCH THE CAT TO WIN!", g.small_font, WHITE, cx, 180) 
        self.draw_text("USE WASD OR ARROW KEYS TO MOVE", g.small_font, WHITE, cx, 200)
        self.draw_text("SELECT CAT AI DIFFICULTY:", g.medium_font, WHITE, cx, 240)
        
        bw, bh, gap, sx = 140, 50, 15, cx - (140 * 3 + 15 * 2) // 2
        
        g.easy_button_rect = pygame.Rect(sx, 270, bw, bh)
        g.medium_button_rect = pygame.Rect(sx + bw + gap, 270, bw, bh)
        g.hard_button_rect = pygame.Rect(sx + (bw + gap) * 2, 270, bw, bh)
        g.start_button_rect = pygame.Rect(cx - 100, 340, 200, 60)
        
        for diff, rect in [('easy', g.easy_button_rect), ('medium', g.medium_button_rect), ('hard', g.hard_button_rect)]:
            pygame.draw.rect(g.screen, GREEN if g.cat_difficulty == diff else BLACK, rect)
            pygame.draw.rect(g.screen, WHITE, rect, 2)
            self.draw_text(diff.upper(), g.small_font, WHITE, rect.centerx, rect.centery)
        
        pygame.draw.rect(g.screen, GREEN if g.cat_difficulty else BLACK, g.start_button_rect)
        pygame.draw.rect(g.screen, WHITE, g.start_button_rect, 2)
        self.draw_text("START!", g.medium_font, WHITE, g.start_button_rect.centerx, g.start_button_rect.centery)

    def draw_end_screen(self):
        g, cx = self.game, SCREEN_WIDTH // 2
        m, s = divmod(g.elapsed_time, 60)
        self.draw_text(g.end_message, g.title_font, GREEN if g.is_win else RED, cx, 150)
        self.draw_text(g.end_details, g.small_font, WHITE, cx, 180)
        self.draw_text(f"FINAL TIME: {m:02d}:{s:02d}", g.small_font, WHITE, cx, 200)
        
        bw, bh, gap, sx = 160, 50, 15, cx - (160 * 2 + 15) // 2
        g.play_again_button_rect = pygame.Rect(sx, 250, bw, bh)
        g.back_to_menu_button_rect = pygame.Rect(sx + bw + gap, 250, bw, bh)
        
        for col, rect, txt in [(GREEN, g.play_again_button_rect, "PLAY AGAIN"), (BLACK, g.back_to_menu_button_rect, "MENU")]:
            pygame.draw.rect(g.screen, col, rect)
            pygame.draw.rect(g.screen, WHITE, rect, 2)
            self.draw_text(txt, g.small_font, WHITE, rect.centerx, rect.centery)