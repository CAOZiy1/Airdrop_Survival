import os, wave, sys

def print_info(path: str):
    print(f"\n== {path} ==")
    print(f"exists: {os.path.exists(path)}")
    if not os.path.exists(path):
        return
    try:
        size = os.path.getsize(path)
        print(f"size: {size} bytes")
    except Exception as e:
        print(f"size: <error: {e}>")
    try:
        with wave.open(path, 'rb') as wf:
            nch = wf.getnchannels()
            sw = wf.getsampwidth()
            fr = wf.getframerate()
            nf = wf.getnframes()
            dur = nf / float(fr) if fr else 0.0
            ct = wf.getcomptype()
            cn = wf.getcompname()
            print(f"channels={nch}, sampwidth={sw*8}bit, rate={fr}Hz, frames={nf}, dur={dur:.3f}s, comptype={ct}, compname={cn}")
    except Exception as e:
        print(f"wave.open error: {e}")

    # Try pygame load
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            pygame.mixer.music.load(path)
            print("pygame.mixer.music.load: OK")
        except Exception as e:
            print(f"pygame.mixer.music.load: ERROR: {e}")
        try:
            snd = pygame.mixer.Sound(path)
            length = snd.get_length()
            print(f"pygame.mixer.Sound: OK (length={length:.3f}s)")
        except Exception as e:
            print(f"pygame.mixer.Sound: ERROR: {e}")
    except Exception as e:
        print(f"pygame init/load failed: {e}")

if __name__ == "__main__":
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'airdrop_survival', 'assets', 'sounds'))
    print_info(os.path.join(base, 'success.wav'))
    print_info(os.path.join(base, 'failure.wav'))
    print("\nDone.")
