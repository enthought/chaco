""" Defines the base class for 2-D plots.
"""
# Standard library imports
from numpy import asarray, isnan

# Enthought library imports.
from traits.api import Enum, Event, Instance, Property, Range, Trait

# Local relative imports
from .abstract_plot_renderer import AbstractPlotRenderer
from .base import reverse_map_1d
from .plot_label import PlotLabel
from .grid_data_source import GridDataSource
from .grid_mapper import GridMapper
from .image_data import ImageData


class Base2DPlot(AbstractPlotRenderer):
    """ Base class for 2-D plots.
    """
    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # The data source to use for the index coordinate.
    index = Instance(GridDataSource)

    # The data source to use as value points.
    value = Instance(ImageData)

    # Screen mapper for 2-D structured (gridded) index data.
    index_mapper = Instance(GridMapper)

    # Convenience property for accessing the data range of the mapper.
    index_range = Property

    # Convenience property for accessing the plots labels.
    labels = Property

    # The direction that the first array returned by self.index.get_data()
    # maps to.
    #
    # * 'h': index maps to x-direction
    # * 'v': index maps to y-direction
    orientation = Enum("h", "v")

    # Overrides PlotComponent; 2-D plots draw on the 'image' layer,
    # underneath all decorations and annotations, and above only the background
    # fill color.
    draw_layer = "image"

    # Convenience property for accessing the x-direction mappers regardless
    # of orientation.  This provides compatibility with a number of tools.
    x_mapper = Property
    # Convenience property for accessing the y-direction mappers regardless
    # of orientation.  This provides compatibility with a number of tools.
    y_mapper = Property

    # Overall alpha value of the image. Ranges from 0.0 for transparent to 1.0
    # for full intensity.
    alpha = Trait(1.0, Range(0.0, 1.0))

    # Event fired when the index data changes. Subclasses can listen for this
    # event and take appropriate steps (except for requesting a redraw, which
    # is done in this class).
    index_data_changed = Event

    # Event fired when the index mapper changes. Subclasses can listen for this
    # event and take appropriate steps (except for requesting a redraw, which
    # is done in this class).
    index_mapper_changed = Event

    # Event fired when the value data changes. Subclasses can listen for this
    # event and take appropriate steps (except for requesting a redraw, which
    # is done in this class).
    value_data_changed = Event

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, **kwargs):
        # Handling the setting/initialization of these traits manually because
        # they should be initialized in a certain order.
        kwargs_tmp = {"trait_change_notify": False}
        for trait_name in ("index", "value"):
            if trait_name in kwargs:
                kwargs_tmp[trait_name] = kwargs.pop(trait_name)
        self.set(**kwargs_tmp)
        super(Base2DPlot, self).__init__(**kwargs)
        if self.index is not None:
            self.index.on_trait_change(self._update_index_data,
                                       "data_changed")
        if self.index_mapper:
            self.index_mapper.on_trait_change(self._update_index_mapper,
                                              "updated")
        if self.value is not None:
            self.value.on_trait_change(self._update_value_data,
                                       "data_changed")
        # If we are not resizable, we will not get a bounds update upon layout,
        # so we have to manually update our mappers
        if self.resizable == "":
            self._update_mappers()
        return

    #------------------------------------------------------------------------
    # AbstractPlotRenderer interface
    #------------------------------------------------------------------------

    def map_screen(self, data_pts):
        """ Maps an array of data points into screen space and returns it as
        an array.

        Implements the AbstractPlotRenderer interface.
        """
        # data_pts is Nx2 array
        if len(data_pts) == 0:
            return []
        return asarray(self.index_mapper.map_screen(data_pts))

    def map_data(self, screen_pts):
        """ Maps a screen space point into the "index" space of the plot.

        Implements the AbstractPlotRenderer interface.
        """
        return self.index_mapper.map_data(screen_pts)

    def map_index(self, screen_pt, threshold=2.0,
                  outside_returns_none=True, index_only=False):
        """ Maps a screen space point to an index into the plot's index arrays.

        Implements the AbstractPlotRenderer interface.
        The *index_only* parameter is ignored because the index is
        intrinsically 2-D.
        """
        if self.orientation == 'h':
            x_pt,y_pt = self.map_data([screen_pt])[0]
        else:
            x_pt,y_pt = self.map_data([(screen_pt[1],screen_pt[0])])[0]

        if ((x_pt < self.index_mapper.range.low[0]) or
            (x_pt > self.index_mapper.range.high[0]) or
            (y_pt < self.index_mapper.range.low[1]) or
            (y_pt > self.index_mapper.range.high[1])) and outside_returns_none:
            return None, None

        x_index_data, y_index_data = self.index.get_data()

        if x_index_data.get_size() == 0 or y_index_data.get_size() == 0:
            return None, None

        # attempt to map to the x index
        x_data = x_index_data.get_data()
        y_data = y_index_data.get_data()
        try:
            x_ndx = reverse_map_1d(x_data, x_pt, self.index.sort_order[0],
                                   floor_only=True)
        except IndexError as e:
            if outside_returns_none:
                return None, None

            # x index
            if x_pt < x_data[0]:
                x_ndx =  0
            else:
                x_ndx = len(x_data) - 1

        try:
            y_ndx = reverse_map_1d(y_data, y_pt, self.index.sort_order[1],
                                   floor_only=True)
        except IndexError as e:
            if outside_returns_none:
                return None, None

            # y index
            if y_pt < y_data[0]:
                y_ndx =  0
            else:
                y_ndx = len(y_data) - 1

        if threshold == 0:
            return x_ndx, y_ndx

        x = x_data[x_ndx]
        y = y_data[y_ndx]
        if isnan(x) or isnan(y):
            return None, None

        sx, sy =  self.map_screen([(x,y)])[0]
        if ((screen_pt[0]-sx)**2 + (screen_pt[1]-sy)**2 < threshold**2):
            return x_ndx, y_ndx
        else:
            return None, None

    #------------------------------------------------------------------------
    # PlotComponent interface
    #------------------------------------------------------------------------

    def _draw_image(self, gc, view_bounds=None, mode="normal"):
        """ Handler for drawing the 'image' layer.

        Used by the PlotComponent interface.
        """
        self._render(gc)
        return

    #------------------------------------------------------------------------
    # Abstract methods that subclasses must implement
    #------------------------------------------------------------------------

    def _render(self, gc, points):
        """ Abstract method for drawing the plot.
        """
        raise NotImplementedError

    #------------------------------------------------------------------------
    # Properties
    #------------------------------------------------------------------------

    def _get_index_range(self):
        return self.index_mapper.range

    def _set_index_range(self, val):
        self.index_mapper.range = val

    def _get_labels(self):
        labels = []
        for obj in self.underlays+self.overlays:
            if isinstance(obj, PlotLabel):
                labels.append(obj)
        return labels

    def _get_x_mapper(self):
        if self.orientation == 'h':
            return self.index_mapper._xmapper
        else:
            return self.index_mapper._ymapper

    def _get_y_mapper(self):
        if self.orientation == 'h':
            return self.index_mapper._ymapper
        else:
            return self.index_mapper._xmapper


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _update_index_mapper(self):
        """ Updates the index mapper.

        Called by various trait change handlers.
        """

        x = self.x
        x2 = self.x2
        y = self.y
        y2 = self.y2

        if "left" in self.origin:
            x_low = x
            x_high = x2
        else:
            x_low = x2
            x_high = x

        if "bottom" in self.origin:
            y_low = y
            y_high = y2
        else:
            y_low = y2
            y_high = y

        if self.index_mapper is not None:
            if self.orientation == 'h':
                self.index_mapper.screen_bounds = (x_low, x_high, y_low, y_high)
            else:
                self.index_mapper.screen_bounds = (y_low, y_high, x_low, x_high)
            self.index_mapper_changed = True
            self.invalidate_draw()

    def _update_index_data(self):
        """ Updates the index data.

        Called by various trait change handlers.
        """
        self.index_data_changed = True
        self.invalidate_draw()

    def _update_value_data(self):
        """ Updates the value data.

        Called by various trait change handlers.
        """
        self.value_data_changed = True
        self.invalidate_draw()


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _bounds_changed(self, old, new):
        super(Base2DPlot, self)._bounds_changed(old, new)
        self._update_index_mapper()

    def _bounds_items_changed(self, event):
        super(Base2DPlot, self)._bounds_items_changed(event)
        self._update_index_mapper()

    def _orientation_changed(self):
        self._update_index_mapper()

    def _origin_changed(self):
        self._update_index_mapper()

    def _index_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._update_index_data,
                                "data_changed", remove=True)
        if new is not None:
            new.on_trait_change(self._update_index_data, "data_changed")
        self._update_index_data()

    def _value_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._update_value_data,
                                "data_changed", remove=True)
        if new is not None:
            new.on_trait_change(self._update_value_data, "data_changed")
        self._update_value_data()

    def _index_mapper_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self._update_index_mapper,
                                "updated", remove=True)
        if new is not None:
            new.on_trait_change(self._update_index_mapper, "updated")
        self._update_index_mapper()

