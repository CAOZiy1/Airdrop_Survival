"""
Intro animation using existing assets in assets/.

Behavior:
- Uses assets/background.png as the background.
- Loads airplane.png and other drop images (coin.png, health_pack.png, bomb.png).
- Plane flies left->right; when crossing center it drops three items.
- After drop, shows two hint lines and an "进入游戏" button. Clicking it returns control.
"""
import os
import pygame
from ui import draw_background
from settings import WIDTH, HEIGHT


def _load_asset(name):
    base = os.path.join(os.path.dirname(__file__), '..', 'assets')
    p = os.path.join(base, name)
    try:
        if os.path.exists(p):
            return pygame.image.load(p).convert_alpha()
    except Exception:
        pass
    return None


class Intro:
    def __init__(self):
        # initialize basic pygame subsystems (Game also does this, but safe here)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Airdrop Survival - Intro')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 34)
        self.small_font = pygame.font.SysFont(None, 22)

        # load assets (use names that exist in the project's assets folder)
        self.bg = None  # background will be loaded via ui.draw_background which prefers assets/background.png
        self.plane_img = _load_asset('airplane.png') or _load_asset('plane.png')
        self.coin_img = _load_asset('coin.png')
        self.health_img = _load_asset('health_pack.png') or _load_asset('medkit.png')
        self.bomb_img = _load_asset('bomb.png')

    def run(self):
        # prepare plane surface
        plane = self.plane_img
        if plane is None:
            # fallback simple plane
            plane = pygame.Surface((140, 80), pygame.SRCALPHA)
            pygame.draw.polygon(plane, (40, 120, 140), [(0, 40), (110, 10), (130, 40), (110, 70)])
        # scale plane down so it flies in the sky area (smaller than player)
        SCALE = 0.6
        plane = pygame.transform.smoothscale(plane, (int(plane.get_width() * SCALE), int(plane.get_height() * SCALE)))
        plane_w, plane_h = plane.get_width(), plane.get_height()
        plane_x = -plane_w
        # position plane higher in the sky (above UI/status area)
        plane_y = 40
        plane_speed = 4

        dropped = False
        drops = []  # each drop: dict with surf, x, y, vy, type
        dropped_at = None

        running = True
        button_rect = None
        show_button = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if show_button and button_rect and button_rect.collidepoint(event.pos):
                        running = False

            # update
            plane_x += plane_speed

            if plane_x > WIDTH // 2 and not dropped:
                self._spawn_drops(plane_x + plane_w // 2, plane_y + plane_h // 2, drops)
                dropped = True
                dropped_at = pygame.time.get_ticks()

            # update drop physics
            for d in drops:
                d['vy'] += 0.25
                d['y'] += d['vy']

            # draw
            draw_background(self.screen, WIDTH, HEIGHT)

            # draw plane
            self.screen.blit(plane, (plane_x, plane_y))

            # draw drops
            for d in drops:
                surf = d.get('surf')
                if surf:
                    sx = int(d['x'] - surf.get_width() // 2)
                    sy = int(d['y'])
                    self.screen.blit(surf, (sx, sy))
                else:
                    color = (212, 175, 55) if d['type'] == 'coin' else (200, 80, 80) if d['type'] == 'bomb' else (180, 255, 180)
                    pygame.draw.circle(self.screen, color, (int(d['x']), int(d['y']) + 8), 10)

            # messages and button after a short delay from drop
            if dropped and dropped_at is not None:
                age = pygame.time.get_ticks() - dropped_at
                if age > 300:
                    # English text for compatibility
                    t1 = self.font.render('Collect 20 coins to trade for a can', True, (255, 230, 180))
                    t2 = self.font.render("Don't starve", True, (255, 230, 180))
                    self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 40))
                    self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))

                    # button
                    label = self.small_font.render('Enter Game', True, (10, 10, 10))
                    padx, pady = 14, 8
                    bw = label.get_width() + padx * 2
                    bh = label.get_height() + pady * 2
                    bx = WIDTH // 2 - bw // 2
                    by = HEIGHT // 2 + 60
                    button_rect = pygame.Rect(bx, by, bw, bh)
                    pygame.draw.rect(self.screen, (255, 230, 140), button_rect, border_radius=6)
                    pygame.draw.rect(self.screen, (60, 60, 60), button_rect, width=2, border_radius=6)
                    self.screen.blit(label, (bx + padx, by + pady - 1))
                    show_button = True

            pygame.display.flip()
            self.clock.tick(60)

            # if plane completely leaves right and button not shown, force show
            if plane_x > WIDTH + 20 and not show_button:
                dropped = True
                if dropped_at is None:
                    dropped_at = pygame.time.get_ticks()

        # brief pause before returning to main
        pygame.time.wait(100)

    def _spawn_drops(self, cx, cy, drops):
        # spawn bomb (left), coin(center), health(right)
        bomb = self.bomb_img = getattr(self, 'bomb_img', None)
        coin = getattr(self, 'coin_img', None)
        health = getattr(self, 'health_img', None)

        drops.append({'surf': bomb, 'x': cx - 60, 'y': cy, 'vy': 2.6, 'type': 'bomb'})
        drops.append({'surf': coin, 'x': cx, 'y': cy, 'vy': 2.0, 'type': 'coin'})
        drops.append({'surf': health, 'x': cx + 60, 'y': cy, 'vy': 2.2, 'type': 'health'})
