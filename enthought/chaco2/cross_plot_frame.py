""" Defines the (deprecated) CrossPlotFrame class.
"""
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
from plot_containers import HPlotContainer, OverlayPlotContainer, VPlotContainer


class CrossPlotFrame(BasePlotFrame):
    """ A simple, box-layout based plotframe.
    
    This class supports a central plot area with optional axes on the top, bottom,
    and sides.  The legend can be placed to the bottom, left, right, or
    inside the plot area.  The title can be placed along any of the four
    edges.
    
    NOTE: PlotFrames are deprecated.  There is no need to use them any more.
    This class will be removed sometime in the future.
    """
    
    # Slots or positions on the frame where plot components can place themselves.
    # Overrides PlotFrame.
    slot_names = ("center", "left", "right", "top", "bottom")

    # Default width and height. Class attribute.
    default_bounds = (500,500)
    
    # The sizes of the various areas
    
    # Width of the left slot.
    left_width = Float(50.0)
    # Width of the right slot.
    right_width = Float(50.0)
    # Height of the top slot.
    top_height = Float(50.0)
    # Height of the bottom slot.
    bottom_height = Float(50.0)
    
    # Does the component need to do a layout call?
    _layout_needed = true


    def __init__(self, **kwtraits):
        if kwtraits.has_key("bounds"):
            bounds = kwtraits.pop("bounds")
        else:
            bounds = list(self.default_bounds)
        BasePlotFrame.__init__(self, **kwtraits)
        
        # Create our plot containers
        self.set_slot("center", OverlayPlotContainer(resizable="hv"))
        self.set_slot("left", HPlotContainer(resizable="v"))
        self.set_slot("right", HPlotContainer(resizable="v"))
        self.set_slot("top", VPlotContainer(resizable="h"))
        self.set_slot("bottom", VPlotContainer(resizable="h"))
        
        self.bounds = bounds
        return

    def set_visible_slots(self, *names):
        """
        Convenience method to set the named slots to visible, while setting
        all others to not visible.
        """
        for slot in self.slot_names:
            if slot in names:
                self.get_slot(slot).visible = True
            else:
                self.get_slot(slot).visible = False
        return

    
    #------------------------------------------------------------------------
    # Protected methods
    #------------------------------------------------------------------------

    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        """ Draws the component.

        This method is preserved for backwards compatibility with _old_draw().
        Overrides PlotComponent.
        """
        try:
            gc.save_state()
            gc.translate_ctm(*self.position)
            for slotname in self.slot_names:
                if getattr(self, slotname).visible:
                    gc.save_state()
                    self.get_slot(slotname).draw(gc, view_bounds, mode)
                    gc.restore_state()
        finally:
            gc.restore_state()
        return
    
    def _do_layout(self):
        """
        Performs a layout and sets the size and positions on this frame's
        containers, given its width and height.
        """
        left = self.left
        right = self.right
        top = self.top
        bottom = self.bottom
        center = self.center

        # Calculate the bounds of the resizable center container, then set
        # the bounds on all the containers.  center_x,_y represent the (x,y)
        # coordinate of the lower-left corner of the center region;
        # center_x2 and center_y2 represent the upper-right corner of the
        # center region.
        
        if self.left.visible:
            center_x = self.left_width
        else:
            center_x = self.x
        if self.bottom.visible:
            center_y = self.bottom_height
        else:
            center_y = self.y
        if self.right.visible:
            center_x2 = self.width - self.right_width - 1
        else:
            center_x2 = self.width
        if self.top.visible:
            center_y2 = self.height - self.top_height - 1
        else:
            center_y2 = self.height
        
        left.outer_position = [0.0, center_y]
        left.outer_bounds = [self.left_width, center_y2 - center_y + 1]
        
        right.outer_position = [center_x2 + 1, center_y]
        right.outer_bounds = [self.right_width, left.height]
        
        bottom.outer_position = [center_x, 0.0]
        bottom.outer_bounds = [center_x2 - center_x + 1, self.bottom_height]
        
        top.outer_position = [center_x, center_y2 + 1]
        top.outer_bounds = [bottom.width, self.top_height]
        
        center.outer_position = [center_x, center_y]
        center.outer_bounds = [bottom.width, left.height]
        
        for slot in self._frame_slots.values():
            if slot.visible:
                preferred_size = slot.get_preferred_size()
                if "h" not in slot.resizable:
                    slot.outer_width = preferred_size[0]
                if "v" not in slot.resizable:
                    slot.outer_height = preferred_size[1]
                slot.do_layout()

        return


    ### Persistence ###########################################################

    #_pickles = ("left_width", "right_width", "top_height", "bottom_height")
    
    def __getstate__(self):
        state = super(CrossPlotFrame,self).__getstate__()
        for key in ['_layout_needed']:
            if state.has_key(key):
                del state[key]

        return state

    
# EOF
