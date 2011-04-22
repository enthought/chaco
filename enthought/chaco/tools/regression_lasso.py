""" Defines the RegressionLasso class.
"""
from __future__ import with_statement

# Major library imports
from numpy import compress, polyfit
from math import fabs

# Enthought library imports
from enable.api import ColorTrait, LineStyle
from traits.api import Any, Float, Instance

# Chaco imports
from enthought.chaco.api import LassoOverlay, Label
from enthought.chaco.tools.api import LassoSelection


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
            if len(x) < 2 or len(y) < 2:
                self.fit_params = None
                self.centroid = None
            else:
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
            c = self.component

            if selection.fit_params[1] < 0:
                operator = "-"
            else:
                operator = "+"
            self._label.text = "%.2fx "%selection.fit_params[0] + operator + \
                               " %.2f" % fabs(selection.fit_params[1])
            w, h = self._label.get_width_height(gc)
            x = (c.x+c.x2)/2 - w/2
            y = c.y + 5  # add some padding on the bottom
            with gc:
                gc.translate_ctm(x, y)
                self._label.draw(gc)

            # draw the line
            slope, y0 = selection.fit_params
            f = lambda x: slope*x + y0
            cx, cy = c.map_screen([selection.centroid])[0]
            left = c.x
            right = c.x2

            left_x = c.map_data([left, c.y])[0]
            right_x = c.map_data([right, c.y])[0]
            left_y = f(left_x)
            right_y = f(right_x)

            left_pt, right_pt = c.map_screen([[left_x, left_y], [right_x, right_y]])

            with gc:
                gc.set_line_dash(self.line_style_)
                gc.set_stroke_color(self.line_color_)
                gc.set_line_width(self.line_width)
                gc.move_to(*left_pt)
                gc.line_to(*right_pt)
                gc.stroke_path()

        return
