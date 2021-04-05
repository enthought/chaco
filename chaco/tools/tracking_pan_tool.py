""" Defines the TrackingPanTool class.
"""
# Chaco imports
from .pan_tool import PanTool


class TrackingPanTool(PanTool):
    """Allows the user to pan around a plot.

    The user clicks a mouse button and drags to pan; the tool then returns to
    a tracking state.
    """

    def _end_pan(self, event):
        plot = self.component
        xrange = plot.x_mapper.range
        yrange = plot.y_mapper.range

        if not self.constrain or self.constrain_direction == "x":
            high = xrange.high
            low = xrange.low
            if xrange.default_state == "low_track":
                hi_val = max(
                    [source.get_bounds()[1] for source in xrange.sources]
                )
                if hi_val >= low and hi_val <= high:
                    xrange.set_bounds("track", "auto")
            elif xrange.default_state == "high_track":
                lo_val = min(
                    [source.get_bounds()[0] for source in xrange.sources]
                )
                if lo_val >= low and lo_val <= high:
                    xrange.set_bounds("auto", "track")

        if not self.constrain or self.constrain_direction == "y":
            high = yrange.high
            low = yrange.low
            if yrange.default_state == "low_track":
                hi_val = max(
                    [source.get_bounds()[1] for source in yrange.sources]
                )
                if hi_val >= low and hi_val <= high:
                    yrange.set_bounds("track", "auto")
            elif yrange.default_state == "high_track":
                lo_val = min(
                    [source.get_bounds()[0] for source in yrange.sources]
                )
                if lo_val >= low and lo_val <= high:
                    yrange.set_bounds("auto", "track")

        if self._auto_constrain:
            self.constrain = False
            self.constrain_direction = None
        self.event_state = "normal"
        event.window.set_pointer("arrow")
        if event.window.mouse_owner == self:
            event.window.set_mouse_owner(None)

        event.handled = True
