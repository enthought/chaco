
# Major library imports
from numpy import ones

# Enthought library imports
from enthought.traits.api import Enum, Float, Tuple

# Chaco imports
from enthought.chaco2.api import AbstractPlotRenderer, BasePlotContainer, BaseTool


class HighlightTool(BaseTool):
    """
    Allows the user to select a plot to be highlighted on the graph
    by clicking on it.
    """

    # Which mouse button initiates the selection
    drag_button = Enum("left", "right")

    # Threshold for hittest
    threshold = Float(20.0)


    #---------------------------------------------------------------------
    # Inherited BaseTool traits
    #---------------------------------------------------------------------

    draw_mode = "none"
    visible = False


    def normal_left_down(self, event):
        if self.drag_button == "left":
            self._highlight(event)
        return

    def normal_right_down(self, event):
        if self.drag_button == "right":
            self._highlight(event)
        return

    def _highlight(self, event):

        if isinstance(self.component, BasePlotContainer):
            event.offset_xy(self.component.x, self.component.y)
            closest_plot = self._find_curve(self.component.plot_components, event)
            if closest_plot:
                index = closest_plot.index
                index.metadata['selections'] = ones(len(index.get_data()))
                closest_plot.request_redraw()
            else:
                # If we are attached to a plot container, then we can deselect
                # all of the plots in the container
                for p in self.component.plot_components:
                    if "selections" in p.index.metadata:
                        del p.index.metadata['selections']
                        p.request_redraw()
            event.pop()

        elif hasattr(self.component, "hittest"):
            hit_point = self.component.hittest((event.x, event.y), self.threshold)
            index = self.component.index
            if hit_point is not None:
                index.metadata['selections'] = ones(len(index.get_data()))
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
