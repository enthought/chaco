"""
Scatterplot in one dimension only
"""


from __future__ import absolute_import

from itertools import izip

from numpy import empty

# Enthought library imports
from chaco.api import Label
from enable.api import black_color_trait, ColorTrait, MarkerTrait
from kiva.trait_defs.kiva_font_trait import KivaFont
from traits.api import Any, Bool, Callable, Enum, Float, Int, List, on_trait_change

# local imports
from .base_1d_plot import Base1DPlot

def default_formatter(val):
    return ("%f"%val).rstrip("0").rstrip(".")

class TextPlot1D(Base1DPlot):
    """ A plot that positions textual labels in 1D """

    #: label formatter: callable that given an index, returns appropriate text
    formatter = Callable(default_formatter)

    #: The font of the tick labels.
    text_font = KivaFont('modern 10')

    #: The color of the tick labels.
    text_color = ColorTrait("black")

    #: The rotation of the tick labels.
    text_rotate_angle = Float(0)

    #: The margin around the tick labels.
    text_margin = Int(2)

    #: the anchor point of the text (corner is better for 45 degree rotation)
    text_alignment = Enum('edge', 'corner')

    #: alignment of text relative to non-index direction
    alignment = Enum("center", "left", "right", "top", "bottom")

    #: offset of text relative to non-index direction in pixels
    text_offset = Float

    #: private trait holding text of text relative to non-index direction
    _text_position = Float

    _label_cache_valid = Bool(False)
    _label_cache = List

    def _compute_labels(self):
        """Generates the labels for text plot.
        """
        # labels are already computed
        formatter = self.formatter

        def build_label(val):
            text = formatter(val) if formatter is not None else str(val)
            return Label(text=text,
                         font=self.text_font,
                         color=self.text_color,
                         rotate_angle=self.text_rotate_angle,
                         margin=self.text_margin)


        self._label_cache = [build_label(val) for val in self.index.get_data()]

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):

        if len(self.index.get_data()) == 0:
            return
        if not self._label_cache_valid:
            self._compute_labels()
        self._label_cache_valid =  True

        coord = self._compute_screen_coord()
        pts = empty(shape=(len(coord), 2))

        if self.orientation == 'v':
            pts[:, 1] = coord
            pts[:, 0] = self._text_position
        else:
            pts[:, 0] = coord
            pts[:, 1] = self._text_position

        self._render(gc, pts, self._label_cache)

    def _render(self, gc, pts, labels):
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            for pt, label in izip(pts, labels):
                with gc:
                    gc.translate_ctm(*pt)
                    label.draw(gc)

    def __text_position_default(self):
        return self._get_text_position()

    def _get_text_position(self):
        x, y = self.position
        w, h = self.bounds

        if self.orientation == 'v':
            y, h = x, w

        if self.alignment == 'center':
            position = y + h/2.0
        elif self.alignment in ['left', 'bottom']:
            position = y
        elif self.alignment in ['right', 'top']:
            position = y + h

        position += self.text_offset
        print position, self.alignment
        return position

    @on_trait_change("index.data_changed")
    def _invalidate(self):
        self._cache_valid = False
        self._screen_cache_valid = False
        self._label_cache_valid = False

    def _bounds_changed(self, old, new):
        super(TextPlot1D, self)._bounds_changed(old, new)
        self._text_position = self._get_text_position()

    def _bounds_items_changed(self, event):
        super(TextPlot1D, self)._bounds_items_changed(event)
        self._text_position = self._get_text_position()

    def _orientation_changed(self):
        super(TextPlot1D, self)._orientation_changed()
        self._text_position = self._get_text_position()

    def _alignment_changed(self):
        self._text_position = self._get_text_position()
