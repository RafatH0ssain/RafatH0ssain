#!/usr/bin/env python3
"""Draw quote.svg — the quote strip at the foot of the README.

    python3 scripts/make_quote.py

Reads scripts/quotes.txt and writes quote.svg at the repository root.

On why this cycles rather than randomises
-----------------------------------------
The obvious brief is "a different quote every time the page is refreshed",
and on GitHub that is not reachable. Picking at random needs either a script,
which GitHub strips out of READMEs, or a server, which is the whole thing this
repository was rebuilt to avoid — the old README pulled its quote from a
third-party app, and that app is a single point of failure for the last thing
on the page.

SMIL has no source of randomness and no access to the clock; every timeline
starts at zero when the image loads, so anything driven by it is identical on
every visit. What it can do is run: all fifty quotes live in the one file and
it moves through them, so the quote changes while the page is being read
rather than only between visits. A reader who lingers sees several; a reader
who refreshes sees the sequence start again.

The order is shuffled once here, with a fixed seed, so the file is
byte-reproducible but the three quotes most people actually see are not all
from the same section of quotes.txt.

The first quote is also the resting state: if SMIL never runs, the strip shows
that one rather than all fifty stacked on top of each other.
"""
import io
import os
import random
import textwrap

import svgkit as kit

SRC = os.path.join(kit.HERE, "quotes.txt")

W = 660.0
FONT = 13.0
LINE_H = 19.0
WRAP = 78           # characters; 78 * 13 * 0.6 = 608, inside the 660 measure
ATTR = 11.0
PAD_TOP = 4.0
GAP = 9.0           # between the last line and the attribution

SLOT = 6.0          # seconds each quote holds
FADE = 0.7          # seconds of cross-fade
SEED = 11


def load():
    out = []
    for raw in io.open(SRC, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        text, _, who = line.rpartition("|")
        out.append((text.strip(), who.strip()))
    random.Random(SEED).shuffle(out)
    return out


def cycle_anim(i, n):
    """Hold this quote clear, bring it up for its slot, take it away again."""
    total = n * SLOT
    a = i * SLOT
    keys = [0.0, a, a + FADE, a + SLOT - FADE, a + SLOT, total]
    keys = [min(max(k / total, 0.0), 1.0) for k in keys]
    for j in range(1, len(keys)):                 # keyTimes must not go back
        keys[j] = max(keys[j], keys[j - 1])
    return ('<animate attributeName="opacity" values="0;0;1;1;0;0" '
            'keyTimes="%s" begin="0s" dur="%.1fs" repeatCount="indefinite"/>'
            % (";".join("%.6f" % k for k in keys), total))


def build(quotes):
    wrapped = [(textwrap.wrap(t, WRAP), who) for t, who in quotes]
    tallest = max(len(lines) for lines, _ in wrapped)
    h = PAD_TOP + tallest * LINE_H + GAP + ATTR + 6

    glyphs = "".join(t + w for t, w in quotes) + "— "
    css = kit.theme_css(
        kit.font_face(glyphs, "Regular", 400)
        + kit.font_face(glyphs, "SemiBold", 600)
        + ".q{font-family:'JBMono',monospace;font-size:%gpx;fill:var(--emph)}" % FONT
        + ".by{font-family:'JBMono',monospace;font-size:%gpx;font-weight:600;"
          "fill:var(--dim);letter-spacing:.9px}" % ATTR
    )

    out = [kit.svg_open(W, h, "A rotating quote"),
           "<defs><style>", css, "</style></defs>"]

    for i, (lines, who) in enumerate(wrapped):
        # the top line sits at a fixed baseline whatever the quote's length,
        # so the strip does not appear to jump as it cycles
        parts = ['<g opacity="%d">' % (1 if i == 0 else 0)]
        for j, line in enumerate(lines):
            parts.append('<text class="q" x="0" y="%.1f">%s</text>'
                         % (PAD_TOP + LINE_H * (j + 0.85), kit.esc(line)))
        parts.append('<text class="by" x="0" y="%.1f">— %s</text>'
                     % (PAD_TOP + tallest * LINE_H + GAP + ATTR, kit.esc(who)))
        parts.append(cycle_anim(i, len(wrapped)))
        parts.append("</g>")
        out.append("".join(parts))

    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    qs = load()
    print("%d quotes, %.0fs a turn, %.0fs round the loop"
          % (len(qs), SLOT, len(qs) * SLOT))
    kit.write("quote.svg", build(qs))
