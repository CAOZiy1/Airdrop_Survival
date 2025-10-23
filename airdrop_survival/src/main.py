# src/main.py

from game import Game
try:
    from intro import Intro
except Exception:
    Intro = None


if __name__ == "__main__":
    # run intro using provided assets if available
    if Intro is not None:
        Intro().run()
    Game().run()

    