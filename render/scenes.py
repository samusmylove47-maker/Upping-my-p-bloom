"""Scene order for the video. Each scene lives in its own module."""
import engine as E


def load():
    if E.REG:
        return
    from sc_chorus import Chorus
    from sc_open import Intro
    from sc_verse1 import Verse1
    from sc_pre import Pre
    from sc_verse2 import Verse2
    from sc_dance import Dance, Verse3
    from sc_bridge import Bridge
    from sc_final import Final
    from sc_end import Outro, EndCard
    E.REG.extend([Intro(), Verse1(), Pre("pre1", False), Pre("pre2", True), Verse2(), Dance(), Verse3(), Bridge(), Final(), Outro(), EndCard(), Chorus("chorus1", False), Chorus("chorus2", True)])
    E.REG.sort(key=lambda s: s.t0)
    for a, b in zip(E.REG, E.REG[1:]):          # every scene ends where the next begins
        a.t1 = b.t0
