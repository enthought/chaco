import numpy

from traits.api import HasTraits, Instance, Property

from chaco.abstract_plot_renderer import AbstractPlotRenderer
from chaco.abstract_data_source import AbstractDataSource
from chaco.base_projection import AbstractProjection
from chaco.grid_mapper import GridMapper


class BaseProjectionPlot(AbstractPlotRenderer):
    """ Base class for plots which model data in some other space, then project into
    a 2D data space window, which is the mapped to regular
    """
    # the base plot makes no distinction between index and value - we just plot data points
    # subclasses have the option of making this distinction by turning this into a property
    model = Instance(AbstractDataSource)
    
    # projection which maps points from model space to data space
    projection = Instance(AbstractProjection)
    
    # map the 2D data space into the screen space
    mapper = Instance(GridMapper)

    # Convenience property for accessing the datarange of the mapper.
    range = Property

    # Convenience property for accessing the x-direction mappers regardless
    # of orientation.  This provides compatibility with a number of tools.
    x_mapper = Property
    # Convenience property for accessing the y-direction mappers regardless
    # of orientation.  This provides compatibility with a number of tools.
    y_mapper = Property

    #------------------------------------------------------------------------
    # AbstractPlotRenderer interface
    #------------------------------------------------------------------------

    def map_screen(self, data_pts):
        """ Maps an array of data points into screen space and returns it as
        an array.

        Implements the AbstractPlotRenderer interface.
        """
        if len(data_pts) == 0:
            return []
        print self.projection.project(data_pts)
        return numpy.asarray(self.mapper.map_screen(self.projection.project(data_pts)))

    def map_data(self, screen_pts):
        """ Maps a screen space point into the "data" space of the plot.

        Implements the AbstractPlotRenderer interface.
        """
        return self.mapper.map_data(screen_pts)

    def map_index(self, screen_pt, threshold=2.0, outside_returns_none=True, index_only=False):
        """ Maps a screen space point to an index into the plot's index arrays.

        Implements the AbstractPlotRenderer interface.
        The *index_only* parameter is ignored because the index is
        intrinsically 2-D.
        """
        if self.orientation == 'h':
            x_pt,y_pt = self.map_data([screen_pt])[0]
        else:
            x_pt,y_pt = self.map_data([(screen_pt[1],screen_pt[0])])[0]

        if ((x_pt < self.mapper.range.low[0]) or
            (x_pt > self.mapper.range.high[0]) or
            (y_pt < self.mapper.range.low[1]) or
            (y_pt > self.mapper.range.high[1])) and outside_returns_none:
            return None, None

        screen_points = around(self.map_screen(self.model.get_data()))
        if len(screen_points) == 0:
            return None
        
        delta = screen_points - array([screen_pt])
        distances = hypot(delta[:,0], delta[:,1])
        closest_ndx = argmin(distances)
        if distances[closest_ndx] <= threshold:
            return closest_ndx
        else:
            return None

    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    def _get_range(self):
        return self.mapper.range

    def _set_range(self, val):
        self.mapper.range = val

    def _get_labels(self):
        labels = []
        for obj in self.underlays+self.overlays:
            if isinstance(obj, PlotLabel):
                labels.append(obj)
        return labels

    def _get_x_mapper(self):
        if self.orientation == 'h':
            return self.mapper._xmapper
        else:
            return self.mapper._ymapper

    def _get_y_mapper(self):
        if self.orientation == 'h':
            return self.mapper._ymapper
        else:
            return self.mapper._xmapper

