"""Per-letter derivation recipes: hamburgevons parts -> the rest.

Every constant in here is image-space pixels measured off the reference
sample sheet (cap 530, x-height 339, lowercase stem 55, capital stem 64)
and scaled through the Metrics ratios where glyph size differs. Recipes
were tuned visually against proof renders; they are design decisions, not
derivations.
"""

from vibefont.derive import Glyph, Metrics, Parts


# ---------------------------------------------------------------- lowercase

def _limb_h(p: Parts):
    """h's left limb: ascender stem, head flag, foot serif."""
    return p.cut("h", 0, 171)


def _limb_n(p: Parts):
    """n's left limb: x-height stem with head flag and foot serif."""
    return p.cut("n", 0, 171)


def _arm_r(p: Parts):
    """r's arm: arc with teardrop terminal, cut just off the stem."""
    return p.cut("r", 119, 265, 250, 355)


def _ebar(p: Parts):
    """e's crossbar."""
    return p.cut("e", 8, 246, 188, 232)


def _hfoot(p: Parts):
    """h's foot serif slab with stem stump."""
    return p.cut("h", 0, 171, -6, 60)


def lc_l(p, m):
    g = Glyph(m, 180)
    g.paste(_limb_h(p), 0)
    g.erase(119, 60, 180, 460)  # arch spring nub
    return g


def lc_i(p, m):
    g = Glyph(m, 180)
    g.paste(_limb_n(p), 0)
    g.erase(119, 60, 180, 360)  # arch spring (n's head flag stays left of it)
    g.fill_ellipse(91, m.xh + (m.asc - m.xh) * 0.42, 34)
    return g


def lc_j(p, m):
    g = Glyph(m, 260)
    stem = p.cut("n", 0, 171, 55).vstretch(round(m.xh + 8 + 165), keep=90,
                                           anchor="top")
    g.paste(stem, 60)
    g.erase(179, -100, 260, 360)
    # tail sweeps left below the stem, finished with a ball terminal
    g.fill_poly([(124, -110), (179, -145), (120, -212), (72, -180)])
    g.fill_ellipse(82, -180, 36, 31)
    g.fill_ellipse(151, m.xh + (m.asc - m.xh) * 0.42, 34)
    return g


def lc_c(p, m):
    g = Glyph(m, 300)
    g.paste(p.cut("e"), 0)
    g.erase(64, 185, 232, 237)  # knock the eye's crossbar out
    return g


def lc_d(p, m):
    g = Glyph(m, 380)
    g.paste(p.cut("b").flip_h(), 0)
    # Replace the whole mirrored apex with h's: erase everything above the
    # join zone, then graft a flag piece deep enough to overlap the stem.
    g.erase(0, 470, 380, 660)
    flag = p.cut("h", 0, 135, 440, 615)
    g.paste(flag, 262 - 64)  # h stem left 64 -> flipped-b stem left 262
    return g


def lc_p(p, m):
    g = Glyph(m, 380)
    g.paste(p.cut("b", 0, None, -16, 352), 0)  # bowl + bare stem stump
    # b's baseline foot serif doesn't belong mid-descender: shave the left
    # wing and the slab under the stem (the bowl-stem join stays).
    g.erase(0, -20, 55, 42)
    g.erase(0, -20, 113, 14)
    g.paste(p.cut("n", 0, 130, 250, 352), -8)  # head flag
    g.paste(p.cut("h", 0, 171, -6, 242), -8, dy=-m.desc)  # descender + foot
    return g


def lc_q(p, m):
    g = Glyph(m, 380)
    g.paste(p.cut("b", 0, None, -16, 352).flip_h(), 0)
    g.erase(319, -20, 374, 42)   # mirrored foot wing (see lc_p)
    g.erase(261, -20, 374, 14)
    g.erase(258, 336, 330, 380)  # flat stem stub above the bowl join
    # dress the stem top with u's small angled right-stem head
    g.paste(p.cut("u", 285, 345, 318, 348), 275)
    g.paste(p.cut("h", 0, 171, -6, 242), 262 - 64, dy=-m.desc)
    return g


def lc_t(p, m):
    g = Glyph(m, 260)
    # cut below u's head flag (starts ~y280) so no fragment rides the
    # stretch; x to 255 keeps the bottom terminal's natural rising taper
    shaft = p.cut("u", 40, 255, -16, 278)
    shaft = shaft.vstretch(486, keep=110)
    g.paste(shaft, -10)  # leaves ~45px of crossbar to the left of the shaft
    g.erase_poly([(30, 600), (30, 380), (118, 460), (118, 600)])  # slant top
    bar = _ebar(p)
    g.paste(bar, 0, dy=m.xh - 232)
    return g


def lc_f(p, m):
    g = Glyph(m, 300)
    # stop the shaft cut at 450 so none of h's head flag survives vstretch
    shaft = p.cut("h", 0, 171, -6, 450).vstretch(516, keep=120)
    g.paste(shaft, 0)
    g.erase(119, 60, 300, 430)
    g.paste(_arm_r(p), 116, dy=230)  # hook crowns near ascender height
    g.paste(_ebar(p), 10, dy=m.xh - 232)
    return g


def lc_k(p, m):
    # Drawn strokes like x (rotating v scrambles its serifs into a bar);
    # thick leg, thin arm, dressed with v's serif and h's foot.
    g = Glyph(m, 420)
    g.paste(_limb_h(p), 0)
    g.erase(119, 60, 420, 460)
    g.fill_poly([(95, 205), (162, 205), (330, 25), (263, 25)])   # leg
    g.fill_poly([(95, 225), (130, 225), (285, 332), (254, 332)])  # arm
    g.paste(p.cut("v", 245, 385, 305, 345), 187)  # arm serif + stroke tip
    g.paste(_hfoot(p).scaled(0.85), 205)          # leg foot
    return g


def lc_w(p, m):
    g = Glyph(m, 640)
    g.paste(p.cut("v"), 0)
    g.paste(p.cut("v"), 230)
    return g


def lc_x(p, m):
    # Drawn diagonals (v's are too short to reach the corners cleanly),
    # dressed with v's own top serifs and h's feet.
    g = Glyph(m, 420)
    g.fill_poly([(30, 339), (96, 339), (380, 0), (314, 0)])   # thick TL-BR
    g.fill_poly([(354, 339), (380, 339), (56, 0), (30, 0)])   # thin TR-BL
    # serif SLABS only — taller cuts drag along offset stroke fragments
    g.paste(p.cut("v", 0, 175, 325, 345), 20)      # top-left serif
    g.paste(p.cut("v", 240, 385, 325, 345), 235)   # top-right serif
    g.paste(_hfoot(p).scaled(0.7), 290)            # BR foot
    g.paste(_hfoot(p).scaled(0.7), 5)              # BL foot
    return g


def lc_y(p, m):
    g = Glyph(m, 420)
    g.paste(p.cut("v"), 30)
    # thin stroke continues through the apex into the descender,
    # finished with a ball terminal
    g.fill_poly([(212, 60), (252, 60), (165, -140), (125, -140)])
    g.fill_ellipse(128, -148, 38, 32)
    return g


def lc_z(p, m):
    s = m.xh / m.cap
    g = Glyph(m, 320)
    # E arms scaled by xh/cap land the top bar's top edge at the x-height.
    top = p.cut("E", 150, 400, 440, 535).flip_h().scaled(1.18, s)
    bot = p.cut("E", 140, 401, -7, 60).scaled(1.13, s)
    g.paste(top, 0)
    g.paste(bot, 25)
    g.fill_poly([(225, m.xh - 25), (295, m.xh - 25), (95, 30), (25, 30)])
    return g


# ---------------------------------------------------------------- capitals

def _limb_H(p: Parts):
    """H's left limb: stem with cupped head and foot serifs."""
    return p.cut("H", 0, 230)


def _Hfoot(p: Parts):
    return p.cut("H", 0, 230, -8, 55)


def _Ihead(p: Parts):
    return p.cut("H", 0, 230, 465, 540)


def cap_I(p, m):
    g = Glyph(m, 230)
    g.paste(_limb_H(p), 0)
    g.erase(157, 150, 230, 360)  # crossbar stump
    return g


def cap_J(p, m):
    g = Glyph(m, 420)
    g.paste(p.cut("U", 0, 380).flip_h(), 0)
    return g


def cap_C(p, m):
    g = Glyph(m, 570)
    g.paste(p.cut("G"), 0)
    g.erase(315, -20, 570, 260)  # bar, spur, and the curve stub they fed
    return g


def cap_D(p, m):
    g = Glyph(m, 580)
    g.paste(_limb_H(p), 0)
    g.erase(157, 150, 230, 360)
    # unscaled half-O keeps the bowl at O's natural stroke weight; trim its
    # overshoot so the horizontals sit flush with the stem
    bowl = p.cut("O", 293, 585, -8, 531)
    g.paste(bowl, 280)
    # bridge the thin cut ends of the half-O back to the stem
    g.fill_poly([(150, 531), (300, 531), (300, 503), (150, 503)])
    g.fill_poly([(150, 26), (310, 26), (310, -7), (150, -7)])
    return g


def cap_F(p, m):
    g = Glyph(m, 410)
    g.paste(p.cut("E"), 0)
    g.erase(153, -10, 410, 110)  # bottom arm
    g.paste(p.cut("H", 156, 230, -8, 50), 153)  # restore right foot wing
    return g


def cap_L(p, m):
    g = Glyph(m, 410)
    g.paste(p.cut("E"), 0)
    g.erase(153, 200, 410, 340)  # middle arm
    g.erase(153, 420, 410, 540)  # top arm
    return g


def cap_K(p, m):
    g = Glyph(m, 560)
    g.paste(_limb_H(p), 0)
    g.erase(157, 150, 230, 360)
    g.fill_poly([(150, 290), (230, 290), (470, 35), (390, 35)])    # leg
    # arm runs into the serif slab so the join can't pinch
    g.fill_poly([(150, 295), (185, 295), (455, 520), (420, 520)])  # arm
    g.paste(p.cut("V", 420, 591, 485, 545), 365)  # arm serif
    g.paste(_Hfoot(p).scaled(0.85), 330)          # leg foot
    return g


def cap_P(p, m):
    g = Glyph(m, 480)
    g.paste(p.cut("R"), 0)
    g.erase(170, -25, 565, 235)  # leg
    g.paste(p.cut("H", 156, 230, -8, 50), 153)  # right foot wing
    return g


def cap_Q(p, m):
    g = Glyph(m, 640)
    g.paste(p.cut("O"), 0)
    tail = p.cut("R", 270, 565, -20, 240).scaled(1.0, 0.8)
    g.paste(tail, 300, dy=-60)
    return g


def cap_T(p, m):
    g = Glyph(m, 560)
    # stem reaches behind the bar fillets so their seam can't notch
    stem = p.cut("H", 0, 230, 0, 510)
    g.paste(stem, 145)
    g.erase(302, 150, 380, 360)
    bar = p.cut("E", 150, 400, 440, 535)
    g.paste(bar.flip_h(), 30)
    g.paste(bar, 280)
    return g


def cap_V_pair(p, m, dx):
    g = Glyph(m, 600 + dx)
    g.paste(p.cut("V"), 0)
    g.paste(p.cut("V"), dx)
    return g


def cap_W(p, m):
    return cap_V_pair(p, m, 380)


def cap_X(p, m):
    g = Glyph(m, 560)
    g.fill_poly([(40, 530), (112, 530), (520, 0), (448, 0)])  # thick TL-BR
    g.fill_poly([(496, 530), (520, 530), (64, 0), (40, 0)])   # thin TR-BL
    g.paste(p.cut("V", 0, 230, 485, 545), 20)     # top-left serif
    g.paste(p.cut("V", 420, 591, 485, 545), 360)  # top-right serif
    g.paste(_Hfoot(p).scaled(0.8), 380)           # BR foot
    g.paste(_Hfoot(p).scaled(0.8), -25)           # BL foot
    return g


def cap_Y(p, m):
    # v scaled up, not V cropped: v's apex is a solid point, so the fork
    # junction lands on the stem without a gap.
    g = Glyph(m, 440)
    g.paste(p.cut("v").scaled(0.95, 0.97), 60, dy=200)
    g.paste(p.cut("H", 0, 156, 0, 260), 120)  # bare stem, no crossbar nub
    g.paste(_Hfoot(p), 120)
    return g


def cap_Z(p, m):
    # Unscaled E arms keep their end flags crisp; plain rects bridge the
    # bar middles (stretching the arms smears the flags).
    g = Glyph(m, 480)
    g.paste(p.cut("E", 150, 400, 440, 535).flip_h(), 0)   # flag at left
    # arm stroke top sits at 524 by its cut edge; slope up to meet the
    # diagonal's 531 corner so neither seam ledges
    g.fill_poly([(225, 524), (470, 531), (470, 500), (225, 500)])
    g.paste(p.cut("E", 140, 401, -7, 60), 209)            # flag at right
    g.fill_poly([(30, 34), (240, 34), (240, 0), (30, 0)])
    g.fill_poly([(355, 528), (470, 528), (145, 30), (30, 30)])
    return g


# ------------------------------------------------------------- punctuation

def punct_period(p, m):
    g = Glyph(m, 90)
    g.fill_ellipse(45, 42, 42)
    return g


def punct_comma(p, m):
    g = Glyph(m, 90)
    g.fill_ellipse(48, 42, 40)
    g.fill_poly([(70, 35), (88, 60), (30, -105), (12, -75)])
    return g


def punct_hyphen(p, m):
    g = Glyph(m, 180)
    g.fill_poly([(0, 165), (180, 165), (180, 118), (0, 118)])
    return g


RECIPES = {
    "c": lc_c, "d": lc_d, "f": lc_f, "i": lc_i, "j": lc_j, "k": lc_k,
    "l": lc_l, "p": lc_p, "q": lc_q, "t": lc_t, "w": lc_w, "x": lc_x,
    "y": lc_y, "z": lc_z,
    "C": cap_C, "D": cap_D, "F": cap_F, "I": cap_I, "J": cap_J, "K": cap_K,
    "L": cap_L, "P": cap_P, "Q": cap_Q, "T": cap_T, "W": cap_W, "X": cap_X,
    "Y": cap_Y, "Z": cap_Z,
    ".": punct_period, ",": punct_comma, "-": punct_hyphen,
}


def derive_missing(sheet, chars):
    """Build (ink, GlyphBox) for every char in ``chars`` with a recipe."""
    m = Metrics.measure(sheet)
    p = Parts(sheet)
    return [RECIPES[c](p, m).result(c) for c in chars if c in RECIPES]
