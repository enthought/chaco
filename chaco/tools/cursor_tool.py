"""
Defines some chaco tools to provide draggable cursor functionality

For XY-plots, the cursor tool requires the index_sort flag to be set
to either 'ascending' or 'descending'.

TODO:

- add some visual feedback to the user when a cursor is "grabbed"
    (e.g. highlight the cursor line)

- update cursor position to the "selections" metadata on the owning
    plot component

"""


# Major library imports
import numpy

# Enthought library imports
from enable.tools.drag_tool import DragTool
from traits.api import Int, Property, cached_property, Float,\
                                Bool, Instance, Tuple, Disallow

# Chaco imports
from chaco.scatter_markers import CircleMarker
from chaco.base_xy_plot import BaseXYPlot
from chaco.base_2d_plot import Base2DPlot
from .line_inspector import LineInspector


def CursorTool(component, *args, **kwds):
    """
    Factory function returning either a CursorTool1D or CursorTool2D instance
    depending on whether the provided plot component is an XY-plot or a 2D plot.
    """
    if isinstance(component, BaseXYPlot):
        return CursorTool1D(component, *args, **kwds)
    elif isinstance(component, Base2DPlot):
        return CursorTool2D(component, *args, **kwds)
    else:
        raise NotImplementedError("cursors available for BaseXYPlot and Base2DPlot only")


class BaseCursorTool(LineInspector, DragTool):
    """
    Abstract base class for CursorTool objects
    """

    #if true, draw a small circle at the cursor/line intersection
    show_marker = Bool(True)

    #the radius of the marker in pixels
    marker_size = Float(3.0)

    #the marker object. this should probably be private
    marker = Instance(CircleMarker, ())

    #pick threshold, in screen units (pixels)
    threshold = Float(5.0)

    #The current index-value of the cursor. Over-ridden in subclasses
    current_index = Disallow

    #The current position of the cursor in data units
    current_position = Property(depends_on=['current_index'])

    #Stuff from line_inspector which is not required
    axis = Disallow
    inspect_mode = Disallow
    is_interactive = Disallow
    is_listener = Disallow
    write_metadata = Disallow
    metadata_name = Disallow

    def _draw_marker(self, gc, sx, sy):
        """
        Ruthlessly hijacked from the scatterplot.py class. This design is silly; the
        choice of rendering path should be encapsulated within the GC.
        """
        if sx < self.component.x or sx > self.component.x2 or \
            sy < self.component.y or sy > self.component.y2:
            return

        marker = self.marker
        marker_size = self.marker_size
        points = [(sx,sy)]

        with gc:
            gc.set_fill_color(self.color_)

            gc.begin_path()

            # This is the fastest method - use one of the kiva built-in markers
            if hasattr(gc, "draw_marker_at_points") \
                and (gc.draw_marker_at_points(points,
                                              marker_size,
                                              marker.kiva_marker) != 0):
                    pass

            # The second fastest method - draw the path into a compiled path, then
            # draw the compiled path at each point
            elif hasattr(gc, 'draw_path_at_points'):
                path = gc.get_empty_path()
                marker.add_to_path(path, marker_size)
                mode = marker.draw_mode
                if not marker.antialias:
                    gc.set_antialias(False)
                gc.draw_path_at_points(points, path, mode)

            # Neither of the fast functions worked, so use the brute-force, manual way
            else:
                if not marker.antialias:
                    gc.set_antialias(False)
                for sx,sy in points:
                    with gc:
                        gc.translate_ctm(sx, sy)
                        # Kiva GCs have a path-drawing interface
                        marker.add_to_path(gc, marker_size)
                        gc.draw_path(marker.draw_mode)

    def normal_mouse_move(self, event):
        """ Handles the mouse being moved.
        """
        return

    def normal_mouse_leave(self, event):
        """ Handles the mouse leaving the plot.
        """
        return


class CursorTool1D(BaseCursorTool):
    """
    This tools provides a draggable cursor bound to a XY plot component instance.

    Note, be sure to select an drag_button which does not conflict with other tools
    (e.g. the PanTool).

    """

    #The current index-value of the cursor
    current_index = Int(0)


    #if true, draws a line parallel to the index-axis
    #through the cursor intersection point
    show_value_line = Bool(True)

    def _current_index_changed(self):
        self.component.request_redraw()

    @cached_property
    def _get_current_position(self):
        plot = self.component
        ndx = self.current_index
        x = plot.index.get_data()[ndx]
        y = plot.value.get_data()[ndx]
        return x,y

    def _set_current_position(self, traitname, args):
        plot = self.component
        ndx = plot.index.reverse_map(args[0])
        if ndx is not None:
            self.current_index = ndx

    def draw(self, gc, view_bounds=None):
        """ Draws this tool on a graphics context.

        Overrides LineInspector, BaseTool.
        """
        # We draw at different points depending on whether or not we are
        # interactive.  If both listener and interactive are true, then the
        # selection metadata on the plot component takes precendence.
        plot = self.component
        if plot is None:
            return

        sx, sy = plot.map_screen(self.current_position)
        orientation = plot.orientation

        if orientation == "h" and sx is not None:
            self._draw_vertical_line(gc, sx)
        elif sy is not None:
            self._draw_horizontal_line(gc, sy)

        if self.show_marker:
            self._draw_marker(gc, sx, sy)

        if self.show_value_line:
            if orientation == "h" and sy is not None:
                self._draw_horizontal_line(gc, sy)
            elif sx is not None:
                self._draw_vertical_line(gc, sx)

    def is_draggable(self, x, y):
        plot = self.component
        if plot is not None:
            orientation = plot.orientation
            sx, sy = plot.map_screen(self.current_position)
            if orientation=='h' and numpy.abs(sx-x) <= self.threshold:
                return True
            elif orientation=='v' and numpy.abs(sy-y) <= self.threshold:
                return True
        return False

    def dragging(self, event):
        x,y = event.x, event.y
        plot = self.component
        ndx = plot.map_index((x, y), threshold=0.0, index_only=True)
        if ndx is None:
            return
        self.current_index = ndx
        plot.request_redraw()


class CursorTool2D(BaseCursorTool):
    _dragV = Bool(False)
    _dragH = Bool(False)

    current_index = Tuple(0,0)

    def _current_index_changed(self):
        self.component.request_redraw()

    @cached_property
    def _get_current_position(self):
        plot = self.component
        ndx, ndy = self.current_index
        xdata, ydata = plot.index.get_data()
        x = xdata.get_data()[ndx]
        y = ydata.get_data()[ndy]
        return x,y

    def _set_current_position(self, traitname, args):
        plot = self.component
        xds, yds = plot.index.get_data()
        ndx = xds.reverse_map(args[0])
        ndy = yds.reverse_map(args[1])
        if ndx is not None and ndy is not None:
            self.current_index = ndx, ndy

    def is_draggable(self, x, y):
        plot = self.component
        if plot is not None:
            orientation = plot.orientation
            sx, sy = plot.map_screen([self.current_position])[0]
            self._dragV = self._dragH = False
            if orientation=='h':
                if numpy.abs(sx-x) <= self.threshold:
                    self._dragH = True
                if numpy.abs(sy-y) <= self.threshold:
                    self._dragV = True
            else:
                if numpy.abs(sx-x) <= self.threshold:
                    self._dragV = True
                if numpy.abs(sy-y) <= self.threshold:
                    self._dragH = True
            return self._dragV or self._dragH
        return False

    def draw(self, gc, view_bounds=None):
        """ Draws this tool on a graphics context.

        Overrides LineInspector, BaseTool.
        """
        # We draw at different points depending on whether or not we are
        # interactive.  If both listener and interactive are true, then the
        # selection metadata on the plot component takes precendence.
        plot = self.component
        if plot is None:
            return
        sx, sy = plot.map_screen([self.current_position])[0]
        orientation = plot.orientation

        if orientation == "h":
            if sx is not None:
                self._draw_vertical_line(gc, sx)
            if sy is not None:
                self._draw_horizontal_line(gc, sy)
        else:
            if sx is not None:
                self._draw_horizontal_line(gc, sx)
            if sy is not None:
                self._draw_vertical_line(gc, sy)

        if self.show_marker and sx is not None and sy is not None:
            self._draw_marker(gc, sx, sy)

    def dragging(self, event):
        x,y = event.x, event.y
        plot = self.component
        ndx = plot.map_index((x, y), threshold=0.0, index_only=True)
        if ndx is None:
            return
        newx, newy = self.current_index
        if self._dragH and ndx[0] is not None:
            newx = ndx[0]
        if self._dragV and ndx[1] is not None:
            newy = ndx[1]
        self.current_index = newx, newy
        plot.request_redraw()
