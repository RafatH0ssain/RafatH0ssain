#!/usr/bin/env python3
"""Draw contact-sheet.svg — one frame of 35mm film, rendered in characters.

    python3 scripts/make_contact_sheet.py

Reads scripts/source/frame.jpg and writes contact-sheet.svg at the repository
root. Run it when the photograph or the copy changes; the output is committed,
so nothing regenerates on a schedule and nothing is fetched at page load.

Three decisions are worth stating, because they are the ones that were got
wrong first:

  * The background stays. The obvious move is to cut the subject out, which is
    what a portrait wants. A film frame is a whole exposure — the pavement and
    the wall belong to it, and removing them makes the frame look broken rather
    than clean. It also drops a 176 MB segmentation model from the toolchain.

  * The tone curve is 0.70, which lifts the mid-tones rather than crushing
    them. Straight off the scan, the grey wall behind the subject maps to the
    same dense characters as his jacket and the frame reads as noise. Lifting
    the midpoint pushes the wall down to '-' and '=' and leaves '#' and '@' to
    the hair, the camera body and the glasses, which are the shapes that carry
    the picture at this size.

  * Rows develop darkest first. A print in a tray comes up in the shadows and
    finishes in the highlights, so the stagger is ordered by row density rather
    than running top to bottom. It costs nothing and it is the difference
    between an image appearing and an image being developed.

Needs pillow, numpy, fonttools and brotli at generation time only.
"""
import numpy as np
from PIL import Image, ImageFilter

import svgkit as kit
from svgkit import RAMP

SRC = "scripts/source/frame.jpg"

COLS = 104          # below ~90 the glasses go; far above and the glyphs blur
CURVE = 0.70        # light theme: <1 lifts mid-tones; see the note above
CURVE_DARK = 1.90   # dark theme: >1 compresses them; see build()
CLIP = (2, 98)      # percentiles used to set black and white points
SMOOTH = 0.25       # pre-blur radius, in destination cells; see to_rows()
                    # 0.55 was too much: blurring by roughly the width of a
                    # cell and then averaging over that same cell flattens
                    # the local contrast twice and the face goes to mush.

FONT = 10.0
CHAR_W = FONT * kit.ADVANCE          # exactly 6.0 — the grid depends on it
LINE_H = 10.0
CELL = LINE_H / CHAR_W               # sampling aspect, so the frame is not squashed

MARGIN = 18.0       # film either side of the aperture
BAND = 22.0         # perforation band, top and bottom
REBATE = 24.0       # edge-printing band, under the frame
HOLE_W, HOLE_H, PITCH = 15.0, 11.0, 33.0

NAME = "RAFATH0SSAIN"
MARKS = "▸ 25   ▸ 25A   ▸ 26"

DEVELOP = 1.9       # seconds across which rows come up
FADE = 0.9          # seconds for any one row to appear
TOTAL = DEVELOP + FADE * 1.4   # one timeline, long enough for the edge print


def to_rows(path):
    """Sample the photograph onto the character grid."""
    im = Image.open(path).convert("L")
    rows = int(round(im.height / im.width * COLS / CELL))

    # This is the difference between a photograph and a field of speckle. The
    # negative is 35mm and carries real grain and dust, and both sit at a much
    # higher frequency than the character grid can hold. Sampling straight down
    # doesn't average them away, it aliases them: single grains land on single
    # cells and fire off a '@' in the middle of a smooth wall. Blurring first,
    # by a radius tied to how far we are about to reduce, takes the grain out
    # at the scale it lives at.
    #
    # The resample filter matters for the same reason. Lanczos is the right
    # choice when sharpness is what you want; here it rings around every edge
    # and keeps exactly the high frequencies we are trying to lose. A box
    # filter averages the source pixels each cell actually covers, which is
    # what the ramp wants — one honest mean per character.
    im = im.filter(ImageFilter.GaussianBlur(SMOOTH * im.width / COLS))
    im = im.resize((COLS, rows), Image.BOX)

    a = np.asarray(im, dtype=np.float32) / 255.0
    lo, hi = np.percentile(a, CLIP[0]), np.percentile(a, CLIP[1])
    return np.clip((a - lo) / max(hi - lo, 1e-6), 0.0, 1.0)


def to_cells(a, curve, invert):
    """Map normalised brightness onto ramp indices.

    `invert` is not the mirror of the positive rendering, and that is the
    point. Mirroring reuses a curve chosen to lift mid-tones, which on the
    dark canvas lifts them into ink: the pavement behind him turns into a
    solid block of '%' and '@' and the frame stops looking like a photograph.
    Compressing instead — a curve above one — keeps the ink for the genuinely
    bright parts.
    """
    last = len(RAMP) - 1
    v = a ** curve
    v = v if invert else (1.0 - v)
    return np.clip((v * last).round().astype(int), 0, last)


def perforations(w, y):
    """Holes marching across the band, clipped at both edges so the strip reads
    as a length cut from a longer roll rather than a tile with tidy ends."""
    out = []
    x = -PITCH / 2.0
    while x < w + PITCH:
        out.append('M%.1f %.1f h%.1f a2.5 2.5 0 0 1 2.5 2.5 v%.1f '
                   'a2.5 2.5 0 0 1 -2.5 2.5 h-%.1f '
                   'a2.5 2.5 0 0 1 -2.5 -2.5 v-%.1f a2.5 2.5 0 0 1 2.5 -2.5 Z'
                   % (x + 2.5, y, HOLE_W - 5, HOLE_H - 5, HOLE_W - 5, HOLE_H - 5))
        x += PITCH
    return " ".join(out)


def build(a):
    pos = to_cells(a, CURVE, invert=False)
    neg = to_cells(a, CURVE_DARK, invert=True)
    idx = pos
    nrows, ncols = idx.shape
    fw, fh = ncols * CHAR_W, nrows * LINE_H
    w = fw + 2 * MARGIN
    h = BAND + fh + REBATE + BAND
    fx, fy = MARGIN, BAND

    # Darkest rows first: the shadows come up before the highlights.
    order = np.argsort(-idx.mean(axis=1))
    begin = {int(r): DEVELOP * i / max(nrows - 1, 1)
             for i, r in enumerate(order)}

    strip = ("M0 0H%.1f V%.1f H0 Z " % (w, h)
             + "M%.1f %.1f H%.1f V%.1f H%.1f Z " % (fx, fy, fx + fw, fy + fh, fx)
             + perforations(w, (BAND - HOLE_H) / 2.0) + " "
             + perforations(w, h - BAND + (BAND - HOLE_H) / 2.0))

    ramp_face = kit.font_face(RAMP, "Regular", 400)
    edge_face = kit.font_face(NAME + MARKS + " ", "SemiBold", 600)

    css = kit.theme_css(
        ramp_face + edge_face
        + ".film{fill:var(--ink);fill-opacity:.10;fill-rule:evenodd}"
        + ".gate{fill:none;stroke:var(--rule);stroke-width:1}"
        + ".px{font-family:'JBMono',monospace;font-size:%gpx;fill:var(--ink);"
          "white-space:pre}" % FONT
        + ".neg{display:none}"
        + "@media (prefers-color-scheme:dark){.pos{display:none}"
          ".neg{display:inline}}"
        + ".edge{font-family:'JBMono',monospace;font-size:8px;font-weight:600;"
          "fill:var(--dim);letter-spacing:1.6px}"
    )

    out = [kit.svg_open(w, h,
                        "A frame of 35mm film: Rafat Hossain raising a camera "
                        "to his eye, drawn in ASCII characters"),
           "<defs><style>", css, "</style></defs>",
           '<path class="film" d="%s"/>' % strip,
           '<rect class="gate" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
           % (fx + .5, fy + .5, fw - 1, fh - 1)]

    # The ink is the ink, so on a dark canvas a single rendering comes out as a
    # negative: the shadows are what carry the glyphs, and glyphs are what is
    # bright. That is a pretty accident for a film strip and a bad one for a
    # face — the head and the camera stop reading. So the frame is drawn twice,
    # the second time down an inverted ramp on its own curve, and the themes
    # swap which one is displayed. It costs about 13 KB and it keeps the
    # picture a positive on both canvases.
    for cells_all, cls in ((pos, "px pos"), (neg, "px neg")):
        for r in range(nrows):
            cells = cells_all[r]
            line = "".join(RAMP[i] for i in cells).rstrip()
            if not line.strip():
                continue
            out.append(
                '<text class="%s" xml:space="preserve" x="%.1f" y="%.1f" '
                'opacity="1">%s%s</text>'
                % (cls, fx, fy + LINE_H * (r + 0.8), kit.esc(line),
                   kit.reveal(begin[r], FADE, TOTAL)))

    ey = BAND + fh + REBATE * 0.62
    edge_at = DEVELOP + FADE * 0.35
    out.append('<text class="edge" x="%.1f" y="%.1f" opacity="1">%s%s</text>'
               % (fx, ey, NAME, kit.reveal(edge_at, 0.7, TOTAL)))
    out.append('<text class="edge" text-anchor="end" x="%.1f" y="%.1f" '
               'opacity="1">%s%s</text>'
               % (fx + fw, ey, kit.esc(MARKS), kit.reveal(edge_at, 0.7, TOTAL)))

    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    kit.write("contact-sheet.svg", build(to_rows(SRC)))
