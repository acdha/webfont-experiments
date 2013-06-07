#!/usr/bin/env python
# encoding: utf-8
"""Display unicode coverage information for fonts
"""

from __future__ import unicode_literals, print_function, absolute_import

from itertools import groupby
import argparse
import os
import sys

import fontforge


def unicode_code_point_iterator(font):
    """Generator which returns Unicode code points from the provided font"""

    for g in font.glyphs():
        if g.unicode > -1:
            yield g.unicode

        # Alternate code points: see http://fontforge.org/python.html#Glyph
        if g.altuni:
            for code_point, variation_selector, reserved in g.altuni:
                yield code_point


def get_unicode_ranges(font):
    ranges = []

    code_points = set(unicode_code_point_iterator(font))

    # Exclude common chaff:
    code_points.discard(0)

    for key, group in groupby(enumerate(sorted(code_points)),
                              lambda (index, item): index - item):

        group = [i[1] for i in group]

        if len(group) > 1:
            ranges.append((group[0], group[-1]))
        else:
            ranges.append(group[0])

    return ranges


#: CSS @font-face template, escaped for Python string formatting:
FONT_FACE = """
@font-face {{
  font-family: '{full_name}';
  font-style: {style};
  font-weight: {weight};
  src: local('{name}'), local('{full_name}'), url({filename}) format('{format}');
  unicode-range: {unicode_range};
}}
"""


def print_font_face_declaration(font, parts):
    # BUG: handle oblique fonts:
    font_style = "italic" if font.italicangle < 0 else "normal";

    font_weight = font.os2_weight

    print(FONT_FACE.format(filename=os.path.basename(font.path),
                           # Ick:
                           format=os.path.splitext(font.path)[-1][1:],
                           name=font.fontname,
                           full_name=font.fullname,
                           style=font_style,
                           weight=font_weight,
                           unicode_range=", ".join(parts)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('--format', default='text', choices=('text', 'css'))
    parser.add_argument('file', nargs='+')

    args = parser.parse_args()

    font_names = []

    for f in args.file:
        # We'll do this early to make it clear which files cause fontforge to spew warnings:
        print("Opening: %s" % f, file=sys.stderr)

        try:
            font = fontforge.open(f)
        except StandardError as exc:
            print("Unable to open %s: %s" % (f, exc), file=sys.stderr)
            continue

        if not font.encoding.startswith('Unicode'):
            print("Can't handle encoding: %s" % font.encoding, file=sys.stderr)
            continue

        ranges = get_unicode_ranges(font)
        parts = []
        for i in ranges:
            if isinstance(i, int):
                parts.append("U+%04X" % i)
            else:
                parts.append("U+%04X-%04X" % i)

        msg = "{filename}: {font.fontname} {font.fullname}".format(filename=f, font=font)
        if args.format == "css":
            print(msg, file=sys.stderr)  # This allows easy saving of the CSS
            print_font_face_declaration(font, parts)
        else:
            print(msg)
            print("\n\t".join(parts))

        font_names.append(font.fullname)

    if args.format == "css":
        print('Combined CSS font-family:\n\t"%s"' % '", "'.join(font_names),
              file=sys.stderr)
