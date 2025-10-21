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
from settings import WIDTH, HEIGHT, DROP_SIZE, INTRO_DROP_PAUSE, INTRO_DROP_PAUSE_MS, INTRO_DROP_TRIGGER_ADVANCE


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
        # changed to 0.3 to use 30% of original size and placed at the very top of the screen
        SCALE = 0.3
        plane = pygame.transform.smoothscale(plane, (int(plane.get_width() * SCALE), int(plane.get_height() * SCALE)))
        plane_w, plane_h = plane.get_width(), plane.get_height()
        plane_x = -plane_w
        # position plane at the very top of the screen
        plane_y = 0
        plane_speed = 3

        # three-stage drop flags: enter, middle, before exit
        dropped_stage1 = False
        dropped_stage2 = False
        dropped_stage3 = False
        drops = []  # each drop: dict with surf, x, y, vy, type
        dropped_at = None

        running = True
        button_rect = None
        show_button = False
        dark_shown_at = None

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

            # stage 1: when plane just enters the screen (x > 0) - trigger earlier by subtracting advance
            if plane_x > int(WIDTH * 0.1) - INTRO_DROP_TRIGGER_ADVANCE and not dropped_stage1:
                self._spawn_drops_random(plane_x + plane_w // 2, plane_y + plane_h, drops)
                dropped_stage1 = True
                if INTRO_DROP_PAUSE:
                    # pause plane for a short duration to let drops start falling
                    pygame.display.flip()
                    pygame.time.wait(INTRO_DROP_PAUSE_MS)

            # stage 2: 
            if plane_x > int(WIDTH * 0.4) - INTRO_DROP_TRIGGER_ADVANCE and not dropped_stage2:
                self._spawn_drops_random(plane_x + plane_w // 2, plane_y + plane_h, drops)
                dropped_stage2 = True
                dropped_at = pygame.time.get_ticks()
                if INTRO_DROP_PAUSE:
                    pygame.display.flip()
                    pygame.time.wait(INTRO_DROP_PAUSE_MS)

            # stage 3: 
            if plane_x > int(WIDTH * 0.7) - INTRO_DROP_TRIGGER_ADVANCE and not dropped_stage3:
                self._spawn_drops_random(plane_x + plane_w // 2, plane_y + plane_h, drops)
                dropped_stage3 = True
                if INTRO_DROP_PAUSE:
                    pygame.display.flip()
                    pygame.time.wait(INTRO_DROP_PAUSE_MS)

            # update drop physics
            for d in drops:
                # slower gravity in intro to match main game feel
                d['vy'] += 0.12
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

            # 飞机完全飞出画面后，先变暗和显示提示，延迟后再显示按钮
            if plane_x > WIDTH + 20:
                if dark_shown_at is None:
                    dark_shown_at = pygame.time.get_ticks()
                # 画面变暗
                dark_overlay = pygame.Surface((WIDTH, HEIGHT))
                dark_overlay.set_alpha(160)
                dark_overlay.fill((0, 0, 0))
                self.screen.blit(dark_overlay, (0, 0))
                # 提示文字
                t1 = self.font.render('Collect 20 coins to trade for a can', True, (255, 230, 180))
                t2 = self.font.render("Don't starve", True, (255, 230, 180))
                self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 40))
                self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))
                # 按钮延迟显示
                if pygame.time.get_ticks() - dark_shown_at > 1200:
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
                dropped_stage2 = True
                if dropped_at is None:
                    dropped_at = pygame.time.get_ticks()

        # brief pause before returning to main
        pygame.time.wait(100)

    def _spawn_drops(self, cx, cy, drops):
        # spawn bomb (left), coin(center), health(right)
        bomb = self.bomb_img = getattr(self, 'bomb_img', None)
        coin = getattr(self, 'coin_img', None)
        health = getattr(self, 'health_img', None)
        # scale assets to DROP_SIZE to match in-game icons and ensure spacing
        try:
            sb = pygame.transform.smoothscale(bomb, (DROP_SIZE, DROP_SIZE)) if bomb else None
        except Exception:
            sb = bomb
        try:
            sc = pygame.transform.smoothscale(coin, (DROP_SIZE, DROP_SIZE)) if coin else None
        except Exception:
            sc = coin
        try:
            sh = pygame.transform.smoothscale(health, (DROP_SIZE, DROP_SIZE)) if health else None
        except Exception:
            sh = health

        spacing = max(16, DROP_SIZE + 8)
        drops.append({'surf': sb, 'x': cx - spacing, 'y': cy, 'vy': 2.6, 'type': 'bomb'})
        drops.append({'surf': sc, 'x': cx, 'y': cy, 'vy': 2.0, 'type': 'coin'})
        drops.append({'surf': sh, 'x': cx + spacing, 'y': cy, 'vy': 2.2, 'type': 'health'})

    def _spawn_drops_random(self, cx, cy, drops):
        """Spawn a randomized set of drops around (cx, cy).
        Uses the assets loaded in __init__. Each call spawns 2..4 items with small x offsets and slower initial vy.
        """
        import random

        assets = [
            ('bomb', getattr(self, 'bomb_img', None)),
            ('coin', getattr(self, 'coin_img', None)),
            ('health', getattr(self, 'health_img', None))
        ]
        count = random.randint(2, 4)
        # use horizontal spacing based on DROP_SIZE to avoid overlap
        spacing = max(16, DROP_SIZE + 8)
        # center the set around cx
        start = - (count - 1) * 0.5 * spacing
        for i in range(count):
            kind, surf = random.choice(assets)
            # small jitter on top of spaced positions
            jitter = random.randint(-8, 8)
            pos_x = int(cx + start + i * spacing + jitter)
            # initial vy moderate so items fall at similar pace to game
            vy = random.uniform(1.2, 2.0)
            # scale surf to DROP_SIZE if available
            s = None
            try:
                s = pygame.transform.smoothscale(surf, (DROP_SIZE, DROP_SIZE)) if surf else None
            except Exception:
                s = surf
            drops.append({
                'surf': s,
                'x': pos_x,
                'y': cy,
                'vy': vy,
                'type': kind
            })
