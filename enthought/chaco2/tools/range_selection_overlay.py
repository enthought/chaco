""" Defines the RangeSelectionOverlay class.
"""
# Major library imports
from numpy import array

# Enthought library imports
from enthought.enable2.api import ColorTrait, LineStyle
from enthought.traits.api import Any, Enum, Float, Instance, Int, Property, Trait
from enthought.chaco2.api import AbstractOverlay, PlotComponent



class RangeSelectionOverlay(AbstractOverlay):
    """ Highlights the selection region on a component.
    
    Looks at the "selections" metadata field of self.component for
    a tuple (dataspace_start, dataspace_end).
    """

    # The axis to which this tool is perpendicular.
    axis = Enum("index", "value")
    
    # Mapping from screen space to data space. By default, it is just 
    # self.component.
    plot = Property
    
    # The mapper (and associated range) that drive this RangeSelectionOverlay.
    # By default, this is the mapper on self.plot that corresponds to self.axis.
    mapper = Property
    
    # The element of an (x,y) tuple that corresponds to the axis index.
    # By default, this is set based on self.asix and self.plot.orientation,
    # but it can be overriden and set to 0 or 1.
    axis_index = Property

    #------------------------------------------------------------------------
    # Appearance traits
    #------------------------------------------------------------------------

    # The color of the selection border line.
    border_color = ColorTrait("dodgerblue")
    # The width, in pixels, of the selection border line.
    border_width = Float(1.0)
    # The line style of the selection border line.
    border_style = LineStyle("solid")
    # The color to fill the selection region.
    fill_color = ColorTrait("lightskyblue")
    # The transparency of the fill color.
    alpha = Float(0.3)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # The value of the override plot to use, if any.  If None, then uses
    # self.component.
    _plot = Trait(None, Any)

    # The value of the override mapper to use, if any.  If None, then uses the
    # mapper on self.component.
    _mapper = Trait(None, Any)
    
    # Shadow trait for the **axis_index** property
    _axis_index = Trait(None, None, Int)


    #------------------------------------------------------------------------
    # AbstractOverlay interface
    #------------------------------------------------------------------------

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.
        
        Overrides AbstractOverlay.
        """
        axis_ndx = self.axis_index
        lower_left = [0,0]
        upper_right = [0,0]
        
        # Draw the selection
        coords = self._get_selection_screencoords()
        if coords is not None:
            start, end = coords
            lower_left[axis_ndx] = start
            lower_left[1-axis_ndx] = component.position[1-axis_ndx]
            upper_right[axis_ndx] = end - start
            upper_right[1-axis_ndx] = component.bounds[1-axis_ndx]
        else:
            # No selection, so nothing to do!
            return
        
        gc.save_state()
        try:
            gc.set_alpha(self.alpha)
            gc.set_fill_color(self.fill_color_)
            gc.set_stroke_color(self.border_color_)
            gc.set_line_width(self.border_width)
            gc.set_line_dash(self.border_style_)
            gc.rect(lower_left[0], lower_left[1], upper_right[0], upper_right[1])
            gc.draw_path()
        finally:
            gc.restore_state()
        return


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------
    
    def _get_selection_screencoords(self):
        """ Returns a tuple of (x1, x2) screen space coordinates of the start
        and end selection points.  
        
        If there is no current selection, then returns None.
        """
        selection = getattr(self.plot, self.axis).metadata["selections"]
        if selection is not None and len(selection) == 2:
            return self.mapper.map_screen(array(selection))
        else:
            return None

    def _determine_axis(self):
        """ Determines which element of an (x,y) coordinate tuple corresponds
        to the tool's axis of interest.
        
        This method is only called if self._axis_index hasn't been set (or is
        None).
        """
        if self.axis == "index":
            if self.plot.orientation == "h":
                return 0
            else:
                return 1
        else:   # self.axis == "value"
            if self.plot.orientation == "h":
                return 1
            else:
                return 0

    #------------------------------------------------------------------------
    # Trait event handlers
    #------------------------------------------------------------------------

    def _component_changed(self, old, new):
        self._attach_metadata_handler(old, new)
        return
    
    def _axis_changed(self, old, new):
        self._attach_metadata_handler(old, new)
        return
    
    def _attach_metadata_handler(self, old, new):
        # This is used to attach a listener to the datasource so that when
        # its metadata has been updated, we catch the event and update properly
        if not self.plot:
            return
        
        datasource = getattr(self.plot, self.axis)
        if old:
            datasource.on_trait_change(self._metadata_change_handler, "metadata_changed",
                                        remove=True)
        if new:
            datasource.on_trait_change(self._metadata_change_handler, "metadata_changed")
        return
    
    def _metadata_change_handler(self, event):
        self.component.request_redraw()
        return

    #------------------------------------------------------------------------
    # Property getter/setters
    #------------------------------------------------------------------------
    
    def _get_plot(self):
        if self._plot is not None:
            return self._plot
        else:
            return self.component
    
    def _set_plot(self, val):
        self._plot = val
        return
    
    def _get_mapper(self):
        if self._mapper is not None:
            return self._mapper
        else:
            return getattr(self.plot, self.axis + "_mapper")
    
    def _set_mapper(self, new_mapper):
        self._mapper = new_mapper
        return
    
    def _get_axis_index(self):
        if self._axis_index is None:
            return self._determine_axis()
        else:
            return self._axis_index

    def _set_axis_index(self, val):
        self._axis_index = val
        return

# EOF
