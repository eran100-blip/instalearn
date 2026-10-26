"""Schematic front-view human figure with an animated highlight (for Anatomy clips).

Coordinates: body units, x = 0 is the midline, NEGATIVE x = patient's RIGHT
(shown on the viewer's left, as in anatomical position), y = 0 top of head, 1000 = soles.
"""
import math
from PIL import Image, ImageDraw
from render import Box, ease, lerp, vtext, hex2rgb, SS, WHITE, GOLD

SKIN = (92, 104, 140, 255)
SKIN_EDGE = (170, 180, 215, 255)

def limb(d, T, k, p0, p1, w, col):
    a, b = T(*p0), T(*p1)
    d.line([a, b], fill=col, width=max(1, int(w * k)))
    r = w * k / 2
    for c in (a, b): d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col)

def silhouette(d, T, k):
    for side in (-1, 1):
        # arms
        limb(d, T, k, (side * 128, 190), (side * 160, 420), 52, SKIN)
        limb(d, T, k, (side * 160, 420), (side * 184, 615), 42, SKIN)
        e = T(side * 192, 660); r1, r2 = 24 * k, 40 * k
        d.ellipse([e[0] - r1, e[1] - r2, e[0] + r1, e[1] + r2], fill=SKIN)
        # legs
        limb(d, T, k, (side * 58, 560), (side * 64, 785), 78, SKIN)
        limb(d, T, k, (side * 64, 785), (side * 68, 955), 56, SKIN)
        f = T(side * 76, 975); d.ellipse([f[0] - 34 * k, f[1] - 18 * k, f[0] + 34 * k, f[1] + 18 * k], fill=SKIN)
    torso = [(-122, 172), (122, 172), (138, 205), (96, 330), (86, 470), (108, 560), (40, 585), (-40, 585), (-108, 560), (-86, 470), (-96, 330), (-138, 205)]
    d.polygon([T(x, y) for x, y in torso], fill=SKIN)
    n0, n1 = T(-24, 120), T(24, 180); d.rectangle([n0, n1], fill=SKIN)
    h = T(0, 70); d.ellipse([h[0] - 52 * k, h[1] - 66 * k, h[0] + 52 * k, h[1] + 66 * k], fill=SKIN, outline=SKIN_EDGE, width=max(1, int(3 * k)))

def draw_shape(d, T, k, sh, col):
    t = sh[0]
    if t == 'line':
        pts = [T(x, y) for x, y in sh[1]]
        d.line(pts, fill=col, width=max(2, int(sh[2] * k)), joint='curve')
        r = sh[2] * k / 2
        for c in (pts[0], pts[-1]): d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col)
    elif t == 'ellipse':
        cx, cy, rx, ry = sh[1:5]; c = T(cx, cy)
        d.ellipse([c[0] - rx * k, c[1] - ry * k, c[0] + rx * k, c[1] + ry * k], fill=col)
    elif t == 'poly':
        d.polygon([T(x, y) for x, y in sh[1]], fill=col)
    elif t == 'ring':
        cx, cy, rx, ry = sh[1:5]; c = T(cx, cy)
        d.ellipse([c[0] - rx * k, c[1] - ry * k, c[0] + rx * k, c[1] + ry * k], outline=col, width=max(2, int(sh[5] * k)))

def k_body(spec, p, s):
    bx = Box(); img = Image.new('RGBA', (bx.w, bx.h)); d = ImageDraw.Draw(img)
    # camera: full body -> zoom into the region
    full_k = (bx.h * 0.94) / 1000
    zx, zy, zk = p.get('zoom', (0, 500, 1.0))
    z = ease((s - 1.4) / 2.2)
    k = lerp(full_k, full_k * zk, z)
    cx, cy = lerp(0, zx, z), lerp(500, zy, z)
    ox = bx.w * 0.34 if p.get('label_side', 'right') == 'right' else bx.w * 0.66
    def T(x, y): return (ox + (x - cx) * k, bx.h / 2 + (y - cy) * k)
    silhouette(d, T, k)

    accent = hex2rgb(spec['accent'])
    hl_a = ease((s - 2.6) / 0.8)
    if hl_a > 0:
        pulse = 0.5 + 0.5 * math.sin(s * 4)
        glow = Image.new('RGBA', (bx.w, bx.h)); gd = ImageDraw.Draw(glow)
        for sh in p['shapes']:
            draw_shape(gd, T, k, sh, accent + (int(255 * hl_a),))
        # glow: blurred copy underneath
        from PIL import ImageFilter
        blur = glow.filter(ImageFilter.GaussianBlur(10 + 8 * pulse))
        img.alpha_composite(blur); img.alpha_composite(blur)
        img.alpha_composite(glow)
        if p.get('planes'):
            for (kind, val) in p['planes']:
                col = (255, 214, 10, int(220 * hl_a))
                if kind == 'v': d.line([T(val, -40), T(val, 1040)], fill=col, width=6)
                else: d.line([T(-260, val), T(260, val)], fill=col, width=6)

    # label with leader line
    la = ease((s - 3.4) / 0.8)
    if la > 0 and p.get('label'):
        ax, ay = T(*p['anchor'])
        right = p.get('label_side', 'right') == 'right'
        lx = bx.w - 30 if right else 30
        ly = max(60, min(bx.h - 60, ay))
        col = (255, 255, 255, int(255 * la))
        d.line([(ax, ay), (lx - (150 if right else -150), ly), (lx, ly)], fill=col, width=4)
        d.ellipse([ax - 10, ay - 10, ax + 10, ay + 10], fill=GOLD[:3] + (int(255 * la),))
        vtext(d, (lx, ly - 30), p['label'], 30 if len(p['label']) <= 12 else 25, GOLD[:3] + (int(255 * la),), anchor='rs' if right else 'ls')
    return img
