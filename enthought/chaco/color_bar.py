""" Defines the ColorBar class.
"""

from __future__ import with_statement

# Major library imports
from numpy import array, arange, ones, transpose, uint8

# Enthought library imports
from enthought.traits.api import Any, Bool, Enum, Instance, Property
from enthought.kiva.image import GraphicsContext

# Local imports
from base_xy_plot import BaseXYPlot
from abstract_plot_renderer import AbstractPlotRenderer
from abstract_mapper import AbstractMapper
from array_data_source import ArrayDataSource
from grid import PlotGrid
from axis import PlotAxis


class ColorBar(AbstractPlotRenderer):
    """ A color bar for a color-mapped plot.
    """
    # Screen mapper for index data.
    index_mapper = Instance(AbstractMapper)

    # Screen mapper for color data
    color_mapper = Property #Instance(ColorMapper)

    # Optional index data source for generic tools to attach metadata to.
    index = Property
    
    # Optional color-mapped plot that this color bar references.  If specified,
    # the plot must have a **color_mapper** attribute.
    plot = Any

    # Is there a visible grid on the colorbar?
    grid_visible = Bool(True)
    
    # Is there a visible axis on the colorbar?
    axis_visible = Bool(True)

    # Corresponds to either **index_mapper** or None, depending on
    # the orientation of the plot.
    x_mapper = Property
    # Corresponds to either **index_mapper** or None, depending on
    # the orientation of the plot.
    y_mapper = Property

    #------------------------------------------------------------------------
    # Override default values of inherited traits
    #------------------------------------------------------------------------

    # The border is visible (overrides enable.Component).    
    border_visible = True
    # The orientation of the index axis.
    orientation = Enum('v', 'h')
    # Should the bar go left-to-right or bottom-to-top (normal) or the reverse?
    direction = Enum('normal', 'flipped')
    # Overrides the default background color trait in PlotComponent.
    bgcolor = 'transparent'
    # Draw layers in "draw order"
    use_draw_order = True
    # Default width is 40 pixels (overrides enable.CoordinateBox)
    width = 40
    
    # Faux origin for the axis to look at
    origin = Enum('bottom left', 'top left', 'bottom right', 'top right')

    #------------------------------------------------------------------------
    # Private attributes
    #------------------------------------------------------------------------
    
    # The grid
    _grid = Instance(PlotGrid)
    
    # The axis
    _axis = Instance(PlotAxis)
    
    # Shadow attribute for color_mapper
    _color_mapper = Any
    
    # Shadow attribute for index
    _index = Instance(ArrayDataSource, args=())
    
    def __init__(self, *args, **kw):
        """ In creating an instance, this method ensures that the grid and the
        axis are created before setting their visibility.
        """
        grid_visible = kw.pop("grid_visible", True)
        axis_visible = kw.pop("axis_visible", True)
        
        super(ColorBar, self).__init__(*args, **kw)

        if self.orientation == 'h':
            if self.direction == 'normal':
                self.origin = 'bottom left'
            else:
                self.origin = 'bottom right'
            grid_orientation = 'vertical'
            axis_orientation = 'bottom'
        else:
            if self.direction == 'normal':
                self.origin = 'bottom left'
            else:
                self.origin = 'top left'
            grid_orientation = 'horizontal'
            axis_orientation = 'left'

        self._grid = PlotGrid(orientation=grid_orientation,
                              mapper=self.index_mapper,
                              component=self)
        self._axis = PlotAxis(orientation=axis_orientation,
                              mapper=self.index_mapper,
                              component=self)
        self.overlays.append(self._grid)
        self.overlays.append(self._axis)
        
        # Now that we have a grid and an axis, we can safely set the visibility
        self.grid_visible = grid_visible
        self.axis_visible = axis_visible
        return

    def _draw_plot(self, gc, view_bounds=None, mode='normal'):
        """ Draws the 'plot' layer.
        """
        self._update_mappers()
        with gc:
            if self.orientation == 'h':
                perpendicular_dim = 1
                axis_dim = 0
            else:
                perpendicular_dim = 0
                axis_dim = 1
            
            mapper = self.index_mapper

            scrn_points = arange(mapper.low_pos, mapper.high_pos+1)
            
            # Get the data values associated with the list of screen points.
            if mapper.range.low == mapper.range.high:
                # LogMapper.map_data() returns something unexpected if low==high,
                # so we'll handle that case here.
                data_points = array([mapper.range.high])
            else:
                data_points = mapper.map_data(scrn_points)

            if self.direction == 'flipped':
                data_points = data_points[::-1]
                
            # Get the colors associated with the data points.
            colors = self.color_mapper.map_screen(data_points)
            
            img = self._make_color_image(colors, self.bounds[perpendicular_dim],
                                                    self.orientation, self.direction)
            gc.draw_image(img, (self.x, self.y, self.width, self.height))
    
    def _make_color_image(self, color_values, width, orientation, direction):
        """
        Returns an image graphics context representing the array of color 
        values (Nx3 or Nx4). The *width* parameter is the width of the 
        colorbar, and *orientation* is the orientation of the plot.
        """
        bmparray = ones((width, color_values.shape[0],
                                    color_values.shape[1]))* color_values * 255
        
        if orientation == "v":
            bmparray = transpose(bmparray, axes=(1,0,2))[::-1]
        bmparray = bmparray.astype(uint8)
        img = GraphicsContext(bmparray, "rgba32")
        return img
        
    
    #------------------------------------------------------------------------
    # Trait events
    #------------------------------------------------------------------------
    
    def _update_mappers(self):
        if not self.index_mapper or not self.color_mapper:
            return
        if self.orientation == 'h' and 'left' in self.origin:
            self.index_mapper.low_pos = self.x
            self.index_mapper.high_pos = self.x2
        elif self.orientation == 'h' and 'right' in self.origin:
            self.index_mapper.low_pos = self.x2
            self.index_mapper.high_pos = self.x
        elif self.orientation == 'v' and 'bottom' in self.origin:
            self.index_mapper.low_pos = self.y
            self.index_mapper.high_pos = self.y2
        elif self.orientation == 'v' and 'top' in self.origin:
            self.index_mapper.low_pos = self.y2
            self.index_mapper.high_pos = self.y
        self.index_mapper.range = self.color_mapper.range

    def _bounds_changed(self, old, new):
        super(ColorBar, self)._bounds_changed(old, new)
        self._update_mappers()

    def _bounds_items_changed(self, event):
        super(ColorBar, self)._bounds_items_changed(event)
        self._update_mappers()

    def _position_changed(self, old, new):
        super(ColorBar, self)._position_changed(old, new)
        self._update_mappers()

    def _position_items_changed(self, event):
        super(ColorBar, self)._position_items_changed(event)
        self._update_mappers()
        
    def _updated_changed_for_index_mapper(self):
        self._update_mappers()

    def _updated_changed_for_color_mapper(self):
        self._update_mappers()

    def _either_mapper_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        
    def _index_mapper_changed(self):
        # Keep the grid and axis index_mappers the same as our index_mapper.
        if self._grid is not None:
            self._grid.mapper = self.index_mapper
        if self._axis is not None:
            self._axis.mapper = self.index_mapper
        self._either_mapper_changed()

    def _color_mapper_changed(self):
        self._either_mapper_changed()

    def _plot_changed(self):
        self.request_redraw()
    
    def _grid_visible_changed(self, old, new):
        self._grid.visible = new
        self.request_redraw()
    
    def _axis_visible_changed(self, old, new):
        self._axis.visible = new
        self.request_redraw()
    
    #------------------------------------------------------------------------
    # Property setters and getters
    #------------------------------------------------------------------------

    def _get_x_mapper(self):
        if self.orientation == "h":
            return self.index_mapper
        else:
            return None
    
    def _get_y_mapper(self):
        if self.orientation == "h":
            return None
        else:
            return self.index_mapper

    def _get_color_mapper(self):
        if self.plot:
            return self.plot.color_mapper
        elif self._color_mapper:
            return self._color_mapper
        else:
            return None

    def _set_color_mapper(self, val):
        self._color_mapper = val

    def _get_index(self):
        if self.plot and hasattr(self.plot, "color_data"):
            return self.plot.color_data
        elif self.plot and isinstance(self.plot, BaseXYPlot):
            return self.plot.index
        elif self._index:
            return self._index
        else:
            return None

    def _set_index(self, val):
        self._index = val


# EOF
