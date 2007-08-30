""" Defines the PlotComponent class.
"""
# Enthought library imports
from enthought.enable2.api import Component
from enthought.traits.api import Any, Bool, Enum, Instance, List, \
                             Property, Str
from enthought.kiva import GraphicsContext, FILL


DEFAULT_DRAWING_ORDER = ["background", "image", "underlay",      "plot",
                         "selection", "border", "annotation", "overlay"]


class PlotComponent(Component):
    """
    PlotComponent is the base class for all plot-related visual components.
    It defines the various methods related to layout and tool handling,
    which virtually every subclass uses or needs to be aware of.
    
    Several of these top-level layout and draw methods have implementations
    that must not be overridden; instead, subclasses implement various
    protected stub methods.
    """

    #------------------------------------------------------------------------
    # Rendering control traits
    #------------------------------------------------------------------------
    
    # The order in which various rendering classes on this component are drawn.
    # Note that if this component is placed in a container, in most cases
    # the container's draw order is used, since the container calls
    # each of its contained components for each rendering pass.
    # Typically, the definitions of the layers are:
    #
    # 1. 'background': Background image, shading, and borders
    # 2. 'underlay': Axes and grids
    # 3. 'image': A special layer for plots that render as images.  This is in
    #    a separate layer since these plots must all render before non-image
    #    plots.
    # 4. 'plot': The main plot area itself
    # 5. 'annotation': Lines and text that are conceptually part of the "plot" but
    #    need to be rendered on top of everything else in the plot.
    # 6. 'overlay': Legends, selection regions, and other tool-drawn visual
    #    elements
    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))
    
    # If **unified_draw** is True for this component, then this attribute
    # determines what layer it will be drawn on.  This is used by containers
    # and external classes, whose drawing loops call this component.
    # If **unified_draw** is False, then this attribute is ignored.
    draw_layer = Str("plot")
        
    # Draw layers in **draw_order**? If False, use _do_draw() (for backwards
    # compatibility).
    use_draw_order = Bool(True)
       
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _cached_handlers = Instance(dict, args=())


    #------------------------------------------------------------------------
    # Abstract methods
    #------------------------------------------------------------------------
    
    def _do_layout(self):
        """ Called by do_layout() to do an actual layout call; it bypasses some
        additional logic to handle null bounds and setting **_layout_needed**.
        """
        pass
    
    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        """ Renders the component. 
        
        Subclasses must implement this method to actually render themselves.
        Note: This method is used only by the "old" drawing calls.
        """
        pass

    def _draw_selection(self, gc, view_bounds=None, mode="normal"):
        """ Renders a selected subset of a component's data. 
        
        This method is used by some subclasses. The notion of selection doesn't 
        necessarily apply to all subclasses of PlotComponent, but it applies to
        enough of them that it is defined as one of the default draw methods.
        """
        pass
    
    #------------------------------------------------------------------------
    # Drawing-related concrete methods
    #------------------------------------------------------------------------

    def draw(self, gc, view_bounds=None, mode="default"):
        """ Draws the plot component.
        
        Parameters
        ----------
        gc : Kiva GraphicsContext
            The graphics context to draw the component on
        view_bounds : 4-tuple of integers
            (x, y, width, height) of the area to draw
        mode : string
            The drawing mode to use; can be one of:
                
            'normal' 
                Normal, antialiased, high-quality rendering
            'overlay'
                The plot component is being rendered over something else,
                so it renders more quickly, and possibly omits rendering
                its background and certain tools
            'interactive'
                The plot component is being asked to render in
                direct response to realtime user interaction, and needs to make
                its best effort to render as fast as possible, even if there is
                an aesthetic cost.
        """
        if self._layout_needed:
            self.do_layout()

        if self.use_draw_order:
            self._draw(gc, view_bounds, mode)
        else:
            self._old_draw(gc, view_bounds, mode)
        return
    

    #------------------------------------------------------------------------
    # Old drawing methods
    #------------------------------------------------------------------------

    def _old_draw(self, gc, view_bounds=None, mode="normal"):
        """ Draws the component, ignoring **draw_order**.
        
        The reason for implementing _old_draw() instead of overriding the 
        top-level draw() method is that the Enable base classes may do things 
        in draw() that mustn't be interfered with (e.g., the Viewable mix-in).
        
        Most PlotComponent subclasses implement the various _draw_*()
        methods above, and do not need to override this method.
        """
        if self.visible:
            # Determine if we have an active tool and if we need to transfer
            # execution to it.
            active_tool = self._active_tool
            if active_tool is not None and active_tool.draw_mode == "overlay":
                # If an active tool is in overlay mode, we transfer
                # execution to it.
                active_tool.draw(gc, view_bounds)
            else:
                if self.use_backbuffer:
                    if mode == 'overlay':
                        # Since kiva doesn't currently support blend modes, if
                        # we have to draw in overlay mode, we have to draw normally.
                        self._do_draw(gc, view_bounds, mode)
                        self._backbuffer = None
                        self.invalidate_draw()
                    if not self.draw_valid:
                        bb = GraphicsContext(tuple(map(int,self.bounds)))
                        bb.translate_ctm(-self.x, -self.y)
                        # There are a couple of strategies we could use here, but we
                        # have to do something about view_bounds.  This is because
                        # if we only partially render the object into the backbuffer,
                        # we will have problems if we then render with different view
                        # bounds.
                        self._do_draw(bb, view_bounds=None, mode=mode)
                        self._backbuffer = bb
                        self.draw_valid = True

                    gc.draw_image(self._backbuffer, self.position + self.bounds)
                else:
                    self._do_draw(gc, view_bounds, mode)
        return

    def _do_draw(self, gc, view_bounds=None, mode="normal"):
        """ Draws the plot component using the mode specified.  
        
        Although this is a protected method, classes that need this component
        to render itself into a graphics context must call this method instead
        of draw(), because draw() is potentially intercepted at the Enable 
        level.
        
        Active tools using this method to render themselves on top of a 
        component must set their **draw_mode** to 'overlay'; otherwise,
        a loop may result.  (This method attempts to render visible,
        non-overlay tools.)
        """
        active_tool = self._active_tool
        gc.save_state()
        try:
            gc.set_antialias(False)
            
            # Render the primary layers of the component
            self._draw_background(gc, mode=mode)
            self._draw_component(gc, view_bounds=view_bounds, mode=mode)
            self._draw_border(gc, mode=mode)
            
            # Render the tools
            for tool in self.tools:
                if tool.visible and tool.draw_mode != "none":
                    if tool != active_tool:
                        tool.draw(gc, view_bounds)
            if (active_tool is not None) and (active_tool.visible) and \
                                        (active_tool.get("draw_mode", "") == "normal"):
                active_tool.draw(gc, view_bounds)
            
        finally:
            gc.restore_state()
        return

