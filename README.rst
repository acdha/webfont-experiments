Webfont Experiments
===================

Container for some experiments with webfonts and Unicode

Generating CSS @font-face from font files
-----------------------------------------

The goal is to automatically produce a single large stylesheet which defines webfonts using the
``unicode-range`` property to help browsers avoid downloading them until they're needed to display text on the
current page, avoiding the need for pages to explicitly hard-code all of the fonts. The second stage might be
optionally generating ``:lang()`` selectors based on Unicode ranges, although that will probably require hand
tweaking if more than one font defines a particular range.

Rough notes
~~~~~~~~~~~

#. Install FontForge and enable the Python module (e.g. ``brew install fontforge``)

#. Confirm everything is working by getting the text inventory::

    font-unicode-inventory.py *.ttf

#. Generate your CSS::

    font-unicode-inventory.py *.woff --format=css > lots-of-fonts.css


