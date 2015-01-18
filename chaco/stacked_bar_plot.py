
from __future__ import with_statement

# Major library imports
from numpy import array, compress, concatenate, searchsorted

# Enthought library imports
from traits.api import Instance, List, Property

# Chaco imports
from abstract_data_source import AbstractDataSource
from base_stacked_bar_plot import BaseStackedBarPlot

def broaden(mask):
    """ Takes a 1D boolean mask array and returns a copy with all the non-zero
    runs widened by 1.
    """
    if len(mask) < 2:
        return mask
    # Note: the order in which these operations are performed is important.
    # Modifying newmask in-place with the |= operator only works for if
    # newmask[:-1] is the L-value.
    newmask = concatenate(([False], mask[1:] | mask[:-1]))
    newmask[:-1] |= mask[1:]
    return newmask


class StackedBarPlot(BaseStackedBarPlot):
    """ A plot consisting of a filled bar(s)

    The values in the **index** datasource indicate the centers of the bins;
    the widths of the bins are *not* specified in data space, and are
    determined by the minimum space between adjacent index values.
    """

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # The "upper" extent of the "bar(s)"
    bar_maxes = Instance(AbstractDataSource)

    value = Property

    def map_data(self, screen_pt, all_values=True):
        """ Maps a screen space point into the "index" space of the plot.

        Overrides the BaseXYPlot implementation, and always returns an
        array of (index, value) tuples.
        """
        x, y = screen_pt
        if self.orientation == 'v':
            x, y = y, x
        return array((self.index_mapper.map_data(x),
                      self.value_mapper.map_data(y)))

    def map_index(self, screen_pt, threshold=0.0, outside_returns_none=True,
                  index_only = True):
        if not index_only:
            raise NotImplementedError("Bar Plots only support index_only map_index()")
        if len(screen_pt) == 0:
            return None

        # Find the closest index point using numpy
        index_data = self.index.get_data()
        if len(index_data) == 0:
            return None

        target_data = self.index_mapper.map_data(screen_pt[0])

        index = searchsorted(index_data, [target_data])[0]
        if index == len(index_data):
            index -= 1
        # Bracket index and map those points to screen space, then
        # compute the distance
        if index > 0:
            lower = index_data[index-1]
            upper = index_data[index]
            screen_low, screen_high = self.index_mapper.map_screen(array([lower, upper]))
            # Find the closest index
            low_dist = abs(screen_pt[0] - screen_low)
            high_dist = abs(screen_pt[0] - screen_high)
            if low_dist < high_dist:
                index = index - 1
                dist = low_dist
            else:
                dist = high_dist
            # Determine if we need to check the threshold
            if threshold > 0 and dist >= threshold:
                return None
            else:
                return index
        else:
            screen = self.index_mapper.map_screen(index_data[0])
            if threshold > 0 and abs(screen - screen_pt[0]) >= threshold:
                return None
            else:
                return index

    def _gather_points(self):
        index = self.index.get_data()
        mask = broaden(self.index_range.mask_data(index))

        if not mask.any():
            self._cached_data_pts = []
            self._cache_valid = True
            return

        data_pts = [compress(mask, index)]

        for v in self.bar_maxes.get_data():
            if v is None or len(v) == 0:
                data_pts.append(None)
            else:
                data_pts.append(compress(mask, v))

        self._cached_data_pts = data_pts
        self._cache_valid = True

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        self._gather_points()

        if len(self._cached_data_pts) == 0:
            return

        index = self.index_mapper.map_screen(self._cached_data_pts[0])
        if len(index) == 0:
            return

        bar_maxes = []
        for v in self._cached_data_pts[1:]:
            if v is None:
                bar_maxes.append(None)
            else:
                bar_maxes.append(self.value_mapper.map_screen(v))

        # Compute lefts and rights from self.index, which represents bin
        # centers.
        if len(index) == 1:
            width = 5.0
        else:
            width = (index[1:] - index[:-1]).min() / 2.5
        left = index - width
        right = index + width

        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            self._render(gc, left, right, bar_maxes)

    def _get_value(self):
        # TODO: Check where this is used to make sure it returns what we want.
        if self.bar_maxes is not None:
            return self.bar_maxes


