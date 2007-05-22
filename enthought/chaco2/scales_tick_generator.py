
from enthought.traits.api import Instance
from ticks import AbstractTickGenerator

# Use the new scales/ticks library
from scales.api import ScaleSystem


class ScalesTickGenerator(AbstractTickGenerator):

    scale = Instance(ScaleSystem, args=())

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
        test_str = "0123456789-+"
        charsize = metrics.get_full_text_extent(test_str)[0] / len(test_str)
        numchars = (bounds_high - bounds_low) / charsize
        ticks, labels = zip(*self.scale.labels(data_low, data_high, numlabels=8, char_width=numchars))
        return array(ticks), labels
