import pygame
import os

pygame.init()
base = os.path.join(os.path.dirname(__file__), '..', 'assets')
base = os.path.normpath(base)
if not os.path.exists(base):
    os.makedirs(base)

SIZE = 128

# Bomb
bomb = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
pygame.draw.circle(bomb, (20, 60, 90), (SIZE//2, SIZE//2+8), SIZE//2 - 8)
pygame.draw.circle(bomb, (40, 100, 140), (SIZE//2 - 10, SIZE//2 - 6), SIZE//2 - 14, 4)
# fuse
pygame.draw.rect(bomb, (80, 60, 40), (SIZE//2 - 6, 8, 12, 28))
pygame.draw.circle(bomb, (255, 220, 80), (SIZE//2, 8), 6)
pygame.image.save(bomb, os.path.join(base, 'bomb.png'))
print('wrote', os.path.join(base, 'bomb.png'))

# Coin
coin = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
pygame.draw.circle(coin, (212, 175, 55), (SIZE//2, SIZE//2), SIZE//2 - 6)
pygame.draw.circle(coin, (120, 90, 20), (SIZE//2, SIZE//2), SIZE//2 - 6, 4)
# inner C
pygame.draw.circle(coin, (0,0,0,0), (SIZE//2+6, SIZE//2), SIZE//2 - 26)
pygame.image.save(coin, os.path.join(base, 'coin.png'))
print('wrote', os.path.join(base, 'coin.png'))

# Health pack
hp = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
pygame.draw.rect(hp, (255,255,255), (8, 18, SIZE-16, SIZE-36), border_radius=12)
pygame.draw.rect(hp, (200, 40, 40), (SIZE//2 - 18, SIZE//2 - 10, 36, 20))
pygame.draw.rect(hp, (200, 40, 40), (SIZE//2 - 10, SIZE//2 - 18, 20, 36))
pygame.image.save(hp, os.path.join(base, 'health_pack.png'))
print('wrote', os.path.join(base, 'health_pack.png'))

pygame.quit()
