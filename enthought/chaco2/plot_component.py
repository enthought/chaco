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
    # Layout-related concrete methods
    #------------------------------------------------------------------------
    
    def dispatch(self, event, suffix):
        """ Dispatches a mouse event based on the current event state.
        
        Parameters
        ----------
        event : an Enable MouseEvent
            A mouse event.
        suffix : string
            The name of the mouse event as a suffix to the event state name,
            e.g. "_left_down" or "_window_enter".
        """
        if self.use_draw_order:
            self._new_dispatch(event, suffix)
        else:
            self._old_dispatch(event, suffix)
        return

    def _new_dispatch(self, event, suffix):
        """ Dispatches a mouse event
        
        If the component has a **controller**, the method dispatches the event 
        to it, and returns. Otherwise, the following objects get a chance to 
        handle the event:
        
        1. The component's active tool, if any.
        2. Any overlays, in reverse order that they were added and are drawn.
        3. The component itself.
        4. Any underlays, in reverse order that they were added and are drawn.
        5. Any listener tools.
        
        If any object in this sequence handles the event, the method returns
        without proceeding any further through the sequence. If nothing
        handles the event, the method simply returns.
        """
        
        # Maintain compatibility with .controller for now
        if self.controller is not None:
            self.controller.dispatch(event, suffix)
            return
        
        if self._active_tool is not None:
            self._active_tool.dispatch(event, suffix)

        if event.handled:
            return
        
        # Dispatch to overlays in reverse of draw/added order
        for overlay in self.overlays[::-1]:
            overlay.dispatch(event, suffix)
            if event.handled:
                break
            
        if not event.handled:
            self._dispatch_to_enable(event, suffix)
        
        if not event.handled:
            # Dispatch to underlays in reverse of draw/added order
            for underlay in self.underlays[::-1]:
                underlay.dispatch(event, suffix)
                if event.handled:
                    break
        
        # Now that everyone who might veto/handle the event has had a chance
        # to receive it, dispatch it to our list of listener tools.
        if not event.handled:
            for tool in self.tools:
                tool.dispatch(event, suffix)
        
        return

    def _old_dispatch(self, event, suffix):
        """ Dispatches a mouse event.
        
        If the component has a **controller**, the method dispatches the event 
        to it and returns. Otherwise, the following objects get a chance to 
        handle the event:
        
        1. The component's active tool, if any.
        2. Any listener tools.
        3. The component itself.
        
        If any object in this sequence handles the event, the method returns
        without proceeding any further through the sequence. If nothing
        handles the event, the method simply returns.
        
        """
        if self.controller is not None:
            self.controller.dispatch(event, suffix)
            return
        
        if self._active_tool is not None:
            self._active_tool.dispatch(event, suffix)

        if event.handled:
            return
        
        for tool in self.tools:
            tool.dispatch(event, suffix)
            if event.handled:
                return
        
        if not event.handled:
            self._dispatch_to_enable(event, suffix)
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

    #------------------------------------------------------------------------
    # Tool-related methods and event handlers
    #------------------------------------------------------------------------
    

    def _dispatch_to_enable(self, event, suffix):
        """ Called by dispatch() to allow subclasses to customize
        how they call Enable-level handlers for dispatching of events
        on the object.

        This method only gets called after all the tools have been called;
        if execution reaches this point, the PlotComponent needs to handle the
        event, as it is actually being dispatched on itself.
        """
        Component.dispatch(self, event, suffix)
        return

# EOF
