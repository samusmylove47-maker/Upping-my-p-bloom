"""On-screen credit pieces. Every wording lives in theme.json."""
from paper import *
from theme import T


def bug(p, x=36, y=24, size=27):
    """Small persistent corner tag: who made this."""
    txt = T["credit_bug"]
    w = font(FRED, size * S).getlength(txt) / S + 62
    h = size * 1.05 + 24
    p.shape(rrect_pts(x, y, x + w, y + h, h / 2), INK, shadow=0.6)
    p.ell(x + 26, y + h / 2, 9, 9, TEAL, shadow=0, hl=False)
    p.text(x + 42 + (w - 62) / 2, y + h / 2 + 1, txt, size, CREAM, shadow=0, hl=False)


def opening_ribbon(p, cx, cy, size=40, maxw=1740):
    """Big opening statement under/over the title."""
    txt = T["credit_open"]
    while font(FRED, size * S).getlength(txt) / S + 80 > maxw and size > 20:
        size -= 1
    p.tag(cx, cy, txt, size, fill=INK, ink=CREAM, padx=40, pady=16)


def bug_alpha(t):
    """0..1 opacity of the corner tag at song time t (seconds). It lives only in a short window after the title card."""
    a, b = T["credit_bug_window"]; f = T.get("credit_bug_fade", 0.5)
    if t < a or t > b:
        return 0.0
    return max(0.0, min(1.0, (t - a) / f, (b - t) / f))
