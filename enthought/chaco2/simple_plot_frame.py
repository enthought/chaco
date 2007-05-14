

#################################################################################
#
# NOTE: PlotFrames are deprecated.  There is no need to use them any more.
# This class will be removed sometime in the near future.
#
#################################################################################


# Enthought library imports
from enthought.traits.api import Enum, false, Float, true

# Local, relative imports
from base_plot_frame import BasePlotFrame
from chaco_traits import box_edge_enum, box_position_enum
from plot_containers import OverlayPlotContainer

class SimplePlotFrame(BasePlotFrame):
    """
    A plot frame with just a single, center container that takes up the entire
    frame.
    """

    slot_names = ("center")
    
    default_bounds = (500, 500)
    
    fit_components = ""
    
    fit_window = True

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    _layout_needed = true


    def __init__(self, **kwtraits):
        # Delay setting the bounds until after base class initialization
        if kwtraits.has_key("bounds"):
            bounds = kwtraits.pop("bounds")
        else:
            bounds = list(self.default_bounds)
        BasePlotFrame.__init__(self, **kwtraits)
        self.set_slot("center", OverlayPlotContainer(resizable="hv"))
        self.bounds = bounds
        return
    
    #------------------------------------------------------------------------
    # Protected methods
    #------------------------------------------------------------------------

    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        try:
            gc.save_state()
            # Translate to our .position, because even though we are supposed
            # to be a top-level Chaco component, we might still be contained
            # within other Enable components.
            gc.translate_ctm(*self.position)
            gc.save_state()
            self.center.draw(gc, view_bounds, mode)
            gc.restore_state()
        finally:
            gc.restore_state()
        return

    def get_preferred_size(self):
        size = [0,0]
        component_pref_size = None
        if "h" not in self.resizable:
            if "h" in self.fit_components:
                component_pref_size = self.center.get_preferred_size()
                size[0] = component_pref_size[0]
            else:
                size[0] = self.default_bounds[0]
        if "v" not in self.resizable:
            if "v" in self.fit_components:
                if not component_pref_size:
                    component_pref_size = self.center.get_preferred_size()
                size[1] = component_pref_size[1]
            else:
                size[1] = self.default_bounds[1]
        return size

    def _do_layout(self):
        """
        Performs a layout and sets the size and positions on our
        containers given our width and height.
        """
        component = self.center
        
        preferred_size = None
        if "h" in component.resizable:
            component.outer_width = self.width
        elif "h" in self.fit_components:
            preferred_size = component.get_preferred_size()
            component.outer_width = preferred_size[0]
            self.width = preferred_size[0]
        else:
            # We are not autosizing to our component, and it's not going to
            # auto-size to our bounds, so do nothing.
            pass
        
        if "v" in component.resizable:
            component.outer_height = self.height
        elif "v" in self.fit_components:
            if preferred_size is None:
                preferred_size = component.get_preferred_size()
            component.outer_height = preferred_size[1]
            self.height = preferred_size[1]
        else:
            # We are not autosizing to our component, and it's not going to
            # auto-size to our bounds, so do nothing.
            pass
        
        component.outer_position = [0,0]
        component.do_layout()
        return

    ### Persistence ###########################################################
    #_pickles = ()

    def __getstate__(self):
        state = super(SimplePlotFrame,self).__getstate__()
        for key in ['_layout_needed']:
            if state.has_key(key):
                del state[key]

        return state


# EOF
