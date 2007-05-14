
# Enthought library imports
from enthought.enable2.api import Component
from enthought.traits.api import Any, Enum, false, Instance, List, \
                             Property, Str, true
from enthought.kiva import GraphicsContext, FILL


DEFAULT_DRAWING_ORDER = ["background", "image", "underlay", "plot",
                         "selection", "border", "annotation", "overlay"]


class PlotComponent(Component):
    """
    PlotComponent serves as the base class for all plot-related visual components.
    It defines the various methods related to layout and to tool handling
    which virtually every subclass uses or needs to be aware of.
    
    Several of these top-level layout and draw methods have implementations
    that should not be overridden; instead, subclasses should implement various
    protected stub methods.
    """

    #------------------------------------------------------------------------
    # Basic appearance traits
    #------------------------------------------------------------------------

    # Is the plot visible?
    visible = true

    # Should the padding area be filled with the background color?
    fill_padding = false

    #------------------------------------------------------------------------
    # Layout-related traits
    #------------------------------------------------------------------------

    # Whether to use chaco-level layout (the 'old' system) or enable-level
    # layout, based on the db/resolver containment model.
    layout_switch = Enum("chaco", "enable")

    # Can this component be resized to consume free space?  Resizable
    # components will get called with get_min_size() before their actual
    # bounds get set.
    #    v = resizable vertically
    #    h = resizable horizontally
    #    hv = resizable horizontall and vertically
    #    "" = not resizable
    # Note that this only means that the parent *can* and *should* resize
    # this component; it does NOT mean that the component will automatically
    # resize itself!
    resizable = Enum("hv", "h", "v", "")

    #------------------------------------------------------------------------
    # Overlays and underlays
    #------------------------------------------------------------------------

    # A list of underlays for this plot.  By default, these get a chance to
    # draw onto the plot area underneath plot itself but above any images and
    # backgrounds of the plot.
    underlays = List  #[AbstractOverlay]
    
    # A list of overlays for the plot.  By default, these are drawn above the
    # plot and its annotations.
    overlays = List   #[AbstractOverlay]

    # Should this plot listen for changes to various selection metadata on
    # the underlying datasources, and render them specially?
    use_selection = false

    #------------------------------------------------------------------------
    # Tool and interaction handling traits
    #------------------------------------------------------------------------

    # An enable Interactor that we defer all events to.
    controller = Any

    # The tools that are registered as listeners
    tools = List

    # The tool that is currently active 
    active_tool = Property
    
    # Override an inherited trait from Enable
    auto_handle_event = False
    
    #------------------------------------------------------------------------
    # Rendering control traits
    #------------------------------------------------------------------------
    
    # The order in which various rendering classes on this component will
    # be drawn.
    # Note that if this component is placed in a container, in most cases
    # the container's draw order will be used, since the container will call
    # each of its contained components for each rendering pass.
    # Typically, the definitions of the layers are:
    #   background: background image, shading, and borders
    #   underlay: axes and grids
    #   image: a special layer for plots that render as images.  This gets
    #          a separate layer since these must all render before non-image
    #          plots
    #   plot: the main plot area itself
    #   annotation: lines and text that are concetually part of the "plot" but
    #               should be rendered on top of everything else in the plot
    #   overlay: legends, selection regions, and other tool-drawn visuals
    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))
    
    # Does this container prefer to draw all of its components in one pass, or
    # does it prefer to cooperate in its container's layer-by-layer drawing?
    # If unified_draw is on, then this component will draw as a unified whole,
    # and its parent container will call our _draw() method when drawing the
    # layer indicated in self.draw_layer.
    # If unified_draw is off, then our parent container will call
    # self._dispatch_draw() with the name of each layer as it goes through its
    # list of layers.
    unified_draw = false

    # If unified_draw is True for this component, then this attribute
    # determines what layer it will be drawn on.  This is used by containers
    # and external classes whose drawing loops will call this component.
    # If unified_draw is False, then this attribute is ignored.
    draw_layer = Str("plot")
    
    # A backwards compatibility flag to indicate whether or not to use the
    # old _do_draw() interface or the new draw_order/draw_loop stuff.
    use_draw_order = true
    
    # Should this component do a backbuffered draw, i.e. render itself to an
    # offscreen buffer that is cached for later use?  If False, then
    # the component will *never* render itself backbuffered, even if asked
    # to do so.
    use_backbuffer = false
    
    # Should the backbuffer extend to the pad area?
    backbuffer_padding = true
    
    # Should the border be drawn as part of the overlay or the background (default)?
    overlay_border = true
    
    # Should the border be drawn inset (on the plot) or outside the plot area?
    inset_border = true
    
    # If a draw were to occur, whether the component would actually change.
    # This is useful for determining whether a backbuffer is valid, and is
    # usually set by the component itself or set on the component by calling
    # _invalidate_draw().  It is exposed as a public trait for the rare cases
    # when another components wants to know the validity of this component's
    # backbuffer.
    draw_valid = false
    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # indicate whether or not we need to do a layout call
    _layout_needed = true

    # Shadow trait for the active_tool property.  Should be an instance of
    # BaseTool or one of its subclasses.
    _active_tool = Any
    
    # The backbuffer of this component.  In most cases, this should be an
    # instance of GraphicsContext, but this is not enforced.
    _backbuffer = Any

    
    _cached_handlers = Instance(dict, args=())


    #------------------------------------------------------------------------
    # Abstract methods
    #------------------------------------------------------------------------
    
    def _do_layout(self):
        """
        This method is called by do_layout() to do an actual layout call,
        and bypasses some additional logic to handle null bounds and settings
        _layout_needed.
        """
        pass
    
    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        """
        Subclasses should implement this method to actually render themselves.
        Note: This is only used by the *old* drawing calls.
        """
        pass

    def _draw_selection(self, gc, view_bounds=None, mode="normal"):
        """
        This method is used by subclasses to render selected data subsets
        of their data.  The notion of selection doesn't necessarily apply
        to all subclasses of PlotComponent, but it applies to enough of them
        that we define it as one of the default draw layers.
        """
        pass
    
    #------------------------------------------------------------------------
    # Drawing-related concrete methods
    #------------------------------------------------------------------------

    def draw(self, gc, view_bounds=None, mode="normal"):
        """
        Drawing mode can be one of the following:
            "normal": normal, antialiased, high-quality rendering
            "overlay": the plotcomponent is being rendered over something else,
                so it should render more quickly, and possibly omit rendering
                its background and certain tools
            "interactive": the plotcomponent is being asked to render in
                direct response to realtime user interaction, and needs to make
                its best effort to render as fast as possible, even if there is
                an aesthetic cost
        """
        if self._layout_needed:
            self.do_layout()
        
        if self.use_draw_order:
            self._draw(gc, view_bounds, mode)
        else:
            self._old_draw(gc, view_bounds, mode)
        return

    def draw_select_box(self, gc, position, bounds, width, dash, inset, color, bgcolor, marker_size):
        """
        Utility method that subclasses can use to render a selection box around themselves.
        To avoid burdening subclasses with various selection-box related traits that they
        might never use, this method takes all of its required data as input arguments.
        """
        gc.save_state()
    
        gc.set_line_width(width)
        gc.set_antialias(False)
        x,y = position
        x += inset
        y += inset
        width, height = bounds
        width -= 2*inset
        height -= 2*inset
        rect = (x, y, width, height)
        
        gc.set_stroke_color(bgcolor)
        gc.set_line_dash(None)
        gc.begin_path()
        gc.rect(*rect)
        gc.stroke_path()
        
        gc.set_stroke_color(color)
        gc.set_line_dash(dash)
        gc.rect(*rect)
        gc.stroke_path()
        
        if marker_size > 0:
            gc.set_fill_color(bgcolor)
            half_y = y + height/2.0
            y2 = y + height
            half_x = x + width/2.0
            x2 = x + width
            marker_positions = ((x,y), (x,half_y), (x,y2), (half_x,y), (half_x,y2),
                                (x2,y), (x2, half_y), (x2,y2))
            gc.set_line_dash(None)
            gc.set_line_width(1.0)
            for pos in marker_positions:
                gc.rect(pos[0]-marker_size/2.0, pos[1]-marker_size/2.0, marker_size, marker_size)
            gc.draw_path()
        
        gc.restore_state()
        return

    def invalidate_draw(self):
        """This method should be called whenever a component's internal state
        changes such that it should be redrawn on the next draw call, as opposed
        to using any backbuffer that may exist."""
        self.draw_valid = False
        if hasattr(self.container, "invalidate_draw"):
            self.container.invalidate_draw()
        return


    #------------------------------------------------------------------------
    # Layout-related concrete methods
    #------------------------------------------------------------------------
    
    def do_layout(self, size=None, force=False):
        """
        Tells this component to do layout with a given size.  Size is a
        tuple (width, height), and either or both can be 0.  If size is
        None, then the component should layout using self.bounds.
        """
        if self._layout_needed or force:
            if size is not None:
                self.bounds = size
            self._do_layout()
            self._layout_needed = False
        for underlay in self.underlays:
            underlay.do_layout()
        for overlay in self.overlays:
            overlay.do_layout()
        return
    
    def get_preferred_size(self):
        """
        Returns the size (width,height) that this component would like to be.
        When called on a component that does not contain other components,
        this should just return the component bounds.  If the component is
        resizable and can draw into any size, it should return a size that
        is visually appropriate.  (The component's actually bounds will be
        determined by its container's do_layout method.)
        """
        size = [0,0]
        outer_bounds = self.outer_bounds
        if "h" not in self.resizable:
            size[0] = outer_bounds[0]
        if "v" not in self.resizable:
            size[1] = outer_bounds[1]
        return size

    def dispatch(self, event, suffix):
        if self.use_draw_order:
            self._new_dispatch(event, suffix)
        else:
            self._old_dispatch(event, suffix)
        return

    def _new_dispatch(self, event, suffix):
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
        """
        This method is the main draw handling logic in plot components.  The
        reason we implement _draw() instead of overriding the top-level draw()
        method is that our Enable base classes may do things in draw() that
        shouldn't be interfered with (e.g. the Viewable mix-in).
        
        Most PlotComponent subclasses should implement the various _draw_*
        methods above, and will not need to override this method.
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
        """
        This just does the draw using the mode specified.  Although this is
        a protected method, classes that need this component to render
        itself into a GC should call this method instead of draw(), because
        that is potentially intercepted at the Enable level.
        
        Active tools using this to render themselves on top of a component
        should make sure that their draw_mode is "overlay", otherwise
        a loop may result.  (This method will attempt to render visible,
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
    # New drawing interface
    #------------------------------------------------------------------------
    
    def _draw(self, gc, view_bounds=None, mode="normal"):
        """
        This implements a drawing loop that follows self.draw_order and pays
        attention to overlays, underlays, and the like.
        """
        if not self.visible:
            return
        
        if self._layout_needed:
            self.do_layout()
        
        if self.use_backbuffer:
            if self.backbuffer_padding:
                x, y = self.outer_position
                width, height = self.outer_bounds
            else:
                x, y = self.position
                width, height = self.bounds
            
            if not self.draw_valid:
                # Fixme: should there be a +1 here?
                bb = GraphicsContext((int(width), int(height)))
                bb.translate_ctm(-x+0.5, -y+0.5)
                # There are a couple of strategies we could use here, but we
                # have to do something about view_bounds.  This is because
                # if we only partially render the object into the backbuffer,
                # we will have problems if we then render with different view
                # bounds.
                
                for layer in self.draw_order:
                    if layer != "overlay":
                        self._dispatch_draw(layer, bb, view_bounds, mode)
                
                self._backbuffer = bb
                self.draw_valid = True
            
            # Blit the backbuffer and then draw the overlay on top
            gc.draw_image(self._backbuffer, (x, y, width, height))
            self._dispatch_draw("overlay", gc, view_bounds, mode)
        else:
            for layer in self.draw_order:
                self._dispatch_draw(layer, gc, view_bounds, mode)
        return

    def _dispatch_draw(self, layer, gc, view_bounds, mode):
        """
        Renders the named layer of this component.  This method can be used
        by container classes that group many components together and want them
        to draw cooperatively - the container iterates through its components
        and asks them to only draw certain layers.
        """
        # Don't render the selection layer if use_selection is false.  This
        # is mostly for backwards compatibility.
        if layer == "selection" and not self.use_selection:
            return

        if self._layout_needed:
            self.do_layout()

        if not self._cached_handlers.get(layer,None):
            handlers = []
            names = ["_draw_" + layer + x for x in ("_pre", "", "_post")]
            for name in names:
                if getattr(self, name, None):
                    handlers.append(getattr(self,name))
            self._cached_handlers[layer] = handlers
            
        for method in self._cached_handlers[layer]:
            method(gc, view_bounds, mode)

        return

    def _draw_underlay(self, gc, view_bounds=None, mode="normal"):
        for underlay in self.underlays:
            # This method call looks funny but it's correct - underlays are
            # just overlays drawn at a different time in the rendering loop.
            underlay.overlay(self, gc, view_bounds, mode)
        return
    
    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        for overlay in self.overlays:
            overlay.overlay(self, gc, view_bounds, mode)
        return

    #------------------------------------------------------------------------
    # Abstract/protected methods for subclasses to implement
    #------------------------------------------------------------------------
    
    def _draw_background(self, gc, view_bounds=None, mode="normal"):
        if self.bgcolor not in ("clear", "transparent", "none"):
            if self.fill_padding:
                r = tuple(self.outer_position) + (self.outer_width-1, self.outer_height-1)
            else:
                r = tuple(self.position) + (self.width-1, self.height-1)
            
            gc.save_state()
            gc.set_antialias(False)
            try:
                gc.set_fill_color(self.bgcolor_)
                gc.draw_rect(r, FILL)
                
            finally:
                gc.restore_state()
        
        # Call the enable _draw_border routine
        if not self.overlay_border and self.border_visible:
            # Tell _draw_border to ignore the self.overlay_border
            self._draw_border(gc, view_bounds, mode, force_draw=True)
        
        return
    
    def _draw_border(self, gc, view_bounds=None, mode="default", force_draw=False):
        if self.overlay_border or force_draw:
            if self.inset_border:
                self._draw_inset_border(gc, view_bounds, mode)
            else:
                super(PlotComponent, self)._draw_border(gc, view_bounds, mode)
        return
    
    def _draw_inset_border(self, gc, view_bounds=None, mode="default"):
        """
        Utility method to draw the borders around this plot.  Unlike the default 
        Enable border, this one is drawn on the inside of the plot instead of
        around it.
        """
        if not self.border_visible:
            return
        
        border_width = self.border_width
        gc.save_state()
        gc.set_line_width(border_width)
        gc.set_line_dash(self.border_dash_)
        gc.set_stroke_color(self.border_color_)
        gc.begin_path()
        gc.set_antialias(0)
        gc.rect(int(self.x + border_width/2.0), int(self.y + border_width/2.0),
                self.width - 2*border_width + 1, self.height - 2*border_width + 1)

        gc.stroke_path()
        gc.restore_state()
        return
    
    def _get_visible_border(self):
        """
        Returns the amount of border that should be taken into account in the
        padding.  Overrides the implementation in enable.Component.
        """
        if self.border_visible:
            if self.inset_border:
                return 0
            else:
                return self.border_width
        else:
            return 0
        
    
    #------------------------------------------------------------------------
    # Tool-related methods and event handlers
    #------------------------------------------------------------------------
    
    def _get_active_tool(self):
        return self._active_tool
    
    def _set_active_tool(self, tool):
        # Deactivate the existing active tool
        old = self._active_tool
        if old == tool:
            return
        
        self._active_tool = tool
        
        if old is not None:
            old.deactivate(self)
            
        if tool is not None and hasattr(tool, "_activate"):
            tool._activate()
        
        self.request_redraw()
        return

    def _tools_items_changed(self):
        self.request_redraw()
        return
    
    def _dispatch_to_enable(self, event, suffix):
        """
        This method is called by dispatch() to allow subclasses to customize
        how they call down to Enable-level handlers for dispatching of events
        on self.
        
        This method only gets called after all the tools have been called;
        if execution reaches this point, the PlotComponent needs to handle the
        event, as it is actually being dispatched on itself.
        """
        Component.dispatch(self, event, suffix)
        return


    #------------------------------------------------------------------------
    # Persistence
    #------------------------------------------------------------------------
    
    def __getstate__(self):
        state = super(PlotComponent,self).__getstate__()
        for key in ['_layout_needed', '_active_tool']:
            if state.has_key(key):
                del state[key]

        return state



# EOF
