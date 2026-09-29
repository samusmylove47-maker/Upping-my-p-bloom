"""Scene order for the video. Each scene lives in its own module."""
import engine as E


def load():
    if E.REG:
        return
    from sc_chorus import Chorus
    E.REG.extend([Chorus("chorus1", False), Chorus("chorus2", True)])
    E.REG.sort(key=lambda s: s.t0)
