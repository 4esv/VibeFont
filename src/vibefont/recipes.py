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
    g.erase(111, 60, 180, 460)  # arch spring, flush with the stem
    return g


def lc_i(p, m):
    g = Glyph(m, 180)
    g.paste(_limb_n(p), 0)
    g.erase(111, 60, 180, 360)  # arch spring (n's head flag stays left of it)
    g.fill_ellipse(91, m.xh + (m.asc - m.xh) * 0.42, 34)
    return g


def lc_j(p, m):
    g = Glyph(m, 260)
    stem = p.cut("n", 0, 171, 55).vstretch(round(m.xh + 8 + 165), keep=90,
                                           anchor="top")
    g.paste(stem, 60)
    g.erase(179, -100, 260, 360)
    # tail sweeps left below the stem, finished with a ball terminal
    # centered on the tail's end edge so the join doesn't kink
    g.fill_poly([(124, -110), (179, -145), (120, -212), (72, -180)])
    g.fill_ellipse(94, -194, 34, 30)
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
    # slant erase starts left of the shaft's left edge, else a barb of
    # full-height shaft survives beside the cut
    g.erase_poly([(-12, 600), (-12, 372), (118, 460), (118, 600)])
    bar = _ebar(p)
    g.paste(bar, 0, dy=m.xh - 232)
    return g


def lc_f(p, m):
    g = Glyph(m, 300)
    # stop the shaft cut at 450 so none of h's head flag survives vstretch
    shaft = p.cut("h", 0, 171, -6, 450).vstretch(516, keep=120)
    g.paste(shaft, 0)
    g.erase(111, 60, 300, 430)  # arch spring, flush with the stem
    g.paste(_arm_r(p), 116, dy=230)  # hook crowns near ascender height
    g.paste(_ebar(p), 10, dy=m.xh - 232)
    return g


def lc_k(p, m):
    # Drawn strokes like x (rotating v scrambles its serifs into a bar);
    # thick leg, thin arm, dressed with v's serif and h's foot.
    g = Glyph(m, 420)
    g.paste(_limb_h(p), 0)
    g.erase(111, 60, 420, 460)  # arch spring, flush with the stem
    g.fill_poly([(95, 205), (162, 205), (330, 25), (263, 25)])   # leg
    g.fill_poly([(95, 225), (130, 225), (285, 332), (254, 332)])  # arm
    # serif slab cut past v's curled tip (it floats over the arm as a tick)
    g.paste(p.cut("v", 262, 385, 305, 345), 204)  # arm serif + stroke tip
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
    # serif SLABS only — taller cuts drag along offset stroke fragments;
    # inner ends stop short of v's curled serif tips (they float as ticks)
    g.paste(p.cut("v", 0, 160, 325, 345), 20)      # top-left serif
    g.paste(p.cut("v", 258, 385, 325, 345), 253)   # top-right serif
    g.paste(_hfoot(p).scaled(0.7), 290)            # BR foot
    g.paste(_hfoot(p).scaled(0.7), 5)              # BL foot
    return g


def lc_y(p, m):
    g = Glyph(m, 420)
    g.paste(p.cut("v"), 30)
    # thin stroke continues through the apex into the descender,
    # finished with a ball terminal centered on the tail's end edge
    g.fill_poly([(212, 60), (252, 60), (165, -140), (125, -140)])
    g.fill_ellipse(142, -152, 36, 30)
    return g


def lc_z(p, m):
    # NOTE: scaling the arms by xh/cap (0.64) thins them to a 13px hairline
    # that detaches from the diagonal; 0.8 keeps believable bar weight and
    # the bars are repositioned so the top edge still lands at the x-height.
    s = 0.8
    g = Glyph(m, 320)
    top = p.cut("E", 150, 400, 440, 535).flip_h().scaled(1.18, s)
    bot = p.cut("E", 140, 401, -7, 60).scaled(1.13, s)
    g.paste(top, 0, dy=m.xh - 535 * s)
    g.paste(bot, 25)
    g.erase(283, 200, 302, m.xh - 28)  # stem-fillet needle at the cut edge
    # diagonal tops inside the bar (xh-10) so the seam can't crack open
    g.fill_poly([(225, m.xh - 10), (295, m.xh - 10), (95, 30), (25, 30)])
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
    g.erase(129, 150, 230, 360)  # crossbar, flush with the stem
    return g


def cap_J(p, m):
    g = Glyph(m, 420)
    g.paste(p.cut("U", 0, 380).flip_h(), 0)
    return g


def cap_C(p, m):
    # G minus bar and spur. The lower arc keeps its natural rise into the
    # (removed) spur base, chopped to stroke height: an upturned beak.
    # The upper arc is sheared vertically where it dove toward the bar.
    g = Glyph(m, 570)
    g.paste(p.cut("G"), 0)
    g.erase(312, 90, 570, 270)   # bar, spur head serif, both wings
    g.erase(460, -20, 570, 90)   # spur base right of the beak
    g.erase(462, 250, 570, 560)  # upper terminal shear
    return g


def cap_D(p, m):
    g = Glyph(m, 580)
    g.paste(_limb_H(p), 0)
    g.erase(129, 150, 230, 360)  # flush with the stem: no crossbar sliver
    # unscaled half-O keeps the bowl at O's natural stroke weight; trim its
    # overshoot so the horizontals sit flush with the stem
    bowl = p.cut("O", 293, 585, -8, 531)
    g.paste(bowl, 280)
    # bridges taper to the bowl's thin cut ends (519 / 5 at the seam) so
    # neither underside steps
    g.fill_poly([(150, 531), (335, 531), (335, 512), (150, 503)])
    g.fill_poly([(150, 26), (335, 6), (335, -7), (150, -7)])
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
    g.erase(129, 150, 230, 360)  # crossbar, flush with the stem
    # strokes run INTO the stem (x 100 < stem right edge 128) so the waist
    # joins solid instead of hanging off the old crossbar sliver
    g.fill_poly([(100, 290), (230, 290), (470, 35), (390, 35)])    # leg
    g.fill_poly([(100, 295), (135, 295), (455, 520), (420, 520)])  # arm
    # serif slab cut past V's curled tip and landed on the arm: no float
    g.paste(p.cut("V", 445, 591, 485, 545), 410)  # arm serif
    g.paste(_Hfoot(p).scaled(0.85), 330)          # leg foot
    return g


def cap_P(p, m):
    g = Glyph(m, 480)
    g.paste(p.cut("R"), 0)
    g.erase(170, -25, 565, 235)  # leg
    # the leg's spring survives the chop as a tooth under the bowl; shave
    # it along the bowl's underside line into the right wall
    g.erase(243, -25, 342, 242)
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
    # stem reaches behind the bar fillets so their seam can't notch;
    # y0=-8 keeps the foot's baseline overshoot (T floated without it)
    stem = p.cut("H", 0, 230, -8, 510)
    g.paste(stem, 145)
    g.erase(296, 150, 380, 360)  # flush with the stem: no crossbar sliver
    bar = p.cut("E", 150, 400, 440, 535)
    g.paste(bar.flip_h(), 30)
    g.paste(bar, 280)
    # H's cupped head serif rides along beside the stem; shave the hanging
    # cup fragments so the bar underside runs flat
    g.erase(150, 420, 208, 502)
    g.erase(295, 420, 314, 502)
    return g


def cap_V_pair(p, m, dx):
    g = Glyph(m, 600 + dx)
    g.paste(p.cut("V"), 0)
    g.paste(p.cut("V"), dx)
    return g


def cap_W(p, m):
    # dx 300 keeps W near M's width (dx 380 made it 40% wider than M,
    # wrecking the caps' rhythm); the V's overlap in the classic
    # crossed-double-V form
    g = cap_V_pair(p, m, 300)
    # where the two middle serifs lap, the inner rising tips poke above
    # the shared cup and read as ticks; shave them so the dish runs smooth
    g.erase(426, 526, 472, 560)   # V1 right-serif left tip
    g.erase(488, 526, 532, 560)   # V2 left-serif right tip
    return g


def cap_X(p, m):
    g = Glyph(m, 560)
    g.fill_poly([(40, 530), (112, 530), (520, 0), (448, 0)])  # thick TL-BR
    g.fill_poly([(496, 530), (520, 530), (64, 0), (40, 0)])   # thin TR-BL
    g.paste(p.cut("V", 0, 230, 485, 545), 20)     # top-left serif
    g.paste(p.cut("V", 420, 591, 485, 545), 360)  # top-right serif
    # V's serif tips curl up where the cuts slice them; detached over the
    # diagonals they read as floating ticks -- shave both inner ends
    g.erase(226, 505, 252, 560)
    g.erase(352, 505, 380, 560)
    g.paste(_Hfoot(p).scaled(0.8), 380)           # BR foot
    g.paste(_Hfoot(p).scaled(0.8), -25)           # BL foot
    return g


def cap_Y(p, m):
    # v scaled up, not V cropped: v's apex is a solid point, so the fork
    # junction lands on the stem without a gap. Widened to cap proportions
    # (Y was 60% of V's width; the source caps keep a wide, even rhythm).
    g = Glyph(m, 560)
    g.paste(p.cut("v").scaled(1.24, 0.97), 25, dy=208)
    g.paste(p.cut("H", 0, 156, 0, 260), 175)  # bare stem, no crossbar nub
    g.paste(_Hfoot(p), 175)
    # fillet the fork-stem junction: the left arm sweeps into the stem
    # base and the right arm's underside meets the stem top without a slit
    g.fill_poly([(245, 200), (262, 60), (318, 60), (322, 285)])
    return g


def cap_Z(p, m):
    # Unscaled E arms keep their end flags crisp; plain rects bridge the
    # bar middles (stretching the arms smears the flags).
    g = Glyph(m, 480)
    g.paste(p.cut("E", 150, 400, 440, 535).flip_h(), 0)   # flag at left
    g.erase(242, 430, 258, 499)  # stem-fillet needle at the arm's cut edge
    # arm stroke top sits at 524 by its cut edge; slope up to meet the
    # diagonal's 531 corner so neither seam ledges
    g.fill_poly([(225, 524), (470, 531), (470, 500), (225, 500)])
    g.paste(p.cut("E", 140, 401, -7, 60), 209)            # flag at right
    g.erase(205, 36, 240, 110)   # same fillet, other arm, poking up
    g.fill_poly([(30, 34), (240, 34), (240, 0), (30, 0)])
    # 80px horizontal width ~= the 64px capital stem once the ~36deg slope
    # is accounted for (80 * cos 36); wider reads as a bolder glyph
    g.fill_poly([(390, 528), (470, 528), (110, 30), (30, 30)])
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
