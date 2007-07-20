""" Defines the RegressionLasso class.
"""
# Major library imports
from numpy import compress
from scipy import polyfit

# Enthought library imports
from enthought.enable2.api import ColorTrait, LineStyle
from enthought.traits.api import Any, Float, Instance

# Chaco imports
from enthought.chaco2.api import LassoOverlay, Label
from enthought.chaco2.tools.api import LassoSelection


class RegressionLasso(LassoSelection):
    """ A controller for "lassoing" a selection of points in a regression plot.
    """
    # The regression updates as more points are added (overrides LassoSelection).
    incremental_select = True

    # Tuple (slope, intercept) of the line that fits the data.
    fit_params = Any

    # The center point of the selected points, in data space.
    centroid = Any
    
    def _selection_changed_fired(self, event):
        indices = self.selection_datasource.metadata["selection"]
        if any(indices):
            x = compress(indices, self.component.index.get_data())
            y = compress(indices, self.component.value.get_data())
            self.fit_params = tuple(polyfit(x,y,1))
            self.centroid = (sum(x)/len(x)), (sum(y)/len(y))
        else:
            self.fit_params = None
            self.centroid = None
        return
    

class RegressionOverlay(LassoOverlay):

    line_color = ColorTrait("black")
    line_style = LineStyle("dash")
    line_width = Float(2.0)
    
    _label = Instance(Label, kw=dict(bgcolor="white", border_color="black",
                                 font="modern 14", border_width=1))
    
    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        LassoOverlay._draw_component(self, gc, view_bounds, mode)
        selection = self.lasso_selection
        
        if selection.fit_params is not None:
            # draw the label overlay 
            self._label.component = self.component
            self._label.text = "%.2fx + %.2f" % selection.fit_params
            w, h = self._label.get_width_height(gc)
            x = (self.component.x+self.component.x2)/2 - w/2
            y = self.component.y + 5  # add some padding on the bottom
            gc.save_state()
            gc.translate_ctm(x, y)
            self._label.draw(gc)
            gc.restore_state()

            # draw the line
            slope, y0 = selection.fit_params
            f = lambda x: slope*x + y0
            cx, cy = self.component.map_screen([selection.centroid])[0]
            left = self.component.x
            right = self.component.x2
            gc.save_state()
            try:
                gc.set_line_dash(self.line_style_)
                gc.set_stroke_color(self.line_color_)
                gc.set_line_width(self.line_width)
                gc.move_to(left, cy - f(cx-left))
                gc.line_to(right, cy + f(right - cx))
                gc.stroke_path()
            finally:
                gc.restore_state()
        return
    
