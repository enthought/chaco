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

from chaco.api import Plot, ArrayPlotData, jet
from chaco.tools.api import PanTool, ZoomTool
from chaco.overlays.coordinate_line_overlay import CoordinateLineOverlay


class PlotExample(HasTraits):

    # 1D arrays of coordinates where a line should be drawn.
    x1 = Array(dtype=np.float64)
    y1 = Array(dtype=np.float64)
    x2 = Array(dtype=np.float64)
    y2 = Array(dtype=np.float64)

    image_plot = Instance(Plot)

    image_plot_data = Instance(ArrayPlotData)

    # These is used in `time_plot` to mark special times.
    line_overlay1 = Instance(CoordinateLineOverlay)
    line_overlay2 = Instance(CoordinateLineOverlay)

    traits_view = \
        View(
            HGroup(
                UItem('image_plot', editor=ComponentEditor(height=20)),
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
        return np.array([-np.pi, np.pi])

    def _x2_default(self):
        return np.array([np.pi/2.0])

    def _y2_default(self):
        return np.array([np.pi])

    def _image_plot_data_default(self):
        xbounds = (-2*np.pi, 2*np.pi, 600)
        ybounds = (-1.5*np.pi, 1.5*np.pi, 300)
        xs = np.linspace(*xbounds)
        ys = np.linspace(*ybounds)
        x, y = np.meshgrid(xs,ys)
        z = np.sin(x)*y
        data = ArrayPlotData(x=x, y=y, z=z)
        return data

    def _image_plot_default(self):
        image_plot = Plot(self.image_plot_data)

        renderer=image_plot.img_plot('z', xbounds=(-2*np.pi, 2*np.pi),
                           ybounds=(-1.5*np.pi, 1.5*np.pi),
                           colormap=jet)[0]

        image_plot.index_axis.title = "Time"

        image_plot.tools.append(PanTool(image_plot))

        zoomtool = ZoomTool(image_plot, drag_button='right',
                                                    always_on=True)
        image_plot.overlays.append(zoomtool)

        lines1 = CoordinateLineOverlay(component=renderer,
                    index_data=self.x1,
                    value_data=self.y1,
                    color=(0.75, 0.25, 0.25, 0.75),
                    line_style='dash', line_width=1)
        renderer.underlays.append(lines1)
        self.line_overlay1 = lines1

        lines2 = CoordinateLineOverlay(component=image_plot,
                    index_data=self.x2,
                    value_data=self.y2,
                    color=(0.2, 0.5, 1.0, 0.75),
                    line_width=3)
        image_plot.underlays.append(lines2)
        self.line_overlay2 = lines2

        return image_plot


demo = PlotExample()


if __name__ == "__main__":
    ##demo.edit_traits()
    demo.configure_traits()
