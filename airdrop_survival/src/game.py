# src/game.py

import pygame
import random
from settings import WIDTH, HEIGHT, WHITE, BLACK, RED, GREEN, PLAYER_HEIGHT
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
        # position player so its bottom sits slightly above the bottom of the screen
        self.player = Player(WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 10)
        self.drops = []
        self.hearts = 3
        self.coins = 0
        self.running = True
        # track start time (milliseconds)
        self.start_ticks = pygame.time.get_ticks()
        # visual feedback: coin pop effects as list of (x, y, start_ms)
        self.coin_pops = []
        # small font for coin pop text
        self.font_small = pygame.font.SysFont(None, 24)

    def run(self):
        while self.running:
            self.clock.tick(60)
            # draw procedural background (sky gradient + ground)
            from ui import draw_background
            draw_background(self.screen, WIDTH, HEIGHT)
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

        # dynamic spawn interval: decreases over time to increase spawn frequency
        elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
        from settings import DROP_SPAWN_INTERVAL_BASE, DROP_SPAWN_INTERVAL_MIN, DROP_SPAWN_DECREASE_PER_MIN
        # compute current interval
        decrease = (elapsed_seconds / 60.0) * DROP_SPAWN_DECREASE_PER_MIN
        interval = max(DROP_SPAWN_INTERVAL_MIN, int(DROP_SPAWN_INTERVAL_BASE - decrease))
        if random.randint(1, interval) == 1:
            self.drops.append(Drop(elapsed_seconds=elapsed_seconds))

        for drop in self.drops[:]:
            drop.update()
            if drop.rect.colliderect(self.player.rect):
                if drop.type == "bomb":
                    self.hearts -= 1
                    # show hurt overlay for ~2 seconds
                    self.player.set_hurt(2)
                elif drop.type == "coin":
                    self.coins += 1
                    # add coin pop at player's position
                    self.coin_pops.append((self.player.rect.centerx, self.player.rect.top, pygame.time.get_ticks()))
                elif drop.type == "health_pack" and self.hearts < 3:
                    self.hearts += 1
                self.drops.remove(drop)
            elif drop.y > HEIGHT:
                self.drops.remove(drop)

        # prune expired coin pops (duration ms)
        now = pygame.time.get_ticks()
        COIN_POP_DURATION = 800
        self.coin_pops = [p for p in self.coin_pops if now - p[2] < COIN_POP_DURATION]

        if self.hearts <= 0:
            # set dead overlay for 10 seconds and show a rising halo above the player
            DEATH_MS = 10000
            self.player.set_dead(DEATH_MS / 1000)
            start = pygame.time.get_ticks()
            # animation loop for death duration
            while pygame.time.get_ticks() - start < DEATH_MS:
                # pump events so window remains responsive
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                # draw frame with halo
                from ui import draw_background
                draw_background(self.screen, WIDTH, HEIGHT)
                # draw drops and status then player so halo can be drawn on top
                for drop in self.drops:
                    drop.draw(self.screen)
                draw_status(self.screen, self.font, self.hearts, self.coins)
                # draw player (dead sprite will be drawn by player.draw)
                self.player.draw(self.screen, BLACK)

                # halo animation: rises from player's head upward over the death duration
                now = pygame.time.get_ticks()
                frac = (now - start) / float(DEATH_MS)
                # halo parameters
                halo_max_rise = 70
                halo_y = self.player.rect.top - int(frac * halo_max_rise) - 10
                halo_x = self.player.rect.centerx
                halo_alpha = max(0, 255 - int(frac * 255))
                halo_size = int(self.player.rect.width * (0.6 + 0.4 * (1 - frac)))
                # draw halo as a ring on a temp surface with per-pixel alpha
                halo_surf = pygame.Surface((halo_size * 2, halo_size // 2), pygame.SRCALPHA)
                ring_rect = halo_surf.get_rect(center=(halo_size, halo_size // 4))
                # ring color (gold) with computed alpha
                ring_color = (255, 230, 120, halo_alpha)
                pygame.draw.ellipse(halo_surf, ring_color, ring_rect, width=max(2, halo_size // 8))
                self.screen.blit(halo_surf, (halo_x - halo_surf.get_width() // 2, halo_y - halo_surf.get_height() // 2))

                pygame.display.flip()
                self.clock.tick(30)

            # after the death animation, convert screen to grayscale if possible
            try:
                import numpy as _np
                from pygame import surfarray
                arr = surfarray.pixels3d(self.screen)
                # compute luminance and copy into RGB channels
                lum = (_np.dot(arr[..., :3], [0.2989, 0.5870, 0.1140])).astype(arr.dtype)
                arr[..., 0] = lum
                arr[..., 1] = lum
                arr[..., 2] = lum
                del arr
            except Exception:
                # fallback: overlay a semi-transparent gray surface to approximate desaturation
                overlay = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
                overlay.fill((120, 120, 120, 150))
                self.screen.blit(overlay, (0, 0))

            # final Game Over message after desaturation
            draw_gameover(self.screen, self.font, "Game Over - You Died", RED)
            pygame.display.flip()
            # short pause for the Game Over display
            pygame.time.wait(1500)
            self.running = False
        elif self.coins >= 50:
            draw_gameover(self.screen, self.font, "Victory! You collected 50 coins!", GREEN)
            self.running = False

    def draw(self):
        self.player.draw(self.screen, BLACK)
        for drop in self.drops:
            drop.draw(self.screen)
        draw_status(self.screen, self.font, self.hearts, self.coins)
        # draw coin pop effects
        now = pygame.time.get_ticks()
        COIN_POP_DURATION = 800
        for x, start_y, t0 in self.coin_pops:
            elapsed = now - t0
            if elapsed < COIN_POP_DURATION:
                frac = elapsed / COIN_POP_DURATION
                y = start_y - int(frac * 30)
                alpha = max(0, 255 - int(255 * frac))
                txt = self.font_small.render("+1", True, (255, 223, 0))
                txt.set_alpha(alpha)
                rect = txt.get_rect(center=(x, y))
                self.screen.blit(txt, rect)
