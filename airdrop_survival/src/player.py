import pygame
from settings import PLAYER_SPEED

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width=40, height=40, color=(0, 160, 255)):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=6)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEED

    def update(self, dt, keys):
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        self.rect.x += dx * self.speed * dt

        # Keep inside screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > pygame.display.get_surface().get_width():
            self.rect.right = pygame.display.get_surface().get_width()
