import pygame
from settings import WHITE, BLACK

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)

    def draw_text(self, text, x, y, color=WHITE):
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def render(self, score, lives):
        self.draw_text(f"Score: {score}", 8, 8)
        self.draw_text(f"Lives: {lives}", 8, 32)
