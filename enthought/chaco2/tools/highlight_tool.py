""" Defines the HighlightTool class.
"""
# Major library imports
from numpy import ones

# Enthought library imports
from enthought.traits.api import Enum, Float
from enthought.enable2.api import BaseTool

# Chaco imports
from enthought.chaco2.api import BasePlotContainer


class HighlightTool(BaseTool):
    """ A tool that enables the user to select a plot to be highlighted on the
    graph by clicking on it.
    """

    # The mouse button that initiates the selection.
    drag_button = Enum("left", "right")

    # Threshold distance for hit-testing.
    threshold = Float(20.0)

    #---------------------------------------------------------------------
    # Inherited BaseTool traits
    #---------------------------------------------------------------------

    # This tool is not drawn. Overrides BaseTool.
    draw_mode = "none"
    
    # This tool is not visible. Overrides BaseTool.
    visible = False

    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed.
        
        If the left mouse button initiates the selection, this method does so.
        """
        if self.drag_button == "left":
            self._highlight(event)
        return

    def normal_right_down(self, event):
        """ Handles the right mouse button being pressed.
        
        If the right mouse button initiates the selection, this method does so.
        """
        if self.drag_button == "right":
            self._highlight(event)
        return

    def _highlight(self, event):
        if isinstance(self.component, BasePlotContainer):
            event.offset_xy(self.component.x, self.component.y)
            closest_plot = self._find_curve(self.component.components, event)
            if closest_plot:
                index = closest_plot.index
                index.metadata['selections'] = ones(len(index.get_data()), dtype=bool)
                closest_plot.request_redraw()
            else:
                # If we are attached to a plot container, then we can deselect
                # all of the plots in the container
                for p in self.component.components:
                    if "selections" in p.index.metadata:
                        del p.index.metadata['selections']
                        p.request_redraw()
            event.pop()

        elif hasattr(self.component, "hittest"):
            hit_point = self.component.hittest((event.x, event.y), self.threshold)
            index = self.component.index
            if hit_point is not None:
                index.metadata['selections'] = ones(len(index.get_data()), dtype=bool)
                self.component.request_redraw()
            elif "selections" in index.metadata:
                del index.metadata["selections"]
                self.component.request_redraw()
 
        event.handled = True
        return


    def _find_curve(self, plots, event):
        # need to change to use distance - not just return first plot within threshold
        for p in plots:
            cpoint = p.hittest((event.x,event.y), self.threshold)
            if cpoint:
                return p
        return None
        
#EOF
