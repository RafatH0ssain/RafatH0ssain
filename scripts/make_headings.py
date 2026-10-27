#!/usr/bin/env python3
"""Draw the hd-*.svg section headings.

    python3 scripts/make_headings.py

A heading is a rebate mark, the section name, and a rule running out to the
right margin — the same three moves as the edge printing under the film
strip, so the page has one voice rather than a picture at the top and a
document underneath.

These are images for a dull reason: GitHub strips CSS from READMEs, so a
markdown '##' is rendered in GitHub's own font at GitHub's own size and
nothing can be done about it. Drawing the heading is the only way to put this
page's typeface on it. Each file subsets the font down to just the letters it
uses, which is why they come out around 3 KB rather than 200.
"""
import svgkit as kit

W = 660.0
H = 20.0
FONT = 11.0
TRACK = 1.2
MARK = "▸"
BASE = 14.0          # baseline
RULE_Y = 10.5

SECTIONS = [
    ("hd-about.svg", "about"),
    ("hd-stack.svg", "stack"),
]

SWEEP = 0.75         # seconds for the rule to run out
HOLD = 1.0           # one timeline, shared by mark, name and rule


def build(name):
    advance = FONT * kit.ADVANCE + TRACK
    x_name = 14.0
    x_rule = x_name + len(name) * advance + 10.0

    css = kit.theme_css(
        kit.font_face(MARK + name, "SemiBold", 600)
        + ".mark{font-family:'JBMono',monospace;font-size:%gpx;fill:var(--dim)}" % FONT
        + ".name{font-family:'JBMono',monospace;font-size:%gpx;font-weight:600;"
          "fill:var(--emph);letter-spacing:%gpx}" % (FONT, TRACK)
        + ".rule{stroke:var(--rule);stroke-width:1}"
    )

    # The rule rests at full length: if the timeline never runs, the heading is
    # simply already drawn. Same reasoning as svgkit.reveal.
    sweep = ('<animate attributeName="x2" values="%.1f;%.1f;%.1f;%.1f" '
             'keyTimes="0;0.10;%.4f;1" begin="0s" dur="%.2fs" fill="freeze"/>'
             % (x_rule, x_rule, W, W, min((0.10 + SWEEP / HOLD), 1.0), HOLD))

    return "".join([
        kit.svg_open(W, H, name),
        "<defs><style>", css, "</style></defs>",
        '<text class="mark" x="0" y="%.1f" opacity="1">%s%s</text>'
        % (BASE, MARK, kit.reveal(0.0, 0.45, HOLD)),
        '<text class="name" x="%.1f" y="%.1f" opacity="1">%s%s</text>'
        % (x_name, BASE, kit.esc(name), kit.reveal(0.12, 0.45, HOLD)),
        '<line class="rule" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f">%s</line>'
        % (x_rule, RULE_Y, W, RULE_Y, sweep),
        "</svg>",
    ])


if __name__ == "__main__":
    for filename, name in SECTIONS:
        kit.write(filename, build(name))
