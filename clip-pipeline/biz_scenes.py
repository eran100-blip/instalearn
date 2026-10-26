"""Animated scenes for the applied (business) calculus videos, based on Applied Calculus
(Calaway, Hoffman, Lippman, CC BY 3.0 US). Same API as calc_scenes: fn(d, bx, s, acc)."""
import math
from calc_scenes import Ax, ph, alpha, label, panel, BLUE, PURPLE, CYAN
from render import WHITE, GOLD, GREEN, RED, lerp

GRAY = (200, 200, 210, 200)

def _axes(d, ax, xl, yl):
    ax.draw(d, ticks=False, labels=(xl, yl))

def _seq(s, keys):
    """Piecewise eased value: keys = [(t, value), ...]."""
    if s <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if s <= t1: return lerp(v0, v1, ph(s, t0, t1))
    return keys[-1][1]

def _tangent(d, ax, f, fp, x, half, col, w=4):
    m = fp(x)
    ax.line(d, x - half, f(x) - m * half, x + half, f(x) + m * half, col, w)

# ---------------------------------------------------------------- marginal cost
def sc_marginal(d, bx, s, acc):
    ax = Ax(bx, (-8, 215), (-80, 1450), pad=(70, 40, 50, 150)); _axes(d, ax, 'q', 'C')
    C = lambda q: 100 + 10 * q - 0.02 * q * q
    Cp = lambda q: 10 - 0.04 * q
    ax.curve(d, C, 0, 210, acc, 7)
    q = _seq(s, [(1, 20), (7, 100)])
    _tangent(d, ax, C, Cp, q, 45, GREEN)
    ax.dashed(d, q, 0, q, C(q), (255, 255, 255, 90))
    ax.dot(d, q, C(q), GOLD, 12)
    if s < 8.8: ax.text(d, q, -45, f'q = {q:.0f}', 18, GOLD)
    panel(d, bx, ['C(q) = 100 + 10q − 0.02q²', f"C'(q) = {Cp(q):.2f}", f'C(q+1) − C(q) = {C(q + 1) - C(q):.2f}'], s, 1, size=21, y=30, right=False)
    if s > 9: label(d, bx, 'עלות שולית = עלות הפריט הבא', s, 9, 23, GOLD, y=bx.h - 86)
    if s > 9.4: label(d, bx, "MC(q) ≈ C'(q)", s, 9.4, 24, GREEN, y=bx.h - 34)

# ---------------------------------------------------------------- average cost
def sc_avg_cost(d, bx, s, acc):
    ax = Ax(bx, (-1, 21), (-30, 520), pad=(70, 40, 50, 150)); _axes(d, ax, 'q', 'C')
    C = lambda q: 100 + q * q
    ax.curve(d, C, 0, 20.5, acc, 7)
    q = _seq(s, [(1, 3), (6, 18), (9.5, 10)])
    ac, mc = C(q) / q, 2 * q
    X0, Y0 = ax.T(0, 0)
    ax.line(d, 0, 0, 21, ac * 21, alpha(GOLD, 0.9), 4)
    _tangent(d, ax, C, lambda x: 2 * x, q, 3.5, GREEN, 5)
    ax.dot(d, 0, 0, GOLD, 8); ax.dot(d, q, C(q), WHITE, 11)
    panel(d, bx, ['שיפוע הקרן מהראשית = AC', f'AC = C/q = {ac:.1f}', f"MC = C'(q) = {mc:.1f}"], s, 1, size=21, y=30, right=True)
    if s > 10.3: label(d, bx, 'AC מינימלי (20) ב־q = 10', s, 10.3, 23, GOLD, y=bx.h - 86)
    if s > 10.7: label(d, bx, 'שם הקרן משיקה לגרף: AC = MC', s, 10.7, 22, GREEN, y=bx.h - 34)

# ---------------------------------------------------------------- profit: MR = MC
def sc_profit(d, bx, s, acc):
    ax = Ax(bx, (-1, 41), (-30, 450), pad=(70, 40, 50, 150)); _axes(d, ax, 'q', '₪')
    R = lambda q: 40 * q - q * q
    C = lambda q: 100 + 4 * q
    ax.curve(d, R, 0, 40, GREEN, 7); ax.curve(d, C, 0, 40, RED, 7)
    ax.text(d, 33, R(33) + 40, 'R', 22, GREEN); ax.text(d, 38, C(38) + 35, 'C', 22, RED)
    q = _seq(s, [(1.5, 4), (6, 34), (9.5, 18)])
    if R(q) > C(q):
        ax.line(d, q, C(q), q, R(q), GOLD, 10)
    else:
        ax.line(d, q, R(q), q, C(q), alpha(RED, 0.5), 10)
    _tangent(d, ax, R, lambda x: 40 - 2 * x, q, 6, (255, 255, 255, 200), 4)
    ax.dot(d, q, R(q), WHITE, 10); ax.dot(d, q, C(q), WHITE, 10)
    panel(d, bx, [f'רווח P = R − C = {R(q) - C(q):.0f}', f'MR = 40 − 2q = {40 - 2 * q:.1f}', 'MC = 4'], s, 1, size=21, y=30, right=True)
    if s > 10.3: label(d, bx, 'רווח מקסימלי (224) ב־q = 18', s, 10.3, 23, GOLD, y=bx.h - 86)
    if s > 10.7: label(d, bx, 'שם המשיקים מקבילים: MR = MC', s, 10.7, 22, WHITE, y=bx.h - 34)

# ---------------------------------------------------------------- elasticity of demand
def sc_elasticity(d, bx, s, acc):
    ax = Ax(bx, (-2, 52), (-0.8, 14.5), pad=(70, 40, 50, 150)); _axes(d, ax, 'p', 'R')
    R = lambda p: p * (1000 - 20 * p) / 1000  # thousands
    p = _seq(s, [(1.5, 5), (6.5, 45), (10, 25)])
    for a, b, c in ((0, 25, GREEN), (25, 50, RED)):
        ax.curve(d, R, a, b, c, 7)
    ax.dashed(d, 25, 0, 25, 12.5, (255, 255, 255, 80))
    ax.dot(d, p, R(p), WHITE, 12)
    E = 20 * p / (1000 - 20 * p)
    ax.text(d, 12, 3.2, 'לא גמיש', 21, GREEN); ax.text(d, 38, 3.2, 'גמיש', 21, RED)
    panel(d, bx, ['q = 1000 − 20p', f'p = {p:.1f}', f'E = |p/q · dq/dp| = {E:.2f}'], s, 1, size=21, y=30, right=True)
    if s > 10.4: label(d, bx, 'E = 1 בדיוק בשיא ההכנסה (p = 25)', s, 10.4, 22, GOLD, y=bx.h - 86)
    if s > 10.8: label(d, bx, 'E < 1: העלאת מחיר מגדילה הכנסה', s, 10.8, 21, GREEN, y=bx.h - 34)

# ---------------------------------------------------------------- continuous compounding
def sc_compound(d, bx, s, acc):
    P, r, t = 1000, 0.05, 10
    items = [('שנתי', 1), ('רבעוני', 4), ('חודשי', 12), ('יומי', 365), ('רציף', 0)]
    lo, hi = 1600, 1655
    ax = Ax(bx, (0, 5.4), (lo, 1688)); ax.draw(d, ticks=False, labels=('', ''))
    for i, (nm, n) in enumerate(items):
        a = ph(s, 1 + i * 1.6, 2.2 + i * 1.6)
        if a <= 0: continue
        val = P * math.exp(r * t) if n == 0 else P * (1 + r / n) ** (n * t)
        h = lerp(lo, val, a)
        x0, x1 = 0.35 + i * 1.0, 0.95 + i * 1.0
        p0, p1 = ax.T(x0, h), ax.T(x1, lo)
        col = GOLD if n == 0 else BLUE
        d.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=col[:3] + (200,))
        ax.text(d, (x0 + x1) / 2, h + 3.2, f'{val:,.2f}' if a > 0.95 else '', 17, WHITE)
        ax.text(d, (x0 + x1) / 2, lo - 3.5, nm, 18, col)
    panel(d, bx, ['1000 ש״ח, 5% לשנה, 10 שנים', 'A = P(1 + r/n)ⁿᵗ'], s, 0.5, size=21, y=20, right=True)
    panel(d, bx, ['רציף (n → ∞):  A = P·eʳᵗ', 'הציר האנכי מתחיל ב־1600'], s, 9.6, size=21, y=140, right=True, col=GRAY)

# ---------------------------------------------------------------- net change: integral of MC
def sc_net_change(d, bx, s, acc):
    ax = Ax(bx, (-8, 215), (-1, 12), pad=(70, 40, 50, 150)); _axes(d, ax, 'q', 'MC')
    MC = lambda q: 10 - 0.04 * q
    x1 = lerp(50, 100, ph(s, 2, 8))
    ax.area(d, MC, 50, x1, (255, 214, 10, 120))
    ax.curve(d, MC, 0, 210, acc, 7)
    for q in (50, 100): ax.text(d, q, -0.55, str(q), 18, WHITE)
    ax.dot(d, x1, MC(x1), WHITE, 10)
    area = (10 * x1 - 0.02 * x1 * x1) - (500 - 50)
    panel(d, bx, ["MC(q) = C'(q) = 10 − 0.04q", f'השטח = {area:.0f} ש״ח'], s, 1, size=21, y=30, right=True)
    if s > 9: label(d, bx, 'C(100) − C(50) = 350', s, 9, 24, GOLD, y=bx.h - 86)
    if s > 9.4: label(d, bx, 'שטח מתחת לעלות השולית = תוספת העלות', s, 9.4, 21, WHITE, y=bx.h - 34)

# ---------------------------------------------------------------- consumer & producer surplus
def sc_surplus(d, bx, s, acc):
    ax = Ax(bx, (-4, 165), (-5, 108)); _axes(d, ax, 'q', 'p')
    dem = lambda q: 100 - 0.5 * q
    sup = lambda q: 20 + 0.3 * q
    k = ph(s, 0.5, 3)
    ax.curve(d, dem, 0, 160 * k + 0.01, BLUE, 7); ax.curve(d, sup, 0, 160 * k + 0.01, RED, 7)
    if s > 3:
        a = ph(s, 3, 4)
        ax.dashed(d, 0, 50, 100, 50, alpha(WHITE, a)); ax.dashed(d, 100, 0, 100, 50, alpha(WHITE, a))
        ax.dot(d, 100, 50, alpha(GOLD, a), 12)
        ax.text(d, 112, 56, '(100, 50)', 18, alpha(GOLD, a))
    c1 = ph(s, 4.5, 7.5)
    if c1 > 0: ax.area(d, dem, 0, 100 * c1, (10, 132, 255, 120), base=50)
    c2 = ph(s, 8, 11)
    if c2 > 0:
        ax.area(d, sup, 0, 100 * c2, (255, 69, 58, 110), base=50)
    ax.text(d, 150, dem(150) + 8, 'ביקוש', 19, BLUE); ax.text(d, 150, sup(150) + 8, 'היצע', 19, RED)
    lines = ['שיווי משקל: q* = 100, p* = 50']
    if s > 6: lines.append('עודף צרכן = 2500')
    if s > 10: lines.append('עודף יצרן = 1500')
    panel(d, bx, lines, s, 3.5, size=21, y=20, right=True)

# ---------------------------------------------------------------- present value of an income stream
def sc_income_stream(d, bx, s, acc):
    ax = Ax(bx, (-0.4, 10.6), (-0.8, 11.5), pad=(70, 40, 50, 150)); _axes(d, ax, 't', 'אלפי ש״ח')
    r = 0.05
    k = ph(s, 4, 8)
    n = int(min(10, max(0, (s - 0.5) * 3)))
    for i in range(n):
        h = 10 * lerp(1, math.exp(-r * (i + 0.5)), k)
        p0, p1 = ax.T(i + 0.1, h), ax.T(i + 0.9, 0)
        d.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=(10, 132, 255, 150))
    if k > 0:
        ax.curve(d, lambda t: 10 * math.exp(-r * t), 0, 10, alpha(GOLD, k), 5)
        ax.dashed(d, 0, 10, 10, 10, (255, 255, 255, 90))
    pv = 10 * (1 - math.exp(-0.5)) / 0.05  # thousands
    lines = ['10,000 ש״ח בשנה, 10 שנים', f'סה״כ: {lerp(100, pv, k):.1f} אלף']
    panel(d, bx, lines, s, 1, size=21, y=20, right=True)
    if s > 9: label(d, bx, 'PV = ∫ F(t)·e^(−rt) dt ≈ 78,694', s, 9, 22, GOLD, y=bx.h - 86)
    if s > 9.4: label(d, bx, 'כסף עתידי שווה פחות היום', s, 9.4, 22, WHITE, y=bx.h - 34)

# ---------------------------------------------------------------- optimal ticket price (revenue)
def sc_ticket(d, bx, s, acc):
    ax = Ax(bx, (-4, 175), (-4, 80), pad=(70, 40, 50, 150)); _axes(d, ax, 'p', 'R')
    R = lambda p: (1700 * p - 10 * p * p) / 1000
    ax.curve(d, R, 0, 170, acc, 7)
    p = _seq(s, [(1.5, 50), (5, 130), (9, 85)])
    _tangent(d, ax, R, lambda x: (1700 - 20 * x) / 1000, p, 28, GREEN)
    ax.dashed(d, p, 0, p, R(p), (255, 255, 255, 90))
    ax.dot(d, p, R(p), GOLD, 12)
    ax.text(d, p, -2.4, f'{p:.0f}', 18, GOLD)
    q = 1700 - 10 * p
    panel(d, bx, ['q = 1700 − 10p', f'כרטיסים: {q:.0f}', f'הכנסה: {p * q:,.0f}'], s, 1, size=21, y=20, right=True)
    if s > 9.6: label(d, bx, "R'(p) = 1700 − 20p = 0", s, 9.6, 23, GREEN, y=bx.h - 86)
    if s > 10: label(d, bx, 'מחיר אופטימלי: 85 ← הכנסה 72,250', s, 10, 22, GOLD, y=bx.h - 34)

BIZ = {k[3:]: v for k, v in globals().items() if k.startswith('sc_')}
