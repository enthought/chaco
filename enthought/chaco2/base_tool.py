"""
Base class for all Chaco tools.  See doc/event_handling.txt for an overview
of how event handling works in Chaco.
"""


# Enthought library imports
from enthought.enable2.api import Interactor
from enthought.traits.api import Enum, false, Instance, true

# Local relative imports
from plot_component import PlotComponent


class KeySpec:
    """
    Creates a key specification to facilitate tools interacting with they
    keyboard.  A tool can either declare a class attribute:
    
        magic_key = KeySpec("Right", "control")
    
    or a trait:
    
        magic_key = Instance(KeySpec, args=("Right", "control"))
    
    and then check to see if the key was pressed by calling:
    
        if self.magic_key.match(event):
            # do stuff...
    
    The names of the keys come from Enable.
    """
    def __init__(self, key, *modifiers):
        """ Creates this key spec with the given modifiers """
        self.key = key
        mods = [m.lower() for m in modifiers]
        self.alt = "alt" in mods
        self.shift = "shift" in mods
        self.control = "control" in mods
        return
    
    def match(self, event):
        """
        Returns True if the given Enable key_pressed event matches this key
        specification.
        """
        if (self.key == event.character) and (self.alt == event.alt_down) and \
           (self.control == event.control_down) and (self.shift == event.shift_down):
            return True
        else:
            return False


class BaseTool(Interactor):
    """
    The base class for Chaco tools.
    
    Chaco tools are not Enable components, but they can draw.  They do not
    participate in layout, but are instead attached to a PlotComponent which
    dispatches methods to the tool and calls the tools' .draw() method.
    
    See doc/event_handling.txt for more information on how tools are structured.
    """
    
    # The component this tool is attached to.
    component = Instance(PlotComponent)

    # Is this tool's visual representation visible?  For passive inspector-type
    # tools, this is most likely a constant value set in the class definition;
    # for stateful/modal tools, this should be set by the tool's listening
    visible = false

    # How the tool draws on top of its component.  This, in conjuction with a
    # a tool's status on the component, is used by the component to determine
    # how to render itself.  In general, the meanings of the draw modes are:
    #   normal: we modify the appearance of part of the component such that
    #           the component should be redrawn even if it has not otherwise
    #           received any indication that its previous rendering is invalid.
    #           The tool controls its own drawing loop, and calls out to this
    #           tool after it's done drawing itself.
    #
    #   overlay: the component needs to be drawn, but can be drawn after all
    #            of the background and foreground elements in the component,
    #            and, furthermore, the tool will render correctly regardless
    #            of how the component renders itself (e.g. via a cached image).
    #            The overlay gets rull control of the rendering loop, and must
    #            explicitly call the component's _draw() method, or else the
    #            component will not render.
    #
    #   none: the tool does not have a visual representation that the component
    #         needs to worry about rendering.
    draw_mode = Enum("none", "overlay", "normal")


    #------------------------------------------------------------------------
    # Concrete methods
    #------------------------------------------------------------------------
    
    def __init__(self, component=None, **kwtraits):
        if "component" in kwtraits:
            component = kwtraits["component"]
        super(BaseTool, self).__init__(**kwtraits)
        self.component = component
        return
    
    def dispatch(self, event, suffix):
        self._dispatch_stateful_event(event, suffix)
        return

    def _dispatch_stateful_event(self, event, suffix):
        # Override the default enable.Interactor behavior of automatically
        # setting the event.handled if a handler is found.  (Without this
        # level of manual control, we could never support multiple listeners.)
        handler = getattr(self, self.event_state + "_" + suffix, None)
        if handler is not None:
            handler(event)
        return

    #------------------------------------------------------------------------
    # Abstract methods that subclasses should implement
    #------------------------------------------------------------------------
    
    def draw(self, gc, view_bounds=None):
        """
        Draws this tool on a graphics context.  It is assumed that the GC has
        a coordinate transform that matches the origin of its component.
        (For containers, this is just the origin; for components, it is the
        origin of their containers.)
        """
        pass

    def _activate(self):
        """
        Called by a PlotComponent when we become the active tool.
        """
        pass

    def _deactivate(self):
        """
        Called by a PlotComponent when we are no longer the active tool.
        """
        pass

    def deactivate(self, component=None):
        # Compatibility with new AbstractController interface
        self._deactivate()
        return


    ### Persistence ###########################################################
#    _pickles = ("component", "visible", "draw_mode")



# EOF
