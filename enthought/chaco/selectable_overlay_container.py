""" Defines the SelectableOverlayPlotContainer class.
"""

from __future__ import with_statement

from numpy import array, float64

# Enthought library imports
from enthought.traits.api import Bool, Float, Enum
from enthought.enable.api import ColorTrait

# Local imports
from plot_containers import OverlayPlotContainer

class SelectableOverlayPlotContainer(OverlayPlotContainer):
    """
    An OverlayPlotContainer that can show a selection region on top of it.
    """

    # Screen position of the start of the selection, which can be in the x- or
    # y-dimension, depending on **selection_direction**.
    selection_screen_start = Float(0.0)
    # Screen position of the end of the selection, which can be in the x- or
    # y-dimension, depending on **selection_direction**.
    selection_screen_end = Float(0.0)
    # Is there an active selection?
    selection_active = Bool(False)
    # The direction of the selection.
    selection_direction = Enum('v', 'h')
    # The color to use to fill the selected region.
    selection_fill_color = ColorTrait('lightskyblue')
    # The color to use to draw the border of the selected region.
    selection_border_color = ColorTrait('dodgerblue')
    # The transparency of the **selection_fill_color**.
    selection_alpha = Float(0.3)

    def _draw_overlays(self, gc, view_bounds=None, mode='normal'):
        """ Method for backward compatability with old drawing scheme.
        
        Overrides BasePlotContainer.
        """
        self._draw_selection(gc, view_bounds=view_bounds, mode=mode)
        return
    
    def _draw_selection(self, gc, view_bounds=None, mode='normal'):
        """ Renders a selected subset of a component's data.
        
        Overrides PlotComponent.
        """
        if self.selection_active:
            if self.selection_direction == 'h':
                x1 = self.selection_screen_start
                x2 = self.selection_screen_end
                y1 = self.y
                y2 = self.position[1] + self.bounds[1] - 1
            else:
                x1 = self.x
                x2 = self.position[0] + self.bounds[0] - 1
                y1 = self.selection_screen_start
                y2 = self.selection_screen_end
            lowerleft = array((min(x1, x2), min(y1, y2)), float64)
            upperright = array((max(x1, x2), max(y1, y2)), float64)
            with gc:
                gc.translate_ctm(*self.position)
                gc.set_fill_color(self.selection_fill_color_)
                gc.set_stroke_color(self.selection_border_color_)
                gc.set_alpha(self.selection_alpha)
                gc.rect(lowerleft[0], lowerleft[1], upperright[0], upperright[1])
                gc.draw_path()
        return
    
            
