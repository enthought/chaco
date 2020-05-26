""" An overlay for drawing "infinite" vertical and horizontal lines.

This module defines the CoordinateLineOverlay class, a Chaco overlay
for Plot (and similar) objects.
"""

from __future__ import with_statement

from traits.api import Instance, Float, Array
from enable.api import black_color_trait, LineStyle, Component
from chaco.abstract_overlay import AbstractOverlay


class CoordinateLineOverlay(AbstractOverlay):

    # The data coordinates of the lines to be drawn perpendicular to the
    # index axis.
    index_data = Array

    # The data coordinates of the lines to be drawn perpendicular to the
    # value axis.
    value_data = Array

    # Width of the lines.
    line_width = Float(1.0)

    # Color of the lines.
    color = black_color_trait

    # Style of the lines ('solid', 'dash' or 'dot').
    line_style = LineStyle

    # The component that this tool overlays.  This must be a Component with
    # the following attributes:
    #     x, y, x2, y2
    #         The screen coordinates of the corners of the component.
    #     orientation ('h' or 'v')
    #         The orientation of the component, either horizontal or vertical.
    #         This is the orientation of the index axis.
    #     index_mapper
    #         index_mapper.map_screen maps `index_data` to screen coordinates.
    #     value_mapper
    #         value_mapper.map_screen maps `value_data` to screen coordinates.
    # Typically this will be a Plot instance.
    component = Instance(Component)

    #----------------------------------------------------------------------
    # Override AbstractOverlay methods
    #----------------------------------------------------------------------

    def overlay(self, component, gc, view_bounds, mode="normal"):

        comp = self.component
        x_pts = comp.index_mapper.map_screen(self.index_data)
        y_pts = comp.value_mapper.map_screen(self.value_data)
        if comp.orientation == "v":
            x_pts, y_pts = y_pts, x_pts

        with gc:
            # Set the line color and style parameters.
            gc.set_stroke_color(self.color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)

            # Draw the vertical lines.
            for screen_x in x_pts:
                self._draw_vertical_line(gc, screen_x)

            # Draw the horizontal lines.
            for screen_y in y_pts:
                self._draw_horizontal_line(gc, screen_y)

    #----------------------------------------------------------------------
    # Private methods
    #----------------------------------------------------------------------

    def _draw_vertical_line(self, gc, screen_x):
        if screen_x < self.component.x or screen_x > self.component.x2:
            return
        gc.move_to(screen_x, self.component.y)
        gc.line_to(screen_x, self.component.y2)
        gc.stroke_path()

    def _draw_horizontal_line(self, gc, screen_y):
        if screen_y < self.component.y or screen_y > self.component.y2:
            return
        gc.move_to(self.component.x, screen_y,)
        gc.line_to(self.component.x2, screen_y)
        gc.stroke_path()
