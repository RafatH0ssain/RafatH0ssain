#!/usr/bin/env python3
"""Draw contact-sheet.svg — one frame of 35mm film, rendered in characters.

    python3 scripts/make_contact_sheet.py

Reads scripts/source/frame.png and writes contact-sheet.svg at the repository
root. Run it when the photograph or the copy changes; the output is committed,
so nothing regenerates on a schedule and nothing is fetched at page load.

The source is grey-plus-alpha: the subject cut out of the original frame, with
the street behind him removed. That cut was made once, by hand, with a
segmentation model — it is deliberately not part of this script, so generating
the page needs nothing but pillow and numpy and no 176 MB model download.

Three things decide whether the result reads, and all three were got wrong at
least once first:

  * The background has to go. Keeping it seemed right — a film frame is a whole
    exposure — but a wall, a pavement and a patterned jacket are all texture at
    the same pitch as the face, and the ramp cannot tell which texture matters.
    Cutting the subject out is what makes it read as a portrait rather than as
    a busy grey rectangle.

  * Cropping closer is not the same as making it smoother. Zooming in magnifies
    the subject and the noise together; it was the background, not the scale,
    that was doing the damage.

  * Grain has to be taken out at the scale it lives at. A 35mm negative carries
    real grain, far finer than the character grid, and sampling straight down
    aliases it rather than averaging it — single grains land on single cells and
    fire off a stray '@' in the middle of smooth skin.
"""
import numpy as np
from PIL import Image, ImageFilter

import svgkit as kit
from svgkit import RAMP

SRC = "scripts/source/frame.png"

# With the background gone, resolution costs nothing. At 104 columns the face
# had about twenty characters to describe itself with and came out blocky;
# every extra column used to buy detail in the wall and the jacket pattern as
# well, which is why raising it made things worse before the cut-out existed.
# Now there is nothing behind him to sharpen, so the grid can be fine enough
# to read as a halftone instead of as tiles.
COLS = 156
CURVE = 1.00        # the tone curve, applied across the subject only
CLIP = (2, 98)      # percentiles, over the subject only, for black and white
SMOOTH = 0.30       # pre-blur radius in destination cells; see sample()

CHAR_W = 4.0                          # 156 * 4 = 624, plus margins = 660 exactly
FONT = CHAR_W / kit.ADVANCE           # the advance is 0.600 em, so this is exact
LINE_H = FONT
CELL = LINE_H / CHAR_W                # so the frame is not squashed

MARGIN = 18.0       # film either side of the aperture
BAND = 22.0         # perforation band, top and bottom
REBATE = 24.0       # edge-printing band, under the frame
HOLE_W, HOLE_H, PITCH = 15.0, 11.0, 33.0

NAME = "RAFATH0SSAIN"
MARKS = "▸ 25   ▸ 25A   ▸ 26"

DEVELOP = 1.9       # seconds across which rows come up
FADE = 0.9          # seconds for any one row to appear
TOTAL = DEVELOP + FADE * 1.4


def sample(path):
    """Return (tone, coverage) on the character grid.

    Both come off the same downsample, and it has to be weighted: a cell that
    is half subject and half nothing must take its tone from the half that is
    subject, or the cut edge drags every border cell toward black. So the
    luminance is premultiplied by alpha, both are averaged over the cell, and
    the tone is the ratio.
    """
    im = Image.open(path)
    lum = np.asarray(im.convert("L"), np.float32) / 255.0
    alpha = np.asarray(im.split()[-1], np.float32) / 255.0
    h, w = lum.shape
    rows = int(round(h / w * COLS / CELL))
    radius = SMOOTH * w / COLS

    def down(arr):
        # 8-bit rather than float: PIL will not blur an "F" image, and at 256
        # levels against a 13-step ramp the quantisation is far below anything
        # that could change which character a cell gets.
        img = Image.fromarray((np.clip(arr, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8))
        if radius:
            img = img.filter(ImageFilter.GaussianBlur(radius))
        return np.asarray(img.resize((COLS, rows), Image.BOX), np.float32) / 255.0

    cover = np.clip(down(alpha), 0.0, 1.0)
    tone = np.where(cover > 1e-3, down(lum * alpha) / np.maximum(cover, 1e-3), 0.0)
    return np.clip(tone, 0.0, 1.0), cover


def to_cells(tone, cover, curve):
    """Map tone to ramp indices, faded out by how much subject a cell holds.

    Multiplying by coverage is what keeps the silhouette from looking cut with
    scissors: a cell on the boundary gets a lighter character instead of the
    full one, so the edge falls away over a character or two the way the ramp
    handles every other gradient.
    """
    inside = cover > 1e-3
    if not inside.any():
        raise SystemExit("the source has no subject in it")
    lo, hi = np.percentile(tone[inside], CLIP[0]), np.percentile(tone[inside], CLIP[1])
    v = np.clip((tone - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
    density = (1.0 - v ** curve) * cover
    return np.clip((density * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)


def perforations(w, y):
    """Holes marching across the band, clipped at both edges so the strip reads
    as a length cut from a longer roll rather than a tile with tidy ends."""
    out, x = [], -PITCH / 2.0
    while x < w + PITCH:
        out.append('M%.1f %.1f h%.1f a2.5 2.5 0 0 1 2.5 2.5 v%.1f '
                   'a2.5 2.5 0 0 1 -2.5 2.5 h-%.1f '
                   'a2.5 2.5 0 0 1 -2.5 -2.5 v-%.1f a2.5 2.5 0 0 1 2.5 -2.5 Z'
                   % (x + 2.5, y, HOLE_W - 5, HOLE_H - 5, HOLE_W - 5, HOLE_H - 5))
        x += PITCH
    return " ".join(out)


def build(tone, cover):
    idx = to_cells(tone, cover, CURVE)
    nrows, ncols = idx.shape
    fw, fh = ncols * CHAR_W, nrows * LINE_H
    w = fw + 2 * MARGIN
    h = BAND + fh + REBATE + BAND
    fx, fy = MARGIN, BAND

    # Darkest rows first: the shadows come up before the highlights, the way a
    # print does in the tray. Rows holding no subject at all never appear, so
    # they are left out of the ordering entirely.
    weight = idx.mean(axis=1)
    order = np.argsort(-weight)
    begin = {int(r): DEVELOP * i / max(nrows - 1, 1) for i, r in enumerate(order)}

    strip = ("M0 0H%.1f V%.1f H0 Z " % (w, h)
             + "M%.1f %.1f H%.1f V%.1f H%.1f Z " % (fx, fy, fx + fw, fy + fh, fx)
             + perforations(w, (BAND - HOLE_H) / 2.0) + " "
             + perforations(w, h - BAND + (BAND - HOLE_H) / 2.0))

    css = kit.theme_css(
        kit.font_face(RAMP, "Regular", 400)
        + kit.font_face(NAME + MARKS + " ", "SemiBold", 600)
        + ".film{fill:var(--ink);fill-opacity:.10;fill-rule:evenodd}"
        + ".gate{fill:none;stroke:var(--rule);stroke-width:1}"
        + ".px{font-family:'JBMono',monospace;font-size:%gpx;fill:var(--ink);"
          "white-space:pre}" % FONT
        + ".edge{font-family:'JBMono',monospace;font-size:8px;font-weight:600;"
          "fill:var(--dim);letter-spacing:1.6px}"
    )

    out = [kit.svg_open(w, h,
                        "Rafat Hossain raising a camera to his eye, cut out of "
                        "the photograph and drawn in ASCII characters, on a "
                        "frame of 35mm film"),
           "<defs><style>", css, "</style></defs>",
           '<path class="film" d="%s"/>' % strip,
           '<rect class="gate" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>'
           % (fx + .5, fy + .5, fw - 1, fh - 1)]

    for r in range(nrows):
        line = "".join(RAMP[i] for i in idx[r]).rstrip()
        if not line.strip():
            continue
        out.append(
            '<text class="px" xml:space="preserve" x="%.1f" y="%.1f" opacity="1">'
            '%s%s</text>'
            % (fx, fy + LINE_H * (r + 0.8), kit.esc(line),
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
    kit.write("contact-sheet.svg", build(*sample(SRC)))
