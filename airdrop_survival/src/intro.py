"""
Intro animation using existing assets in assets/.

Behavior:
- Uses assets/background.png as the background.
- Loads airplane.png and other drop images (coin.png, health_pack.png, bomb.png).
- Plane flies left->right; at three points it drops a few items.
- After the plane exits, dim the screen and show an "ENTER GAME" button.
"""
import os
import pygame
from ui import draw_background
from settings import WIDTH, HEIGHT, DROP_SIZE, INTRO_DROP_PAUSE, INTRO_DROP_PAUSE_MS, INTRO_DROP_TRIGGER_ADVANCE, SOUND_VOLUME, SOUND_MUTED


def _assets_path(*names: str) -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', *names))


def _load_asset(name):
    p = _assets_path(name)
    try:
        if os.path.exists(p):
            return pygame.image.load(p).convert_alpha()
    except Exception:
        pass
    return None


def _load_sound(candidates, volume: float = 1.0):
    """Try loading the first existing sound file from candidates under assets/sounds.
    Returns a pygame.mixer.Sound or None. Applies master volume and mute.
    """
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except Exception:
        return None

    base = _assets_path('sounds')
    for name in candidates:
        p = os.path.join(base, name)
        try:
            if os.path.exists(p):
                snd = pygame.mixer.Sound(p)
                # master volume and mute
                vol = float(volume) * (0.0 if SOUND_MUTED else float(SOUND_VOLUME))
                try:
                    snd.set_volume(vol)
                except Exception:
                    pass
                return snd
        except Exception:
            continue
    return None


class Intro:
    def __init__(self):
        # initialize basic pygame subsystems (Game also does this, but safe here)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Airdrop Survival - Intro')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 34)
        # title font for intro
        self.title_font = pygame.font.SysFont(None, 48, bold=True)
        self.button_font = pygame.font.SysFont(None, 32)

        # load assets (use names that exist in the project's assets folder)
        self.plane_img = _load_asset('airplane.png') or _load_asset('plane.png')
        self.coin_img = _load_asset('coin.png')
        self.health_img = _load_asset('health_pack.png') or _load_asset('medkit.png')
        self.bomb_img = _load_asset('bomb.png')
        # load sounds from assets/sounds/ (simple candidates, no verbose prints)
        self.plane_sound = _load_sound(['plane_loop.mp3', 'plane_loop.wav', os.path.join('..', 'airplane-engine-sound-2-67757.mp3')], volume=0.3)
        self.drop_sound = _load_sound(['drop_thud.mp3', 'drop_thud.wav', os.path.join('..', 'impact-258054.mp3')], volume=0.95)

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

        running = True
        button_rect = None
        show_button = False
        dark_shown_at = None
        # play looping plane sound if available
        try:
            if self.plane_sound is not None:
                self.plane_sound.play(loops=-1)
        except Exception:
            pass

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
            if plane_x > int(WIDTH * 0.05) - INTRO_DROP_TRIGGER_ADVANCE and not dropped_stage1:
                self._spawn_drops_random(plane_x + plane_w // 2, plane_y + plane_h, drops)
                dropped_stage1 = True
                if INTRO_DROP_PAUSE:
                    # pause plane for a short duration to let drops start falling
                    pygame.display.flip()
                    pygame.time.wait(INTRO_DROP_PAUSE_MS)

            # stage 2:
            if plane_x > int(WIDTH * 0.3) - INTRO_DROP_TRIGGER_ADVANCE and not dropped_stage2:
                self._spawn_drops_random(plane_x + plane_w // 2, plane_y + plane_h, drops)
                dropped_stage2 = True
                if INTRO_DROP_PAUSE:
                    pygame.display.flip()
                    pygame.time.wait(INTRO_DROP_PAUSE_MS)

            # stage 3:
            if plane_x > int(WIDTH * 0.6) - INTRO_DROP_TRIGGER_ADVANCE and not dropped_stage3:
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
            # Draw centered game title during intro while plane is still on-screen
            if plane_x <= WIDTH:
                title_surf = self.title_font.render('Airdrop Survival', True, (255, 240, 200))
                tx = WIDTH // 2 - title_surf.get_width() // 2
                ty = HEIGHT // 2 - title_surf.get_height() // 2
                # subtle shadow for readability
                shadow = self.title_font.render('Airdrop Survival', True, (30, 30, 30))
                self.screen.blit(shadow, (tx + 2, ty + 2))
                self.screen.blit(title_surf, (tx, ty))

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

            # After the plane leaves the screen, dim the scene and show a hint,
            # then display the button after a short delay.
            if plane_x > WIDTH + 20:
                if dark_shown_at is None:
                    dark_shown_at = pygame.time.get_ticks()
                # Dim the screen
                dark_overlay = pygame.Surface((WIDTH, HEIGHT))
                dark_overlay.set_alpha(160)
                dark_overlay.fill((0, 0, 0))
                self.screen.blit(dark_overlay, (0, 0))
                # Can icon (can.png) — move the icon and hint down slightly to vertically align with the buttons
                can_img = _load_asset('can.png')
                if can_img:
                    scale = int(DROP_SIZE * 1.5)
                    can_img = pygame.transform.smoothscale(can_img, (scale, scale))
                    can_x = WIDTH // 2 - can_img.get_width() // 2
                    # Move down about 40 pixels (closer to center), aligning with the button group
                    can_y = HEIGHT // 2 - 80
                    self.screen.blit(can_img, (can_x, can_y))
                # Hint text (only the objective). Move it down a bit so it sits closer to the can icon and button group
                t1 = self.font.render('COLLECT 20 COINS FOR A CAN', True, (255, 230, 180))
                # Move from HEIGHT//2 - 20 to HEIGHT//2 + 10
                self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 + 10))
                # Don't show the movement hint in the intro (it will be shown in-game)
                # Delay showing the button
                if pygame.time.get_ticks() - dark_shown_at > 900:
                    label = self.button_font.render('ENTER GAME', True, (10, 10, 10))
                    padx, pady = 20, 14  # increase inner padding
                    bw = label.get_width() + padx * 2
                    bh = label.get_height() + pady * 2
                    bx = WIDTH // 2 - bw // 2
                    by = HEIGHT // 2 + 60
                    button_rect = pygame.Rect(bx, by, bw, bh)
                    pygame.draw.rect(self.screen, (255, 230, 140), button_rect, border_radius=10)
                    pygame.draw.rect(self.screen, (60, 60, 60), button_rect, width=3, border_radius=10)
                    self.screen.blit(label, (bx + padx, by + pady - 1))
                    show_button = True


            pygame.display.flip()
            self.clock.tick(60)

        # brief pause before returning to main
        pygame.time.wait(100)
        # stop plane sound if any
        try:
            if self.plane_sound is not None:
                self.plane_sound.stop()
        except Exception:
            pass

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
        # play a drop sound when spawning randomized drops
        try:
            if getattr(self, 'drop_sound', None) is not None:
                self.drop_sound.play()
        except Exception:
            pass
