"""Convert near-white background in assets to transparent.
Backs up originals as *.bak.png then overwrites the asset with a PNG that has alpha.
Usage: run with the project's Python in the venv.
"""
import os
import pygame

THRESHOLD = 240  # channel value above which a pixel is considered 'white'
FILES = ['coin.png', 'bomb.png', 'health_pack.png']

base = os.path.join(os.path.dirname(__file__), '..', 'assets')
base = os.path.normpath(base)

pygame.init()
# Ensure a minimal display is available so convert_alpha and image operations work
try:
    pygame.display.init()
    pygame.display.set_mode((1, 1))
except Exception:
    # If display can't be initialized (very headless environment), proceed and hope load works without convert_alpha
    pass

for fn in FILES:
    p = os.path.join(base, fn)
    if not os.path.exists(p):
        print('skip, not found', p)
        continue
    print('processing', p)
    try:
        surf = pygame.image.load(p).convert_alpha()
    except Exception as e:
        print('failed to load', p, e)
        continue

    w, h = surf.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA, 32)
    out = out.convert_alpha()

    # iterate pixels
    for x in range(w):
        for y in range(h):
            r, g, b, a = surf.get_at((x, y))
            # If pixel is near-white and opaque, make it transparent
            if a > 0 and r >= THRESHOLD and g >= THRESHOLD and b >= THRESHOLD:
                out.set_at((x, y), (255, 255, 255, 0))
            else:
                out.set_at((x, y), (r, g, b, a))

    # backup original
    bak = p + '.bak.png'
    if not os.path.exists(bak):
        try:
            os.rename(p, bak)
            print('backed up', p, '->', bak)
        except Exception as e:
            print('could not back up', p, e)
            # continue and overwrite
    else:
        print('backup already exists', bak)

    # save new file (overwrite original path)
    try:
        pygame.image.save(out, p)
        print('wrote transparent', p)
    except Exception as e:
        print('failed to save', p, e)

pygame.quit()
