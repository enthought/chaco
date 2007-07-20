""" Defines the BasePlotContainer class.
"""
from sets import Set
from numpy import array


# Enthought library imports
from enthought.enable2.api import Container, Interactor, black_color_trait, \
                            white_color_trait, color_table, empty_rectangle, \
                            intersect_bounds
from enthought.traits.api import Bool, Enum, List, Tuple

# Local, relative imports
from plot_component import PlotComponent
from plot_template import Templatizable


class BasePlotContainer(PlotComponent, Container, Templatizable):
    """
    A container for PlotComponents that conforms to being laid out by
    PlotFrames.  Serves as the base class for other PlotContainers.
    
    PlotContainers define a layout, i.e., a spatial relationship between
    their contained components.  (BasePlotContainer doesn't define one,
    but its various subclasses do.)
    
    BasePlotContainer is a subclass of Enable Container, so it is possible to
    insert Enable-level components into it.  However, because Enable
    components don't have the correct interfaces to participate in layout,
    the visual results will probably be incorrect.
    """

    # A list of the plot container's components.  In general, the order of
    # items defines the Z-order or draw order, depending on the subclass.  
    # Subclasses can redefine this as appropriate.
    plot_components = List

    # Dimensions in which this container can resize to fit its components.
    # This is similar to the **resizable** trait on PlotComponent. Chaco
    # plot containers use this attribute in preference to the Enable 
    # **auto_size** attribute (which is overridden to be False by default).
    fit_components = Enum("", "h", "v", "hv") # TODO: remove the auto_size trait from enable's Container

    #use_draw_order = True

    # The default size of this container if it is empty.
    default_size = Tuple(0, 0)

    # Overrides the Enable **auto_size** trait (which will be deprecated in the
    # future).
    auto_size = False
    
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # This container can render itself in a different mode than what it asks of 
    # its contained components.  This attribute stores the rendering mode that 
    # this container requests of its children when it does a _draw(). If the
    # attribute is set to "default", then whatever mode is handed in to _draw()
    # is used.
    _children_draw_mode = Enum("default", "normal", "overlay", "interactive")
    

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------
    
    def __init__(self, **kwtraits):
        """ In creating an instance, this method sets the instance's
        **auto_size** trait to False, unless it is explicitly set.
        """
        # Unless the user explicitly sets it, PlotContainers shouldn't
        # automatically resize themselves to fit their contained components.
        if not kwtraits.has_key("auto_size"):
            self.auto_size = False
        PlotComponent.__init__(self, **kwtraits)
        Container.__init__(self, **kwtraits)
        return

    #------------------------------------------------------------------------
    # Container interface
    #------------------------------------------------------------------------
    
    def add(self, *components):
        """ Convenience method to add new components to the container.
        """
        if self in components:
            raise ValueError, 'BasePlotContiner.add attempt to add self as component.'
        self.plot_components.extend(components)
        Container.add(self, *components)
        self.invalidate_draw()
        return
    
    def remove(self, *components):
        """ Convenience method to remove an existing component.
        """
        for component in components:
            self.plot_components.remove(component)
        Container.remove(self, *components)
        self.invalidate_draw()
        return

    def insert(self, index, *components):
        """
        Inserts the components starting at a particular index.
        """
        for component in components:
            self.plot_components.insert(index, component)
            Container.add(self, component)
            index += 1

        self.invalidate_draw()
        return

    #------------------------------------------------------------------------
    # PlotComponent interface
    #------------------------------------------------------------------------

    def get_preferred_size(self, components=None):
        """ Returns the container's preferred size.
        
        Overrides PlotComponent. Different container subclasses have different
        layout mechanisms, which determine how the preferred size is computed
        from component sizes. 
        
        If *component* is None, the method can use self.plot_components.
        """
        raise NotImplementedError

    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        """ Draws the component.

        This method is preserved for backwards compatibility. Overrides 
        PlotComponent.
        """
        gc.save_state()
        gc.set_antialias(False)

        self._draw_container(gc, mode)
        self._draw_children(gc, view_bounds, mode) #This was children_draw_mode
        self._draw_overlays(gc, view_bounds, mode)
        gc.restore_state()
        return
    
    def _dispatch_draw(self, layer, gc, view_bounds, mode):
        """ Renders the named *layer* of this component. 
        """
        new_bounds = self._transform_view_bounds(view_bounds)
        if new_bounds == empty_rectangle:
            return
        
        if self._layout_needed:
            self.do_layout()

        # Give the container a chance to draw first for the layers that are
        # considered "under" or "at" the plot level.
        if layer in ("background", "image", "underlay", "plot"):
            my_handler = getattr(self, "_draw_container_" + layer, None)
            if my_handler:
                my_handler(gc, view_bounds, mode)
        
        # Now transform coordinates and draw the children
        visible_components = self._get_visible_components(new_bounds)
        if visible_components:
            gc.save_state()
            try:
                gc.translate_ctm(*self.position)
                for component in visible_components:
                    #if isinstance(component, BasePlotContainer) and component.unified_draw:
                    if component.unified_draw:
                        # Plot containers that want unified_draw only get called if
                        # their draw_layer matches the current layer we're rendering
                        if component.draw_layer == layer:
                            component._draw(gc, new_bounds, mode)
                    else:
                        component._dispatch_draw(layer, gc, new_bounds, mode)
            finally:
                gc.restore_state()
        
        # The container's annotation and overlay layers draw over those of its components.
        if layer in ("annotation", "overlay"):
            my_handler = getattr(self, "_draw_container_" + layer, None)
            if my_handler:
                my_handler(gc, view_bounds, mode)
        
        return

    def _draw_container_background(self, gc, view_bounds=None, mode="normal"):
        PlotComponent._draw_background(self, gc, view_bounds, mode)
        return

    def _draw_container_overlay(self, gc, view_bounds=None, mode="normal"):
        PlotComponent._draw_overlay(self, gc, view_bounds, mode)
        return

    def _draw_container_underlay(self, gc, view_bounds=None, mode="normal"):
        PlotComponent._draw_underlay(self, gc, view_bounds, mode)
        return

    def _get_visible_components(self, bounds):
        """ Returns a list of this plot's children that are in the bounds. """
        if bounds is None:
            return self.plot_components
        
        visible_components = []
        for component in self.plot_components:
            if not component.visible:
                continue
            tmp = intersect_bounds(component.outer_position + component.outer_bounds, bounds)
            if tmp != empty_rectangle:
                visible_components.append(component)
        return visible_components

    #------------------------------------------------------------------------
    # Templatizable interface
    #------------------------------------------------------------------------

    def get_templatizable_children(self):
        # JMS 2007/07/06: This method is not in the Templatizable interface
        # and this implementation doesn't appear to do anything.
        template_children = []
        for component in self.plot_components:
            if isinstance(component, Templatizable):
                template_children.append(component)
        return

    #------------------------------------------------------------------------
    # Protected methods
    #------------------------------------------------------------------------

    def _draw_children(self, gc, view_bounds=None, mode="normal"):
        
        new_bounds = self._transform_view_bounds(view_bounds)
        if new_bounds == empty_rectangle:
            return
        
        gc.save_state()
        try:
            gc.set_antialias(False)
            gc.translate_ctm(*self.position)
            for component in self.plot_components:
                if new_bounds:
                    tmp = intersect_bounds(component.outer_position + component.outer_bounds, new_bounds)
                    if tmp == empty_rectangle:
                        continue
                
                gc.save_state()
                try:
                    component.draw(gc, new_bounds, mode)
                finally:
                    gc.restore_state()
        finally:
            gc.restore_state()
        return

    def _draw_overlays(self, gc, view_bounds=None, mode="normal"):
        """ Method for backward compatability with old drawing scheme.
        """
        for component in self.overlays:
            component.overlay(component, gc, view_bounds, mode)
        return

    def _should_layout(self, component):
        """ Returns True if it is appropriate for the container to lay out
        the component; False if not.
        """
        if not component or (not component.visible and not component.invisible_layout):
            return False
        else:
            return True
    
    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _dispatch_to_enable(self, event, suffix):
        """ Calls Enable-level handlers for dispatching events on the object.
        
        Overrides PlotComponent.
        """
        Container.dispatch(self, event, suffix)
        return
    
    def _plot_components_items_changed(self, event):
        self._layout_needed = True
        return
    
    def _plot_components_changed(self, event):
        self._layout_needed = True
        self.invalidate_draw()
        return

    def _bounds_changed(self, old, new):
        # crappy... calling our parent's handler seems like a common traits
        # event handling problem
        super(BasePlotContainer, self)._bounds_changed(old, new)
        self._layout_needed = True
        self.invalidate_draw()
        return

    def _bounds_items_changed(self, event):
        super(BasePlotContainer, self)._bounds_items_changed(event)
        self._layout_needed = True
        self.invalidate_draw()
        return

    def _bgcolor_changed(self):
        self.invalidate_draw()
        self.request_redraw()
        return
    
    ### Persistence ###########################################################
    # Although PlotComponent gets our enable.Component attributes, we need to
    # pick up all the enable.Container attributes.
    #_pickles = ("plot_components", "use_backbuffer",
    #            "border_dash", "_components", "auto_size", "fit_window")


    def __getstate__(self):
        state = super(BasePlotContainer,self).__getstate__()
        for key in ['_backbuffer', '_children_draw_mode']:
            if state.has_key(key):
                del state[key]
        return state
    
    
    def post_load(self, path=None):
        # Need to re-initialize this Container attribute here, since Enable
        # components/attributes don't participate in serialization.
        self._prev_event_handlers = Set()
        self.invalidate_draw()
        self._layout_needed = True
        for component in self.plot_components:
            component.post_load(path)
        return


# EOF
