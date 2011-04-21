""" Defines the LineInspector tool class.
"""
from __future__ import with_statement

# Enthought library imports
from enthought.enable.api import BaseTool, ColorTrait, LineStyle
from traits.api import Any, Bool, Enum, Float, Str, Trait

# Chaco imports
from enthought.chaco.api import BaseXYPlot, Base2DPlot


class LineInspector(BaseTool):
    """ A simple tool to draw a line parallel to the index or the value axis of
    an X-Y plot.

    This tool supports only plots with a 1-D index.
    """

    # The axis that this tool is parallel to.
    axis = Enum("index", "value", "index_x", "index_y")

    # The possible inspection modes of the tool.
    #
    # space:
    #    The tool maps from screen space into the data space of the plot.
    # indexed:
    #    The tool maps from screen space to an index into the plot's index array.
    inspect_mode = Enum("space", "indexed")

    # Respond to user mouse events?
    is_interactive = Bool(True)

    # Does the tool respond to updates in the metadata on the data source
    # and update its own position?
    is_listener = Bool(False)

    # If interactive, does the line inspector write the current data space point
    # to the appropriate data source's metadata?
    write_metadata = Bool(False)

    # The name of the metadata field to listen or write to.
    metadata_name = Str("selections")

    #------------------------------------------------------------------------
    # Override default values of inherited traits in BaseTool
    #------------------------------------------------------------------------

    # This tool is visible (overrides BaseTool).
    visible = True
    # This tool is drawn as an overlay (overrides BaseTool).
    draw_mode = "overlay"

    # TODO:STYLE

    # Color of the line.
    color = ColorTrait("black")
    # Width in pixels of the line.
    line_width = Float(1.0)
    # Dash style of the line.
    line_style = LineStyle("solid")

    # Last recorded position of the mouse
    _last_position = Trait(None, Any)

    def draw(self, gc, view_bounds=None):
        """ Draws this tool on a graphics context.

        Overrides BaseTool.
        """
        # We draw at different points depending on whether or not we are
        # interactive.  If both listener and interactive are true, then the
        # selection metadata on the plot component takes precendence.
        plot = self.component
        if plot is None:
            return

        if self.is_listener:
            tmp = self._get_screen_pts()
        elif self.is_interactive:
            tmp = self._last_position

        if tmp:
            sx, sy = tmp
        else:
            return

        if self.axis == "index" or self.axis == "index_x":
            if plot.orientation == "h" and sx is not None:
                self._draw_vertical_line(gc, sx)
            elif sy is not None:
                self._draw_horizontal_line(gc, sy)
        else:   # self.axis == "value"
            if plot.orientation == "h" and sy is not None:
                self._draw_horizontal_line(gc, sy)
            elif sx is not None:
                self._draw_vertical_line(gc, sx)
        return

    def do_layout(self, *args, **kw):
        pass

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on a graphics context.
        """
        self.draw(gc, view_bounds)
        return

    def normal_mouse_move(self, event):
        """ Handles the mouse being moved.
        """
        if not self.is_interactive:
            return
        plot = self.component
        if plot is not None:
            self._last_position = (event.x, event.y)
            if isinstance(plot, BaseXYPlot):
                if self.write_metadata:
                    if self.inspect_mode == "space":
                        index_coord, value_coord = \
                            self._map_to_data(event.x, event.y)
                        plot.index.metadata[self.metadata_name] = index_coord
                        plot.value.metadata[self.metadata_name] = value_coord
                    else:
                        ndx = plot.map_index((event.x, event.y),
                                             threshold=5.0, index_only=True)
                        if ndx:
                            plot.index.metadata[self.metadata_name] = ndx
                            plot.value.metadata[self.metadata_name] = ndx
            elif isinstance(plot, Base2DPlot):
                if self.write_metadata:
                    try:
                        old_x_data, old_y_data = \
                            plot.index.metadata[self.metadata_name]
                    except:
                        old_x_data, old_y_data = (None, None)

                    if self.inspect_mode == "space":
                        if plot.orientation == "h":
                            x_coord, y_coord = \
                                plot.map_data([(event.x, event.y)])[0]
                        else:
                            y_coord, x_coord = \
                                plot.map_data([(event.x, event.y)])[0]
                        if self.axis == "index_x":
                            metadata = x_coord, old_y_data
                        elif self.axis == "index_y":
                            metadata = old_x_data, y_coord
                    else:
                        if plot.orientation == "h":
                            x_ndx, y_ndx =  plot.map_index((event.x, event.y),
                                                           threshold=5.0)
                        else:
                            y_ndx, x_ndx = plot.map_index((event.x, event.y),
                                                          threshold=5.0)
                        if self.axis == "index_x":
                            metadata = x_ndx, old_y_data
                        elif self.axis == "index_y":
                            metadata = old_x_data, y_ndx

                    plot.index.metadata[self.metadata_name] = metadata

            plot.request_redraw()
        return

    def normal_mouse_leave(self, event):
        """ Handles the mouse leaving the plot.
        """
        if not self.is_interactive:
            return
        self._last_position = None
        plot = self.component
        if plot is not None:
            if self.write_metadata:
                if isinstance(plot, BaseXYPlot):
                    plot.index.metadata.pop(self.metadata_name, None)
                    plot.value.metadata.pop(self.metadata_name, None)
                elif isinstance(plot, Base2DPlot):
                    plot.index.metadata.pop(self.metadata_name, None)
            plot.request_redraw()
        return

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _get_screen_pts(self):
        """ Returns the screen-space coordinates of the selected point on
        the plot component as a tuple (x, y).

        A dimension that doesn't have a selected point has the value None at
        its index in the tuple, or won't have the key.
        """
        plot = self.component
        if plot is None:
            return

        retval = [None, None]

        if isinstance(plot, BaseXYPlot):
            index_coord = plot.index.metadata.get(self.metadata_name, None)
            value_coord = plot.value.metadata.get(self.metadata_name, None)

            if index_coord not in (None, []):
                if self.inspect_mode == "indexed":
                    index_coord = plot.index.get_data()[index_coord]
                retval[0] = plot.index_mapper.map_screen(index_coord)

            if value_coord not in (None, []):
                if self.inspect_mode == "indexed":
                    value_coord = plot.index.get_data()[value_coord]
                retval[1] = plot.value_mapper.map_screen(value_coord)

        elif isinstance(plot, Base2DPlot):
            try:
                x_coord, y_coord = plot.index.metadata[self.metadata_name]
            except:
                x_coord, y_coord = (None, None)

            if x_coord not in (None, []):
                if self.inspect_mode == "indexed":
                    x_coord = plot.index.get_data()[0].get_data()[x_coord]
                retval[0] = plot.index_mapper._xmapper.map_screen(x_coord)

            if y_coord not in (None, []):
                if self.inspect_mode == "indexed":
                    y_coord = plot.index.get_data()[1].get_data()[y_coord]
                retval[1] = plot.index_mapper._ymapper.map_screen(y_coord)

        if plot.orientation == "h":
            return retval
        else:
            return retval[1], retval[0]

    def _map_to_data(self, x, y):
        """ Returns the data space coordinates of the given x and y.

        Takes into account orientation of the plot and the axis setting.
        """

        plot = self.component
        if plot.orientation == "h":
            index = plot.index_mapper.map_data(x)
            value = plot.value_mapper.map_data(y)
        else:
            index = plot.index_mapper.map_data(y)
            value = plot.value_mapper.map_data(x)
        return index, value

    def _draw_vertical_line(self, gc, sx):
        """ Draws a vertical line through screen point (sx,sy) having the height
        of the tool's component.
        """
        if sx < self.component.x or sx > self.component.x2:
            return

        with gc:
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)
            gc.move_to(sx, self.component.y)
            gc.line_to(sx, self.component.y2)
            gc.stroke_path()
        return

    def _draw_horizontal_line(self, gc, sy):
        """ Draws a horizontal line through screen point (sx,sy) having the
        width of the tool's component.
        """
        if sy < self.component.y or sy > self.component.y2:
            return

        with gc:
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)
            gc.move_to(self.component.x, sy)
            gc.line_to(self.component.x2, sy)
            gc.stroke_path()
        return



# EOF
