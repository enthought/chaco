from enable.api import BaseTool, ColorTrait
from traits.api import (
    Any,
    Bool,
    Dict,
    Enum,
    HasTraits,
    Int,
    List,
    Trait,
    Tuple,
)


class RangeController(HasTraits):

    canvas = Any

    # The list of active plots and which of their ranges was set
    plots_ranges = List

    # Stores the old ranges
    _ranges = Dict

    def notify(self, axistool, rangename, type, event):
        plot = axistool.component
        range = getattr(plot, rangename)
        if (type == "down") and ((plot, rangename) not in self.plots_ranges):
            if len(self.plots_ranges) > 0:
                src_plot, src_rangename = self.plots_ranges[0]
                src_range = getattr(src_plot, src_rangename)
                self.link(src_range, plot, rangename)
            self.plots_ranges.append((plot, rangename))
        else:
            if (plot, rangename) in self.plots_ranges:
                if len(self.plots_ranges) > 1:
                    self.unlink(plot, rangename)
                self.plots_ranges.remove((plot, rangename))
        return True

    def link(self, src_range, dst_plot, dst_rangename):
        self._ranges[(dst_plot, dst_rangename)] = getattr(
            dst_plot, dst_rangename
        )
        setattr(dst_plot, dst_rangename, src_range)
        dst_plot.request_redraw()

    def unlink(self, plot, rangename):
        setattr(plot, rangename, self._ranges.pop((plot, rangename)))
        plot.request_redraw()


class AxisTool(BaseTool):

    # The object to notify when we've been clicked
    # We notify by calling its .notify method, which should have the
    # signature:
    #     should_handle_event = notify(axis_tool, axis, down_or_up, event)
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

    attr_list = (
        "tick_color",
        "axis_line_color",
        "tick_label_color",
        "bgcolor",
        "border_visible",
        "border_color",
    )

    def normal_left_down(self, event):
        if self.component is None:
            return
        plot = self.component
        if plot.index_axis.is_in(event.x, event.y):
            axis = plot.index_axis
            rangename = "index_range"
        elif plot.value_axis.is_in(event.x, event.y):
            axis = plot.value_axis
            rangename = "value_range"
        else:
            return

        # If we have a controller, we let it decide whether
        # or not we get to handle the event.
        if self.range_controller is not None:
            should_handle = self.range_controller.notify(
                self, rangename, "down", event
            )
            if not should_handle:
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

    def normal_left_up(self, event):
        if self.component is None:
            return
        plot = self.component
        if plot.index_axis.is_in(event.x, event.y):
            axis = plot.index_axis
            rangename = "index_range"
        elif plot.value_axis.is_in(event.x, event.y):
            axis = plot.value_axis
            rangename = "value_range"
        else:
            return

        if self.range_controller is not None:
            should_handle = self.range_controller.notify(
                self, rangename, "up", event
            )
            if not should_handle:
                return

        for attr in self.attr_list:
            cached = "_cached_" + attr
            setattr(axis, attr, getattr(self, cached))

        axis.request_redraw()
        event.handled = True


class MPAxisTool(AxisTool):

    cur_bid = Int(-1)
    _last_blob_pos = Tuple

    def normal_blob_down(self, event):
        if self.cur_bid == -1:
            self.cur_bid = event.bid
            if hasattr(event, "bid"):
                event.window.capture_blob(
                    self, event.bid, event.net_transform()
                )
            self.normal_left_down(event)
            self._last_blob_pos = (event.x, event.y)

    def normal_blob_up(self, event):
        print("Axis blob up")
        if event.bid == self.cur_bid:
            if hasattr(event, "bid"):
                event.window.release_blob(event.bid)
            self.cur_bid = -1
            event.x, event.y = self._last_blob_pos
            self.normal_left_up(event)
