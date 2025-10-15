# src/game.py

import pygame
import random
from settings import WIDTH, HEIGHT, WHITE, BLACK
from player import Player
from drop import Drop
from ui import draw_status, draw_gameover

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Airdrop Survival")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.player = Player(WIDTH // 2, HEIGHT - 60)
        self.drops = []
        self.hearts = 3
        self.coins = 0
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.screen.fill(WHITE)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)

        if random.randint(1, 30) == 1:
            self.drops.append(Drop())

        for drop in self.drops[:]:
            drop.update()
            if drop.rect.colliderect(self.player.rect):
                if drop.type == "bomb":
                    self.hearts -= 1
                elif drop.type == "coin":
                    self.coins += 1
                elif drop.type == "food" and self.hearts < 3:
                    self.hearts += 1
                self.drops.remove(drop)
            elif drop.y > HEIGHT:
                self.drops.remove(drop)

        if self.hearts <= 0:
            draw_gameover(self.screen, self.font, "Game Over - You Died", RED)
            self.running = False
        elif self.coins >= 50:
            draw_gameover(self.screen, self.font, "Victory! You collected 50 coins!", GREEN)
            self.running = False

    def draw(self):
        self.player.draw(self.screen, BLACK)
        for drop in self.drops:
            drop.draw(self.screen)
        draw_status(self.screen, self.font, self.hearts, self.coins)
