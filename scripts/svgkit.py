#!/usr/bin/env python3
"""Shared machinery for the profile README's graphics.

Everything on that page is an SVG generated from this repository, because
GitHub's README renderer takes three things away:

  * <script>, so motion has to be SMIL, declared inside the SVG;
  * CSS, so the only way to put a chosen typeface on the page is to draw the
    text inside an image that carries the font itself;
  * links inside SVG, which is why the project list stays markdown and only
    the headings and the film strip are images.

The font is subset to exactly the characters a given file draws and inlined
as base64. That is not only for looks. The strip's grid assumes an advance
width of exactly 0.600 em, and JetBrains Mono is one of the few monospace
faces that is; a viewer whose default is Consolas (~0.55) would see the
frame sheared about 8% narrow.

Needs fonttools and brotli, at generation time only. Nothing in the committed
output depends on them, or on anything else.
"""
import base64
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(HERE, "fonts")

# One mid-grey does the work of a palette. #6e7681 is GitHub's own neutral,
# which is the point: it sits between the light and dark canvas so the same
# ink is legible on both without a media query. Only the accents move.
LIGHT = dict(ink="#6e7681", emph="#424a53", dim="#8c959f", rule="#d0d7de")
DARK = dict(ink="#7d8590", emph="#c9d1d9", dim="#6e7681", rule="#30363d")

# Bright and sparse to dark and dense. Thirteen steps, because a photograph
# needs a mid-range: four steps is enough for a calendar heat map and turns a
# face into mud.
RAMP = " .`:-=+*cs#%@"

ADVANCE = 0.600          # em, and the grid depends on it being exactly this


def subset_font(chars, weight="Regular"):
    """Return (base64 woff2, ok) for a font carrying just `chars`."""
    from fontTools import subset
    from fontTools.ttLib import TTFont

    path = os.path.join(FONTS, "JetBrainsMonoNL-%s.ttf" % weight)
    font = TTFont(path)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.layout_features = []          # no ligatures; "=+" must stay two glyphs
    opts.notdef_outline = True
    opts.recalc_bounds = True
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(text="".join(sorted(set(chars))))
    subsetter.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def font_face(chars, weight="Regular", css_weight=400):
    """An @font-face rule with the subset inlined, ready to drop in <style>."""
    b64 = subset_font(chars, weight)
    return (
        "@font-face{font-family:'JBMono';font-style:normal;"
        "font-weight:%d;font-display:block;"
        "src:url(data:font/woff2;base64,%s) format('woff2')}" % (css_weight, b64)
    )


def theme_css(extra=""):
    """Palette as custom properties, with the dark variant behind a query.

    Both themes are defined; only the accents differ. GitHub serves the same
    file to light and dark readers, so the SVG has to decide for itself.
    """
    light = ";".join("--%s:%s" % kv for kv in LIGHT.items())
    dark = ";".join("--%s:%s" % kv for kv in DARK.items())
    return (
        ":root{%s}"
        "@media (prefers-color-scheme:dark){:root{%s}}"
        "%s" % (light, dark, extra)
    )


def svg_open(w, h, title):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 %g %g" width="%g" height="%g" '
        'role="img" aria-label="%s">' % (w, h, w, h, esc(title))
    )


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def write(name, svg):
    path = os.path.join(ROOT, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("%-26s %6.1f KB" % (name, os.path.getsize(path) / 1024.0))
