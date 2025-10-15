import pygame
import random
from settings import WIDTH, HEIGHT, FPS, SPAWN_INTERVAL, BLACK
from player import Player
from drop import Drop
from ui import UI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Airdrop Survival (starter)")
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)

        self.player = Player(WIDTH // 2, HEIGHT - 50)
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.drops = pygame.sprite.Group()

        self.running = True
        self.spawn_timer = 0.0
        self.score = 0
        self.lives = 3

    def spawn_drop(self):
        drop = Drop.random_spawn(self.screen.get_width())
        self.drops.add(drop)

    def handle_collisions(self):
        hits = pygame.sprite.spritecollide(self.player, self.drops, True)
        if hits:
            self.score += len(hits)

        # Drops that reach bottom already kill themselves; reduce lives whenever there are no drops
        # touching the bottom this function doesn't handle that — keep simple for starter.

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            self.player_group.update(dt, keys)
            self.drops.update(dt)

            # Spawning
            self.spawn_timer += dt
            if self.spawn_timer >= SPAWN_INTERVAL:
                self.spawn_timer -= SPAWN_INTERVAL
                self.spawn_drop()

            self.handle_collisions()

            self.screen.fill(BLACK)
            self.drops.draw(self.screen)
            self.player_group.draw(self.screen)
            self.ui.render(self.score, self.lives)
            pygame.display.flip()

        pygame.quit()
