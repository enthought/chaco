""" Defines the PolygonPlot class.
"""

from __future__ import with_statement

# Major library imports
import numpy as np

# Enthought library imports.
from enable.api import LineStyle, black_color_trait, \
                                  transparent_color_trait
from kiva.api import points_in_polygon
from traits.api import Enum, Float, Tuple, Property, cached_property, \
                        on_trait_change

# Local imports.
from .base_xy_plot import BaseXYPlot

class PolygonPlot(BaseXYPlot):
    """ Plots a polygon in dataspace.

    Assuming that the index and value mappers are linear mappers, and that
    "index" corresponds to X-coordinates and "value" corresponds to
    Y-coordinates, the points are arranged in a counter-clockwise fashion.
    The polygon is closed automatically, so there is no need to reproduce
    the first point as the last point.

    Nonlinear mappers are possible, but the results may be unexpected. Only the
    data-space points are mapped in a nonlinear fashion. Straight lines
    connecting them in a linear screen-space become curved in a nonlinear
    screen-space; however, the drawing still contains straight lines in
    screen-space.

    If you don't want the edge of the polygon to be drawn, set **edge_color**
    to transparent; don't try to do this by setting **edge_width** to 0. In
    some drawing systems, such as PostScript, a line width of 0 means to make
    the line as small as possible while still putting ink on the page.
    """

    #: The color of the line on the edge of the polygon.
    edge_color = black_color_trait

    #: The thickness of the edge of the polygon.
    edge_width = Float(1.0)

    #: The line dash style for the edge of the polygon.
    edge_style = LineStyle

    #: The color of the face of the polygon.
    face_color = transparent_color_trait

    #: Override the hittest_type trait inherited from BaseXYPlot
    hittest_type = Enum("poly", "point", "line")
    
    #: The RGBA tuple for rendering edges.  It is always a tuple of length 4.
    #: It has the same RGB values as edge_color_, and its alpha value is the
    #: alpha value of self.edge_color multiplied by self.alpha.
    effective_edge_color = Property(Tuple, depends_on=['edge_color', 'alpha'])
    
    #: The RGBA tuple for rendering the face.  It is always a tuple of length 4.
    #: It has the same RGB values as face_color_, and its alpha value is the
    #: alpha value of self.face_color multiplied by self.alpha.
    effective_face_color = Property(Tuple, depends_on=['face_color', 'alpha'])

    #----------------------------------------------------------------------
    # Private 'BaseXYPlot' interface
    #----------------------------------------------------------------------

    def _gather_points(self):
        """ Collects the data points that are within the bounds of the plot and
        caches them.
        """
        if self._cache_valid:
            return

        index = self.index.get_data()
        value = self.value.get_data()

        if not self.index or not self.value:
            return

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            self._cached_data_pts = []
            self._cache_valid = True
            return

        points = np.transpose(np.array((index,value)))
        self._cached_data_pts = points

        self._cache_valid = True


    def _render(self, gc, points):
        """ Renders an Nx2 array of screen-space points as a polygon.
        """
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            gc.set_stroke_color(self.effective_edge_color)
            gc.set_line_width(self.edge_width)
            gc.set_line_dash(self.edge_style_)
            gc.set_fill_color(self.effective_face_color)

            gc.lines(points)
            gc.close_path()
            gc.draw_path()


    def _render_icon(self, gc, x, y, width, height):
        """ Renders a representation of this plot as an icon into the box
        defined by the parameters.

        Used by the legend.
        """
        with gc:
            gc.set_stroke_color(self.effective_edge_color)
            gc.set_line_width(self.edge_width)
            gc.set_fill_color(self.effective_face_color)
            if hasattr(self, 'line_style_'):
                gc.set_line_dash(self.line_style_)
            gc.draw_rect((x,y,width,height))
        return

    def hittest(self, screen_pt, threshold=7.0, return_distance=False):
        """ Performs point-in-polygon testing or point/line proximity testing.
        If self.hittest_type is "line" or "point", then behaves like the
        parent class BaseXYPlot.hittest().

        If self.hittest_type is "poly", then returns True if the given
        point is inside the polygon, and False otherwise.
        """
        if self.hittest_type in ("line", "point"):
            return BaseXYPlot.hittest(self, screen_pt, threshold, return_distance)

        data_pt = self.map_data(screen_pt, all_values=True)
        index = self.index.get_data()
        value = self.value.get_data()
        poly = np.column_stack((index, value))
        if points_in_polygon([data_pt], poly)[0] == 1:
            return True
        else:
            return False

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    @on_trait_change('edge_color, edge_width, edge_style, face_color, alpha')
    def _attributes_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    #------------------------------------------------------------------------
    # Property getters
    #------------------------------------------------------------------------

    @cached_property
    def _get_effective_edge_color(self):
        if len(self.edge_color_) == 4:
            edge_alpha = self.edge_color_[-1]
        else:
            edge_alpha = 1.0
        c = self.edge_color_[:3] + (edge_alpha * self.alpha,)
        return c

    @cached_property
    def _get_effective_face_color(self):
        if len(self.face_color_) == 4:
            face_alpha = self.face_color_[-1]
        else:
            face_alpha = 1.0
        c = self.face_color_[:3] + (face_alpha * self.alpha,)
        return c
