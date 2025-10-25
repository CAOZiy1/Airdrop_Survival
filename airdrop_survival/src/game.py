# src/game.py

import pygame
import random
from settings import WIDTH, HEIGHT, PLAYER_HEIGHT
from player import Player
from drop import Drop
from ui import draw_status, draw_gameover
from settings import LEVELS, CAN_IMAGE


class Game:
    def __init__(self):
        pygame.init()
        # initialize sounds for drops and pickups (safe to call even if mixer already init)
        try:
            import drop as drop_module
            drop_module.init_sounds()
        except Exception:
            pass
        # Prepare and play urgent gameplay BGM (generate file at runtime if missing)
        try:
            # ensure mixer is available
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
            except Exception:
                pass
            # synthesizer will create assets/sounds/urgent_bgm.wav if needed
            try:
                from audio import ensure_urgent_bgm
                import os
                base = os.path.join(os.path.dirname(__file__), '..', 'assets')
                bgm_path = ensure_urgent_bgm(os.path.join(base, 'sounds', 'urgent_bgm.wav'))
            except Exception:
                bgm_path = None

            if bgm_path:
                try:
                    # load via music API so it streams and loops efficiently
                    pygame.mixer.music.load(bgm_path)
                    try:
                        from settings import SOUND_VOLUME, SOUND_MUTED
                    except Exception:
                        SOUND_VOLUME = 1.0; SOUND_MUTED = False
                    vol = 0.6 * (0.0 if SOUND_MUTED else float(SOUND_VOLUME))
                    try:
                        pygame.mixer.music.set_volume(vol)
                    except Exception:
                        pass
                    pygame.mixer.music.play(loops=-1)
                except Exception:
                    # if music fails to load/play, ignore and continue
                    pass
        except Exception:
            pass
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
        # level state
        self.level_index = 0
        self.level = LEVELS[self.level_index] if LEVELS else None
        self.level_end_time = self.start_ticks + (self.level['time_seconds'] * 1000) if self.level else None
        self.level_active = True if self.level else False
        # 不再显示关卡开始提示，直接进入游戏
        # visual feedback: floating pop texts as list of tuples
        # tuple formats supported for backward compatibility:
        #  (x, start_y, start_ms)                   -> text '+1', yellow
        #  (x, start_y, start_ms, text)             -> color defaults to yellow
        #  (x, start_y, start_ms, text, (r,g,b))    -> explicit color
        self.coin_pops = []
        # small font for coin pop text (increased to 30 per user request)
        self.font_small = pygame.font.SysFont(None, 30)
        # control hint: show shortly after entering the game (appears after Intro)
        try:
            # show control hint a bit longer so players can read it
            self.control_hint_duration_ms = 5000
            self.control_hint_end = pygame.time.get_ticks() + self.control_hint_duration_ms
            # Prefer to use the game's SysFont so the hint matches other UI text
            hint_size = 28
            base_font = pygame.font.SysFont(None, hint_size, bold=True)

            # Always use the base font for the main text so it remains visually unified.
            # Try to find a separate arrow-capable font for the ←/→ glyphs; if found,
            # we'll render the arrows using that font and keep other text in base_font.
            self.control_hint_font = base_font
            self.control_hint_arrow_font = None
            self.control_hint_use_unicode = False

            candidates = ['Segoe UI Symbol', 'Segoe UI', 'DejaVu Sans', 'Noto Sans', 'Symbola', 'Arial Unicode MS', 'FreeSerif']
            found_path = None
            for name in candidates:
                try:
                    path = pygame.font.match_font(name)
                    if not path:
                        continue
                    tmp = pygame.font.Font(path, hint_size)
                    # test metrics for arrows
                    try:
                        m_left = tmp.metrics('←')
                        m_right = tmp.metrics('→')
                        ok_left = (m_left is not None and len(m_left) > 0 and m_left[0] is not None)
                        ok_right = (m_right is not None and len(m_right) > 0 and m_right[0] is not None)
                    except Exception:
                        ok_left = ok_right = False
                    if ok_left and ok_right:
                        found_path = path
                        break
                except Exception:
                    continue

            if found_path:
                try:
                    self.control_hint_arrow_font = pygame.font.Font(found_path, hint_size)
                    self.control_hint_use_unicode = True
                except Exception:
                    self.control_hint_arrow_font = None
                    self.control_hint_use_unicode = False

            # split main hint text into parts around the arrows so we can render arrows with
            # a separate font while keeping other text in the unified base font.
            self.control_hint_text_before = "PRESS "
            self.control_hint_text_after = " OR A/D KEYS TO MOVE THE CHARACTER"
        except Exception:
            self.control_hint_duration_ms = 0
            self.control_hint_end = 0
            self.control_hint_font = self.font_small
            self.control_hint_text = ""

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
            try:
                self.draw()
                pygame.display.flip()
            except pygame.error as e:
                # If the display surface was quit (window closed) we should exit cleanly.
                msg = str(e).lower()
                if 'display surface quit' in msg or 'video system not initialized' in msg:
                    self.running = False
                    break
                else:
                    # re-raise unexpected pygame errors
                    raise
        # fade out music if playing, then quit
        try:
            try:
                pygame.mixer.music.fadeout(800)
            except Exception:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
        except Exception:
            pass
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # keydown for buying food
            elif event.type == pygame.KEYDOWN:
                # debug: print A/D keydowns to verify input
                try:
                    if event.key in (pygame.K_a, pygame.K_d):
                        print(f"keydown: {event.key}, name: {pygame.key.name(event.key)}")
                except Exception:
                    pass

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
            # compute per-level speed multiplier (level 0 -> 1.0)
            try:
                from settings import LEVEL_SPEED_INCREASE_PER_LEVEL
                level_mult = 1.0 + (self.level_index * LEVEL_SPEED_INCREASE_PER_LEVEL) if hasattr(self, 'level_index') else 1.0
            except Exception:
                level_mult = 1.0
            self.drops.append(Drop(elapsed_seconds=elapsed_seconds, level_speed_multiplier=level_mult))

        for drop in self.drops[:]:
            drop.update()
            if drop.rect.colliderect(self.player.rect):
                if drop.type == "bomb":
                    self.hearts -= 1
                    # play bomb explosion sound
                    try:
                        import drop as drop_module
                        drop_module.play_bomb()
                    except Exception:
                        pass
                    # show hurt overlay for ~2 seconds
                    self.player.set_hurt(2)
                    # floating red -1 feedback above player
                    try:
                        self.coin_pops.append((self.player.rect.centerx, self.player.rect.top, pygame.time.get_ticks(), "-1", (200, 30, 30)))
                    except Exception:
                        pass
                elif drop.type == "coin":
                    self.coins += 1
                    # play coin pickup sound
                    try:
                        import drop as drop_module
                        drop_module.play_coin()
                    except Exception:
                        pass
                    # add coin pop at player's position
                    self.coin_pops.append((self.player.rect.centerx, self.player.rect.top, pygame.time.get_ticks(), "+1"))
                elif drop.type == "health_pack" and self.hearts < 3:
                    self.hearts += 1
                    # play heal pickup sound
                    try:
                        import drop as drop_module
                        drop_module.play_heal()
                    except Exception:
                        pass
                    # floating green +1 feedback for heal
                    try:
                        self.coin_pops.append((self.player.rect.centerx, self.player.rect.top, pygame.time.get_ticks(), "+1", (50, 200, 50)))
                    except Exception:
                        pass
                self.drops.remove(drop)
            elif drop.y > HEIGHT:
                self.drops.remove(drop)

        # prune expired coin pops (duration ms)
        now = pygame.time.get_ticks()
        COIN_POP_DURATION = 800
        # coin_pops now contain tuples (x, start_y, t0, text)
        self.coin_pops = [p for p in self.coin_pops if now - p[2] < COIN_POP_DURATION]

        # ...hunger system removed...

        # Level timer check: if level active and time reached, evaluate outcome
        if self.level_active and self.level_end_time is not None and now >= self.level_end_time:
            # determine success if coins >= required
            coins_required = self.level.get('coins_required', 0)
            reward = self.level.get('reward', {})
            from ui import draw_level_result
            # try to load reward image from assets
            reward_img = None
            try:
                import os
                base = os.path.join(os.path.dirname(__file__), '..', 'assets')
                p = os.path.join(base, reward.get('image', CAN_IMAGE))
                if os.path.exists(p):
                    reward_img = pygame.image.load(p).convert_alpha()
            except Exception:
                reward_img = None

            if self.coins >= coins_required:
                # success: consume coins
                self.coins -= coins_required
                # show success UI with can image
                draw_level_result(self.screen, self.font, f"CONGRATULATIONS! YOU GOT A {reward.get('type', '奖励')}", success=True, reward_image=reward_img)
                # advance to next level if available
                if self.level_index + 1 < len(LEVELS):
                    self.level_index += 1
                    self.level = LEVELS[self.level_index]
                    # reset timers: start_ticks and level_end_time based on now
                    self.start_ticks = pygame.time.get_ticks()
                    self.level_end_time = self.start_ticks + (self.level['time_seconds'] * 1000)
                    self.level_active = True
                    # clear drops to give the player a fresh start for next level
                    self.drops.clear()
                    # show level start hint for the new level
                    try:
                        from ui import draw_level_start_hint
                        reward = self.level.get('reward', {})
                        reward_img = None
                        import os
                        base = os.path.join(os.path.dirname(__file__), '..', 'assets')
                        p = os.path.join(base, reward.get('image', CAN_IMAGE))
                        if os.path.exists(p):
                            reward_img = pygame.image.load(p).convert_alpha()
                        draw_level_start_hint(self.screen, self.font, self.level.get('coins_required', 0), reward.get('type', 'can'), reward_image=reward_img)
                    except Exception:
                        pass
                else:
                    # no more levels: end game — show back-to-menu overlay
                    self._show_back_to_menu("All levels cleared!", (0, 220, 0))
                    self.running = False
                    return
            else:
                # failure: show message
                draw_level_result(self.screen, self.font, "Time's up! Not enough coins, challenge failed.", success=False, reward_image=None)
                self.level_active = False
                # show game over after failure with back-to-menu option
                self._show_back_to_menu("GAME OVER", (255, 0, 0))
                self.running = False
                return
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
                draw_status(self.screen, self.font, self.hearts, self.coins)
                # draw player (dead sprite will be drawn by player.draw)
                self.player.draw(self.screen, (0, 0, 0))

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

            # final Game Over message after desaturation — back-to-menu option
            self._show_back_to_menu("Game Over - You Died", (255, 0, 0))
            self.running = False


    def draw(self):
        self.player.draw(self.screen, (0, 0, 0))
        for drop in self.drops:
            drop.draw(self.screen)
        # compute remaining level time if active
        time_left = None
        if self.level_active and self.level_end_time is not None:
            ms_left = max(0, self.level_end_time - pygame.time.get_ticks())
            time_left = int(ms_left / 1000)
        draw_status(self.screen, self.font, self.hearts, self.coins)
        # show centered countdown message about starvation
        if time_left is not None:
            try:
                from ui import draw_center_countdown
                draw_center_countdown(self.screen, self.font, time_left)
            except Exception:
                pass
        # draw coin pop effects
        now = pygame.time.get_ticks()
        COIN_POP_DURATION = 800
        for p in self.coin_pops:
            # support tuples:
            # (x, start_y, t0) -> text '+1', yellow
            # (x, start_y, t0, text) -> default color yellow
            # (x, start_y, t0, text, (r,g,b)) -> explicit color
            try:
                if len(p) == 3:
                    x, start_y, t0 = p
                    text = "+1"
                    color = (255, 223, 0)
                elif len(p) == 4:
                    x, start_y, t0, text = p
                    color = (255, 223, 0)
                else:
                    x, start_y, t0, text, color = p
            except Exception:
                # malformed entry, skip
                continue
            elapsed = now - t0
            if elapsed < COIN_POP_DURATION:
                frac = elapsed / COIN_POP_DURATION
                y = start_y - int(frac * 30)
                alpha = max(0, 255 - int(255 * frac))
                txt = self.font_small.render(text, True, color)
                try:
                    txt.set_alpha(alpha)
                except Exception:
                    pass
                rect = txt.get_rect(center=(x, y))
                self.screen.blit(txt, rect)

        # show a brief control hint at game start (after Intro) — larger font, slightly up
        try:
            now_hint = pygame.time.get_ticks()
            if getattr(self, 'control_hint_end', 0) and now_hint < self.control_hint_end:
                # If we have a Unicode-capable font, render the arrow glyphs directly
                if getattr(self, 'control_hint_use_unicode', False) and getattr(self, 'control_hint_arrow_font', None):
                    # Mixed-font rendering: main text (unified UI font) + arrow glyphs from arrow-capable font
                    try:
                        color = (255, 230, 180)
                        shadow_color = (30, 30, 30)

                        t_before = self.control_hint_font.render(self.control_hint_text_before, True, color)
                        t_after = self.control_hint_font.render(self.control_hint_text_after, True, color)

                        # arrows rendered with the arrow-capable font
                        arrow_l = self.control_hint_arrow_font.render('←', True, color)
                        # slash between arrows for clarity; render with base font (should exist)
                        slash = self.control_hint_font.render('/', True, color)
                        arrow_r = self.control_hint_arrow_font.render('→', True, color)

                        total_w = t_before.get_width() + arrow_l.get_width() + slash.get_width() + arrow_r.get_width() + t_after.get_width()
                        hx = WIDTH // 2 - total_w // 2
                        hy = HEIGHT // 2 - 10

                        # compute vertical centering so arrows align with text baseline visually
                        pieces = [t_before, arrow_l, slash, arrow_r, t_after]
                        try:
                            heights = [p.get_height() for p in pieces]
                            base_h = max(heights) if heights else 0
                            center_y = hy + base_h // 2

                            # draw shadows for each piece at y centered on center_y
                            x = hx
                            # small upward nudge for arrow glyphs to visually align with text
                            # adjusted: -4 to move arrows 1px down from previous -5
                            arrow_vertical_nudge = -4
                            shadow_surfaces = [
                                self.control_hint_font.render(self.control_hint_text_before, True, shadow_color),
                                self.control_hint_arrow_font.render('←', True, shadow_color),
                                self.control_hint_font.render('/', True, shadow_color),
                                self.control_hint_arrow_font.render('→', True, shadow_color),
                                self.control_hint_font.render(self.control_hint_text_after, True, shadow_color),
                            ]
                            for idx, s in enumerate(shadow_surfaces):
                                # index 1 and 3 are arrow glyphs
                                y_s = center_y - s.get_height() // 2
                                if idx in (1, 3):
                                    y_s += arrow_vertical_nudge
                                self.screen.blit(s, (x + 2, y_s + 2))
                                x += s.get_width()

                            # blit main pieces centered vertically, applying same nudge for arrows
                            x = hx
                            for idx, p in enumerate(pieces):
                                y_p = center_y - p.get_height() // 2
                                if idx in (1, 3):
                                    y_p += arrow_vertical_nudge
                                self.screen.blit(p, (x, y_p))
                                x += p.get_width()
                        except Exception:
                            # fallback to previous simple blit if centering fails
                            try:
                                x = hx
                                self.screen.blit(t_before, (x, hy)); x += t_before.get_width()
                                self.screen.blit(arrow_l, (x, hy)); x += arrow_l.get_width()
                                self.screen.blit(slash, (x, hy)); x += slash.get_width()
                                self.screen.blit(arrow_r, (x, hy)); x += arrow_r.get_width()
                                self.screen.blit(t_after, (x, hy))
                            except Exception:
                                pass
                    except Exception:
                        # fall back to simple rendering if anything unexpected happens
                        try:
                            hint_s = self.control_hint_font.render('PRESS ←/→ OR A/D KEYS TO MOVE THE CHARACTER', True, (255, 230, 180))
                            hx = WIDTH // 2 - hint_s.get_width() // 2
                            hy = HEIGHT // 2 - 10
                            shadow = self.control_hint_font.render('PRESS ←/→ OR A/D KEYS TO MOVE THE CHARACTER', True, (30, 30, 30))
                            self.screen.blit(shadow, (hx + 2, hy + 2))
                            self.screen.blit(hint_s, (hx, hy))
                        except Exception:
                            pass
                else:
                    # Render ASCII text and draw small triangle arrows on both sides
                    hint_s = self.control_hint_font.render(self.control_hint_text, True, (255, 230, 180))
                    hx = WIDTH // 2 - hint_s.get_width() // 2
                    hy = HEIGHT // 2 - 10

                    # draw arrows (triangles)
                    try:
                        arrow_size = 12
                        arrow_gap = 8
                        half = arrow_size // 2
                        cy = hy + hint_s.get_height() // 2

                        ax_left = hx - arrow_gap - arrow_size
                        left_points = [
                            (ax_left + arrow_size, cy - half),
                            (ax_left + arrow_size, cy + half),
                            (ax_left, cy),
                        ]
                        ax_right = hx + hint_s.get_width() + arrow_gap
                        right_points = [
                            (ax_right, cy - half),
                            (ax_right, cy + half),
                            (ax_right + arrow_size, cy),
                        ]

                        # shadow for arrows
                        try:
                            pygame.draw.polygon(self.screen, (30, 30, 30), [(x + 2, y + 2) for (x, y) in left_points])
                            pygame.draw.polygon(self.screen, (30, 30, 30), [(x + 2, y + 2) for (x, y) in right_points])
                        except Exception:
                            pass

                        pygame.draw.polygon(self.screen, (255, 230, 180), left_points)
                        pygame.draw.polygon(self.screen, (255, 230, 180), right_points)
                    except Exception:
                        pass

                    # shadow and text
                    try:
                        shadow = self.control_hint_font.render(self.control_hint_text, True, (30, 30, 30))
                        self.screen.blit(shadow, (hx + 2, hy + 2))
                    except Exception:
                        pass
                    self.screen.blit(hint_s, (hx, hy))
        except Exception:
            pass

    def _show_back_to_menu(self, message, color):
        """Display an overlay with a Back to Menu button and Quit option.

        Blocks until the player selects an option. If 'Back to Menu' is clicked,
        attempt to run the Intro screen (if available) before returning.
        """
        try:
            overlay = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
            overlay.fill((0, 0, 0, 180))

            # Match intro ENTER GAME styling: font size, color, padding, border
            big_font = pygame.font.SysFont(None, 32)
            label = big_font.render('BACK TO MENU', True, (10, 10, 10))
            quit_label = big_font.render('QUIT', True, (10, 10, 10))
            padx, pady = 20, 14
            bw = label.get_width() + padx * 2
            bh = label.get_height() + pady * 2
            qw = quit_label.get_width() + padx * 2
            qh = quit_label.get_height() + pady * 2

            bx = WIDTH // 2 - bw // 2
            by = HEIGHT // 2 + 20
            qx = WIDTH // 2 - qw // 2
            qy = by + bh + 12

            button_rect = pygame.Rect(bx, by, bw, bh)
            quit_rect = pygame.Rect(qx, qy, qw, qh)

            text_surf = self.font.render(message, True, color)

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if button_rect.collidepoint(event.pos):
                            # run intro/menu then return
                            try:
                                from intro import Intro
                                if Intro is not None:
                                    Intro().run()
                            except Exception:
                                pass
                            waiting = False
                            break
                        if quit_rect.collidepoint(event.pos):
                            waiting = False
                            break

                from ui import draw_background
                draw_background(self.screen, WIDTH, HEIGHT)
                self.screen.blit(overlay, (0, 0))
                self.screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEIGHT // 2 - 80))

                # draw main button with same look as intro's ENTER GAME
                pygame.draw.rect(self.screen, (255, 230, 140), button_rect, border_radius=10)
                pygame.draw.rect(self.screen, (60, 60, 60), button_rect, width=3, border_radius=10)
                self.screen.blit(label, (bx + padx, by + pady - 1))

                # draw quit button using inverted colors (swap bg/text)
                # previous quit bg was (255,230,140) and text was (10,10,10)
                # swap so bg becomes dark and text becomes light
                pygame.draw.rect(self.screen, (60, 60, 60), quit_rect, border_radius=10)
                pygame.draw.rect(self.screen, (255, 230, 140), quit_rect, width=3, border_radius=10)
                # render quit label in the former bg color for contrast
                quit_label = big_font.render('QUIT', True, (255, 230, 140))
                self.screen.blit(quit_label, (qx + padx, qy + pady - 1))

                pygame.display.flip()
                self.clock.tick(30)
        except Exception:
            try:
                from ui import draw_gameover
                draw_gameover(self.screen, self.font, message, color)
            except Exception:
                pass
