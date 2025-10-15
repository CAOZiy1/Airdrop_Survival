import pygame
import random
from settings import DROP_SPEED

class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y, size=20, color=(200, 80, 50)):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, color, self.image.get_rect())
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = DROP_SPEED

    def update(self, dt):
        self.rect.y += self.speed * dt
        # If it's off the bottom, kill it so sprite group removes it
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

    @staticmethod
    def random_spawn(surface_width):
        x = random.randint(20, surface_width - 20)
        return Drop(x, -10)
