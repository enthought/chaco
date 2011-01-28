
from __future__ import with_statement

from numpy import array, compress, matrix, newaxis, sqrt, zeros

# Enthought library imports
from enthought.enable.api import ColorTrait
from enthought.traits.api import Array, Enum, Float, Instance, Int

# Chaco relative imports
from abstract_data_source import AbstractDataSource
from scatterplot import ScatterPlot

class QuiverPlot(ScatterPlot):

    # Determines how to interpret the data in the **vectors** data source.
    #   "vector": each tuple is a (dx, dy)
    #   "radial": each tuple is an (r, theta)
    data_type = Enum("vector", "radial") # TODO: implement "radial"

    # A datasource that returns an Nx2 array array indicating directions
    # of the vectors.  The interpretation of this array is dependent on
    # the setting of the **data_type** attribute.
    #
    # Usually this will be a MultiArrayDataSource.
    vectors = Instance(AbstractDataSource)

    #------------------------------------------------------------------------
    # Visual attributes of the vector
    #------------------------------------------------------------------------

    # The color of the lines
    line_color = ColorTrait("black")

    # The width of the lines
    line_width = Float(1.0)

    # The length, in pixels, of the arrowhead
    arrow_size = Int(5)

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------

    _cached_vector_data = Array
    _selected_vector_data = Array

    def _gather_points_old(self):
        # In addition to the standard scatterplot _gather_points, we need
        # to also grab the vectors that fall inside the view range
        super(QuiverPlot, self)._gather_points_old()

        if not self.index or not self.value:
            return

        if len(self._cached_point_mask) == 0:
            self._cached_vector_data = []
            return

        vectors = self.vectors.get_data()
        self._cached_vector_data = compress(self._cached_point_mask, vectors, axis=0)

        if self._cached_selected_pts is not None:
            indices = self._cached_selection_point_mask
            self._selected_vector_data = compress(indices, vectors, axis=0)
        else:
            self._selected_vector_data = None
        return


    def _render(self, gc, points, icon_mode=False):
        with gc:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)

            gc.set_stroke_color(self.line_color_)
            gc.set_line_width(self.line_width)

            # Draw the body of the arrow
            starts = points
            ends = points + self._cached_vector_data
            gc.begin_path()
            gc.line_set(starts, ends)
            gc.stroke_path()

            if self.arrow_size > 0:
                vec = self._cached_vector_data
                unit_vec = vec / sqrt(vec[:,0] ** 2 + vec[:,1] ** 2)[:, newaxis]
                a = 0.707106781   # sqrt(2)/2

                # Draw the left arrowhead (for an arrow pointing straight up)
                arrow_ends = ends - array(unit_vec * matrix([[a, a], [-a, a]])) * self.arrow_size
                gc.begin_path()
                gc.line_set(ends, arrow_ends)
                gc.stroke_path()

                # Draw the left arrowhead (for an arrow pointing straight up)
                arrow_ends = ends - array(unit_vec * matrix([[a, -a], [a, a]])) * self.arrow_size
                gc.begin_path()
                gc.line_set(ends, arrow_ends)
                gc.stroke_path()
