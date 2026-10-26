"""Animated math scenes for the Calculus 1 course (each one moves to explain the idea).

Every scene is a function (d, bx, s, accent) drawn on the supersampled visual canvas.
s = seconds since the clip started (0..15).
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from render import Box, SS, ease, lerp, vtext, arrow, font, hex2rgb, WHITE, DIM, GOLD, GREEN, RED, PINK, is_rtl, iso

BLUE = (10, 132, 255, 255)
PURPLE = (191, 90, 242, 255)
CYAN = (100, 210, 255, 255)

def ph(s, a, b):
    """Progress 0..1 of phase [a, b] (eased)."""
    return ease((s - a) / (b - a))

def alpha(c, a):
    return c[:3] + (int(c[3] * max(0, min(1, a))) if len(c) > 3 else int(255 * a),)

# ---------------------------------------------------------------- axes

class Ax:
    def __init__(self, bx, xr, yr, pad=(70, 40, 50, 70), step=None):
        self.bx, self.xr, self.yr = bx, xr, yr
        self.l, self.r, self.t, self.b = [p * SS / 2 for p in pad]
        self.step = step
    def T(self, x, y):
        X = self.l + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * (self.bx.w - self.l - self.r)
        Y = self.bx.h - self.b - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * (self.bx.h - self.t - self.b)
        return X, Y
    def sx(self, dx):  # pixels per unit (x)
        return dx / (self.xr[1] - self.xr[0]) * (self.bx.w - self.l - self.r)
    def draw(self, d, a=1.0, ticks=True, labels=('x', 'y')):
        xs = self.step or _nice(self.xr[1] - self.xr[0])
        ys = self.step or _nice(self.yr[1] - self.yr[0])
        f = font(17 * SS, bold=False)
        for gx in np.arange(math.ceil(self.xr[0] / xs) * xs, self.xr[1] + 1e-9, xs):
            d.line([self.T(gx, self.yr[0]), self.T(gx, self.yr[1])], fill=(255, 255, 255, int(16 * a)), width=2)
            if ticks and abs(gx) > 1e-9 and self.yr[0] <= 0 <= self.yr[1]:
                X, Y = self.T(gx, 0)
                d.text((X, Y + 22), _fmt(gx), font=f, fill=(200, 200, 210, int(160 * a)), anchor='mm')
        for gy in np.arange(math.ceil(self.yr[0] / ys) * ys, self.yr[1] + 1e-9, ys):
            d.line([self.T(self.xr[0], gy), self.T(self.xr[1], gy)], fill=(255, 255, 255, int(16 * a)), width=2)
            if ticks and abs(gy) > 1e-9 and self.xr[0] <= 0 <= self.xr[1]:
                X, Y = self.T(0, gy)
                d.text((X - 14, Y), _fmt(gy), font=f, fill=(200, 200, 210, int(160 * a)), anchor='rm')
        col = (255, 255, 255, int(110 * a))
        if self.yr[0] <= 0 <= self.yr[1]:
            arrow(d, self.T(self.xr[0], 0), self.T(self.xr[1], 0), col, 4, 16)
            vtext(d, (self.T(self.xr[1], 0)[0] - 6, self.T(self.xr[1], 0)[1] - 22), labels[0], 18, col, anchor='rm')
        if self.xr[0] <= 0 <= self.xr[1]:
            arrow(d, self.T(0, self.yr[0]), self.T(0, self.yr[1]), col, 4, 16)
            vtext(d, (self.T(0, self.yr[1])[0] + 14, self.T(0, self.yr[1])[1] + 10), labels[1], 18, col, anchor='lm')
    def curve(self, d, f, a, b, col, w=7, n=400, clip=True):
        pts, seg = [], []
        for x in np.linspace(a, b, n):
            try:
                y = f(x)
            except (ZeroDivisionError, ValueError):
                y = float('nan')
            ok = y == y and (not clip or self.yr[0] - (self.yr[1] - self.yr[0]) <= y <= self.yr[1] + (self.yr[1] - self.yr[0]))
            if ok:
                seg.append(self.T(x, max(min(y, self.yr[1] + 0.5 * (self.yr[1] - self.yr[0])), self.yr[0] - 0.5 * (self.yr[1] - self.yr[0]))))
            elif len(seg) > 1:
                pts.append(seg); seg = []
            else:
                seg = []
        if len(seg) > 1: pts.append(seg)
        for sgm in pts:
            d.line(sgm, fill=col, width=w, joint='curve')
    def dot(self, d, x, y, col=WHITE, r=11, hollow=False):
        X, Y = self.T(x, y)
        if hollow:
            d.ellipse([X - r, Y - r, X + r, Y + r], fill=(10, 12, 24, 255), outline=col, width=5)
        else:
            d.ellipse([X - r, Y - r, X + r, Y + r], fill=col)
    def line(self, d, x0, y0, x1, y1, col, w=5):
        d.line([self.T(x0, y0), self.T(x1, y1)], fill=col, width=w)
    def dashed(self, d, x0, y0, x1, y1, col, w=3, n=24):
        for i in range(n):
            if i % 2: continue
            t0, t1 = i / n, (i + 1) / n
            d.line([self.T(lerp(x0, x1, t0), lerp(y0, y1, t0)), self.T(lerp(x0, x1, t1), lerp(y0, y1, t1))], fill=col, width=w)
    def area(self, d, f, a, b, col, base=0.0, n=200):
        if b <= a: return
        xs = np.linspace(a, b, n)
        pts = [self.T(a, base)] + [self.T(x, f(x)) for x in xs] + [self.T(b, base)]
        d.polygon(pts, fill=col)
    def text(self, d, x, y, t, size=22, col=WHITE, anchor='mm'):
        d.text(self.T(x, y), t, font=font(size * SS), fill=col, anchor=anchor,
               direction='rtl' if is_rtl(t) else None, stroke_width=5, stroke_fill=(6, 18, 44, 220))

def _nice(span):
    for st in (0.25, 0.5, 1, 2, 5, 10, 20, 50):
        if span / st <= 12: return st
    return 100

def _fmt(v):
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f'{v:g}'

def label(d, bx, text, s, t0=0.0, size=26, col=GOLD, y=None):
    a = ph(s, t0, t0 + 0.6)
    if a <= 0: return
    f = font(size * SS); text = iso(text)
    d.text((bx.w / 2, y if y is not None else 30), text, font=f, fill=alpha(col, a), anchor='mm',
           direction='rtl' if is_rtl(text) else None, stroke_width=6, stroke_fill=(6, 18, 44, int(230 * a)))

def panel(d, bx, lines, s, t0, x=None, y=None, size=24, col=WHITE, gap=1.35, right=True):
    """A small text panel in a corner; lines appear one by one."""
    f = font(size * SS)
    for i, ln in enumerate(lines):
        a = ph(s, t0 + i * 0.7, t0 + i * 0.7 + 0.5)
        if a <= 0: continue
        yy = (y or 30) + i * size * SS * gap
        xx = x if x is not None else (bx.w - 30 if right else 30)
        d.text((xx, yy), iso(ln), font=f, fill=alpha(col if i else GOLD, a), anchor='ra' if right else 'la',
               stroke_width=6, stroke_fill=(6, 18, 44, int(230 * a)))

# ================================================================= Chapter 1

def sc_vertical_line(d, bx, s, acc):
    ax = Ax(bx, (-3.2, 3.2), (-2.3, 2.6)); ax.draw(d)
    f = lambda x: 0.35 * x ** 3 - x + 0.3
    ax.curve(d, f, -3, 3, acc, 7)
    # left half: function passes; right: a circle fails
    x = -2.8 + 5.6 * ph(s, 1.0, 7.0)
    if s < 7.5:
        ax.line(d, x, -2.3, x, 2.6, GOLD, 4)
        ax.dot(d, x, f(x), GREEN, 13)
        label(d, bx, 'קו אנכי פוגש את הגרף בנקודה אחת ✓', s, 1.0, 24, GREEN)
    else:
        a = ph(s, 7.5, 8.3)
        cx, cy, r = 0, 0.2, 1.6
        pts = [ax.T(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 120)]
        d.line(pts + [pts[0]], fill=alpha(PINK, a), width=7)
        xx = -1.4 + 2.8 * ph(s, 8.5, 13)
        ax.line(d, xx, -2.3, xx, 2.6, GOLD, 4)
        dy = math.sqrt(max(0, r * r - (xx - cx) ** 2))
        ax.dot(d, xx, cy + dy, RED, 13); ax.dot(d, xx, cy - dy, RED, 13)
        label(d, bx, 'מעגל: שתי נקודות ✗ – לא פונקציה', s, 8.3, 24, RED)

def sc_inverse(d, bx, s, acc):
    ax = Ax(bx, (-1.5, 6.0), (-1.5, 6.0)); ax.draw(d)
    f = lambda x: 2 ** x * 0.5
    ax.dashed(d, -1.5, -1.5, 6, 6, (255, 255, 255, 120))
    ax.text(d, 5.2, 5.6, 'y = x', 20, DIM)
    ax.curve(d, f, -1.5, 3.5, acc, 7)
    t = ph(s, 2.0, 7.0)
    # reflect: (x,y) -> (x,y)*(1-t) + (y,x)*t
    pts = []
    for x in np.linspace(-1.5, 3.5, 200):
        y = f(x)
        X, Y = lerp(x, y, t), lerp(y, x, t)
        if -1.5 <= X <= 6 and -1.5 <= Y <= 6: pts.append(ax.T(X, Y))
    if t > 0 and len(pts) > 1: d.line(pts, fill=GOLD, width=7)
    if s > 3:
        x0 = 2; y0 = f(x0)
        ax.dot(d, x0, y0, acc); ax.dot(d, lerp(x0, y0, t), lerp(y0, x0, t), GOLD)
        ax.dashed(d, x0, y0, y0, x0, (255, 214, 10, 150))
        ax.text(d, x0 + 0.1, y0 + 0.45, '(a, b)', 20, WHITE)
        if t > 0.9: ax.text(d, y0 + 0.5, x0 - 0.1, '(b, a)', 20, GOLD)
    if s > 8:
        yl = lerp(4.5, 1.0, ph(s, 8.5, 12.5))
        ax.line(d, -1.5, yl, 6, yl, (100, 210, 255, 200), 3)
        label(d, bx, 'מבחן הקו האופקי: חותך פעם אחת ← חח״ע ← יש הפכית', s, 8.5, 21, CYAN)
    else:
        label(d, bx, 'f⁻¹ = שיקוף של f סביב y = x', s, 1.0, 24, GOLD)

def sc_exp_log(d, bx, s, acc):
    ax = Ax(bx, (-3, 5), (-3, 5)); ax.draw(d)
    ax.dashed(d, -3, -3, 5, 5, (255, 255, 255, 90))
    t1 = ph(s, 0.8, 4); t2 = ph(s, 4.5, 8)
    ax.curve(d, math.exp, -3, -3 + 4.6 * t1 if t1 < 1 else 1.6, acc, 7)
    if t2 > 0: ax.curve(d, lambda x: math.log(x) if x > 0 else float('nan'), 0.04, 0.04 + 4.9 * t2, GOLD, 7)
    if s > 2: ax.dot(d, 0, 1, acc); ax.text(d, -0.9, 1.3, '(0,1)', 19, acc)
    if s > 6: ax.dot(d, 1, 0, GOLD); ax.text(d, 1.6, -0.45, '(1,0)', 19, GOLD)
    if s > 9:
        panel(d, bx, ['e^(ln x) = x', 'ln(eˣ) = x', 'ln(ab) = ln a + ln b'], s, 9.0, size=22, y=40, right=False)
    label(d, bx, 'eˣ  ו־  ln x  – פונקציות הפוכות', s, 0.8, 24, WHITE, y=bx.h - 30)

# ================================================================= Chapter 2

def sc_limit_hole(d, bx, s, acc):
    ax = Ax(bx, (-1, 3), (-0.5, 4)); ax.draw(d)
    f = lambda x: x + 1
    ax.curve(d, lambda x: x + 1 if abs(x - 1) > 0.02 else float('nan'), -1, 3, acc, 7)
    ax.dot(d, 1, 2, acc, 12, hollow=True)
    k = ph(s, 2, 10)
    for side in (-1, 1):
        x = 1 + side * 1.6 * (1 - k) ** 1.5 + side * 0.01
        ax.dot(d, x, f(x), GOLD if side < 0 else GREEN, 12)
        ax.dashed(d, x, 0, x, f(x), (255, 255, 255, 90))
        X, Y = ax.T(x, 0)
        vtext(d, (X, Y + 26), f'{x:.2f}', 17, GOLD if side < 0 else GREEN)
    if s > 3:
        yv = f(1 - 1.6 * (1 - k) ** 1.5 - 0.01)
        panel(d, bx, ['f(x) = (x² − 1)/(x − 1)', f'f(x) → {yv:.3f}'], s, 3, size=22, y=36, right=False)
    if s > 10.5: label(d, bx, 'lim f(x) = 2  (x→1)  –  גם בלי ערך בנקודה', s, 10.5, 22, GOLD, y=bx.h - 30)

def sc_one_sided(d, bx, s, acc):
    ax = Ax(bx, (-1, 5), (-0.5, 4.5)); ax.draw(d)
    ax.curve(d, lambda x: 0.5 * x + 0.5 if x < 2 else float('nan'), -1, 1.999, acc, 7)
    ax.curve(d, lambda x: 0.4 * x + 2.2 if x > 2 else float('nan'), 2.001, 5, PURPLE, 7)
    ax.dot(d, 2, 1.5, acc, 11, hollow=True); ax.dot(d, 2, 3.0, PURPLE, 11)
    k = ph(s, 1.5, 8.5)
    xl = 2 - 1.8 * (1 - k) - 0.02; xr = 2 + 1.8 * (1 - k) + 0.02
    ax.dot(d, xl, 0.5 * xl + 0.5, GOLD); ax.dot(d, xr, 0.4 * xr + 2.2, GREEN)
    panel(d, bx, ['גבול משמאל: 1.5', 'גבול מימין: 3.0'], s, 3, size=22, y=36, right=False)
    if s > 9.5: label(d, bx, 'הגבול הדו־צדדי לא קיים, כי 1.5 ≠ 3', s, 9.5, 24, RED, y=bx.h - 30)

def sc_infinite_limit(d, bx, s, acc):
    ax = Ax(bx, (-3, 3), (-0.5, 9)); ax.draw(d)
    f = lambda x: 1 / x ** 2
    ax.curve(d, f, -3, -0.12, acc, 7); ax.curve(d, f, 0.12, 3, acc, 7)
    ax.dashed(d, 0, -0.5, 0, 9, (255, 69, 58, 200), 4)
    k = ph(s, 1.5, 9)
    x = 2.5 * (1 - k) + 0.34
    y = f(x)
    ax.dot(d, x, min(y, 9), GOLD); ax.dot(d, -x, min(y, 9), GOLD)
    panel(d, bx, ['x → 0', f'1/x² = {y:,.1f}'], s, 2, size=22, y=36, right=True)
    if s > 9.5: label(d, bx, 'lim 1/x² = ∞   (x → 0)', s, 9.5, 22, RED, y=bx.h - 86); label(d, bx, 'אסימפטוטה אנכית ב־x = 0', s, 10, 22, RED, y=bx.h - 30)

def sc_factor_cancel(d, bx, s, acc):
    lines = ['lim (x² − 4)/(x − 2)   x→2', 'הצבה ישירה: 0/0 ⚠', '= lim (x − 2)(x + 2)/(x − 2)', '= lim (x + 2)', '= 4']
    for i, ln in enumerate(lines):
        a = ph(s, 0.8 + i * 2.0, 1.6 + i * 2.0)
        if a <= 0: continue
        col = (RED if i == 1 else GOLD if i == 4 else WHITE)
        vtext(d, (bx.w / 2, 60 + i * 150 + (1 - a) * 20), ln, 34 if i < 4 else 48, alpha(col, a))
        if i == 2 and s > 6.5:  # strike the cancelled factors
            a2 = ph(s, 6.5, 7.2)
            X = bx.w / 2; Y = 60 + 2 * 150
            d.line([(X - 170, Y + 22), (X - 170 + 180 * a2, Y - 22)], fill=alpha(RED, a2), width=6)
            d.line([(X + 210, Y + 22), (X + 210 + 170 * a2, Y - 22)], fill=alpha(RED, a2), width=6)

def sc_squeeze(d, bx, s, acc):
    ax = Ax(bx, (-1.2, 1.2), (-1.2, 1.2), step=0.5); ax.draw(d)
    z = ph(s, 6, 11)  # zoom
    xr = lerp(1.2, 0.3, z)
    ax.xr = (-xr, xr); ax.yr = (-xr, xr)
    g = lambda x: x * x
    ax.curve(d, g, -xr, xr, GREEN, 6); ax.curve(d, lambda x: -x * x, -xr, xr, RED, 6)
    a = ph(s, 2, 3)
    if a > 0:
        ax.curve(d, lambda x: x * x * math.sin(1 / x) if x != 0 else 0, -xr, xr, alpha(acc, a), 5, n=1500)
    ax.dot(d, 0, 0, GOLD, 13)
    panel(d, bx, ['−x² ≤ x²·sin(1/x) ≤ x²', 'שני הצדדים שואפים ל־0', 'ולכן גם האמצעית שואפת ל־0'], s, 3.5, size=21, y=30, right=True)

def sc_continuity(d, bx, s, acc):
    ax = Ax(bx, (0, 9.5), (-0.5, 5), step=1); ax.draw(d, ticks=False)
    # three panels: removable, jump, infinite
    ax.curve(d, lambda x: 1 + 0.4 * (x - 1.5) ** 2 if abs(x - 1.5) > 0.03 else float('nan'), 0.2, 2.8, acc, 6)
    ax.dot(d, 1.5, 1, acc, 10, hollow=True); ax.dot(d, 1.5, 2.6, acc, 10)
    ax.curve(d, lambda x: 1.2 if x < 4.75 else float('nan'), 3.5, 4.74, PURPLE, 6)
    ax.curve(d, lambda x: 3 if x > 4.75 else float('nan'), 4.76, 6.0, PURPLE, 6)
    ax.dot(d, 4.75, 1.2, PURPLE, 10); ax.dot(d, 4.75, 3, PURPLE, 10, hollow=True)
    ax.curve(d, lambda x: 0.6 / abs(x - 8) if abs(x - 8) > 0.12 else float('nan'), 6.9, 9.2, PINK, 6)
    for i, (x, t) in enumerate([(1.5, 'סליקה'), (4.75, 'קפיצה'), (8, 'אינסופית')]):
        if s > 1 + i * 1.2: ax.text(d, x, 4.7, t, 21, GOLD)
    panel(d, bx, ['רציפות ב־a:', '1. f(a) מוגדרת', '2. lim f(x) קיים', '3. lim f(x) = f(a)'], s, 5.0, size=21, y=bx.h - 300, right=False)

def sc_ivt(d, bx, s, acc):
    ax = Ax(bx, (-0.3, 4.3), (-2.5, 3.5)); ax.draw(d)
    f = lambda x: 0.5 * x ** 3 - 2.2 * x ** 2 + 2.2 * x - 1.8
    a_, b_ = 0.0, 4.0
    t = ph(s, 0.8, 4)
    ax.curve(d, f, a_, a_ + (b_ - a_) * t, acc, 7)
    ax.dot(d, a_, f(a_), WHITE); ax.dot(d, b_, f(b_), WHITE) if t > 0.98 else None
    if s > 4.5:
        k = lerp(f(a_) + 0.2, f(b_) - 0.2, 0.5 - 0.5 * math.cos((s - 4.5) * 0.9))
        ax.line(d, -0.3, k, 4.3, k, GOLD, 4)
        ax.text(d, 4.0, k + 0.3, 'k', 22, GOLD)
        xs = np.linspace(a_, b_, 2000); ys = [f(x) - k for x in xs]
        for i in range(len(xs) - 1):
            if ys[i] == 0 or ys[i] * ys[i + 1] < 0:
                ax.dot(d, xs[i], k, GREEN, 13)
    label(d, bx, 'אם f רציפה בקטע הסגור [a,b]', s, 1.0, 21, WHITE, y=24); label(d, bx, 'היא מקבלת כל ערך k שבין f(a) ל־f(b)', s, 1.5, 21, WHITE, y=76)

def sc_epsilon_delta(d, bx, s, acc):
    ax = Ax(bx, (0, 4), (0, 5)); ax.draw(d)
    f = lambda x: 0.8 * x + 1.0
    a, L = 2.0, 2.6
    ax.curve(d, f, 0, 4, acc, 7)
    eps = lerp(1.2, 0.25, ph(s, 3, 12))
    dl = eps / 0.8
    if s > 1.5:
        p0, p1 = ax.T(0, L + eps), ax.T(4, L - eps)
        d.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=(255, 214, 10, 40))
        ax.line(d, 0, L + eps, 4, L + eps, GOLD, 3); ax.line(d, 0, L - eps, 4, L - eps, GOLD, 3)
        ax.text(d, 3.75, L + eps + 0.25, 'L+ε', 19, GOLD); ax.text(d, 3.75, L - eps - 0.25, 'L−ε', 19, GOLD)
    if s > 2.5:
        q0, q1 = ax.T(a - dl, 5), ax.T(a + dl, 0)
        d.rectangle([q0[0], q0[1], q1[0], q1[1]], fill=(48, 209, 88, 40))
        ax.line(d, a - dl, 0, a - dl, 5, GREEN, 3); ax.line(d, a + dl, 0, a + dl, 5, GREEN, 3)
        ax.text(d, a - dl, 4.75, 'a−δ', 19, GREEN); ax.text(d, a + dl, 4.75, 'a+δ', 19, GREEN)
        ax.curve(d, f, a - dl, a + dl, WHITE, 9)
    ax.dot(d, a, L, WHITE)
    panel(d, bx, [f'ε = {eps:.2f}', f'δ = {dl:.2f}'], s, 3, size=22, y=36, right=False)
    if s > 12.3: label(d, bx, 'לכל ε > 0 קיים δ > 0', s, 12.3, 26, GOLD, y=bx.h - 30)

# ================================================================= Chapter 3

def sc_secant_tangent(d, bx, s, acc):
    ax = Ax(bx, (-0.5, 4), (-0.5, 5)); ax.draw(d)
    f = lambda x: 0.3 * x * x + 0.4
    a = 1.2
    ax.curve(d, f, -0.5, 4, acc, 7)
    h = lerp(2.4, 0.01, ph(s, 1.5, 10.5))
    m = (f(a + h) - f(a)) / h
    L = 2.2
    col = GOLD if h > 0.05 else GREEN
    ax.line(d, a - L, f(a) - m * L, a + h + L, f(a) + m * (h + L), col, 5)
    ax.dot(d, a, f(a), WHITE); ax.dot(d, a + h, f(a + h), col)
    ax.dashed(d, a + h, 0, a + h, f(a + h), (255, 255, 255, 80))
    panel(d, bx, ['[f(a+h) − f(a)] / h', f'h = {h:.2f}', f'שיפוע = {m:.3f}'], s, 1.5, size=22, y=36, right=False)
    if s > 11: label(d, bx, "f'(a) = 0.72", s, 11, 24, GREEN, y=bx.h - 86); label(d, bx, 'כש־h שואף ל־0 המיתר הופך למשיק', s, 11.3, 22, GREEN, y=bx.h - 30)

def sc_abs_corner(d, bx, s, acc):
    ax = Ax(bx, (-2.5, 2.5), (-0.5, 2.8)); ax.draw(d)
    ax.curve(d, abs, -2.5, 2.5, acc, 7)
    h = lerp(2.0, 0.05, ph(s, 1.5, 7.5))
    ax.line(d, 0, 0, -h * 1.3, h * 1.3, PINK, 5); ax.dot(d, -h, h, PINK)
    ax.line(d, 0, 0, h * 1.3, h * 1.3, GREEN, 5); ax.dot(d, h, h, GREEN)
    ax.dot(d, 0, 0, WHITE)
    panel(d, bx, ['שיפוע משמאל: \u200e−1', 'שיפוע מימין: \u200e+1'], s, 2, size=22, y=36, right=True)
    if s > 8.5:
        label(d, bx, '|x| רציפה ב־0 אבל לא גזירה שם', s, 8.5, 22, GOLD, y=bx.h - 86)
        label(d, bx, 'גזירה ← רציפה (ולא להפך)', s, 10.5, 22, WHITE, y=bx.h - 28)

def sc_power_rule(d, bx, s, acc):
    ax = Ax(bx, (-2.2, 2.2), (-3.2, 4.2)); ax.draw(d)
    f = lambda x: x ** 3 / 3 * 1.0
    fp = lambda x: x * x
    ax.curve(d, lambda x: x ** 3 - x, -2.2, 2.2, acc, 6)
    # trace derivative
    x0 = -2 + 4 * ph(s, 2, 10)
    g = lambda x: x ** 3 - x; gp = lambda x: 3 * x * x - 1
    if s > 2:
        ax.curve(d, gp, -2, x0, GOLD, 6)
        ax.line(d, x0 - 0.6, g(x0) - 0.6 * gp(x0), x0 + 0.6, g(x0) + 0.6 * gp(x0), WHITE, 4)
        ax.dot(d, x0, g(x0), WHITE); ax.dot(d, x0, gp(x0), GOLD)
        ax.dashed(d, x0, g(x0), x0, gp(x0), (255, 214, 10, 120))
    panel(d, bx, ['f(x) = x³ − x', "f'(x) = 3x² − 1", '(xⁿ)\' = n·xⁿ⁻¹'], s, 1.0, size=22, y=36, right=False)

def sc_product_rule(d, bx, s, acc):
    # rectangle u × v growing by du, dv
    W, H = bx.w, bx.h
    u = lerp(300, 360, ph(s, 4, 8)); v = lerp(200, 240, ph(s, 4, 8))
    x0, y0 = 160, H - 60
    u0, v0 = 300, 200
    d.rectangle([x0, y0 - v0 * 1.4, x0 + u0 * 1.4, y0], fill=hex2rgb('#0a84ff') + (180,))
    vtext(d, (x0 + u0 * 0.7, y0 - v0 * 0.7), 'u·v', 34, WHITE)
    if s > 4:
        d.rectangle([x0 + u0 * 1.4, y0 - v0 * 1.4, x0 + u * 1.4, y0], fill=(255, 214, 10, 200))
        d.rectangle([x0, y0 - v * 1.4, x0 + u0 * 1.4, y0 - v0 * 1.4], fill=(48, 209, 88, 200))
        d.rectangle([x0 + u0 * 1.4, y0 - v * 1.4, x0 + u * 1.4, y0 - v0 * 1.4], fill=(255, 69, 58, 220))
    if s > 8.3:
        vtext(d, (x0 + u0 * 1.4 + (u - u0) * 0.7, y0 - v0 * 0.7), 'v·du', 22, (0, 0, 0, 255))
        vtext(d, (x0 + u0 * 0.7, y0 - v0 * 1.4 - (v - v0) * 0.7), 'u·dv', 22, (0, 0, 0, 255))
    vtext(d, (x0 + u0 * 0.7, y0 + 30), 'u', 26, WHITE); vtext(d, (x0 - 30, y0 - v0 * 0.7), 'v', 26, WHITE)
    panel(d, bx, ['השטח גדל ב־', 'u·dv + v·du', 'הריבוע הקטן du·dv זניח', "(uv)' = u'v + uv'"], s, 9, size=24, y=40, right=True)

def sc_velocity(d, bx, s, acc):
    ax = Ax(bx, (0, 6), (-1, 9), pad=(70, 40, 120, 70)); ax.draw(d, labels=('t', 's'))
    pos = lambda t: 8 * (1 - math.cos(t * math.pi / 6)) / 2
    vel = lambda t: 8 * math.pi / 12 * math.sin(t * math.pi / 6)
    t = 6 * ph(s, 1, 12)
    ax.curve(d, pos, 0, t, acc, 7)
    ax.dot(d, t, pos(t), WHITE)
    m = vel(t)
    ax.line(d, t - 0.8, pos(t) - 0.8 * m, t + 0.8, pos(t) + 0.8 * m, GOLD, 4)
    # particle on a track at the top
    tx0, tx1 = 80, bx.w - 80
    d.line([(tx0, 50), (tx1, 50)], fill=DIM, width=4)
    px = lerp(tx0, tx1, pos(t) / 8)
    d.ellipse([px - 18, 32, px + 18, 68], fill=acc)
    arrow(d, (px, 90), (px + m * 45, 90), GOLD, 5, 14) if abs(m) > 0.05 else None
    panel(d, bx, [f"v = s'(t) = {m:.2f}"], s, 1.5, size=22, y=110, right=False)

def sc_trig_derivative(d, bx, s, acc):
    ax = Ax(bx, (0, 2 * math.pi), (-1.5, 1.5), step=1); ax.draw(d)
    ax.curve(d, math.sin, 0, 2 * math.pi, acc, 6)
    x0 = 2 * math.pi * ph(s, 1.5, 12)
    ax.curve(d, math.cos, 0, x0, GOLD, 6)
    m = math.cos(x0)
    ax.line(d, x0 - 0.6, math.sin(x0) - 0.6 * m, x0 + 0.6, math.sin(x0) + 0.6 * m, WHITE, 4)
    ax.dot(d, x0, math.sin(x0), WHITE); ax.dot(d, x0, m, GOLD)
    panel(d, bx, ['sin x', "(sin x)' = cos x"], s, 1, size=22, y=36, right=True)

def sc_chain(d, bx, s, acc):
    # two gears: x -> u -> y ; rates multiply
    W, H = bx.w, bx.h
    def gear(cx, cy, r, ang, col, teeth):
        pts = []
        for i in range(teeth * 2):
            a = ang + i * math.pi / teeth
            rr = r if i % 2 == 0 else r * 0.82
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=col)
        d.ellipse([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25], fill=(10, 12, 24, 255))
    t = max(0, s - 1)
    gear(W * 0.78, H * 0.45, 150, t * 0.6, hex2rgb('#0a84ff') + (255,), 10)
    gear(W * 0.47, H * 0.45, 100, -t * 0.9, (255, 214, 10, 255), 7)
    gear(W * 0.24, H * 0.45, 70, t * 1.8, (48, 209, 88, 255), 5)
    vtext(d, (W * 0.78, H * 0.88), 'x', 30); vtext(d, (W * 0.47, H * 0.88), 'u = g(x)', 26, GOLD); vtext(d, (W * 0.24, H * 0.88), 'y = f(u)', 26, GREEN)
    panel(d, bx, ['dy/dx = dy/du · du/dx', "(f(g(x)))' = f'(g(x))·g'(x)"], s, 3, size=23, y=20, right=True)

def sc_implicit(d, bx, s, acc):
    ax = Ax(bx, (-3.2, 3.2), (-2.6, 2.6), step=1); ax.draw(d)
    r = 2
    pts = [ax.T(r * math.cos(t), r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 200)]
    d.line(pts + [pts[0]], fill=acc, width=7)
    th = 0.3 + 2 * math.pi * ph(s, 1.5, 12)
    x, y = r * math.cos(th), r * math.sin(th)
    if abs(y) > 0.15:
        m = -x / y
        L = 1.2 / math.sqrt(1 + m * m)
        ax.line(d, x - L, y - m * L, x + L, y + m * L, GOLD, 5)
    else:
        ax.line(d, x, y - 1.2, x, y + 1.2, GOLD, 5)
    ax.dot(d, x, y, WHITE)
    ax.line(d, 0, 0, x, y, (255, 255, 255, 90), 3)
    mm = '∞' if abs(y) < 0.15 else f'{-x / y:.2f}'
    panel(d, bx, ['x² + y² = 4', '2x + 2y·y\' = 0', f"y' = −x/y = {mm}"], s, 1, size=21, y=30, right=False)

def sc_exp_slope(d, bx, s, acc):
    ax = Ax(bx, (-2.5, 2.2), (-0.5, 8)); ax.draw(d)
    ax.curve(d, math.exp, -2.5, 2.1, acc, 7)
    x0 = -2 + 3.8 * ph(s, 1.5, 11)
    y0 = math.exp(x0)
    ax.line(d, x0 - 1, y0 - y0, x0 + 0.6, y0 + 0.6 * y0, GOLD, 5)
    ax.dot(d, x0, y0, WHITE)
    ax.line(d, x0, 0, x0, y0, (48, 209, 88, 220), 6)
    panel(d, bx, [f'גובה = eˣ = {y0:.2f}', f'שיפוע = {y0:.2f}'], s, 2, size=22, y=36, right=False)
    if s > 11.5: label(d, bx, "(eˣ)' = eˣ   ·   (ln x)' = 1/x", s, 11.5, 24, GOLD, y=bx.h - 30)

# ================================================================= Chapter 4

def sc_ladder(d, bx, s, acc):
    W, H = bx.w, bx.h
    L = 10
    x = lerp(4, 8, ph(s, 1, 11))
    y = math.sqrt(L * L - x * x)
    sc = 38
    ox, oy = W * 0.62, H - 60
    d.line([(ox, oy), (ox, 40)], fill=(200, 200, 210, 255), width=10)  # wall
    d.line([(60, oy), (ox + 40, oy)], fill=(200, 200, 210, 255), width=8)  # floor
    top = (ox, oy - y * sc); bot = (ox - x * sc, oy)
    d.line([top, bot], fill=hex2rgb('#ff9f0a') + (255,), width=12)
    d.ellipse([bot[0] - 14, bot[1] - 14, bot[0] + 14, bot[1] + 14], fill=GOLD)
    d.ellipse([top[0] - 14, top[1] - 14, top[0] + 14, top[1] + 14], fill=GREEN)
    arrow(d, (bot[0], bot[1] + 30), (bot[0] - 70, bot[1] + 30), GOLD, 5, 16)
    dxdt = 1.0; dydt = -x / y * dxdt
    panel(d, bx, ['x² + y² = 10²', "2x·x' + 2y·y' = 0", f'x = {x:.1f}   y = {y:.1f}', f"y' = −(x/y)·x' = {dydt:.2f}"], s, 1.5, size=21, y=30, right=True)

def sc_linear_approx(d, bx, s, acc):
    z = ph(s, 5, 11)
    span = lerp(4.5, 0.25, z)
    a = 4.0
    ax = Ax(bx, (a - span, a + span), (2 - span * 0.45, 2 + span * 0.45)); ax.draw(d, ticks=z < 0.3)
    f = math.sqrt
    ax.curve(d, lambda x: f(x) if x >= 0 else float('nan'), max(0, a - span), a + span, acc, 7)
    ax.line(d, a - span, 2 + (-span) / 4, a + span, 2 + span / 4, GOLD, 4)
    ax.dot(d, a, 2, WHITE)
    panel(d, bx, ['L(x) = f(a) + f\'(a)(x − a)', '√x ≈ 2 + (x − 4)/4', '√4.1 ≈ 2.025', 'ערך אמיתי: 2.0248'], s, 1, size=21, y=30, right=False)
    if s > 11: label(d, bx, 'בזום מספיק – הגרף נראה כמו המשיק', s, 11, 22, GOLD, y=bx.h - 30)

def sc_critical_points(d, bx, s, acc):
    ax = Ax(bx, (-2.6, 2.6), (-3, 3)); ax.draw(d)
    f = lambda x: x ** 3 - 3 * x
    ax.curve(d, f, -2.3, 2.3, acc, 7)
    x0 = -2.2 + 4.4 * ph(s, 1, 9)
    m = 3 * x0 * x0 - 3
    ax.line(d, x0 - 0.5, f(x0) - 0.5 * m, x0 + 0.5, f(x0) + 0.5 * m, GOLD if abs(m) > 0.25 else GREEN, 5)
    ax.dot(d, x0, f(x0), WHITE)
    for xc in (-1, 1):
        if x0 > xc - 0.05 or s > 9:
            ax.dot(d, xc, f(xc), GREEN, 14)
            ax.text(d, xc + (-0.6 if xc < 0 else 0.6), f(xc), 'מקס׳' if xc < 0 else 'מינ׳', 21, GREEN)
    panel(d, bx, ["f'(x) = 3x² − 3", "f'(x) = 0 ⇒ x = ±1"], s, 2, size=21, y=30, right=False)
    if s > 10: label(d, bx, "פרמה: בקיצון מקומי f'(c) = 0 או לא קיימת", s, 10, 21, GOLD, y=bx.h - 30)

def sc_extreme_value(d, bx, s, acc):
    ax = Ax(bx, (-0.3, 4.3), (-1.5, 4)); ax.draw(d)
    f = lambda x: 0.6 * x ** 3 - 3.3 * x ** 2 + 4.6 * x + 0.2
    a, b = 0.2, 4.0
    ax.curve(d, f, a, a + (b - a) * ph(s, 0.8, 3.5), acc, 7)
    if s > 3.5:
        ax.dot(d, a, f(a), WHITE); ax.dot(d, b, f(b), WHITE)
    cands = [a, b]
    disc = 6.6 ** 2 - 4 * 1.8 * 4.6
    for r in ((6.6 - math.sqrt(disc)) / 3.6, (6.6 + math.sqrt(disc)) / 3.6):
        cands.append(r)
    if s > 5:
        for i, c in enumerate(cands):
            if s > 5 + i * 0.8:
                ax.dot(d, c, f(c), GOLD, 12); ax.dashed(d, c, 0, c, f(c), (255, 214, 10, 100))
    if s > 9:
        vals = [f(c) for c in cands]
        cm, cn = cands[vals.index(max(vals))], cands[vals.index(min(vals))]
        ax.dot(d, cm, f(cm), GREEN, 16); ax.text(d, cm, f(cm) + 0.45, 'מקסימום', 21, GREEN)
        ax.dot(d, cn, f(cn), RED, 16); ax.text(d, cn, f(cn) - 0.45, 'מינימום', 21, RED)
    panel(d, bx, ['מועמדים: נקודות קריטיות', '+ קצות הקטע'], s, 5, size=21, y=30, right=True)

def sc_rolle(d, bx, s, acc):
    ax = Ax(bx, (-0.3, 4.3), (-0.5, 3.5)); ax.draw(d)
    f = lambda x: 1 + 1.8 * math.sin(x * math.pi / 4) * (1 - 0.15 * x)
    a, b = 0.0, 4.0
    ax.curve(d, f, a, b, acc, 7)
    ax.dot(d, a, f(a), WHITE); ax.dot(d, b, f(b), WHITE)
    ax.dashed(d, a, f(a), b, f(b), (255, 255, 255, 120))
    xs = np.linspace(a, b, 2000)
    fp = [(f(x + 1e-4) - f(x - 1e-4)) / 2e-4 for x in xs]
    c = xs[int(np.argmin(np.abs(fp)))]
    x0 = lerp(0.3, c, ph(s, 2, 8)) if s < 8 else c
    m = (f(x0 + 1e-4) - f(x0 - 1e-4)) / 2e-4
    ax.line(d, x0 - 0.9, f(x0) - 0.9 * m, x0 + 0.9, f(x0) + 0.9 * m, GREEN if s >= 8 else GOLD, 5)
    ax.dot(d, x0, f(x0), GOLD)
    panel(d, bx, ['f(a) = f(b)', "ולכן קיים c עם f'(c) = 0"], s, 1.5, size=22, y=30, right=True)

def sc_mvt(d, bx, s, acc):
    ax = Ax(bx, (-0.3, 4.3), (-0.5, 4.5)); ax.draw(d)
    f = lambda x: 0.15 * x ** 3 - 0.6 * x ** 2 + 1.2 * x + 0.6
    a, b = 0.2, 4.0
    ax.curve(d, f, a - 0.4, b + 0.2, acc, 7)
    msec = (f(b) - f(a)) / (b - a)
    if s > 1.5:
        ax.line(d, a, f(a), b, f(b), PURPLE, 5); ax.dot(d, a, f(a), WHITE); ax.dot(d, b, f(b), WHITE)
    fp = lambda x: 0.45 * x * x - 1.2 * x + 1.2
    # solve fp = msec
    A, B, C = 0.45, -1.2, 1.2 - msec
    roots = [(-B + sg * math.sqrt(B * B - 4 * A * C)) / (2 * A) for sg in (-1, 1)]
    c = [r for r in roots if a < r < b][0]
    x0 = lerp(a + 0.1, c, ph(s, 3, 10))
    m = fp(x0)
    ok = abs(m - msec) < 0.03
    ax.line(d, x0 - 1, f(x0) - m, x0 + 1, f(x0) + m, GREEN if ok else GOLD, 5)
    ax.dot(d, x0, f(x0), GOLD)
    panel(d, bx, [f'שיפוע המיתר = {msec:.2f}', f'שיפוע המשיק = {m:.2f}'], s, 2, size=21, y=30, right=False)
    if s > 10.5: label(d, bx, "f'(c) = [f(b) − f(a)] / (b − a)", s, 10.5, 24, GREEN, y=bx.h - 30)

def sc_monotonic(d, bx, s, acc):
    ax = Ax(bx, (-2.6, 2.6), (-3, 3), pad=(70, 40, 50, 130)); ax.draw(d)
    f = lambda x: x ** 3 - 3 * x
    x0 = -2.3 + 4.6 * ph(s, 1, 10)
    xs = np.linspace(-2.3, x0, 300)
    for i in range(len(xs) - 1):
        up = 3 * xs[i] ** 2 - 3 > 0
        d.line([ax.T(xs[i], f(xs[i])), ax.T(xs[i + 1], f(xs[i + 1]))], fill=GREEN if up else RED, width=8)
    ax.dot(d, x0, f(x0), WHITE)
    # sign chart
    y = bx.h - 45
    for (xa, xb, sg) in ((-2.6, -1, '+'), (-1, 1, '−'), (1, 2.6, '+')):
        if x0 > xa:
            X0, X1 = ax.T(xa, 0)[0], ax.T(min(xb, x0), 0)[0]
            if X1 - X0 > 12: d.rounded_rectangle([X0 + 4, y - 22, X1 - 4, y + 22], radius=10, fill=(GREEN if sg == '+' else RED)[:3] + (90,))
            if x0 > (xa + xb) / 2: vtext(d, ((ax.T(xa, 0)[0] + ax.T(xb, 0)[0]) / 2, y), f"f' {sg}", 22)
    panel(d, bx, ["עולה כאשר f' > 0", "יורדת כאשר f' < 0"], s, 1.5, size=21, y=30, right=False)

def sc_concavity(d, bx, s, acc):
    ax = Ax(bx, (-2.4, 2.4), (-3, 3)); ax.draw(d)
    f = lambda x: x ** 3 - 3 * x
    fp = lambda x: 3 * x * x - 3
    ax.curve(d, f, -2.2, 0, RED, 7); ax.curve(d, f, 0, 2.2, GREEN, 7)
    x0 = -2 + 4 * ph(s, 1.5, 11)
    m = fp(x0)
    ax.line(d, x0 - 0.8, f(x0) - 0.8 * m, x0 + 0.8, f(x0) + 0.8 * m, GOLD, 4)
    ax.dot(d, x0, f(x0), WHITE)
    if s > 6: ax.dot(d, 0, 0, PURPLE, 15); ax.text(d, 0.95, 0.45, 'פיתול', 21, PURPLE)
    panel(d, bx, ["f'' < 0: קעורה (∩) – המשיק מעל", "f'' > 0: קמורה (∪) – המשיק מתחת"], s, 2, size=20, y=30, right=True)

def sc_horizontal_asymptote(d, bx, s, acc):
    span = lerp(6, 40, ph(s, 5, 12))
    ax = Ax(bx, (0, span), (-0.5, 3.5)); ax.draw(d, ticks=False)
    f = lambda x: (2 * x * x + 3) / (x * x + 1)
    ax.curve(d, f, 0, span, acc, 7, n=600)
    ax.dashed(d, 0, 2, span, 2, (255, 214, 10, 200), 4)
    ax.text(d, span * 0.9, 2.35, 'y = 2', 22, GOLD)
    panel(d, bx, ['(2x² + 3)/(x² + 1)', 'x → ∞  ⇒  → 2/1 = 2'], s, 1.5, size=22, y=bx.h - 140, right=True)

def sc_optimization(d, bx, s, acc):
    # rectangle with fixed perimeter 20 -> max area at square
    W, H = bx.w, bx.h
    x = 5 + 4 * math.sin((s - 1) * 0.7) if s > 1 else 1
    x = max(1, min(9, x))
    y = 10 - x
    sc = 26
    d.rectangle([60, H - 60 - y * sc, 60 + x * sc, H - 60], fill=hex2rgb('#0a84ff') + (170,), outline=WHITE, width=4)
    vtext(d, (60 + x * sc / 2, H - 30), f'x = {x:.1f}', 22); vtext(d, (60 + x * sc + 70, H - 60 - y * sc / 2), f'{y:.1f}', 22)
    # area graph
    ax = Ax(bx, (0, 10), (0, 30), pad=(330, 30, 50, 70)); ax.draw(d, ticks=False, labels=('x', 'A'))
    ax.curve(d, lambda t: t * (10 - t), 0, 10, GOLD, 6)
    ax.dot(d, x, x * y, WHITE)
    ax.dot(d, 5, 25, GREEN, 9)
    panel(d, bx, ['היקף 20:  A = x(10 − x)', "A' = 10 − 2x = 0 ⇒ x = 5", 'ריבוע!'], s, 6, size=21, y=20, right=True)

def sc_lhopital(d, bx, s, acc):
    z = ph(s, 3, 9)
    span = lerp(3, 0.4, z)
    ax = Ax(bx, (-span, span), (-span * 0.9, span * 0.9)); ax.draw(d, ticks=False)
    f = math.sin; g = lambda x: math.exp(x) - 1
    ax.curve(d, f, -span, span, acc, 6); ax.curve(d, g, -span, span, GOLD, 6)
    ax.dot(d, 0, 0, WHITE)
    panel(d, bx, ['sin x / (eˣ − 1)  →  0/0', 'ליד 0 שניהם כמעט ישרים:', "→ f'(0)/g'(0) = cos 0 / e⁰ = 1"], s, 1, size=21, y=30, right=False)
    if s > 10: label(d, bx, "lim f/g = lim f'/g'", s, 10, 24, GREEN, y=bx.h - 86); label(d, bx, 'כשמתקבל 0/0 או ∞/∞', s, 10.3, 22, GREEN, y=bx.h - 30)

def sc_antiderivative(d, bx, s, acc):
    ax = Ax(bx, (-2.4, 2.4), (-2.5, 4.5)); ax.draw(d)
    F = lambda x: x * x / 2 - 1
    for i, C in enumerate([-1, 0, 1, 2, 3]):
        a = ph(s, 1 + i * 0.8, 1.6 + i * 0.8)
        if a > 0: ax.curve(d, lambda x, C=C: F(x) + C, -2.4, 2.4, alpha(acc if C != 1 else GOLD, a), 5)
    x0 = -1.8 + 3.6 * ph(s, 6, 12)
    for C in [-1, 0, 1, 2, 3]:
        if s > 6:
            m = x0
            y0 = F(x0) + C
            ax.line(d, x0 - 0.4, y0 - 0.4 * m, x0 + 0.4, y0 + 0.4 * m, WHITE, 3)
    panel(d, bx, ['∫ x dx = x²/2 + C', 'כל הגרפים – אותו שיפוע בכל x'], s, 2, size=21, y=30, right=False)

# ================================================================= Chapter 5

def sc_riemann(d, bx, s, acc):
    ax = Ax(bx, (-0.2, 3.3), (-0.3, 4.5)); ax.draw(d)
    f = lambda x: 0.4 * x * x + 0.5
    a, b = 0.0, 3.0
    exact = 0.4 * 9 + 1.5
    stages = [(1, 4), (4, 8), (7, 16), (10, 64)]
    n = 4
    for t0, nn in stages:
        if s >= t0: n = nn
    dx = (b - a) / n
    tot = 0
    for i in range(n):
        x = a + i * dx
        h = f(x + dx / 2)
        tot += h * dx
        p0, p1 = ax.T(x, h), ax.T(x + dx, 0)
        d.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=hex2rgb('#0a84ff') + (120,), outline=(255, 255, 255, 120), width=2 if n < 40 else 1)
    ax.curve(d, f, -0.2, 3.3, GOLD, 6)
    panel(d, bx, [f'n = {n}', f'Σ f(xᵢ*)Δx = {tot:.4f}', f'∫ = {exact:.4f}'], s, 1, size=22, y=30, right=False)

def sc_signed_area(d, bx, s, acc):
    ax = Ax(bx, (-0.3, 6.6), (-1.5, 1.5), step=1); ax.draw(d)
    f = math.sin
    x1 = 2 * math.pi * ph(s, 1, 9)
    ax.area(d, f, 0, min(x1, math.pi), (48, 209, 88, 140))
    if x1 > math.pi: ax.area(d, f, math.pi, x1, (255, 69, 58, 140))
    ax.curve(d, f, 0, 2 * math.pi, acc, 6)
    pos = 1 - math.cos(min(x1, math.pi)); neg = (math.cos(math.pi) - math.cos(x1)) if x1 > math.pi else 0
    panel(d, bx, [f'מעל הציר: \u200e+{pos:.2f}', f'מתחת לציר: \u200e{neg:.2f}', f'∫ = {pos + neg:.2f}'], s, 1, size=22, y=30, right=True)

def sc_ftc1(d, bx, s, acc):
    ax = Ax(bx, (-0.2, 4.2), (-0.3, 3.5), pad=(70, 40, 50, 70)); ax.draw(d, labels=('t', 'y'))
    f = lambda t: 1 + 0.8 * math.sin(t * 1.3)
    x = 0.3 + 3.6 * ph(s, 1, 11)
    ax.area(d, f, 0, x, (10, 132, 255, 140))
    ax.curve(d, f, -0.2, 4.2, acc, 6)
    ax.line(d, x, 0, x, f(x), GOLD, 6)
    # the next thin strip
    p0, p1 = ax.T(x, f(x)), ax.T(x + 0.15, 0)
    d.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=(255, 214, 10, 200))
    Fx = x - 0.8 / 1.3 * (math.cos(1.3 * x) - 1)
    panel(d, bx, [f'F(x) = ∫₀ˣ f(t)dt = {Fx:.2f}', 'רצועה חדשה ≈ f(x)·Δx', "⇒ F'(x) = f(x)"], s, 2, size=21, y=30, right=True)

def sc_ftc2(d, bx, s, acc):
    lines = ['∫ₐᵇ f(x)dx = F(b) − F(a)', '∫₁³ x² dx', '= [x³/3]₁³', '= 27/3 − 1/3', '= 26/3 ≈ 8.67']
    for i, ln in enumerate(lines):
        a = ph(s, 0.8 + i * 2.0, 1.6 + i * 2.0)
        if a > 0:
            vtext(d, (bx.w / 2, 70 + i * 150 + (1 - a) * 20), ln, 38 if i else 34, alpha(GOLD if i in (0, 4) else WHITE, a))

def sc_mvt_integral(d, bx, s, acc):
    ax = Ax(bx, (-0.2, 4.2), (-0.3, 4)); ax.draw(d)
    f = lambda x: 1 + 0.25 * x * x
    a, b = 0.0, 4.0
    avg = (4 + 0.25 * 64 / 3) / 4
    ax.area(d, f, a, b, (10, 132, 255, 120))
    ax.curve(d, f, a, b, acc, 6)
    t = ph(s, 3, 8)
    if t > 0:
        hh = lerp(0, avg, t)
        p0, p1 = ax.T(a, hh), ax.T(b, 0)
        d.rectangle([p0[0], p0[1], p1[0], p1[1]], outline=GOLD, width=6, fill=(255, 214, 10, 50))
    if s > 8.5:
        c = math.sqrt((avg - 1) / 0.25)
        ax.dot(d, c, avg, GREEN, 14); ax.text(d, c, avg + 0.4, 'f(c)', 22, GREEN)
    panel(d, bx, ['f(c) = 1/(b−a) · ∫ₐᵇ f(x)dx', f'ממוצע = {avg:.2f}'], s, 9, size=21, y=30, right=False)

def sc_substitution(d, bx, s, acc):
    lines = ['∫ 2x·cos(x²) dx', 'u = x²   ⇒   du = 2x dx', '= ∫ cos(u) du', '= sin(u) + C', '= sin(x²) + C']
    for i, ln in enumerate(lines):
        a = ph(s, 0.8 + i * 2.0, 1.6 + i * 2.0)
        if a > 0:
            vtext(d, (bx.w / 2, 70 + i * 150 + (1 - a) * 20), ln, 36, alpha(GOLD if i in (1, 4) else WHITE, a))

# ================================================================= Chapter 6

def sc_area_between(d, bx, s, acc):
    ax = Ax(bx, (-0.3, 2.3), (-0.3, 4.6)); ax.draw(d)
    top = lambda x: x + 2; bot = lambda x: x * x
    x1 = -1 if False else 0
    xs = 2 * ph(s, 1.5, 9)
    pts = [ax.T(x, top(x)) for x in np.linspace(0, xs, 100)] + [ax.T(x, bot(x)) for x in np.linspace(xs, 0, 100)]
    if xs > 0.01: d.polygon(pts, fill=(10, 132, 255, 120))
    ax.curve(d, top, -0.3, 2.3, GOLD, 6); ax.curve(d, bot, -0.3, 2.3, acc, 6)
    ax.line(d, xs, bot(xs), xs, top(xs), WHITE, 5)
    area = (xs ** 2 / 2 + 2 * xs) - xs ** 3 / 3
    panel(d, bx, ['∫ [f(x) − g(x)] dx', f'= {area:.2f}'], s, 2, size=22, y=30, right=False)
    ax.text(d, 2.05, 4.35, 'f = x + 2', 19, GOLD); ax.text(d, 2.0, 3.4, 'g = x²', 19, acc)

def sc_disk(d, bx, s, acc):
    W, H = bx.w, bx.h
    ax = Ax(bx, (-0.3, 4.3), (-2.5, 2.5)); ax.draw(d, ticks=False)
    f = lambda x: math.sqrt(x) * 1.0
    ax.curve(d, f, 0, 4, acc, 6)
    rot = ph(s, 1.5, 6)
    if rot > 0:
        ax.curve(d, lambda x: -f(x) * rot, 0, 4, alpha(acc, rot), 4)
    n = int(lerp(0, 14, ph(s, 6, 11)))
    for i in range(n):
        x = 0.15 + i * 4 / 14
        r = f(x)
        X, Y = ax.T(x, 0)
        R = ax.sx(r) * (ax.bx.h - ax.t - ax.b) / (ax.bx.w - ax.l - ax.r) * (ax.xr[1] - ax.xr[0]) / (ax.yr[1] - ax.yr[0])
        ry = abs(ax.T(x, r)[1] - Y)
        d.ellipse([X - ry * 0.28, Y - ry, X + ry * 0.28, Y + ry], outline=GOLD, width=4, fill=(255, 214, 10, 50))
    panel(d, bx, ['V = ∫ π[f(x)]² dx', 'כל פרוסה: עיגול ברדיוס f(x)', 'V = π∫₀⁴ x dx = 8π'], s, 7, size=21, y=20, right=True)

def sc_growth(d, bx, s, acc):
    ax = Ax(bx, (0, 4.2), (0, 18), pad=(70, 40, 50, 70)); ax.draw(d, labels=('t', 'y'))
    k = math.log(2)
    f = lambda t: math.exp(k * t)
    t1 = 4 * ph(s, 1, 10)
    ax.curve(d, f, 0, t1, acc, 7)
    for n in range(1, 5):
        if t1 >= n:
            ax.dot(d, n, f(n), GOLD, 12); ax.text(d, n, f(n) + 1.1, f'×{2 ** n}', 20, GOLD)
    panel(d, bx, ["y' = ky  ⇒  y = y₀·eᵏᵗ", 'זמן הכפלה = ln2 / k'], s, 2, size=22, y=30, right=False)

SCENES = {k[3:]: v for k, v in globals().items() if k.startswith('sc_')}

def k_calc(spec, p, s):
    bx = Box(); img = Image.new('RGBA', (bx.w, bx.h)); d = ImageDraw.Draw(img)
    SCENES[p['scene']](d, bx, s, hex2rgb(spec['accent']) + (255,))
    return img

from biz_scenes import BIZ  # applied (business) scenes
SCENES.update(BIZ)
