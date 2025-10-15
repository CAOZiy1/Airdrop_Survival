# src/drop.py

import pygame
import random
from settings import WIDTH, DROP_SIZE, DROP_TYPES, RED, GOLD, GREEN

class Drop:
    def __init__(self):
        self.x = random.randint(0, WIDTH - DROP_SIZE)
        self.y = 0
        self.speed = random.randint(3, 6)
        self.type = random.choice(DROP_TYPES)
        self.rect = pygame.Rect(self.x, self.y, DROP_SIZE, DROP_SIZE)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        color = RED if self.type == "bomb" else GOLD if self.type == "coin" else GREEN
        pygame.draw.circle(screen, color, self.rect.center, DROP_SIZE // 2)
