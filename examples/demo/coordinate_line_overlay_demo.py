"""
Demonstration of the Chaco overlay CoordinateLineOverlay.

A CoordinateLineOverlay is a Chaco overlay that draws "infinite"
vertical and horizontal lines in a Chaco Plot.  In this demo,
two instances of CoordinateLineOverlay are added to the overlays
of a Plot containing a single line plot.

Zoom out, pan around, and notice that the blue solid lines and
the red dashed lines are always drawn all the way across the
window.  They do not have end points.
"""

import numpy as np

from traits.api import HasTraits, Instance, Array
from traitsui.api import View, HGroup, UItem

from enable.api import ComponentEditor

from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import PanTool, ZoomTool
from chaco.overlays.coordinate_line_overlay import CoordinateLineOverlay


class PlotExample(HasTraits):

    # 1D arrays of coordinates where a line should be drawn.
    x1 = Array(dtype=np.float64)
    y1 = Array(dtype=np.float64)
    x2 = Array(dtype=np.float64)
    y2 = Array(dtype=np.float64)

    time_plot = Instance(Plot)

    time_plot_data = Instance(ArrayPlotData)

    # These is used in `time_plot` to mark special times.
    line_overlay1 = Instance(CoordinateLineOverlay)
    line_overlay2 = Instance(CoordinateLineOverlay)

    traits_view = \
        View(
            HGroup(
                UItem('time_plot', editor=ComponentEditor(height=20)),
            ),
            title="Demo",
            width=1000, height=640, resizable=True,
        )

    #------------------------------------------------------------------------
    # Trait change handlers
    #------------------------------------------------------------------------

    def _x1_changed(self):
        self.line_overlay1.index_data = self.x1

    def _y1_changed(self):
        self.line_overlay1.value_data = self.y1

    def _x2_changed(self):
        self.line_overlay2.index_data = self.x2

    def _y2_changed(self):
        self.line_overlay2.value_data = self.y2

    #------------------------------------------------------------------------
    # Trait defaults
    #------------------------------------------------------------------------

    def _x1_default(self):
        return np.array([1.8, 8.4])

    def _x2_default(self):
        return np.array([3.25])

    def _y2_default(self):
        return np.array([5.25])

    def _time_plot_data_default(self):
        t = np.linspace(0, 10, 201)
        y = (0.5 * t + 0.1 * np.sin(0.4 * 2 * np.pi * t) +
                0.3 * (t + 2) * (8 - t) * np.cos(0.33 * 2 * np.pi * t))
        data = ArrayPlotData(t=t, y=y)
        return data

    def _time_plot_default(self):
        time_plot = Plot(self.time_plot_data)

        time_plot.plot(('t', 'y'))

        time_plot.index_axis.title = "Time"

        time_plot.tools.append(PanTool(time_plot))

        zoomtool = ZoomTool(time_plot, drag_button='right',
                                                    always_on=True)
        time_plot.overlays.append(zoomtool)

        lines1 = CoordinateLineOverlay(component=time_plot,
                    index_data=self.x1,
                    value_data=self.y1,
                    color=(0.75, 0.25, 0.25, 0.75),
                    style='dash', width=1)
        time_plot.underlays.append(lines1)
        self.line_overlay1 = lines1

        lines2 = CoordinateLineOverlay(component=time_plot,
                    index_data=self.x2,
                    value_data=self.y2,
                    color=(0.2, 0.5, 1.0, 0.75),
                    width=3)
        time_plot.underlays.append(lines2)
        self.line_overlay2 = lines2

        return time_plot


demo = PlotExample()


if __name__ == "__main__":
    ##demo.edit_traits()
    demo.configure_traits()
