# src/game.py

import pygame
import random
from settings import WIDTH, HEIGHT, WHITE, BLACK, RED, GREEN, PLAYER_HEIGHT
from player import Player
from drop import Drop
from ui import draw_status, draw_gameover
from settings import MAX_HUNGER, HUNGER_DECAY_SECONDS, COINS_PER_FOOD


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
        # hunger: starts full
        self.hunger = MAX_HUNGER
        # next timestamp (ms) when hunger will decay by 1
        self.next_hunger_decay = pygame.time.get_ticks() + int(HUNGER_DECAY_SECONDS * 1000)
        self.running = True
        # track start time (milliseconds)
        self.start_ticks = pygame.time.get_ticks()
        # visual feedback: coin pop effects as list of (x, y, start_ms, text)
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
            # if update() turned off running (e.g. death/game-over sequence),
            # skip the regular draw/flip so we don't render a normal player frame.
            if not self.running:
                break
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # keydown for buying food
            elif event.type == pygame.KEYDOWN:
                # spend coins to buy food: 'f' key
                if event.key == pygame.K_f:
                    if self.coins >= COINS_PER_FOOD and self.hunger < MAX_HUNGER:
                        self.coins -= COINS_PER_FOOD
                        self.hunger = min(MAX_HUNGER, self.hunger + 1)
                        # show a +food coin pop at player
                        self.coin_pops.append((self.player.rect.centerx, self.player.rect.top, pygame.time.get_ticks(), "+food"))

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
                    self.coin_pops.append((self.player.rect.centerx, self.player.rect.top, pygame.time.get_ticks(), "+1"))
                elif drop.type == "health_pack" and self.hearts < 3:
                    self.hearts += 1
                self.drops.remove(drop)
            elif drop.y > HEIGHT:
                self.drops.remove(drop)

        # prune expired coin pops (duration ms)
        now = pygame.time.get_ticks()
        COIN_POP_DURATION = 800
        # coin_pops now contain tuples (x, start_y, t0, text)
        self.coin_pops = [p for p in self.coin_pops if now - p[2] < COIN_POP_DURATION]

        # hunger decay over time
        if now >= self.next_hunger_decay:
            # reduce hunger by 1 if >0
            if self.hunger > 0:
                self.hunger -= 1
            # schedule next decay
            self.next_hunger_decay = now + int(HUNGER_DECAY_SECONDS * 1000)

        if self.hearts <= 0:
            # set dead overlay and show a rising halo above the player
            # total death display target: ~7000ms (animation + final pause)
            # we keep the final pause at 1500ms, so animation loop is 5500ms
            DEATH_MS = 5500
            self.player.set_dead(DEATH_MS / 1000)
            start = pygame.time.get_ticks()
            # animation loop for death duration; halo rises faster than total death time
            HALO_RISE_MS = 3000
            halo_reached_at = None
            FLASH_MS = 300
            FAST_FADE_MS = 300
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
                draw_status(self.screen, self.font, self.hearts, self.coins, self.hunger)
                # draw player (dead sprite will be drawn by player.draw)
                self.player.draw(self.screen, BLACK)

                # halo animation: rises from player's head upward over the death duration
                now = pygame.time.get_ticks()
                # overall fraction for death (0..1)
                frac = (now - start) / float(DEATH_MS)
                # halo parameters
                halo_x = self.player.rect.centerx
                # halo rise fraction completes by HALO_RISE_MS
                halo_frac = min(1.0, (now - start) / float(HALO_RISE_MS))
                halo_max_rise = 50
                halo_y = self.player.rect.top - int(halo_frac * halo_max_rise) - 6
                # halo fade slightly based on overall death frac
                halo_alpha = max(0, 255 - int(frac * 255))
                # make halo smaller than player: 40% of player width down to 25% over halo_frac
                halo_size = int(self.player.rect.width * (0.4 - 0.15 * halo_frac))
                halo_size = max(8, halo_size)
                # draw halo as a smaller ring on a temp surface with per-pixel alpha
                halo_surf = pygame.Surface((halo_size * 2, halo_size // 2), pygame.SRCALPHA)
                ring_rect = halo_surf.get_rect(center=(halo_size, halo_size // 4))
                # ring color (gold) with computed alpha
                ring_color = (255, 230, 120, halo_alpha)
                pygame.draw.ellipse(halo_surf, ring_color, ring_rect, width=max(1, halo_size // 10))
                self.screen.blit(halo_surf, (halo_x - halo_surf.get_width() // 2, halo_y - halo_surf.get_height() // 2))

                # when halo reaches top, trigger a short bright flash
                if halo_frac >= 1.0 and halo_reached_at is None:
                    halo_reached_at = now
                if halo_reached_at is not None:
                    flash_age = now - halo_reached_at
                    # first, a short bright flash (FLASH_MS)
                    if flash_age < FLASH_MS:
                        flash_frac = flash_age / float(FLASH_MS)
                        # flash alpha that quickly fades
                        flash_alpha = int(200 * (1.0 - flash_frac))
                        flash_size = int(halo_size * 1.2) + 2
                        flash_surf = pygame.Surface((flash_size * 2, flash_size // 2), pygame.SRCALPHA)
                        flash_rect = flash_surf.get_rect(center=(flash_size, flash_size // 4))
                        flash_color = (255, 250, 200, flash_alpha)
                        pygame.draw.ellipse(flash_surf, flash_color, flash_rect, width=max(1, flash_size // 6))
                        self.screen.blit(flash_surf, (halo_x - flash_surf.get_width() // 2, halo_y - flash_surf.get_height() // 2))
                    # then a quick fade out window (FAST_FADE_MS) after flash finishes
                    elif flash_age < FLASH_MS + FAST_FADE_MS:
                        fade_age = flash_age - FLASH_MS
                        fade_frac = min(1.0, fade_age / float(FAST_FADE_MS))
                        fade_alpha = int(halo_alpha * (1.0 - fade_frac))
                        if fade_alpha > 0:
                            fade_surf = pygame.Surface((halo_size * 2, halo_size // 2), pygame.SRCALPHA)
                            fade_rect = fade_surf.get_rect(center=(halo_size, halo_size // 4))
                            fade_color = (255, 230, 120, fade_alpha)
                            pygame.draw.ellipse(fade_surf, fade_color, fade_rect, width=max(1, halo_size // 10))
                            self.screen.blit(fade_surf, (halo_x - fade_surf.get_width() // 2, halo_y - fade_surf.get_height() // 2))
                    # after fade window, stop drawing halo

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
        draw_status(self.screen, self.font, self.hearts, self.coins, self.hunger)
        # draw coin pop effects
        now = pygame.time.get_ticks()
        COIN_POP_DURATION = 800
        for p in self.coin_pops:
            # support tuples (x, start_y, t0) or (x, start_y, t0, text)
            if len(p) == 3:
                x, start_y, t0 = p
                text = "+1"
            else:
                x, start_y, t0, text = p
            elapsed = now - t0
            if elapsed < COIN_POP_DURATION:
                frac = elapsed / COIN_POP_DURATION
                y = start_y - int(frac * 30)
                alpha = max(0, 255 - int(255 * frac))
                txt = self.font_small.render(text, True, (255, 223, 0))
                txt.set_alpha(alpha)
                rect = txt.get_rect(center=(x, y))
                self.screen.blit(txt, rect)
