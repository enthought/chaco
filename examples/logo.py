""" LOGO overlay """

from __future__ import with_statement

from numpy import array, cos, invert, isnan, nan, pi, sin, vstack
from enthought.traits.api import Array, Enum, Float, Range
from enthought.traits.ui.api import Group, Item, View
from enthought.enable.api import ColorTrait
from enthought.chaco.api import arg_find_runs, AbstractOverlay


class Turtle(AbstractOverlay):
    x = Float
    y = Float
    angle = Range(0.0, 360.0, value=90.0)    # degrees, clockwise
    color = ColorTrait("blue")
    line_color = ColorTrait("green")
    size = Float(10.0)
    path = Array

    _pen = Enum("down", "up")

    view = View(Group("x", "y", "angle", Item("color", style="custom"),
                      Item("line_color", style="custom"), "size",
                      orientation="vertical"))

    def __init__(self, component=None, **traits):
        super(Turtle, self).__init__(component=component, **traits)
        if 'path' not in traits:
            self.path = array([self.x, self.y], ndmin=2)

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        self.render(gc, other_component)

    def render_turtle(self, gc, component):
        with gc:
            x, y = component.map_screen(array([self.x, self.y], ndmin=2))[0]
            gc.translate_ctm(x, y)
            angle = self.angle * pi / 180.0
            gc.rotate_ctm(angle)
            gc.set_stroke_color(self.color_)
            gc.set_fill_color(self.color_)
            gc.begin_path()
            gc.lines([[-0.707*self.size, 0.707*self.size],
                      [-0.707*self.size, -0.707*self.size],
                      [self.size, 0.0]])
            gc.fill_path()

    def render(self, gc, component):
        # Uses the component to map our path into screen space
        nan_mask = invert(isnan(self.path[:,0])).astype(int)
        blocks = [b for b in arg_find_runs(nan_mask, "flat") if nan_mask[b[0]] != 0]
        screen_pts = component.map_screen(self.path)
        with gc:
            gc.clip_to_rect(component.x, component.y, component.width, component.height)
            gc.set_stroke_color(self.line_color_)
            for start, end in blocks:
                gc.begin_path()
                gc.lines(screen_pts[start:end])
                gc.stroke_path()
            self.render_turtle(gc, component)

    def pendown(self):
        self._pen = "down"
        self.path = vstack((self.path, [self.x, self.y]))

    def penup(self):
        self.path = vstack((self.path, [nan,nan]))
        self._pen = "up"

    def forward(self, amt):
        angle = self.angle * pi / 180.0
        self.x += amt * cos(angle)
        self.y += amt * sin(angle)
        if self._pen == "down":
            self.path = vstack((self.path, [self.x, self.y]))

    def back(self, amt):
        self.forward(-amt)

    def left(self, angle):
        self.angle = (self.angle + angle) % 360

    def right(self, angle):
        self.angle = ((self.angle - angle) + 360) % 360

    def clear(self):
        self.path = array([self.x, self.y], ndmin=2)

    def reset(self):
        self.x = self.y = 0.0
        self.angle = 90.0
        self.clear()

    def _anytrait_changed(self, trait, val):
        self.component.request_redraw()



