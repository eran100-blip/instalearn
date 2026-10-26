"""Renders 15-second vertical learning clips (720x1280, H.264) for InstaLearn.

Each clip = animated background + course chip + title + an animated visual
+ a short definition. Text is burned into the video; the long explanation
lives in the app ("Read more").
"""
import math, subprocess, sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 720, 1280
FPS = 20
DUR = 15
NF = FPS * DUR
SS = 2  # supersampling for the visual layer

FONT_DIR = '/usr/share/fonts/truetype/dejavu/'
def font(size, bold=True, mono=False):
    name = 'DejaVuSansMono-Bold.ttf' if mono else ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
    return ImageFont.truetype(FONT_DIR + name, size)

# Content zones (see VideoCard overlay: bottom ~34% and right column are covered by app UI)
X0, X1 = 84, 636
TITLE_Y = 150
VIS = (84, 360, 636, 650)          # visual box
CAP = (84, 668, 560, 845)          # definition box (avoids the right action column)

LAYOUTS = {
    'default': ((84, 360, 636, 650), (84, 668, 560, 845)),
    # bigger animation area (controls now sit at the very bottom of the screen)
    'tall': ((70, 335, 650, 745), (84, 762, 636, 990)),
}

def set_layout(spec):
    global VIS, CAP
    VIS, CAP = LAYOUTS[spec.get('layout', 'default')]

def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def lerp(a, b, t): return a + (b - a) * t

def is_rtl(text):
    return any('֐' <= ch <= '׿' for ch in text)

# ---------------------------------------------------------------- text

def text_w(draw, text, f):
    d = 'rtl' if is_rtl(text) else 'ltr'
    return draw.textlength(text, font=f, direction=d)

def wrap(draw, text, f, maxw):
    lines = []
    for para in text.split('\n'):
        words, cur = para.split(' '), ''
        for w in words:
            cand = (cur + ' ' + w).strip()
            if text_w(draw, cand, f) <= maxw or not cur:
                cur = cand
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines

import re as _re
_HEB = _re.compile('[\u0590-\u05FF]')
def iso(line):
    """Wrap each math/Latin run inside a Hebrew line in a bidi isolate (LRI…PDI), so formulas keep their order."""
    if not _HEB.search(line): return line
    out, i = [], 0
    for m in _re.finditer('[^\u0590-\u05FF]+', line):
        seg = m.group(); a, b = 0, len(seg)
        for _ in range(3):
            while a < b and seg[a] in ' ,.:;!?״)=≈': a += 1
            while b > a and seg[b - 1] in ' ,.:;!?״(=≈': b -= 1
            core = seg[a:b]
            if core.startswith('(') and core.count('(') > core.count(')'): a += 1
            if core.endswith(')') and core.count(')') > core.count('('): b -= 1
        core = seg[a:b]
        if core and _re.search('[A-Za-z0-9∞π∫ε-ωᵃ-ᶻ]', core):
            out.append(line[i:m.start() + a] + '\u2066' + core + '\u2069'); i = m.start() + b
    out.append(line[i:])
    return ''.join(out)

def draw_lines(draw, lines, f, x0, x1, y, fill, rtl, gap=1.25, center=False):
    lh = f.size * gap
    for ln in lines:
        if rtl: ln = iso(ln)
        d = 'rtl' if is_rtl(ln) else 'ltr'
        w = draw.textlength(ln, font=f, direction=d)
        if center: x = (x0 + x1 - w) / 2
        elif rtl: x = x1 - w
        else: x = x0
        draw.text((x, y), ln, font=f, fill=fill, direction=d)
        y += lh
    return y

# ---------------------------------------------------------------- background

def make_background(accent):
    a = np.array(hex2rgb(accent), dtype=float)
    top = np.array([8, 10, 24], float)
    bot = top * 0.6 + a * 0.18
    ys = np.linspace(0, 1, H)[:, None, None]
    img = (top * (1 - ys) + bot * ys) * np.ones((H, W, 3))
    # soft glow behind the visual
    yy, xx = np.mgrid[0:H, 0:W]
    g = np.exp(-(((xx - 360) / 330) ** 2 + ((yy - 500) / 260) ** 2))
    img += g[..., None] * a * 0.22
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

class Particles:
    def __init__(self, seed, accent):
        rng = np.random.default_rng(seed)
        self.p = rng.random((26, 2)) * [W, H]
        self.v = (rng.random((26, 2)) - 0.5) * [10, 30]
        self.r = rng.random(26) * 2.5 + 1
        self.c = hex2rgb(accent)
    def draw(self, d, s):
        for (x, y), (vx, vy), r in zip(self.p, self.v, self.r):
            px, py = (x + vx * s) % W, (y + vy * s) % H
            d.ellipse([px - r, py - r, px + r, py + r], fill=self.c + (70,))

# ---------------------------------------------------------------- static text layer

def make_text_layer(spec, accent):
    """Course chip, title and definition, as separate RGBA layers (for fade-ins)."""
    rtl = spec.get('lang') == 'he'
    chip = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(chip)
    f = font(24)
    label = spec['chip']
    tw = text_w(d, label, f)
    cx = X1 - tw - 36 if rtl else X0
    d.rounded_rectangle([cx, 92, cx + tw + 36, 136], radius=22, fill=hex2rgb(accent) + (255,))
    d.text((cx + 18, 100), label, font=f, fill=(255, 255, 255), direction='rtl' if is_rtl(label) else 'ltr')
    if spec.get('chip2'):
        f2 = font(22, bold=False)
        l2 = spec['chip2']; w2 = text_w(d, l2, f2)
        cx2 = cx - w2 - 52 if rtl else cx + tw + 52
        d.rounded_rectangle([cx2, 94, cx2 + w2 + 32, 134], radius=20, fill=(255, 255, 255, 40))
        d.text((cx2 + 16, 101), l2, font=f2, fill=(235, 235, 245), direction='rtl' if is_rtl(l2) else 'ltr')

    title = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(title)
    ft = font((56 if len(spec['title']) < 22 else 46) if spec.get('layout') != 'tall' else (52 if len(spec['title']) < 18 else 42))
    lines = wrap(d, spec['title'], ft, X1 - X0)
    y = draw_lines(d, lines, ft, X0, X1, TITLE_Y, (255, 255, 255), rtl)
    if spec.get('subtitle'):
        fs = font(32, bold=False)
        draw_lines(d, wrap(d, spec['subtitle'], fs, X1 - X0), fs, X0, X1, y + 4, hex2rgb(accent), rtl)

    cap = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(cap)
    fc = font(29 if rtl else 27, bold=False)
    lines = wrap(d, spec['definition'], fc, CAP[2] - CAP[0] - 36)
    lh = fc.size * 1.3
    hgt = len(lines) * lh + 30
    y0 = CAP[1]
    d.rounded_rectangle([CAP[0] - 6, y0, CAP[2], y0 + hgt], radius=20, fill=(0, 0, 0, 120))
    bar_x = CAP[2] - 10 if rtl else CAP[0] - 6
    d.rounded_rectangle([bar_x, y0 + 12, bar_x + 6, y0 + hgt - 12], radius=3, fill=hex2rgb(accent) + (255,))
    draw_lines(d, lines, fc, CAP[0] + 14, CAP[2] - 20, y0 + 14, (240, 240, 245), rtl, gap=1.3)
    return chip, title, cap

def fade(layer, a):
    if a >= 1: return layer
    if a <= 0: return None
    l = layer.copy(); l.putalpha(layer.getchannel('A').point(lambda v: int(v * a)))
    return l

# ---------------------------------------------------------------- visual helpers (drawn at SS scale)

class Box:
    def __init__(self):
        self.w = (VIS[2] - VIS[0]) * SS; self.h = (VIS[3] - VIS[1]) * SS
    def canvas(self):
        img = Image.new('RGBA', (self.w, self.h)); return img, ImageDraw.Draw(img)

def arrow(d, p0, p1, fill, width=6, head=22):
    d.line([p0, p1], fill=fill, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    l = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    head = min(head, l * 0.6)
    a1 = (p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45))
    a2 = (p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45))
    d.polygon([p1, a1, a2], fill=fill)

def vtext(d, xy, text, size, fill=(255, 255, 255), anchor='mm', bold=True, mono=False):
    f = font(size * SS, bold=bold, mono=mono)
    d.text(xy, text, font=f, fill=fill, anchor=anchor, direction='rtl' if is_rtl(text) else None)

WHITE = (255, 255, 255, 255)
DIM = (255, 255, 255, 70)
GOLD = (255, 214, 10, 255)
GREEN = (48, 209, 88, 255)
RED = (255, 69, 58, 255)
PINK = (255, 55, 95, 255)

def acc(spec): return hex2rgb(spec['accent']) + (255,)

# ---------------------------------------------------------------- visual kinds
# each: fn(spec, params, s) -> RGBA image at SS scale. s = seconds since start.

def prog(s, start=1.2, dur=9.0): return ease((s - start) / dur)

def plot_axes(d, bx, xr, yr, pad=40):
    def T(x, y):
        X = pad * SS + (x - xr[0]) / (xr[1] - xr[0]) * (bx.w - 2 * pad * SS)
        Y = bx.h - pad * SS - (y - yr[0]) / (yr[1] - yr[0]) * (bx.h - 2 * pad * SS)
        return X, Y
    # grid
    gs = 1 if xr[1] - xr[0] <= 20 else 10
    for gx in range(math.ceil(xr[0] / gs) * gs, math.floor(xr[1]) + 1, gs):
        d.line([T(gx, yr[0]), T(gx, yr[1])], fill=(255, 255, 255, 18), width=2)
    for gy in range(math.ceil(yr[0]), math.floor(yr[1]) + 1):
        d.line([T(xr[0], gy), T(xr[1], gy)], fill=(255, 255, 255, 18), width=2)
    if yr[0] <= 0 <= yr[1]: arrow(d, T(xr[0], 0), T(xr[1], 0), DIM, 4, 18)
    if xr[0] <= 0 <= xr[1]: arrow(d, T(0, yr[0]), T(0, yr[1]), DIM, 4, 18)
    return T

def k_plot(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    xr, yr = p['xr'], p['yr']
    T = plot_axes(d, bx, xr, yr)
    f = eval('lambda x: ' + p['f'], {'np': np, 'math': math})
    t = prog(s, 0.8, 4.5)
    xs = np.linspace(xr[0], xr[1], 400)
    ys = np.array([f(x) for x in xs])
    n = max(2, int(len(xs) * t))
    if 'area' in p:
        a, b = p['area']; ta = prog(s, 5.5, 4)
        bb = a + (b - a) * ta
        pts = [T(a, 0)] + [T(x, f(x)) for x in np.linspace(a, bb, 120)] + [T(bb, 0)]
        if ta > 0: d.polygon(pts, fill=hex2rgb(spec['accent']) + (110,))
    pts = [T(x, y) for x, y in zip(xs[:n], ys[:n]) if yr[0] - 1 <= y <= yr[1] + 1]
    if len(pts) > 1: d.line(pts, fill=acc(spec), width=8, joint='curve')
    if 'f2' in p:
        f2 = eval('lambda x: ' + p['f2'], {'np': np, 'math': math})
        pts = [T(x, f2(x)) for x in xs[:n] if yr[0] - 1 <= f2(x) <= yr[1] + 1]
        if len(pts) > 1: d.line(pts, fill=GOLD, width=6, joint='curve')
    if 'tangent' in p and s > 5.5:
        lo, hi = p['tangent']
        x0 = lo + (hi - lo) * (0.5 - 0.5 * math.cos((s - 5.5) * 0.7))
        h = 1e-4; m = (f(x0 + h) - f(x0 - h)) / (2 * h); y0 = f(x0)
        L = (xr[1] - xr[0]) * 0.22
        d.line([T(x0 - L, y0 - m * L), T(x0 + L, y0 + m * L)], fill=GOLD, width=6)
        X, Y = T(x0, y0); d.ellipse([X - 14, Y - 14, X + 14, Y + 14], fill=WHITE)
        vtext(d, (bx.w - 30, 40), f'slope = {m:.2f}', 26, GOLD, anchor='rm')
    if 'limit' in p and s > 5.5:
        x0 = p['limit']; L = p.get('lim_val', f(x0 + 1e-6))
        k = (s - 5.5) / 6
        for side in (-1, 1):
            xx = x0 + side * (xr[1] - xr[0]) * 0.35 * max(0.02, 1 - k)
            X, Y = T(xx, f(xx)); d.ellipse([X - 12, Y - 12, X + 12, Y + 12], fill=GOLD)
        X, Y = T(x0, L); d.ellipse([X - 14, Y - 14, X + 14, Y + 14], outline=WHITE, width=5)
    if 'dots' in p:
        for (x, y) in p['dots']:
            X, Y = T(x, y); d.ellipse([X - 12, Y - 12, X + 12, Y + 12], fill=GOLD)
    if p.get('label'):
        vtext(d, (60, 40), p['label'], 28, acc(spec), anchor='lm')
    return img

def k_wave(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    mid = bx.h / 2
    d.line([(0, mid), (bx.w, mid)], fill=DIM, width=3)
    amp = bx.h * 0.3
    k = p.get('k', 2.0); w = p.get('w', 2.0)
    env = p.get('packet', False)
    a = ease((s - 0.5) / 2)
    for i, (kk, col) in enumerate([(k, acc(spec))] + ([(k * 2, GOLD)] if p.get('second') and s > 6 else [])):
        pts = []
        for X in range(0, bx.w, 6):
            x = X / bx.w * 4 * math.pi
            y = math.sin(kk * x / 2 - w * s * (1 + i))
            if env: y *= math.exp(-((x - (2 + 0.5 * math.sin(s * 0.5)) * math.pi * 0.9) ** 2) / 4)
            pts.append((X, mid - amp * a * y))
        d.line(pts, fill=col, width=8, joint='curve')
    if p.get('lambda') and s > 3:
        lam = bx.w / (k)
        y = mid + amp + 40
        arrow(d, (60, y), (60 + lam, y), WHITE, 4, 16); arrow(d, (60 + lam, y), (60, y), WHITE, 4, 16)
        vtext(d, (60 + lam / 2, y + 36), 'λ', 32)
    return img

def k_vectors(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    fx = eval('lambda x,y: ' + p['fx'], {'np': np, 'math': math})
    fy = eval('lambda x,y: ' + p['fy'], {'np': np, 'math': math})
    n = 7; t = prog(s, 0.8, 4)
    for i in range(n):
        for j in range(5):
            x = -1 + 2 * i / (n - 1); y = -1 + 2 * j / 4
            X = bx.w * (0.08 + 0.84 * (i / (n - 1))); Y = bx.h * (0.9 - 0.8 * (j / 4))
            vx, vy = fx(x, y), fy(x, y); m = math.hypot(vx, vy) or 1
            L = 52 * t * min(1.4, m)
            col = acc(spec) if m < 1.0 else GOLD
            if L > 4: arrow(d, (X, Y), (X + vx / m * L, Y - vy / m * L), col, 5, 16)
    if p.get('label'): vtext(d, (bx.w / 2, 30), p['label'], 28, WHITE)
    return img

def k_graph(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    nodes = p['nodes']; edges = p['edges']
    pos = {k: (v[0] * bx.w, v[1] * bx.h) for k, v in nodes.items()}
    order = p.get('order', [])
    step = int(max(0, s - 2) / p.get('step', 1.4))
    visited = set(order[:step + 1]) if s > 2 else set()
    for e in edges:
        a, b = e[0], e[1]
        col = GOLD if (a in visited and b in visited) else (255, 255, 255, 90)
        if p.get('directed'):
            (x0, y0), (x1, y1) = pos[a], pos[b]
            if a == b:
                R = p.get('r', 40)
                d.arc([x0 - R * 1.1, y0 - R * 2.6, x0 + R * 1.1, y0 - R * 0.6], 160, 380, fill=col, width=5)
            else:
                ang = math.atan2(y1 - y0, x1 - x0); r = p.get('r', 40) + 6
                arrow(d, (x0 + r * math.cos(ang), y0 + r * math.sin(ang)), (x1 - r * math.cos(ang), y1 - r * math.sin(ang)), col, 5, 20)
        else:
            d.line([pos[a], pos[b]], fill=col, width=6)
        if len(e) > 2:
            (x0, y0), (x1, y1) = pos[a], pos[b]
            mx, my = ((x0 + x1) / 2, (y0 + y1) / 2) if a != b else (x0, y0 - p.get('r', 40) * 2.9)
            vtext(d, (mx, my - 18), e[2], 24, (230, 230, 240))
    for k, (x, y) in pos.items():
        on = k in visited; r = p.get('r', 40)
        pulse = 1 + 0.08 * math.sin(s * 5) if on else 1
        r *= pulse
        d.ellipse([x - r, y - r, x + r, y + r], fill=acc(spec) if on else (40, 44, 60, 255), outline=WHITE, width=4)
        if k in p.get('accept', []):
            d.ellipse([x - r + 9, y - r + 9, x + r - 9, y + r - 9], outline=WHITE, width=3)
        vtext(d, (x, y), str(k), p.get('fs', 28))
    if p.get('label'): vtext(d, (bx.w / 2, 26), p['label'], 26, GOLD)
    return img

def k_bars(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    states = p['_states']
    i = min(len(states) - 1, int(max(0, s - 1.5) / p.get('step', 0.6)))
    vals, hl, done = states[i]
    n = len(vals); mx = max(vals)
    bw = bx.w / n
    for j, v in enumerate(vals):
        h = (bx.h - 90) * v / mx
        col = GOLD if j in hl else (GREEN if j in done else acc(spec))
        if p.get('dim') and j not in hl and j not in done and p['dim'](i, j): col = (70, 70, 90, 255)
        d.rounded_rectangle([j * bw + 8, bx.h - h - 10, (j + 1) * bw - 8, bx.h - 10], radius=10, fill=col)
        if p.get('numbers', True): vtext(d, ((j + 0.5) * bw, bx.h - h - 34), str(v), 24)
    if p.get('label'): vtext(d, (bx.w / 2, 26), p['label'], 26, WHITE)
    return img

def bubble_states(vals):
    vals = list(vals); st = [(list(vals), [], [])]; n = len(vals); done = []
    for i in range(n):
        for j in range(n - 1 - i):
            st.append((list(vals), [j, j + 1], list(done)))
            if vals[j] > vals[j + 1]:
                vals[j], vals[j + 1] = vals[j + 1], vals[j]
                st.append((list(vals), [j, j + 1], list(done)))
        done.append(n - 1 - i)
    st.append((list(vals), [], list(range(n))))
    return st

def bsearch_states(vals, target):
    lo, hi = 0, len(vals) - 1; st = [(vals, [], [])]
    while lo <= hi:
        mid = (lo + hi) // 2
        st.append((vals, [mid], [k for k in range(len(vals)) if k < lo or k > hi]))
        if vals[mid] == target:
            st += [(vals, [mid], [k for k in range(len(vals)) if k != mid])] * 3; break
        if vals[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return st

def k_atom(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    cx, cy = bx.w / 2, bx.h / 2
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=PINK)
    vtext(d, (cx, cy), p.get('nucleus', '+'), 30)
    shells = p.get('shells', [2, 8])
    for si, ne in enumerate(shells):
        R = 120 + si * 110
        d.ellipse([cx - R, cy - R * 0.62, cx + R, cy + R * 0.62], outline=(255, 255, 255, 80), width=3)
        for e in range(ne):
            a = s * (1.2 - si * 0.3) + 2 * math.pi * e / ne
            x, y = cx + R * math.cos(a), cy + R * 0.62 * math.sin(a)
            d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=acc(spec))
    if p.get('photon') and s > 4:
        k = ((s - 4) % 4) / 4
        x = lerp(0, cx - 360, 1 - k) if k < 1 else 0
        pts = [(X, 60 + 20 * math.sin(X / 18)) for X in range(int(x), int(x) + 200, 6)]
        if len(pts) > 1: d.line(pts, fill=GOLD, width=5)
    if p.get('label'): vtext(d, (bx.w / 2, 26), p['label'], 26, GOLD)
    return img

def k_complex(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    T = plot_axes(d, bx, (-1.9, 1.9), (-1.3, 1.3), pad=20)
    R = T(1, 0)[0] - T(0, 0)[0]
    cx, cy = T(0, 0)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255, 110), width=4)
    th = (s - 1) * 0.6 if s > 1 else 0
    x, y = T(math.cos(th), math.sin(th))
    d.line([(cx, cy), (x, y)], fill=acc(spec), width=8)
    d.line([(x, y), (x, cy)], fill=GOLD, width=4)
    d.line([(cx, cy), (x, cy)], fill=GREEN, width=4)
    d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=WHITE)
    d.arc([cx - 60, cy - 60, cx + 60, cy + 60], -math.degrees(th) % 360 if False else 360 - (math.degrees(th) % 360), 360, fill=GOLD, width=4)
    vtext(d, (bx.w - 20, 30), f'θ = {math.degrees(th) % 360:.0f}°', 26, GOLD, anchor='rm')
    vtext(d, (T(1.3, 0)[0], cy + 34), 'Re', 24, DIM); vtext(d, (cx + 40, T(0, 1.2)[1]), 'Im', 24, DIM)
    return img

def k_circuit(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    x0, y0, x1, y1 = 120, 90, bx.w - 120, bx.h - 90
    path = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    d.line(path, fill=WHITE, width=6)
    # battery on left
    by = (y0 + y1) / 2
    d.rectangle([x0 - 50, by - 30, x0 + 50, by + 30], fill=(0, 0, 0, 0))
    d.rectangle([x0 - 10, by - 40, x0 + 10, by + 40], fill=(0, 0, 0, 255))
    d.line([(x0 - 50, by - 12), (x0 + 50, by - 12)], fill=GOLD, width=8)
    d.line([(x0 - 28, by + 12), (x0 + 28, by + 12)], fill=GOLD, width=8)
    vtext(d, (x0 - 80, by), 'V', 30, GOLD)
    # resistors on top (and right if parallel)
    def resistor(xa, xb, y, lab):
        d.rectangle([xa, y - 30, xb, y + 30], fill=(0, 0, 0, 255))
        pts = [(xa, y)] + [(xa + (xb - xa) * (k + 0.5) / 8, y + (-24 if k % 2 == 0 else 24)) for k in range(8)] + [(xb, y)]
        d.line(pts, fill=acc(spec), width=6)
        vtext(d, ((xa + xb) / 2, y - 56), lab, 26, acc(spec))
    mx = (x0 + x1) / 2
    for i, lab in enumerate(p.get('resistors', ['R'])):
        if i == 0: resistor(mx - 110, mx + 110, y0, lab)
        else: resistor(mx - 110, mx + 110, y1, lab)
    # moving charges
    per = 2 * ((x1 - x0) + (y1 - y0))
    for k in range(14):
        u = ((k / 14) * per + s * 140) % per
        segs = [(x1 - x0), (y1 - y0), (x1 - x0), (y1 - y0)]
        pt = None; acc_len = 0
        for (a, b), L in zip(zip(path[:-1], path[1:]), segs):
            if u <= acc_len + L:
                t = (u - acc_len) / L; pt = (lerp(a[0], b[0], t), lerp(a[1], b[1], t)); break
            acc_len += L
        if pt and s > 1.5: d.ellipse([pt[0] - 10, pt[1] - 10, pt[0] + 10, pt[1] + 10], fill=GREEN)
    if p.get('label'): vtext(d, (bx.w / 2, bx.h / 2), p['label'], 34, WHITE)
    return img

def k_incline(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    th = math.radians(p.get('angle', 30))
    bxl, byb = 60, bx.h - 40
    L = bx.w - 140
    top = (bxl + L * math.cos(th) * 0 + 0, byb - L * math.sin(th))
    d.polygon([(bxl, byb), (bxl + L, byb), (bxl, byb - L * math.tan(th) if False else byb - L * math.sin(th) / math.cos(th) * math.cos(th))], fill=(60, 64, 90, 255))
    # block slides down from top-left to bottom-right
    hyp = L / math.cos(th)
    k = (0.5 * ((max(0, s - 2)) / 9) ** 2 * 1.8) % 1 if s > 2 else 0
    k = min(k, 0.85)
    start = (bxl, byb - L * math.tan(th))
    def along(u): return (start[0] + u * L, start[1] + u * L * math.tan(th))
    cxp, cyp = along(0.1 + k * 0.7)
    nx, ny = math.sin(th), -math.cos(th)  # outward normal (up-right)
    size = 70
    c = (cxp + nx * size / 2, cyp + ny * size / 2)
    ux, uy = math.cos(th), math.sin(th)
    corners = [(c[0] + sx * ux * size / 2 + sy * nx * size / 2, c[1] + sx * uy * size / 2 + sy * ny * size / 2) for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
    d.polygon(corners, fill=acc(spec))
    if s > 1:
        arrow(d, c, (c[0], c[1] + 130), RED, 6, 20); vtext(d, (c[0] - 40, c[1] + 120), 'mg', 26, RED)
        arrow(d, c, (c[0] + nx * 110, c[1] + ny * 110), GREEN, 6, 20); vtext(d, (c[0] + nx * 140, c[1] + ny * 140), 'N', 26, GREEN)
    if s > 4:
        arrow(d, c, (c[0] + ux * 120, c[1] + uy * 120), GOLD, 6, 20); vtext(d, (c[0] + ux * 120 + 70, c[1] + uy * 120), 'ma', 26, GOLD)
    vtext(d, (bxl + L - 90, byb - 30), 'θ', 30)
    return img

def k_charges(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    q = p.get('q', ['+', '+'])
    sep = bx.w * 0.18 + bx.w * 0.12 * (0.5 + 0.5 * math.sin(s * 0.8)) if p.get('move') else bx.w * 0.25
    cy = bx.h / 2
    c1, c2 = (bx.w / 2 - sep, cy), (bx.w / 2 + sep, cy)
    # field lines (simple radial)
    for c, sign in ((c1, q[0]), (c2, q[1])):
        for k in range(12):
            a = 2 * math.pi * k / 12
            r0, r1 = 50, 50 + 120 * ease((s - 0.5) / 2)
            p0 = (c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a)); p1 = (c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a))
            if sign == '+': arrow(d, p0, p1, (255, 255, 255, 70), 3, 12)
            else: arrow(d, p1, p0, (255, 255, 255, 70), 3, 12)
    for c, sign in ((c1, q[0]), (c2, q[1])):
        col = RED if sign == '+' else (10, 132, 255, 255)
        d.ellipse([c[0] - 44, c[1] - 44, c[0] + 44, c[1] + 44], fill=col, outline=WHITE, width=4)
        vtext(d, c, sign, 44)
    F = 5000 / (sep ** 1.0) * 6
    same = q[0] == q[1]
    if s > 3:
        dirn = -1 if same else 1
        arrow(d, (c1[0], cy - 80), (c1[0] - dirn * F, cy - 80), GOLD, 6, 20)
        arrow(d, (c2[0], cy - 80), (c2[0] + dirn * F, cy - 80), GOLD, 6, 20)
        vtext(d, (bx.w / 2, cy + 110), 'F ∝ q₁q₂ / r²', 30, GOLD)
    return img

def k_matrix(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    T = plot_axes(d, bx, (-1.2, 3.3), (-1.1, 2.6), pad=20)
    A = np.array(p['A'], float)
    t = prog(s, 1.5, 5)
    M = np.eye(2) * (1 - t) + A * t
    sq = [np.array(v) for v in [(0, 0), (1, 0), (1, 1), (0, 1)]]
    pts = [T(*(M @ v)) for v in sq]
    d.polygon(pts, fill=hex2rgb(spec['accent']) + (110,), outline=acc(spec))
    arrow(d, T(0, 0), T(*(M @ np.array([1, 0]))), GOLD, 7, 22)
    arrow(d, T(0, 0), T(*(M @ np.array([0, 1]))), GREEN, 7, 22)
    if p.get('eig') and s > 7:
        for v in p['eig']:
            v = np.array(v, float); v /= np.linalg.norm(v)
            d.line([T(*(-1 * v)), T(*(2.6 * v))], fill=(255, 255, 255, 120), width=3)
    vtext(d, (bx.w - 30, 34), f'det = {np.linalg.det(M):.2f}', 28, GOLD, anchor='rm')
    return img

def k_code(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    d.rounded_rectangle([0, 0, bx.w, bx.h], radius=30, fill=(18, 20, 30, 235))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([30 + i * 40, 26, 54 + i * 40, 50], fill=c + (255,))
    lines = p['lines']
    total = sum(len(l) for l in lines)
    shown = int(total * prog(s, 0.8, 7))
    y = 90; f = font(25 * SS, bold=False, mono=True)
    for ln in lines:
        part = ln[:max(0, shown)]; shown -= len(ln)
        d.text((36, y), part, font=f, fill=(230, 230, 240, 255))
        y += 25 * SS * 1.45
        if shown < 0: break
    if p.get('out') and s > 9:
        d.text((36, bx.h - 70), '> ' + p['out'], font=f, fill=GREEN)
    return img

def k_formula(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    lines = p['lines']
    for i, ln in enumerate(lines):
        a = ease((s - 1 - i * 1.8) / 1.0)
        if a <= 0: continue
        y = bx.h * (i + 1) / (len(lines) + 1)
        col = (GOLD if i == len(lines) - 1 else (255, 255, 255))[:3] + (int(255 * a),)
        sz = p.get('size', 40)
        vtext(d, (bx.w / 2, y + (1 - a) * 30), ln, sz, col)
    return img

def k_pendulum(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    px, py = bx.w / 2, 40; L = bx.h - 120
    th = 0.6 * math.cos(2 * math.pi * s / p.get('T', 2.5))
    x, y = px + L * math.sin(th), py + L * math.cos(th)
    d.line([(px - 120, py), (px + 120, py)], fill=WHITE, width=6)
    d.line([(px, py), (x, y)], fill=(220, 220, 230, 255), width=4)
    d.ellipse([x - 40, y - 40, x + 40, y + 40], fill=acc(spec))
    vtext(d, (px + 40, py + 70), 'L', 28)
    return img

def k_dist(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    vals = p['vals']; n = len(vals); mx = max(vals); bw = bx.w / n
    t = prog(s, 1, 4)
    for j, v in enumerate(vals):
        h = (bx.h - 100) * v / mx * ease(t * n - j * 0.6 if n > 1 else t)
        col = GOLD if j in p.get('hl', []) and s > 6 else acc(spec)
        d.rounded_rectangle([j * bw + 10, bx.h - 50 - h, (j + 1) * bw - 10, bx.h - 50], radius=10, fill=col)
        if p.get('values', True) and h > 40:
            vtext(d, ((j + 0.5) * bw, bx.h - 50 - h + 34), f'{v:,}', 30, (0, 0, 0, 230))
        vtext(d, ((j + 0.5) * bw, bx.h - 22), str(p['labels'][j]), 24, DIM)
    if p.get('label'): vtext(d, (bx.w / 2, 26), p['label'], 26, WHITE)
    return img

def k_tree(spec, p, s):
    # binary tree / heap
    bx = Box(); img, d = bx.canvas()
    keys = p['keys']; pos = {}
    for i, k in enumerate(keys):
        if k is None: continue
        depth = int(math.log2(i + 1)); idx = i + 1 - 2 ** depth
        x = bx.w * (idx + 0.5) / 2 ** depth; y = 60 + depth * (bx.h - 120) / max(1, int(math.log2(len(keys))))
        pos[i] = (x, y)
    path = p.get('path', [])
    step = int(max(0, s - 2) / 1.5)
    hl = set(path[:step + 1]) if s > 2 else set()
    for i in pos:
        if i > 0 and (i - 1) // 2 in pos:
            col = GOLD if i in hl and (i - 1) // 2 in hl else (255, 255, 255, 100)
            d.line([pos[(i - 1) // 2], pos[i]], fill=col, width=6)
    for i, (x, y) in pos.items():
        d.ellipse([x - 38, y - 38, x + 38, y + 38], fill=acc(spec) if i in hl else (40, 44, 60, 255), outline=WHITE, width=4)
        vtext(d, (x, y), str(keys[i]), 26)
    if p.get('label'): vtext(d, (bx.w / 2, bx.h - 20), p['label'], 26, GOLD)
    return img

def k_molecule(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    cx, cy = bx.w / 2, bx.h / 2 + 10
    rot = s * 0.4
    for (name, ang, dist, col) in p['atoms']:
        a = math.radians(ang) + (rot if p.get('spin') else 0)
        x, y = cx + dist * math.cos(a) * SS, cy + dist * math.sin(a) * SS * 0.8
        if dist > 0: d.line([(cx, cy), (x, y)], fill=(230, 230, 240, 255), width=10)
    for (name, ang, dist, col) in sorted(p['atoms'], key=lambda t: t[2]):
        a = math.radians(ang) + (rot if p.get('spin') else 0)
        x, y = cx + dist * math.cos(a) * SS, cy + dist * math.sin(a) * SS * 0.8
        r = 60 if dist == 0 else 42
        d.ellipse([x - r, y - r, x + r, y + r], fill=hex2rgb(col) + (255,), outline=WHITE, width=4)
        vtext(d, (x, y), name, 30)
    if p.get('label'): vtext(d, (bx.w / 2, 30), p['label'], 28, GOLD)
    return img

def k_signal(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    hh = bx.h / 2
    # top: input signal (sum of sines), bottom: spectrum bars
    comps = p['comps']
    a = ease((s - 0.8) / 2)
    pts = []
    for X in range(0, bx.w, 5):
        x = X / bx.w * 2 * math.pi * 2
        y = sum(A * math.sin(f * x - s * 2) for f, A in comps)
        pts.append((X, hh * 0.5 - y * hh * 0.18 * a))
    d.line(pts, fill=acc(spec), width=6)
    t2 = ease((s - 5) / 2)
    d.line([(40, bx.h - 40), (bx.w - 40, bx.h - 40)], fill=DIM, width=3)
    for f, A in comps:
        X = 40 + (bx.w - 80) * f / (max(f for f, _ in comps) + 1)
        d.rectangle([X - 16, bx.h - 40 - A * 220 * t2, X + 16, bx.h - 40], fill=GOLD)
        if t2 > 0.5: vtext(d, (X, bx.h - 15), f'{f}', 22, DIM)
    if s > 5: vtext(d, (bx.w / 2, hh + 20), 'Fourier → frequencies', 26, GOLD)
    return img

def k_bignum(spec, p, s):
    bx = Box(); img, d = bx.canvas()
    cx, cy = bx.w / 2, bx.h * 0.45
    t = ease((s - 0.8) / 3.0)
    v = p['value'] * t
    txt = f"{p.get('prefix', '')}{v:,.{p.get('decimals', 0)}f}"
    # pulsing ring behind the number
    pulse = 0.5 + 0.5 * math.sin(s * 2.5)
    R = bx.h * 0.42 + pulse * 10
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=hex2rgb(spec['accent']) + (90,), width=8)
    d.ellipse([cx - R * 0.86, cy - R * 0.86, cx + R * 0.86, cy + R * 0.86], fill=hex2rgb(spec['accent']) + (45,))
    vtext(d, (cx, cy - 6), txt, 96 if len(txt) <= 5 else 72)
    if p.get('suffix'):
        vtext(d, (cx, cy + 82 * SS / 2 + 30), p['suffix'].strip(), 34, GOLD)
    if p.get('label') and s > 3:
        a = ease((s - 3) / 0.8)
        vtext(d, (cx, bx.h - 24), p['label'], 26, (230, 230, 240, int(255 * a)))
    return img

# ---------------------------------------------------------------- schema kinds (law course)

def _wrap_center(d, text, size, cx, cy, maxw, fill=(255, 255, 255, 255), bold=True, gap=1.2):
    f = font(size * SS, bold=bold)
    lines = wrap(d, text, f, maxw)
    lh = f.size * gap
    y = cy - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        d.text((cx, y), ln, font=f, fill=fill, anchor='mm', direction='rtl' if is_rtl(ln) else None)
        y += lh

def k_flow(spec, p, s):
    """Flowchart: nodes appear one by one, then the arrows between them."""
    bx = Box(); img, d = bx.canvas()
    nodes = {n['id']: n for n in p['nodes']}
    order = [n['id'] for n in p['nodes']]
    step = p.get('step', 1.3)
    shown = {nid: ease((s - 0.8 - i * step) / 0.6) for i, nid in enumerate(order)}
    acc_c = hex2rgb(spec['accent'])
    def box_of(n):
        w = n.get('w', 0.30) * bx.w; h = n.get('h', 0.24) * bx.h
        cx, cy = n['x'] * bx.w, n['y'] * bx.h
        return cx, cy, w, h
    # edges
    for e in p.get('edges', []):
        a, b = nodes[e[0]], nodes[e[1]]
        al = min(shown[e[0]], shown[e[1]])
        if al <= 0: continue
        ax, ay, aw, ah = box_of(a); bxx, byy, bw, bh = box_of(b)
        # leave from the side facing the other node
        dx, dy = bxx - ax, byy - ay
        if abs(dx) * ah > abs(dy) * aw:
            p0 = (ax + math.copysign(aw / 2, dx), ay); p1 = (bxx - math.copysign(bw / 2, dx), byy)
        else:
            p0 = (ax, ay + math.copysign(ah / 2, dy)); p1 = (bxx, byy - math.copysign(bh / 2, dy))
        col = (255, 255, 255, int(170 * al))
        arrow(d, p0, p1, col, 5, 18)
        if len(e) > 2 and e[2]:
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            f = font(20 * SS); tw = d.textlength(e[2], font=f, direction='rtl' if is_rtl(e[2]) else None)
            d.rounded_rectangle([mx - tw / 2 - 10, my - 22, mx + tw / 2 + 10, my + 22], radius=14, fill=(20, 20, 30, int(235 * al)))
            d.text((mx, my), e[2], font=f, fill=GOLD[:3] + (int(255 * al),), anchor='mm', direction='rtl' if is_rtl(e[2]) else None)
    # nodes
    for nid in order:
        n = nodes[nid]; a = shown[nid]
        if a <= 0: continue
        cx, cy, w, h = box_of(n)
        kind = n.get('shape', 'box')
        col = hex2rgb(n['color']) if n.get('color') else acc_c
        if kind == 'diamond':
            d.polygon([(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)], fill=col + (int(60 * a),), outline=col + (int(255 * a),))
            maxw = w * 0.62
        elif kind == 'result':
            d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(h / 2), fill=col + (int(255 * a),))
            maxw = w * 0.85
        else:
            d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=22, fill=(28, 30, 44, int(245 * a)), outline=col + (int(255 * a),), width=5)
            maxw = w * 0.86
        _wrap_center(d, n['text'], int(n.get('fs', 21) * 1.15), cx, cy, maxw, (255, 255, 255, int(255 * a)))
    return img

def k_timeline(spec, p, s):
    """Horizontal timeline with labelled ticks (right-to-left for Hebrew)."""
    bx = Box(); img, d = bx.canvas()
    pts = p['points']  # list of (pos 0..1, top label, bottom label)
    rtl = p.get('rtl', True)
    y = bx.h * 0.55
    x0, x1 = 50, bx.w - 50
    t = ease((s - 0.8) / 2.0)
    if rtl:
        d.line([(x1, y), (x1 - (x1 - x0) * t, y)], fill=(255, 255, 255, 150), width=6)
    else:
        d.line([(x0, y), (x0 + (x1 - x0) * t, y)], fill=(255, 255, 255, 150), width=6)
    for i, (pos, top, bottom) in enumerate(pts):
        a = ease((s - 1.5 - i * 1.2) / 0.6)
        if a <= 0: continue
        x = x1 - (x1 - x0) * pos if rtl else x0 + (x1 - x0) * pos
        col = hex2rgb(spec['accent']) + (int(255 * a),)
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col, outline=(255, 255, 255, int(255 * a)), width=4)
        if top: _wrap_center(d, top, 26, x, y - 70, 240, GOLD[:3] + (int(255 * a),))
        if bottom: _wrap_center(d, bottom, 20, x, y + 75, 250, (230, 230, 240, int(255 * a)), bold=False)
    if p.get('label'): vtext(d, (bx.w / 2, 26), p['label'], 24, (255, 255, 255, 230))
    return img

def k_table(spec, p, s):
    """Comparison table: header row, then rows appear one by one. Columns run right-to-left."""
    bx = Box(); img, d = bx.canvas()
    cols = p['cols']; rows = p['rows']
    nC = len(cols); nR = len(rows) + 1
    cw = bx.w / nC; rh = bx.h / nR
    acc_c = hex2rgb(spec['accent'])
    for r in range(nR):
        a = ease((s - 0.8 - r * p.get('step', 1.4)) / 0.6)
        if a <= 0: continue
        cells = cols if r == 0 else rows[r - 1]
        for c, txt in enumerate(cells):
            x1 = bx.w - c * cw; x0 = x1 - cw
            y0 = r * rh
            fill = acc_c + (int(230 * a),) if r == 0 else ((38, 40, 56, int(230 * a)) if c == 0 else (24, 26, 38, int(220 * a)))
            d.rounded_rectangle([x0 + 4, y0 + 4, x1 - 4, y0 + rh - 4], radius=14, fill=fill)
            _wrap_center(d, txt, int((p.get('fs', 19) if r else 21) * 1.12), (x0 + x1) / 2, y0 + rh / 2, cw - 30,
                         (255, 255, 255, int(255 * a)), bold=(r == 0 or c == 0))
    return img

KINDS = {
    'plot': k_plot, 'wave': k_wave, 'vectors': k_vectors, 'graph': k_graph, 'bars': k_bars,
    'atom': k_atom, 'complex': k_complex, 'circuit': k_circuit, 'incline': k_incline,
    'charges': k_charges, 'matrix': k_matrix, 'code': k_code, 'formula': k_formula,
    'pendulum': k_pendulum, 'bignum': k_bignum, 'flow': k_flow, 'timeline': k_timeline, 'table': k_table, 'dist': k_dist, 'tree': k_tree, 'molecule': k_molecule, 'signal': k_signal,
}

# ---------------------------------------------------------------- render

def render(spec, out_path):
    set_layout(spec)
    from body import k_body  # anatomy figure
    KINDS['body'] = k_body
    from calc_scenes import k_calc
    KINDS['calc'] = k_calc
    accent = spec['accent']
    p = dict(spec['visual'])
    kind = p.pop('kind')
    if kind == 'bars':
        p['_states'] = bubble_states(p['vals']) if p.get('mode') == 'sort' else bsearch_states(p['vals'], p['target'])
    bg = make_background(accent)
    parts = Particles(abs(hash(spec['id'])) % 10000, accent)
    chip, title, cap = make_text_layer(spec, accent)
    fn = KINDS[kind]
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '30',
           '-pix_fmt', 'yuv420p', '-profile:v', 'main', '-movflags', '+faststart', out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    vw, vh = VIS[2] - VIS[0], VIS[3] - VIS[1]
    for i in range(NF):
        s = i / FPS
        frame = bg.copy().convert('RGBA')
        pl = Image.new('RGBA', (W, H)); parts.draw(ImageDraw.Draw(pl), s)
        frame.alpha_composite(pl)
        for layer, a in ((chip, ease(s / 0.6)), (title, ease((s - 0.2) / 0.8)), (cap, ease((s - 2.0) / 1.0))):
            l = fade(layer, a)
            if l is not None: frame.alpha_composite(l)
        vis = fn(spec, p, s).resize((vw, vh), Image.BILINEAR)
        va = ease((s - 0.6) / 0.8)
        if va < 1: vis.putalpha(vis.getchannel('A').point(lambda v: int(v * va)))
        frame.alpha_composite(vis, (VIS[0], VIS[1]))
        # progress bar at the very top, like stories
        bar = Image.new('RGBA', (W, 80)); dr = ImageDraw.Draw(bar)
        # thin story-style progress line (3px), a little below the status bar
        dr.rounded_rectangle([X0, 76, X1, 79], radius=1, fill=(255, 255, 255, 45))
        dr.rounded_rectangle([X0, 76, X0 + max(3, (X1 - X0) * (s / DUR)), 79], radius=1, fill=(255, 255, 255, 200))
        frame.alpha_composite(bar)
        proc.stdin.write(frame.convert('RGB').tobytes())
    proc.stdin.close(); proc.wait()
    return out_path

def still(spec, s, path):
    """Single frame preview (for checking layouts)."""
    set_layout(spec)
    from body import k_body
    KINDS['body'] = k_body
    from calc_scenes import k_calc
    KINDS['calc'] = k_calc
    accent = spec['accent']; p = dict(spec['visual']); kind = p.pop('kind')
    if kind == 'bars':
        p['_states'] = bubble_states(p['vals']) if p.get('mode') == 'sort' else bsearch_states(p['vals'], p['target'])
    frame = make_background(accent).convert('RGBA')
    for layer in make_text_layer(spec, accent): frame.alpha_composite(layer)
    vis = KINDS[kind](spec, p, s).resize((VIS[2] - VIS[0], VIS[3] - VIS[1]), Image.BILINEAR)
    frame.alpha_composite(vis, (VIS[0], VIS[1]))
    frame.convert('RGB').save(path)
