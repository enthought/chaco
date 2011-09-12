"""Demonstrate a simple polygon plot.  The UI allows you to change
some of the attributes of the plot.
"""

import numpy as np

from traits.api import HasTraits, Instance, Range
from traitsui.api import View, UItem, Item, Group, HGroup, VGroup, spring
from chaco.api import Plot, ArrayPlotData, PolygonPlot
from enable.api import ComponentEditor, LineStyle


class PolygonPlotDemo(HasTraits):

    # The main plot container.
    plot = Instance(Plot)

    # Data holder for `plot`.
    apd = Instance(ArrayPlotData)

    # The polygon plot renderer.
    polygon_plot = Instance(PolygonPlot)

    # Assorted styles that will be set on `polygon_plot`.    
    edge_style = LineStyle
    edge_width = Range(value=1, low=0, high=8)
    edge_alpha = Range(value=1.0, low=0.0, high=1.0)
    face_alpha = Range(value=0.4, low=0.0, high=1.0)
    alpha = Range(value=1.0, low=0.0, high=1.0)

    traits_view = \
        View(
            VGroup(
                Group(
                    UItem('plot', editor=ComponentEditor(), style='custom'),
                ),
                VGroup(
                    HGroup(
                        Item('edge_style'),
                        spring,
                    ),
                    Item('edge_width'),
                    Item('edge_alpha'),
                    Item('face_alpha'),
                    Item('alpha'),
                ),
            ),
            resizable=True,
        )

    #----------------------------------------------------------------------
    # Default values
    #----------------------------------------------------------------------

    def _apd_default(self):
        # Create the data to plot.
        px = np.array([0.5, 1.0, 2.0, 2.5, 2.0, 1.5, 0.5, 0.0])
        py = np.array([0.0, 0.8, 0.5, 3.0, 3.5, 2.0, 3.0, 0.5])

        # Create the ArrayPlotData container used by the Plot.
        apd = ArrayPlotData(px=px, py=py)
        return apd

    def _plot_default(self):
        plot = Plot(self.apd, title='PolygonPlot Demo')
        return plot

    def _polygon_plot_default(self):
        p = self.plot.plot(('px', 'py'),
                  type='polygon',
                  face_color=(0,0.8,1) + (self.face_alpha,),
                  edge_color=(0,0,0) + (self.edge_alpha,),
                  edge_style=self.edge_style,
                  alpha=self.alpha)
        return p[0]

    #----------------------------------------------------------------------
    # Trait change handlers
    #----------------------------------------------------------------------

    def _edge_style_changed(self):
        self.polygon_plot.edge_style = self.edge_style

    def _edge_width_changed(self):
        self.polygon_plot.edge_width = self.edge_width

    def _edge_alpha_changed(self):
        self.polygon_plot.edge_color = self.polygon_plot.edge_color[:3] + (self.edge_alpha,)

    def _face_alpha_changed(self):
        self.polygon_plot.face_color = self.polygon_plot.face_color[:3] + (self.face_alpha,)

    def _alpha_changed(self):
        self.polygon_plot.alpha = self.alpha


demo = PolygonPlotDemo()
# Hack to force initial rendering of the plot.
demo.face_alpha = 0.5


if __name__ == "__main__":
    demo.configure_traits()
