import os
import time
import pygame
import numpy as np

"""
Create a small window, draw colors, convert to grayscale using the same
numpy surfarray technique used in game.py, and save a screenshot.

Output: assets/screenshots/grayscale_test.png
"""

def project_root():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def main():
    base = project_root()
    out_dir = os.path.join(base, 'assets', 'screenshots')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'grayscale_test.png')

    pygame.init()
    try:
        screen = pygame.display.set_mode((320, 200))
        pygame.display.set_caption('Grayscale Test')
        # Draw a simple colored gradient
        w, h = screen.get_size()
        for y in range(h):
            t = y / max(h - 1, 1)
            color = (int(255 * t), int(120 * (1 - t)), int(200 * (0.5 + 0.5 * t)))
            pygame.draw.line(screen, color, (0, y), (w, y))
        pygame.display.flip()

        # Let the frame show briefly
        time.sleep(0.2)

        # Apply grayscale using numpy the same way as in game.py
        from pygame import surfarray
        arr = surfarray.pixels3d(screen)
        lum = (np.dot(arr[..., :3], [0.2989, 0.5870, 0.1140])).astype(arr.dtype)
        arr[..., 0] = lum
        arr[..., 1] = lum
        arr[..., 2] = lum
        del arr
        pygame.display.flip()

        # Save the grayscale result
        pygame.image.save(screen, out_path)
        print(f'[grayscale-test] Saved: {out_path}')
        # Keep window visible a moment
        time.sleep(0.3)
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
