#!/usr/bin/env python3
"""Draw scene.svg — a frame of 35mm film holding a starfield.

    python3 scripts/make_scene.py

Everything is generated here and committed; nothing is fetched at page load and
nothing runs on a schedule.

On what this can and cannot do
------------------------------
The brief was a different scene on every reload, and on GitHub that is not
reachable. Choosing at random needs either a script, which GitHub strips out of
READMEs, or a server, which is the thing this repository exists to avoid. SMIL
has no source of randomness and no access to the wall clock; every timeline
starts at zero when the image loads, so anything driven by it is identical on
every visit.

What SMIL can do is run continuously, so the scene is built to be looked at
rather than reloaded: three depths of star drift at their own speeds, every
star keeps its own twinkle, a nebula breathes, and a comet crosses about every
eighteen seconds. Nothing in it ever lands on the same arrangement twice within
a loop long enough that you will not catch it repeating.

Every element rests visible or rests off-frame, so a renderer that ignores SMIL
shows a still starfield rather than an empty rectangle.
"""
import math
import random

import svgkit as kit

COLS, ROWS = 156, 62
CHAR_W = 4.0
FONT = CHAR_W / kit.ADVANCE            # 0.600 em advance, so this is exact
LINE_H = FONT

MARGIN = 18.0
BAND = 22.0
REBATE = 24.0
HOLE_W, HOLE_H, PITCH = 15.0, 11.0, 33.0

NAME = "RAFATH0SSAIN"
MARKS = "▸ 25   ▸ 25A   ▸ 26"

SEED = 20260822

FW, FH = COLS * CHAR_W, ROWS * LINE_H
W = FW + 2 * MARGIN
H = BAND + FH + REBATE + BAND
FX, FY = MARGIN, BAND

# Planet: placed low and right, running off the bottom edge so the frame reads
# as a crop of something bigger rather than a diagram centred in a box.
PCX, PCY = 108.0, 36.0                 # in cells
PR = 88.0                              # radius in px
# Lit from the upper left and mostly from the side. Pointing the light at the
# viewer instead puts the terminator off the edge of the disc, and the sphere
# flattens into a plate: half of it saturates to solid block and the falloff
# that reads as roundness never happens.
LIGHT = (-0.58, -0.40, 0.42)
GAMMA = 1.45                           # spreads the lit end so the highlight stays small
RING_A = 1.95 * PR                     # semi-major, px
RING_TILT = 0.36                       # semi-minor as a fraction of the major
RING_IN = 0.86                         # inner edge, as a fraction of the outer

SHADE = " ░▒▓█"                        # the page's own blocks, five steps


def cell_px(dx, dy):
    return dx * CHAR_W, dy * LINE_H


def blank():
    return [[" "] * COLS for _ in range(ROWS)]


def in_planet(dx, dy):
    px, py = cell_px(dx, dy)
    return (px * px + py * py) <= PR * PR


def draw_world():
    """The planet and its ring, in one pass because they occlude each other.

    Returns (body, front): the sphere with the ring's far side already merged
    behind it, and separately the near side of the ring, which is drawn over
    the disc afterwards. Splitting on whether a cell is above or below the
    planet's centre is what makes it a ring rather than a hoop painted on the
    sky."""
    lx, ly, lz = LIGHT
    n = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / n, ly / n, lz / n
    a = RING_A
    b = a * RING_TILT
    body, front = blank(), blank()
    for r in range(ROWS):
        for c in range(COLS):
            dx, dy = c - PCX, r - PCY
            px, py = cell_px(dx, dy)
            rr = (px * px + py * py) / (PR * PR)
            rho = math.sqrt((px / a) ** 2 + (py / b) ** 2)
            on_ring = RING_IN <= rho <= 1.0
            if rr <= 1.0:
                nx, ny = px / PR, py / PR
                nz = math.sqrt(max(0.0, 1.0 - rr))
                lam = nx * lx + ny * ly + nz * lz
                if lam <= 0.04:
                    # the limb still catches a little light, which stops the
                    # unlit side from vanishing into the stars entirely
                    if rr > 0.93 and lam > -0.20:
                        body[r][c] = SHADE[1]
                else:
                    body[r][c] = SHADE[min(len(SHADE) - 1,
                                           1 + int((lam ** GAMMA) * 3.999))]
                if on_ring and py > 0:
                    front[r][c] = "─"
            elif on_ring:
                body[r][c] = "─"
    return body, front


def draw_nebula(rng):
    """Low, soft cloud in the upper left, from a handful of summed sines. Noise
    would be more correct and much harder to keep reproducible."""
    grid = blank()
    waves = [(rng.uniform(0.05, 0.14), rng.uniform(0.10, 0.26), rng.uniform(0, 6.3))
             for _ in range(4)]
    for r in range(ROWS):
        for c in range(COLS):
            v = 0.0
            for fx, fy, ph in waves:
                v += math.sin(c * fx + r * fy + ph)
            v /= len(waves)
            fade = max(0.0, 1.0 - ((c / 62.0) ** 2 + (r / 34.0) ** 2) ** 0.5)
            v = (v * 0.5 + 0.5) * fade
            if v > 0.46:
                grid[r][c] = "░" if v < 0.58 else "▒"
    return grid


def stars(rng, count, chars, avoid):
    out = []
    for _ in range(count):
        c = rng.randrange(COLS)
        r = rng.randrange(ROWS)
        if avoid and in_planet(c - PCX, r - PCY):
            continue
        out.append((c, r, rng.choice(chars),
                    rng.uniform(2.6, 7.4),        # twinkle period
                    rng.uniform(0.0, 7.4)))       # phase, applied as -begin
    return out


def runs(grid):
    """Rows of the grid as (row, col, text) with the blanks dropped, so a
    mostly-empty starfield does not ship thousands of spaces."""
    for r in range(ROWS):
        c = 0
        while c < COLS:
            if grid[r][c] == " ":
                c += 1
                continue
            s = c
            while c < COLS and grid[r][c] != " ":
                c += 1
            yield r, s, "".join(grid[r][s:c])


def text_rows(grid, cls):
    out = []
    for r, c, s in runs(grid):
        out.append('<text class="%s" xml:space="preserve" x="%.1f" y="%.2f">%s</text>'
                   % (cls, FX + c * CHAR_W, FY + LINE_H * (r + 0.8), kit.esc(s)))
    return "".join(out)


def perforations(y):
    out, x = [], -PITCH / 2.0
    while x < W + PITCH:
        out.append('M%.1f %.1f h%.1f a2.5 2.5 0 0 1 2.5 2.5 v%.1f '
                   'a2.5 2.5 0 0 1 -2.5 2.5 h-%.1f '
                   'a2.5 2.5 0 0 1 -2.5 -2.5 v-%.1f a2.5 2.5 0 0 1 2.5 -2.5 Z'
                   % (x + 2.5, y, HOLE_W - 5, HOLE_H - 5, HOLE_W - 5, HOLE_H - 5))
        x += PITCH
    return " ".join(out)


def drift(dx, dy, secs):
    """A slow there-and-back. A one-way loop would need the layer to tile, and
    a starfield that tiles stops looking like a sky."""
    return ('<animateTransform attributeName="transform" type="translate" '
            'values="0 0;%.2f %.2f;0 0" dur="%.0fs" repeatCount="indefinite"/>'
            % (dx, dy, secs))


def build():
    rng = random.Random(SEED)
    neb = draw_nebula(rng)
    far = stars(rng, 150, ".··", True)
    mid = stars(rng, 60, "·*+", True)
    near = stars(rng, 16, "*+✦", True)
    planet, ring_front = draw_world()

    css = kit.theme_css(
        kit.font_face(" .·*+✦░▒▓█─", "Regular", 400)
        + kit.font_face(NAME + MARKS + " ", "SemiBold", 600)
        + ".film{fill:var(--ink);fill-opacity:.10;fill-rule:evenodd}"
        + ".gate{fill:none;stroke:var(--rule);stroke-width:1}"
        + "text{font-family:'JBMono',monospace;font-size:%gpx;fill:var(--ink);"
          "white-space:pre}" % FONT
        + ".neb{opacity:.26}.far{opacity:.58}.mid{opacity:.80}.near{opacity:1}"
        + ".pl{opacity:.92}.rg{opacity:.55}.cm{opacity:.9}"
        # Light on a dark ground blooms, so the solid areas are held back there
        # for the same reason the portrait's dark exposure was.
        + "@media (prefers-color-scheme:dark){.pl{opacity:.74}.neb{opacity:.16}"
          ".far{opacity:.40}.mid{opacity:.66}}"
        + ".edge{font-family:'JBMono',monospace;font-size:8px;font-weight:600;"
          "fill:var(--dim);letter-spacing:1.6px}"
    )

    out = [kit.svg_open(W, H,
                        "A frame of 35mm film holding a starfield: a ringed "
                        "planet lit from the left, drifting stars, and a comet "
                        "crossing the frame"),
           "<defs><style>", css, "</style>",
           '<clipPath id="gate"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
           "</clipPath></defs>" % (FX, FY, FW, FH),
           '<g clip-path="url(#gate)">']

    out.append('<g class="neb">%s%s</g>' % (text_rows(neb, "neb"), drift(5, 2, 90)))

    for cls, group, dx, dy, secs in (("far", far, 3.0, 1.2, 120),
                                     ("mid", mid, 6.0, 2.4, 80),
                                     ("near", near, 11.0, 4.0, 55)):
        parts = ['<g class="%s">' % cls]
        for c, r, ch, per, ph in group:
            parts.append(
                '<text x="%.1f" y="%.2f">%s'
                '<animate attributeName="opacity" values="1;.28;1" dur="%.2fs" '
                'begin="-%.2fs" repeatCount="indefinite"/></text>'
                % (FX + c * CHAR_W, FY + LINE_H * (r + 0.8), ch, per, ph))
        parts.append(drift(dx, dy, secs))
        parts.append("</g>")
        out.append("".join(parts))

    out.append('<g class="pl">%s%s<animateTransform attributeName="transform" '
               'type="translate" values="0 0;0 -1.4;0 0" dur="46s" '
               'repeatCount="indefinite"/></g>'
               % (text_rows(planet, "pl"),
                  '<g class="rg">%s</g>' % text_rows(ring_front, "rg")))

    # the comet: one pass every eighteen seconds, clear of the frame the rest
    comet = ('<text x="0" y="0">✦</text>'
             '<text x="-14" y="-3" opacity=".55">···</text>'
             '<text x="-34" y="-7" opacity=".25">··</text>')
    out.append(
        '<g class="cm" transform="translate(-60,%.1f)">%s'
        '<animateTransform attributeName="transform" type="translate" '
        'values="-60 %.1f;760 %.1f;760 %.1f" keyTimes="0;0.22;1" dur="18s" '
        'repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;.9;.9;0;0" '
        'keyTimes="0;0.03;0.18;0.22;1" dur="18s" repeatCount="indefinite"/></g>'
        % (FY + 60, comet, FY + 60, FY + 210, FY + 210))

    out.append("</g>")

    strip = ("M0 0H%.1f V%.1f H0 Z " % (W, H)
             + "M%.1f %.1f H%.1f V%.1f H%.1f Z " % (FX, FY, FX + FW, FY + FH, FX)
             + perforations((BAND - HOLE_H) / 2.0) + " "
             + perforations(H - BAND + (BAND - HOLE_H) / 2.0))
    out.append('<path class="film" d="%s"/>' % strip)
    out.append('<rect class="gate" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
               % (FX + .5, FY + .5, FW - 1, FH - 1))

    ey = BAND + FH + REBATE * 0.62
    out.append('<text class="edge" x="%.1f" y="%.1f">%s</text>' % (FX, ey, NAME))
    out.append('<text class="edge" text-anchor="end" x="%.1f" y="%.1f">%s</text>'
               % (FX + FW, ey, kit.esc(MARKS)))
    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    kit.write("scene.svg", build())
