
from enthought.enable2.api import BaseTool, ColorTrait
from enthought.traits.api import Any, Bool, Enum, HasTraits, Trait

class RangeController(HasTraits):
    canvas = Any

    def notify(self, axistool, type, event):
        return True

class AxisTool(BaseTool):

    # The object to notify when we've been clicked
    # We notify by calling its .notify method, which should have the
    # signature:
    #     should_handle_event = notify(axis_tool, down_or_up, event)
    #
    # It should return a bool indicating whether or not we should process the
    # event.
    range_controller = Any

    down_tick_color = ColorTrait("red")
    down_axis_line_color = ColorTrait("red")
    down_tick_label_color = ColorTrait("red")
    down_bgcolor = ColorTrait("lightgray")
    down_border_visible = Bool(True)
    down_border_color = Trait(None, None, ColorTrait)

    _cached_tick_color = ColorTrait
    _cached_axis_line_color = ColorTrait
    _cached_tick_labl_color = ColorTrait
    _cached_bgcolor = ColorTrait
    _cached_border_visible = Bool(True)
    _cached_border_color = ColorTrait

    attr_list = ("tick_color", "axis_line_color", "tick_label_color", "bgcolor", 
                 "border_visible", "border_color")

    def normal_left_down(self, event):
        if self.component is None:
            return

        # If we have a controller, we let it decide whether
        # or not we get to handle the event.
        if self.range_controller is not None:
            should_handle = self.range_controller.notify(self, "down", event)
            if not should_handle:
                return

        plot = self.component
        if plot.index_axis.is_in(event.x, event.y):
            axis = plot.index_axis
        elif plot.value_axis.is_in(event.x, event.y):
            axis = plot.value_axis
        else:
            return
        for attr in self.attr_list:
            cached = "_cached_" + attr
            down = "down_" + attr
            setattr(self, cached, getattr(axis, attr))
            if getattr(self, down) is not None:
                setattr(axis, attr, getattr(self, down))
        
        axis.request_redraw()
        plot._debug = True
        event.handled = True
        return

    def normal_left_up(self, event):
        if self.component is None:
            return
        if self.range_controller is not None:
            should_handle = self.range_controller.notify(self, "up", event)
            if not should_handle:
                return

        plot = self.component
        if plot.index_axis.is_in(event.x, event.y):
            axis = plot.index_axis
        elif plot.value_axis.is_in(event.x, event.y):
            axis = plot.value_axis
        else:
            return
        for attr in self.attr_list:
            setattr(axis, attr, getattr(self, "_cached_" + attr))

        axis.request_redraw()
        event.handled = True
        return

