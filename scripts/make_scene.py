#!/usr/bin/env python3
"""Draw scene.svg — a frame of 35mm film holding a turning planet.

    python3 scripts/make_scene.py

Everything is generated here and committed; nothing is fetched at page load and
nothing runs on a schedule.

On what this can and cannot do
------------------------------
The brief was a different scene on every reload, and on GitHub that is not
reachable. Choosing at random needs either a script, which GitHub strips out of
READMEs, or a server, which is the thing this repository exists to avoid. SMIL
has no source of randomness and no access to the wall clock; every timeline
starts at zero when the image loads.

So the scene is built to be looked at rather than reloaded: the planet turns,
three depths of star drift at their own speeds, every star keeps its own
twinkle, and four different craft cross on four different periods. None of the
periods divide into each other, so the arrangement takes a long time to repeat.

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

MARGIN, BAND, REBATE = 18.0, 22.0, 24.0
HOLE_W, HOLE_H, PITCH = 15.0, 11.0, 33.0

NAME = "RAFATH0SSAIN"
MARKS = "▸ 25   ▸ 25A   ▸ 26"
SEED = 20260823

FW, FH = COLS * CHAR_W, ROWS * LINE_H
W = FW + 2 * MARGIN
H = BAND + FH + REBATE + BAND
FX, FY = MARGIN, BAND

PCX, PCY = 108.0, 36.0                 # planet centre, in cells
PR = 88.0                              # radius, px
# Lit from the upper left and mostly from the side. Pointing the light at the
# viewer instead puts the terminator off the edge of the disc and the sphere
# flattens into a plate: half saturates to solid block and the falloff that
# reads as roundness never happens.
LIGHT = (-0.58, -0.40, 0.42)
GAMMA = 1.45
RING_A = 1.95 * PR
RING_TILT = 0.36                       # semi-minor as a fraction of the major
RING_IN = 0.86

SHADE = " ░▒▓█"
SPIN_FRAMES = 12
SPIN_SECS = 11.0

# The axis is tilted to match the ring, so the equator and the ring plane are
# the same plane — which is what they are on a real planet.
AXIS = math.asin(RING_TILT)

# Storms, as (latitude, longitude, size, strength). These are the only reason
# the spin is visible at all: banding runs along lines of latitude and looks
# identical however far the planet has turned, so a striped ball rotates
# without appearing to move. Something has to sit at a longitude.
SPOTS = [(-0.34, 0.7, 0.30, 0.30), (0.28, 2.6, 0.22, -0.26),
         (0.06, 4.4, 0.16, 0.24), (-0.55, 5.5, 0.18, -0.18)]

SPR_FONT = 9.0                         # craft are drawn larger than the grid


def blank():
    return [[" "] * COLS for _ in range(ROWS)]


def cell_px(dx, dy):
    return dx * CHAR_W, dy * LINE_H


def albedo(lat, lon):
    v = 1.0 + 0.15 * math.sin(lat * 5.2) + 0.06 * math.sin(lon * 3.0 + lat * 2.2)
    for slat, slon, size, amp in SPOTS:
        d = math.hypot(lat - slat,
                       math.atan2(math.sin(lon - slon), math.cos(lon - slon))
                       * math.cos(lat))
        v += amp * math.exp(-(d / size) ** 2)
    return max(0.55, min(1.35, v))


def planet_frame(rot):
    """The lit sphere at one rotation. The night side is left empty: a planet
    lit from one side is a crescent, and filling its dark half would turn it
    into a disc with a stripe on it."""
    lx, ly, lz = LIGHT
    n = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / n, ly / n, lz / n
    ca, sa = math.cos(AXIS), math.sin(AXIS)
    g = blank()
    for r in range(ROWS):
        for c in range(COLS):
            px, py = cell_px(c - PCX, r - PCY)
            rr = (px * px + py * py) / (PR * PR)
            if rr > 1.0:
                continue
            nx, ny = px / PR, py / PR
            nz = math.sqrt(max(0.0, 1.0 - rr))
            lam = nx * lx + ny * ly + nz * lz
            if lam <= 0.04:
                if rr > 0.93 and lam > -0.20:
                    g[r][c] = SHADE[1]
                continue
            y1 = ny * ca + nz * sa
            z1 = -ny * sa + nz * ca
            lat = math.asin(max(-1.0, min(1.0, y1)))
            lon = math.atan2(nx, z1) + rot
            t = min(1.0, lam * albedo(lat, lon)) ** GAMMA
            g[r][c] = SHADE[min(len(SHADE) - 1, 1 + int(t * 3.999))]
    return g


def rings():
    """(outside, over) — the part of the ring clear of the disc, and the part
    that crosses in front of it. Splitting on whether a cell sits above or
    below the planet's centre is the whole difference between a ring and a
    hoop painted on the sky."""
    a, b = RING_A, RING_A * RING_TILT
    outside, over = blank(), blank()
    for r in range(ROWS):
        for c in range(COLS):
            px, py = cell_px(c - PCX, r - PCY)
            rho = math.sqrt((px / a) ** 2 + (py / b) ** 2)
            if not (RING_IN <= rho <= 1.0):
                continue
            inside = (px * px + py * py) <= PR * PR
            if not inside:
                outside[r][c] = "─"
            elif py > 0:
                over[r][c] = "─"
    return outside, over


def nebula(rng):
    g = blank()
    waves = [(rng.uniform(0.05, 0.14), rng.uniform(0.10, 0.26), rng.uniform(0, 6.3))
             for _ in range(4)]
    for r in range(ROWS):
        for c in range(COLS):
            v = sum(math.sin(c * fx + r * fy + ph) for fx, fy, ph in waves) / len(waves)
            fade = max(0.0, 1.0 - ((c / 62.0) ** 2 + (r / 34.0) ** 2) ** 0.5)
            v = (v * 0.5 + 0.5) * fade
            if v > 0.46:
                g[r][c] = "░" if v < 0.58 else "▒"
    return g


def stars(rng, count, chars):
    out = []
    for _ in range(count):
        c, r = rng.randrange(COLS), rng.randrange(ROWS)
        px, py = cell_px(c - PCX, r - PCY)
        if (px * px + py * py) <= PR * PR:
            continue
        out.append((c, r, rng.choice(chars),
                    rng.uniform(2.6, 7.4), rng.uniform(0.0, 7.4)))
    return out


def runs(grid):
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


def text_rows(grid):
    return "".join(
        '<text xml:space="preserve" x="%.1f" y="%.2f">%s</text>'
        % (FX + c * CHAR_W, FY + LINE_H * (r + 0.8), kit.esc(s))
        for r, c, s in runs(grid))


# ---- craft ---------------------------------------------------------------
# Drawn at their own size rather than on the character grid: at 4 px a cell,
# anything with a recognisable silhouette would be a smudge.

SATELLITE = ["  ▗▄▖  ",
             "▚▞▐█▌▞▚",
             "  ▝▀▘  "]

PROBE = ["  ▄▖   ",
         "◀█████▙",
         "  ▀▘   "]

SAUCER = [" ▗▄███▄▖ ",
          "▝▀▀▀▀▀▀▀▘",
          "   ▘ ▝   "]

# a truss rather than another capsule: the satellite already owns that
# silhouette, and two craft with the same outline read as one craft seen twice
STATION = ["  ▐▌  ",
           "▄▄██▄▄",
           "  ▐▌  "]


def sprite(lines, cls):
    out = ['<g class="%s">' % cls]
    for i, line in enumerate(lines):
        out.append('<text xml:space="preserve" x="0" y="%.1f">%s</text>'
                   % (i * SPR_FONT * 1.02, kit.esc(line)))
    out.append("</g>")
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


def crossing(y0, y1, secs, share, phase):
    """One pass across the frame every `secs`, off-frame the rest of the time.

    `share` is the fraction of the period spent crossing; `phase` shifts the
    whole cycle backwards so the craft do not all arrive together. Without it
    every period starts at zero on load and all four cross the frame in the
    first few seconds, which looks like a queue rather than traffic."""
    return (
        '<animateTransform attributeName="transform" type="translate" '
        'values="-70 %.1f;%.1f %.1f;%.1f %.1f" keyTimes="0;%.3f;1" dur="%.1fs" '
        'begin="-%.1fs" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;1;1;0;0" '
        'keyTimes="0;%.3f;%.3f;%.3f;1" dur="%.1fs" begin="-%.1fs" '
        'repeatCount="indefinite"/>'
        % (y0, W + 70, y1, W + 70, y1, share, secs, phase,
           share * 0.06, share * 0.9, share, secs, phase))


def build():
    rng = random.Random(SEED)
    neb = nebula(rng)
    far = stars(rng, 150, ".··")
    mid = stars(rng, 60, "·*+")
    near = stars(rng, 16, "*+●")
    ring_out, ring_over = rings()
    frames = [planet_frame(2 * math.pi * k / SPIN_FRAMES)
              for k in range(SPIN_FRAMES)]

    glyphs = " .·*+●░▒▓█─│╱╲▔▁▄▀▖▗▘▝▙▟█▌▐◀"
    css = kit.theme_css(
        kit.font_face(glyphs + "".join("".join(s) for s in
                                       (SATELLITE, PROBE, SAUCER, STATION)),
                      "Regular", 400)
        + kit.font_face(NAME + MARKS + " ", "SemiBold", 600)
        + ".film{fill:var(--ink);fill-opacity:.10;fill-rule:evenodd}"
        + ".gate{fill:none;stroke:var(--rule);stroke-width:1}"
        + "text{font-family:'JBMono',monospace;font-size:%gpx;fill:var(--ink);"
          "white-space:pre}" % FONT
        + ".neb{opacity:.26}.far{opacity:.58}.mid{opacity:.80}.near{opacity:1}"
        + ".pl{opacity:.92}.rg{opacity:.55}.cm{opacity:.9}"
        + ".cr text{font-size:%gpx}.cr{opacity:.85}" % SPR_FONT
        # Light on a dark ground blooms, so the solid areas are held back there.
        + "@media (prefers-color-scheme:dark){.pl{opacity:.74}.neb{opacity:.16}"
          ".far{opacity:.40}.mid{opacity:.66}.cr{opacity:.75}}"
        + ".edge{font-family:'JBMono',monospace;font-size:8px;font-weight:600;"
          "fill:var(--dim);letter-spacing:1.6px}"
    )

    out = [kit.svg_open(W, H,
                        "A frame of 35mm film holding a starfield: a ringed "
                        "planet turning on its axis, drifting stars, a comet, "
                        "and passing spacecraft"),
           "<defs><style>", css, "</style>",
           '<clipPath id="gate"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
           "</clipPath></defs>" % (FX, FY, FW, FH),
           '<g clip-path="url(#gate)">']

    out.append('<g class="neb">%s%s</g>' % (text_rows(neb), drift(5, 2, 90)))

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

    out.append('<g class="rg">%s</g>' % text_rows(ring_out))

    # Craft go in behind the planet. Drawn over it they are the same grey as
    # the disc and simply dissolve into it; behind, the disc occludes them and
    # a pass across the frame reads as going behind the planet, which is what
    # it would be.
    # craft, each on its own period so they rarely share the frame
    craft = [(SATELLITE, FY + 70,  FY + 120, 26.0, 0.30, 3.0),
             (PROBE,     FY + 250, FY + 210, 37.0, 0.26, 22.0),
             (SAUCER,    FY + 320, FY + 150, 53.0, 0.18, 40.0),
             (STATION,   FY + 40,  FY + 60,  71.0, 0.34, 58.0)]
    for lines, y0, y1, secs, share, phase in craft:
        anim = crossing(y0, y1, secs, share, phase)
        out.append('<g class="cr" opacity="0" transform="translate(-70,%.1f)">'
                   '%s%s</g>'
                   % (y0, "".join(
                       '<text xml:space="preserve" x="0" y="%.1f">%s</text>'
                       % (i * SPR_FONT * 1.02, kit.esc(line))
                       for i, line in enumerate(lines)), anim))

    # the turning planet: one group per rotation step, switched discretely,
    # because a flipbook that cross-fades reads as a wobble rather than a turn
    body = ['<g class="pl">']
    for k, g in enumerate(frames):
        a, b = k / float(SPIN_FRAMES), (k + 1) / float(SPIN_FRAMES)
        body.append(
            '<g opacity="%d">%s<animate attributeName="opacity" '
            'values="0;1;0;0" keyTimes="0;%.4f;%.4f;1" calcMode="discrete" '
            'dur="%.1fs" repeatCount="indefinite"/></g>'
            % (1 if k == 0 else 0, text_rows(g), a, b, SPIN_SECS))
    body.append('<g class="rg">%s</g>' % text_rows(ring_over))
    body.append('<animateTransform attributeName="transform" type="translate" '
                'values="0 0;0 -1.4;0 0" dur="46s" repeatCount="indefinite"/>')
    body.append("</g>")
    out.append("".join(body))


    comet = ('<text x="0" y="0">●</text>'
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
