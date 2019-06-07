"""
A plot that renders text values in two dimensions

"""

from __future__ import absolute_import

import six.moves as sm

from numpy import array, column_stack, empty, isfinite

# Enthought library imports
from enable.api import black_color_trait
from kiva.trait_defs.kiva_font_trait import KivaFont
from traits.api import (
    Bool, Enum, Float, Int, Instance, List, Tuple, on_trait_change
)

# local imports
from .array_data_source import ArrayDataSource
from .label import Label
from .base_xy_plot import BaseXYPlot


class TextPlot(BaseXYPlot):
    """ A plot that positions textual labels in 2D """

    #: text values corresponding to indices
    text = Instance(ArrayDataSource)

    #: The font of the tick labels.
    text_font = KivaFont('modern 10')

    #: The color of the tick labels.
    text_color = black_color_trait

    #: The rotation of the tick labels.
    text_rotate_angle = Float(0)

    #: The margin around the label.
    text_margin = Int(2)

    #: horizontal position of text relative to target point
    h_position = Enum("center", "left", "right")

    #: vertical position of text relative to target point
    v_position = Enum("center", "top", "bottom")

    #: offset of text relative to non-index direction in pixels
    text_offset = Tuple(Float, Float)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    #: flag for whether the cache of Label instances is valid
    _label_cache_valid = Bool(False)

    #: cache of Label instances for faster rendering
    _label_cache = List

    #: cache of bounding boxes of labels
    _label_box_cache = List

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_labels(self, gc):
        """Generate the Label instances for the plot. """
        self._label_cache = [
            Label(
                text=text,
                font=self.text_font,
                color=self.text_color,
                rotate_angle=self.text_rotate_angle,
                margin=self.text_margin
            ) for text in self.text.get_data()
        ]
        self._label_box_cache = [
            array(label.get_bounding_box(gc), float)
            for label in self._label_cache
        ]
        self._label_cache_valid = True

    def _gather_points(self):
        """ Abstract method to collect data points that are within the range of
        the plot, and cache them.
        """
        if self._cache_valid:
            return

        if not self.index or not self.value:
            return

        index, index_mask = self.index.get_data_mask()
        value, value_mask = self.value.get_data_mask()

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            self._cached_data_pts = []
            self._cached_point_mask = []
            self._cache_valid = True
            return

        index_range_mask = self.index_mapper.range.mask_data(index)
        value_range_mask = self.value_mapper.range.mask_data(value)

        nan_mask = (
            isfinite(index) & index_mask & isfinite(value) & value_mask
        )
        point_mask = nan_mask & index_range_mask & value_range_mask

        if not self._cache_valid:
            if not point_mask.all():
                points = column_stack([index[point_mask], value[point_mask]])
            else:
                points = column_stack([index, value])
            self._cached_data_pts = points
            self._cached_point_mask = point_mask
            self._cache_valid = True

    def _render(self, gc, pts):
        if not self._label_cache_valid:
            self._compute_labels(gc)

        labels = [
            label
            for label, mask in zip(self._label_cache, self._cached_point_mask)
            if mask
        ]
        boxes = [
            label
            for label, mask in
            zip(self._label_box_cache, self._cached_point_mask) if mask
        ]
        offset = empty((2, ), float)

        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            for pt, label, box in sm.zip(pts, labels, boxes):
                with gc:
                    if self.h_position == "center":
                        offset[0] = -box[0] / 2 + self.text_offset[0]
                    elif self.h_position == "right":
                        offset[0] = self.text_offset[0]
                    elif self.h_position == "left":
                        offset[0] = -box[0] / 2 + self.text_offset[0]
                    if self.v_position == "center":
                        offset[1] = -box[1] / 2 + self.text_offset[1]
                    elif self.v_position == "top":
                        offset[1] = self.text_offset[1]
                    elif self.v_position == "bottom":
                        offset[1] = -box[1] / 2 - self.text_offset[1]

                    pt += offset
                    gc.translate_ctm(*pt)

                    label.draw(gc)

    #------------------------------------------------------------------------
    # Trait events
    #------------------------------------------------------------------------

    @on_trait_change("index.data_changed")
    def _invalidate(self):
        self._cache_valid = False
        self._screen_cache_valid = False
        self._label_cache_valid = False

    @on_trait_change("value.data_changed")
    def _invalidate_labels(self):
        self._label_cache_valid = False
