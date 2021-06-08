# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
A plot that renders text values along one dimension

"""


from numpy import array, empty

# Enthought library imports
from enable.api import black_color_trait
from kiva.trait_defs.kiva_font_trait import KivaFont
from traits.api import Bool, Enum, Float, Int, Instance, List, observe

# local imports
from chaco.array_data_source import ArrayDataSource
from chaco.label import Label
from chaco.base_1d_plot import Base1DPlot


class TextPlot1D(Base1DPlot):
    """ A plot that positions textual labels in 1D """

    #: text values corresponding to indices
    value = Instance(ArrayDataSource)

    #: The font of the tick labels.
    text_font = KivaFont("modern 10")

    #: The color of the tick labels.
    text_color = black_color_trait

    #: The rotation of the tick labels.
    text_rotate_angle = Float(0)

    #: The margin around the tick labels.
    text_margin = Int(2)

    #: the anchor point of the text (corner is better for 45 degree rotation)
    text_alignment = Enum("edge", "corner")

    #: alignment of text relative to non-index direction
    alignment = Enum("center", "left", "right", "top", "bottom")

    #: alignment of text relative to index direction and centered around the
    #: provided value point
    index_alignment = Enum("right", "center", "left", "top", "bottom")

    #: offset of text relative to non-index direction in pixels
    text_offset = Float

    # ------------------------------------------------------------------------
    # Private traits
    # ------------------------------------------------------------------------

    #: private trait holding position of text relative to non-index direction
    _text_position = Float

    #: flag for whether the cache of Label instances is valid
    _label_cache_valid = Bool(False, transient=True)

    #: cache of Label instances for faster rendering
    _label_cache = List(transient=True)

    #: cache of bounding boxes of labels
    _label_box_cache = List(transient=True)

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _compute_labels(self, gc):
        """Generate the Label instances for the plot. """
        self._label_cache = [
            Label(
                text=text,
                font=self.text_font,
                color=self.text_color,
                rotate_angle=self.text_rotate_angle,
                margin=self.text_margin,
            )
            for text in self.value.get_data()
        ]
        self._label_box_cache = [
            array(label.get_bounding_box(gc), float)
            for label in self._label_cache
        ]
        self._label_cache_valid = True

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        """ Draw the text at the specified index values """

        if len(self.index.get_data()) == 0:
            return
        if not self._label_cache_valid:
            self._compute_labels(gc)

        coord = self._compute_screen_coord()
        pts = empty(shape=(len(coord), 2))

        if self.orientation == "v":
            pts[:, 1] = coord
            pts[:, 0] = self._text_position
        else:
            pts[:, 0] = coord
            pts[:, 1] = self._text_position

        self._render(gc, pts, self._label_cache)

    def _render(self, gc, pts, labels):
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            for pt, label in zip(pts, labels):
                with gc:
                    x, y = self._get_index_text_position(gc, pt, label)
                    gc.translate_ctm(x, y)
                    label.draw(gc)

    def _get_index_text_position(self, gc, pt, label):
        """ Compute the text label position in the index direction """
        x, y = pt
        width, height = label.get_bounding_box(gc)

        if self.orientation == "v":
            position, width = y, height
        else:
            position = x

        if self.index_alignment == "center":
            position -= width / 2.0
        elif self.index_alignment in ["left", "bottom"]:
            position -= width
        # If alignment is 'right' or 'top' we do nothing as that already
        # matches the default behavior

        if self.orientation == "v":
            return x, position
        else:
            return position, y

    def _get_text_position(self):
        """ Compute the text label position in the non-index direction """
        x, y = self.position
        w, h = self.bounds

        if self.orientation == "v":
            y, h = x, w

        if self.alignment == "center":
            position = y + h / 2.0
        elif self.alignment in ["left", "bottom"]:
            position = y
        elif self.alignment in ["right", "top"]:
            position = y + h

        position += self.text_offset
        return position

    # ------------------------------------------------------------------------
    # Trait handlers
    # ------------------------------------------------------------------------

    def __text_position_default(self):
        return self._get_text_position()

    # ------------------------------------------------------------------------
    # Trait events
    # ------------------------------------------------------------------------

    @observe("index.data_changed")
    def _invalidate(self, event):
        self._cache_valid = False
        self._screen_cache_valid = False
        self._label_cache_valid = False

    @observe("value.data_changed")
    def _invalidate_labels(self, event):
        self._label_cache_valid = False

    def _bounds_changed(self, old, new):
        super()._bounds_changed(old, new)
        self._text_position = self._get_text_position()

    def _bounds_items_changed(self, event):
        super()._bounds_items_changed(event)
        self._text_position = self._get_text_position()

    def _orientation_changed(self):
        super()._orientation_changed()
        self._text_position = self._get_text_position()

    def _direction_changed(self):
        super()._direction_changed()
        self._text_position = self._get_text_position()

    def _alignment_changed(self):
        self._text_position = self._get_text_position()
