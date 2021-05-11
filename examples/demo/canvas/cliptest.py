#!/usr/bin/env python
"""
The main app for the Cliptest application
"""


# Enthought library imports
from traits.api import Float
from enable.api import Window, Container, Component, Pointer
from enable.tools.api import MoveTool
from enable.example_support import DemoFrame, demo_main


class Box(Component):
    """
    The box moves wherever the user clicks and drags.
    """

    normal_pointer = Pointer("arrow")
    moving_pointer = Pointer("hand")

    offset_x = Float
    offset_y = Float

    fill_color = (0.8, 0.0, 0.1, 1.0)
    moving_color = (0.0, 0.8, 0.1, 1.0)

    resizable = ""

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        with gc:
            gc.set_fill_color(self.fill_color)
            dx, dy = self.bounds
            x, y = self.position
            gc.clip_to_rect(x, y, dx, dy)
            gc.rect(x, y, dx, dy)
            gc.fill_path()

            ## draw line around outer box
            # gc.set_stroke_color((0,0,0,1))
            # gc.rect(self.outer_x, self.outer_y, self.outer_width, self.outer_height)
            # gc.stroke_path()

    def normal_left_down(self, event):
        self.event_state = "moving"
        event.window.set_pointer(self.moving_pointer)
        event.window.set_mouse_owner(self, event.net_transform())
        self.offset_x = event.x - self.x
        self.offset_y = event.y - self.y
        event.handled = True

    def moving_mouse_move(self, event):
        self.position = [event.x - self.offset_x, event.y - self.offset_y]
        event.handled = True
        self.request_redraw()

    def moving_left_up(self, event):
        self.event_state = "normal"
        event.window.set_pointer(self.normal_pointer)
        event.window.set_mouse_owner(None)
        event.handled = True
        self.request_redraw()

    def moving_mouse_leave(self, event):
        self.moving_left_up(event)
        event.handled = True


class MainFrame(DemoFrame):
    def _create_component(self):
        a = Box(bounds=[75, 75], position=[50, 50], fill_color=(1, 0, 0, 1))
        b = Box(bounds=[75, 75], position=[200, 50], fill_color=(0, 1, 0, 1))
        c = Box(bounds=[75, 75], position=[50, 200], fill_color=(0, 0, 1, 1))
        cont = Container(
            a,
            b,
            c,
            bounds=[400, 400],
            border_visible=True,
            bgcolor="lightgray",
        )
        # cont.unified_draw = True
        # cont.draw_layer = "background"
        cont2 = Container(
            bounds=[300, 300], border_visible=True, bgcolor="cyan"
        )
        cont.tools.append(MoveTool(cont, drag_button="left"))
        cont2.tools.append(MoveTool(cont2, drag_button="left"))
        outer = Container(cont, cont2, fit_window=True)
        return outer


if __name__ == "__main__":
    # Save demo so that it doesn't get garbage collected when run within
    # existing event loop (i.e. from ipython).
    demo = demo_main(MainFrame, size=(800, 800), title="ClipTest")
