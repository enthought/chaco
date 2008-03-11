""" Defines the PlotGrid class, and associated Traits UI View and validator
function.
"""

import pdb
from numpy import around, array, column_stack, float64, inf, zeros_like

# Enthought library imports
from enthought.enable2.api import black_color_trait, LineStyle
from enthought.traits.api import Any, Enum, false, Float, Instance, Int, CInt, Trait, \
                            Array, Property, TraitError
from enthought.traits.ui.api import HGroup, Item, VGroup, View, TextEditor

# Local, relative imports
from abstract_overlay import AbstractOverlay
from abstract_mapper import AbstractMapper
from log_mapper import LogMapper
from ticks import AbstractTickGenerator, DefaultTickGenerator


def float_or_auto(val):
    """
    Validator function that returns *val* if *val* is either a number or 
    the word 'auto'.  This is used as a validator for the text editor
    in the traits UI for the tick_interval trait.
    """
    try:
        return float(val)
    except:
        if isinstance(val, basestring) and val == "auto":
            return val
    raise TraitError, "Tick interval must be a number or 'auto'."

# View for setting grid properties.
GridView = View(VGroup(
                HGroup(Item("grid_interval", label="Interval", editor=TextEditor(evaluate=float_or_auto)),
                       Item("visible", label="Visible")),
                Item("line_color", label="Color", style="custom"),
                Item("line_style", label="Dash style"),
                Item("line_width", label="Thickness")
                ),
                buttons = ["OK", "Cancel"]
            )

    
def Alias(name):
    return Property(lambda obj: getattr(obj, name),
                    lambda obj, val: setattr(obj, name, val))


class PlotGrid(AbstractOverlay):
    """ An overlay that represents a grid. 
    
    A grid is a set of parallel lines, horizontal or vertical. You can use 
    multiple grids with different settings for the horizontal and vertical
    lines in a plot.
    """
    # The mapper (and associated range) that drive this PlotGrid.
    mapper = Instance(AbstractMapper)

    # The orientation of the grid lines.
    orientation = Enum('horizontal', 'vertical')
    
    # Draw the ticks starting at the end of the mapper range? If False, the
    # ticks are drawn starting at 0. This setting can be useful to keep the 
    # grid from from "flashing" as the user resizes the plot area.
    flip_axis = false
    
    # The color of the grid lines.
    line_color = black_color_trait
    
    # The style (i.e., dash pattern) of the grid lines.
    line_style = LineStyle('solid')
    
    # The thickness, in pixels, of the grid lines.
    line_width = CInt(1)
    
    line_weight = Alias("line_width")

    # The dataspace interval between grid lines.
    grid_interval = Trait('auto', 'auto', Float)

    # A callable that implements the AbstractTickGenerator Interface.
    tick_generator = Instance(AbstractTickGenerator)

    # Dimensions that the grid is resizable in (overrides PlotComponent).
    resizable = "hv"
    
    # Default Traits UI View for modifying grid attributes.
    traits_view = GridView
    
    # Private traits; cached info
    
    _cache_valid = false
    _tick_list = Any
    _tick_positions = Any
    _length = Float(0.0)
    
    
    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, **traits):
        # TODO: change this back to a factory in the instance trait some day
        self.tick_generator = DefaultTickGenerator()
        super(PlotGrid, self).__init__(**traits)
        self.bgcolor = "none" #make sure we're transparent
        return

    def invalidate(self):
        """ Invalidate cached information about the grid.
        """
        self._reset_cache()
        return


    #------------------------------------------------------------------------
    # PlotComponent and AbstractOverlay interface
    #------------------------------------------------------------------------
    
    def do_layout(self, *args, **kw):
        """ Tells this component to do layout at a given size.
        
        Overrides PlotComponent.
        """
        if self.use_draw_order and self.component is not None:
            self._layout_as_overlay(*args, **kw)
        else:
            super(PlotGrid, self).do_layout(*args, **kw)
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _do_layout(self):
        """ Performs a layout.
        
        Overrides PlotComponent.
        """
        return
    
    def _layout_as_overlay(self, size=None, force=False):
        """ Lays out the axis as an overlay on another component.
        """
        if self.component is not None:
            self.position = self.component.position
            self.bounds = self.component.bounds
        return
    
    def _reset_cache(self):
        """ Clears the cached tick positions.
        """
        self._tick_positions = array([], dtype=float)
        self._length = 0.0
        self._cache_valid = False
        return
    
    def _compute_ticks(self, component=None):
        """ Calculates the positions for the grid lines.
        """
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
        
        if component is None:
            component = self.component
        
        if component is not None:
            bounds = component.bounds
            position = component.position
        else:
            bounds = self.bounds
            position = self.position

        if isinstance(self.mapper, LogMapper):
            scale = 'log'
        else:
            scale = 'linear'

        ticks = self.tick_generator.get_ticks(datalow, datahigh, datalow, datahigh,
                                              self.grid_interval, use_endpoints = False,
                                              scale=scale)
        tick_positions = self.mapper.map_screen(array(ticks, float64))
        
        if self.orientation == 'horizontal':
            length = bounds[0]
            self._tick_positions = around(column_stack((zeros_like(tick_positions) + position[0],
                                           tick_positions)))
        elif self.orientation == 'vertical':
            length = bounds[1]
            self._tick_positions = around(column_stack((tick_positions,
                                           zeros_like(tick_positions) + position[1])))
        else:
            raise self.NotImplementedError

        self._length = length
        self._cache_valid = True
        
    
    def _draw_overlay(self, gc, view_bounds=None, mode='normal'):
        """ Draws the overlay layer of a component.
        
        Overrides PlotComponent.
        """
        self._draw_component(gc, view_bounds, mode)
        return

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.
        
        Overrides AbstractOverlay.
        """
        if not self.visible:
            return
        self._compute_ticks(other_component)
        self._draw_component(gc, view_bounds, mode)
        self._cache_valid = False
        return
    
    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        """ Draws the component.

        This method is preserved for backwards compatibility. Overrides 
        PlotComponent.
        """
        # What we're really trying to do with a grid is plot contour lines in
        # the space of the plot.  In a rectangular plot, these will always be
        # straight lines.
        if not self.visible:
            return

        if not self._cache_valid:
            self._compute_ticks()

        if len(self._tick_positions) == 0:
            return
        
        try:
            gc.save_state()
            gc.set_line_width(self.line_weight)
            gc.set_line_dash(self.line_style_)
            gc.set_stroke_color(self.line_color_)
            gc.set_antialias(False)
            gc.begin_path()
            
            if self.orientation == "horizontal":
                length_vec = array((self._length, 0.0))
            else:
                length_vec = array((0.0, self._length))
            starts = self._tick_positions
            ends = starts + length_vec
            if self.flip_axis:
                starts, ends = ends, starts
            gc.line_set(starts, ends)
            gc.stroke_path()
        finally:
            gc.restore_state()
        return
        
    def _mapper_changed(self, old, new):
        if old is not None:
            old.on_trait_change(self.mapper_updated, "updated", remove=True)
        if new is not None:
            new.on_trait_change(self.mapper_updated, "updated")
        self.invalidate()
        return
        
    def mapper_updated(self):
        """
        Event handler that is bound to this mapper's **updated** event.
        """
        self.invalidate()
        return
    
    def _bounds_changed(self, old, new):
        super(PlotGrid, self)._bounds_changed(old, new)
        self.invalidate()
    
    def _bounds_items_changed(self, event):
        super(PlotGrid, self)._bounds_items_changed(event)
        self.invalidate()

    def _position_changed(self, old, new):
        super(PlotGrid, self)._position_changed(old, new)
        self.invalidate()

    def _position_items_changed(self, event):
        super(PlotGrid, self)._position_items_changed(event)
        self.invalidate()

    def _position_changed_for_component(self):
        self.invalidate()

    def _position_items_changed_for_component(self):
        self.invalidate()

    def _bounds_changed_for_component(self):
        self.invalidate()

    def _bounds_items_changed_for_component(self):
        self.invalidate()
    
    #------------------------------------------------------------------------
    # Event handlers for visual attributes.  These mostly just call request_redraw()
    #------------------------------------------------------------------------
    
    def visual_attr_changed(self):
        """ Called when an attribute that affects the appearance of the grid
        is changed.
        """
        if self.component:
            self.component.invalidate_draw()
            self.component.request_redraw()
        else:
            self.invalidate_draw()
            self.request_redraw()
        
    def _visible_changed(self):
        self.visual_attr_changed()

    def _line_color_changed(self):
        self.visual_attr_changed()
        
    def _line_style_changed(self):
        self.visual_attr_changed()
        
    def _line_weight_changed(self):
        self.visual_attr_changed()
        
    def _grid_interval_changed(self):
        self.invalidate()
        self.visual_attr_changed()
        
    def _orientation_changed(self):
        self.invalidate()
        self.visual_attr_changed()
        return

        


    ### Persistence ###########################################################
    #_pickles = ("orientation", "line_color", "line_style", "line_weight",
    #            "grid_interval", "mapper")

    def __getstate__(self):
        state = super(PlotGrid,self).__getstate__()
        for key in ['_cache_valid', '_tick_list', '_tick_positions', '_length_vec']:
            if state.has_key(key):
                del state[key]

        return state

    def _post_load(self):
        super(PlotGrid, self)._post_load()
        self._mapper_changed(None, self.mapper)
        self._reset_cache()
        self._cache_valid = False
        return


# EOF
