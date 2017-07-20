""" Defines the ScalesTickGenerator class.
"""

import six.moves as sm

from numpy import array

from traits.api import Any
from enable.font_metrics_provider import font_metrics_provider

from .ticks import AbstractTickGenerator

# Use the new scales/ticks library
from .scales.api import ScaleSystem


class ScalesTickGenerator(AbstractTickGenerator):

    scale = Any #Instance(ScaleSystem, args=())

    font = Any

    def _scale_default(self):
        return ScaleSystem()

    def get_ticks(self, data_low, data_high, bounds_low, bounds_high, interval,
                  use_endpoints=False, scale=None):
        if interval != "auto":
            ticks = self.scale.ticks(data_low, data_high, (data_high - data_low) / interval)
        else:
            ticks = self.scale.ticks(data_low, data_high)
        return ticks

    def get_ticks_and_labels(self, data_low, data_high, bounds_low, bounds_high,
                             orientation = "h"):
        # TODO: add support for Interval
        # TODO: add support for vertical labels
        metrics = font_metrics_provider()
        if self.font is not None and hasattr(metrics, "set_font"):
            metrics.set_font(self.font)
        test_str = "0123456789-+"
        charsize = metrics.get_full_text_extent(test_str)[0] / len(test_str)
        numchars = (bounds_high - bounds_low) / charsize
        tmp = list(sm.zip(*self.scale.labels(data_low, data_high, numlabels=8,
                                             char_width=numchars)))
        # Check to make sure we actually have labels/ticks to show before
        # unpacking the return tuple into (tick_array, labels).
        if len(tmp) == 0:
            return array([]), []
        else:
            tick_array, labels = tmp
            return array(tick_array), labels
