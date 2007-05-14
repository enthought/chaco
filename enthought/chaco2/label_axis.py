
# Major library imports
from traceback import print_exc
from numpy import array, compress, float64, inf, searchsorted, take

# Enthought library imports
from enthought.traits.api import Any, Str, List, Float

# Local, relative imports
from axis import PlotAxis
from base import reverse_map_1d
from label import Label
from ticks import auto_ticks


class LabelAxis(PlotAxis):
    """ Much like a plot axis, but instead of numbers, we have a series of labels.
    """
    
    labels = List(Str)
    label_rotation = Float(0)
    positions = Any  # List(Float), Array
    
    def _compute_tick_positions(self, gc, component=None):
        if (self.mapper is None):
            self._reset_cache()
            self._cache_valid = True
            return
        
        datalow = self.mapper.range.low
        datahigh = self.mapper.range.high
        screenhigh = self.mapper.high_pos
        screenlow = self.mapper.low_pos
        
        if (datalow == datahigh) or (screenlow == screenhigh) or \
           (datalow in [inf, -inf]) or (datahigh in [inf, -inf]):
            self._reset_cache()
            self._cache_valid = True
            return

        if not self.tick_generator:
            return
        
        tick_list = array(self.tick_generator.get_ticks(datalow, datahigh,
                                                        datalow, datahigh,
                                                        self.tick_interval), float64)
                
        
        tick_indices = searchsorted(self.positions, tick_list)
        tick_indices = compress(tick_indices < len(self.positions), tick_indices)
        tick_positions =  take(self.positions, tick_indices)
        self._tick_label_list = take(self.labels, tick_indices)
        
        if datalow > datahigh:
            raise RuntimeError, "DataRange low is greater than high; unable to compute axis ticks."
        
        if self.small_haxis_style:
            mapped_label_positions = [((self.mapper.map_screen(pos)-screenlow) / \
                                       (screenhigh-screenlow)) for pos in tick_positions]
            self._tick_positions = [self._axis_vector*tickpos + self._origin_point \
                                          for tickpos in mapped_label_positions]    
            self._tick_label_positions = self._tick_positions        
        else:
            mapped_label_positions = [((self.mapper.map_screen(pos)-screenlow) / \
                                       (screenhigh-screenlow)) for pos in tick_positions]
            self._tick_positions = [self._axis_vector*tickpos + self._origin_point \
                                    for tickpos in mapped_label_positions]
            self._tick_label_positions = self._tick_positions
        return
        
        
    def _compute_labels(self, gc):
        try:
            self.ticklabel_cache = []
            for text in self._tick_label_list:
                ticklabel = Label(text=text, font=self.tick_label_font,
                                  color=self.tick_label_color,
                                  rotate_angle=self.label_rotation)
                self.ticklabel_cache.append(ticklabel)
    
            self._tick_label_bounding_boxes = [array(ticklabel.get_bounding_box(gc), float64) for ticklabel in self.ticklabel_cache]
        except:
            print_exc()
        return
        