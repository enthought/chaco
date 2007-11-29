""" Defines the DataView class, and associated property traits and property
functions.
"""
from enthought.traits.api import Enum, Instance, Property

from axis import PlotAxis
from base_1d_mapper import Base1DMapper
from data_range_2d import DataRange2D
from grid import PlotGrid
from linear_mapper import LinearMapper
from log_mapper import LogMapper
from plot_containers import OverlayPlotContainer


#-----------------------------------------------------------------------------
# Define new traits to condense the definition of some convenience
# properties in the Plot class
#-----------------------------------------------------------------------------

def get_mapper(self, attr_name):
    """ Getter function used by OrientedMapperProperty.
    """
    if (attr_name,self.orientation) in [("x_mapper","h"), ("y_mapper","v")]:
        return self.index_mapper
    else:
        return self.value_mapper

def set_mapper(self, attr_name, new):
    """ Setter function used by OrientedMapperProperty.
    """
    if (attr_name,self.orientation) in [("x_mapper","h"), ("y_mapper","v")]:
        self.index_mapper = new
    else:
        self.value_mapper = new

# Property that represents a mapper for an orientation.
OrientedMapperProperty = Property(get_mapper, set_mapper)


def get_axis(self, attr_name):
    """ Getter function used by AxisProperty.
    """
    if (attr_name,self.orientation) in [("index_axis","h"), ("value_axis","v")]:
        return self.x_axis
    else:
        return self.y_axis

def set_axis(self, attr_name, new):
    """ Setter function used by AxisProperty.
    """
    if (attr_name,self.orientation) in [("index_axis","h"), ("value_axis","v")]:
        self.x_axis = new
    else:
        self.y_axis = new

# Property that represents an axis.
AxisProperty = Property(get_axis, set_axis)


def get_grid(self, attr_name):
    """ Getter function used by GridProperty.
    """
    if (attr_name,self.orientation) in [("index_grid","v"), ("value_grid","h")]:
        return self.y_grid
    else:
        return self.x_grid

def set_grid(self, attr_name, new):
    """ Setter function used by GridProperty.
    """
    if (attr_name,self.orientation) in [("index_grid","v"), ("value_grid","h")]:
        self.y_grid = new
    else:
        self.y_grid = new

# Property that represents a grid for a particular orientation.
GridProperty = Property(get_grid, set_grid)


class DataView(OverlayPlotContainer):
    """ Represents a mapping from 2-D data space into 2-D screen space.
    
    It can house renderers and other plot components, and otherwise behaves
    just like a normal PlotContainer.
    """
    
    # The orientation of the index axis.
    orientation = Enum("h", "v")

    # The default location of the origin 
    default_origin = Enum("bottom left", "top left", 
                          "bottom right", "top right")

    # The mapper to use for the index data.
    index_mapper = Instance(Base1DMapper)

    # The mapper to use for value data.
    value_mapper = Instance(Base1DMapper)

    # For x-y plots, the scale of the index axis.
    index_scale = Enum("linear", "log")

    # For x-y plots, the scale of the index axis.
    value_scale = Enum("linear", "log")

    # The range used for the index data.
    index_range = Property

    # The range used for the value data.
    value_range = Property

    # The 2-D data range whose x- and y-ranges are exposed as the 
    # **index_range** and **value_range** property traits. This allows 
    # supporting both XY plots and 2-D (image) plots.
    range2d = Instance(DataRange2D)
    
    # Convenience property that offers access to whatever mapper corresponds
    # to the X-axis.
    x_mapper = OrientedMapperProperty
    
    # Convenience property that offers access to whatever mapper corresponds
    # to the Y-axis
    y_mapper = OrientedMapperProperty

    #------------------------------------------------------------------------
    # Axis and Grids
    #------------------------------------------------------------------------

    # The horizontal axis.  Its position relative to the plot
    # area can be "top", "bottom", or "float".  The default position for a new
    # x-axis is "bottom".
    x_axis = Instance(PlotAxis)
    
    # The vertical axis.  Its position relative to the plot
    # area can be "left", "right", or "float".  The default position for a new
    # y-axis is "left".
    y_axis = Instance(PlotAxis)

    # The grid that intersects the x-axis, i.e., a set of vertical lines.
    x_grid = Instance(PlotGrid)
    
    # The grid that intersects the y-axis, i.e., a set of horizontal lines.
    y_grid = Instance(PlotGrid)

    # Convenience property for accessing the index axis, which can be X or Y,
    # depending on **orientation**.
    index_axis = AxisProperty
    # Convenience property for accessing the value axis, which can be Y or X,
    # depending on **orientation**.
    value_axis = AxisProperty
    # Convenience property for accessing the index grid, which can be horizontal
    # or vertical, depending on **orientation**.
    index_grid = GridProperty
    # Convenience property for accessing the value grid, which can be vertical
    # or horizontal, depending on **orientation**.
    value_grid = GridProperty

    #------------------------------------------------------------------------
    # Appearance
    #------------------------------------------------------------------------

    # Background color (overrides Enable2 Component)
    bgcolor = "white"

    # Draw borders as part of the background layer (overrides PlotComponent).
    overlay_border = False


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, **kwtraits):
        # Crappy - have to initialize a property this way instead of by
        # overriding the defaults
        if "padding" not in kwtraits:
            kwtraits["padding"] = 50

        super(DataView, self).__init__(**kwtraits)
        self._init_components()

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _init_components(self):
        # Since this is called after the HasTraits constructor, we have to make
        # sure that we don't blow away any components that the caller may have
        # already set.

        if not self.range2d:
            self.range2d = DataRange2D()

        if not self.index_mapper:
            if self.index_scale == "linear":
                imap = LinearMapper(range=self.range2d.x_range)
            else:
                imap = LogMapper(range=self.range2d.x_range)
            self.index_mapper = imap
        
        if not self.value_mapper:
            if self.value_scale == "linear":
                vmap = LinearMapper(range=self.range2d.y_range)
            else:
                vmap = LogMapper(range=self.range2d.y_range)
            self.value_mapper = vmap

        if not self.x_grid:
            self.x_grid = PlotGrid(mapper=self.x_mapper, orientation="vertical",
                                  line_color="lightgray", line_style="dot",
                                  component=self)
        if not self.y_grid:
            self.y_grid = PlotGrid(mapper=self.y_mapper, orientation="horizontal",
                                  line_color="lightgray", line_style="dot",
                                  component=self)

        if not self.x_axis:
            self.x_axis = PlotAxis(mapper=self.x_mapper, orientation="bottom",
                                  component=self)

        if not self.y_axis:
            self.y_axis = PlotAxis(mapper=self.y_mapper, orientation="left",
                                  component=self)

    #-------------------------------------------------------------------------
    # Event handlers
    #-------------------------------------------------------------------------

    def _update_mappers(self):

        x = self.x
        x2 = self.x2
        y = self.y
        y2 = self.y2
        
        if self.x_mapper is not None:
            if "left" in self.origin:
                self.x_mapper.low_pos = x
                self.x_mapper.high_pos = x2
            else:
                self.x_mapper.low_pos = x2
                self.x_mapper.high_pos = x
        
        if self.y_mapper is not None:
            if "bottom" in self.origin:
                self.y_mapper.low_pos = y
                self.y_mapper.high_pos = y2
            else:
                self.y_mapper.low_pos = y2
                self.y_mapper.high_pos = y
        
        self.invalidate_draw()
        return

    def _bounds_changed(self, old, new):
        self._update_mappers()
        super(DataView, self)._bounds_changed(old, new)
        return

    def _bounds_items_changed(self, event):
        self._update_mappers()
        super(DataView, self)._bounds_items_changed(event)
        return

    def _position_changed(self):
        self._update_mappers()
        return

    def _position_items_changed(self):
        self._update_mappers()
        return

    def _orientation_changed(self):
        self._update_mappers()
        for renderer in self.components:
            if hasattr(renderer, "orientation"):
                renderer.orientation = self.orientation
        return

    def _index_mapper_changed(self, old, new):
        if new is not None:
            if new.range is not None:
                # Add the range's datasources to our range
                for source in new.range.sources:
                    self.index_range.add(source)
            new.range = self.index_range
        if self.index_axis:
            self.index_axis.mapper = new
        if self.index_grid:
            self.index_grid.mapper = new
    
    def _value_mapper_changed(self, old, new):
        if new is not None:
            if new.range is not None:
                # Add the range's datasources to our range
                for source in new.range.sources:
                    self.value_range.add(source)
            new.range = self.value_range
        if self.value_axis:
            self.value_axis.mapper = new
        if self.value_grid:
            self.value_grid.mapper = new

    def _bgcolor_changed(self):
        self.invalidate_draw()

    def _x_grid_changed(self, old, new):
        self._underlay_change_helper(old, new)

    def _y_grid_changed(self, old, new):
        self._underlay_change_helper(old, new)

    def _x_axis_changed(self, old, new):
        self._underlay_change_helper(old, new)

    def _y_axis_changed(self, old, new):
        self._underlay_change_helper(old, new)

    def _underlay_change_helper(self, old, new):
        if old in self.underlays:
            self.underlays.remove(old)
        if new is not None:
            self.underlays.append(new)

    def _overlay_change_helper(self, old, new):
        if old in self.overlays:
            self.overlays.remove(old)
        if new is not None:
            self.overlays.append(new)

    def _range2d_changed(self, old, new):
        if new is not None:
            if self.index_mapper is not None:
                self.index_mapper.range = new.x_range
            if self.value_mapper is not None:
                self.value_mapper.range = new.y_range
        else:
            self.index_mapper.range = None
            self.value_mapper.range = None
        if old is not None:
            for datasource in old.sources[:]:
                old.remove(datasource)
                if new is not None:
                    new.add(datasource)
        for renderer in self.components:
            if hasattr(renderer, 'range2d'):
                setattr(renderer, 'range2d', new)
            else:
                if hasattr(renderer, 'index_range'):
                    setattr(renderer, 'index_range', self.index_range)
                if hasattr(renderer, 'value_range'):
                    setattr(renderer, 'value_range', self.value_range)



    #------------------------------------------------------------------------
    # Property getters and setters
    #------------------------------------------------------------------------

    def _get_index_range(self):
        return self.range2d.x_range

    def _set_index_range(self, newrange):
        self._handle_range_changed("index", self.range2d.x_range, newrange)
        self.range2d.x_range = newrange

    def _get_value_range(self):
        return self.range2d.y_range

    def _set_value_range(self, newrange):
        self._handle_range_changed("value", self.range2d.y_range, newrange)
        self.range2d.y_range = newrange

    def _handle_range_changed(self, name, old, new):
        mapper = getattr(self, name+"_mapper")
        if mapper.range == old:
            mapper.range = new
        if old is not None:
            for datasource in old.sources[:]:
                old.remove(datasource)
                if new is not None:
                    new.add(datasource)
        range_name = name + "_range"
        for renderer in self.components:
            if hasattr(renderer, range_name):
                setattr(renderer, range_name, new)


