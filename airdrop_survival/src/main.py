# src/main.py

from game import Game
try:
    from intro import Intro
except Exception:
    Intro = None

try:
    import state
except Exception:
    state = None


if __name__ == "__main__":
    # Only play Intro the first time (unless state is missing, then behave like before)
    played_intro = False
    if state is not None and Intro is not None:
        if not getattr(state, 'intro_shown', False):
            Intro().run()
            try:
                state.intro_shown = True
            except Exception:
                pass
            played_intro = True
    elif Intro is not None:
        # fallback: behave like original
        Intro().run()
        played_intro = True

    Game().run()

    