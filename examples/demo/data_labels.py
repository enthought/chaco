#!/usr/bin/env python
"""
Draws a line plot with several points labelled.  Demonstrates how to annotate
plots.

Left-drag pans the plot.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow and
alt-right-arrow moves you forwards and backwards through the "zoom history".
"""

# Major library imports
from numpy import arange
from scipy.special import jn

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import Float, HasTraits, Instance, Int
from traitsui.api import Item, View

# Chaco imports
from chaco.api import create_line_plot, add_default_axes, add_default_grids, \
                      OverlayPlotContainer, DataLabel
from chaco.example_support import COLOR_PALETTE
from chaco.tools.api import PanTool, ZoomTool, DataLabelTool


class PlotExample(HasTraits):
    plot = Instance(Component)
    numpoints = Int(100)
    low = Float(-5.0)
    high = Float(15.0)

    traits_view = View(Item('plot', editor=ComponentEditor(),
                            show_label=False),
                       width=800, height=700, resizable=True,
                       title="Data label example")

    def _plot_default(self):

        container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                         bgcolor = "lightgray", use_backbuffer=True)

        # Create the initial X-series of data
        numpoints = self.numpoints
        low = self.low
        high = self.high
        x = arange(low, high+0.001, (high-low)/numpoints)
        y = jn(0, x)
        plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[0]), width=2.0)
        plot.index.sort_order = "ascending"
        plot.bgcolor = "white"
        plot.border_visible = True
        add_default_grids(plot)
        add_default_axes(plot)

        # Add some tools
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Add a dynamic label.  This can be dragged and moved around using the
        # right mouse button.  Note the use of padding to offset the label
        # from its data point.
        label = DataLabel(component=plot, data_point=(x[40], y[40]),
                          label_position="top left", padding=40,
                          bgcolor = "lightgray",
                          border_visible=False)
        plot.overlays.append(label)
        tool = DataLabelTool(label, drag_button="right", auto_arrow_root=True)
        label.tools.append(tool)

        # Add some static labels.
        label2 = DataLabel(component=plot, data_point=(x[20], y[20]),
                           label_position="bottom right",
                           border_visible=False,
                           bgcolor="transparent",
                           marker_color="blue",
                           marker_line_color="transparent",
                           marker = "diamond",
                           font='modern 14',
                           arrow_visible=False)
        plot.overlays.append(label2)

        label3 = DataLabel(component=plot, data_point=(x[80], y[80]),
                           label_position="top", padding_bottom=20,
                           marker_color="transparent",
                           marker_size=8,
                           marker="circle",
                           arrow_visible=False)
        plot.overlays.append(label3)

        label4 = DataLabel(component=plot, data_point=(x[60], y[60]),
                           border_padding=10,
                           marker_color="red",
                           marker_size=3,
                           label_position=(20, 50),
                           label_style='bubble',
                           label_text="Something interesting",
                           label_format="at x=%(x).2f, y=%(y).2f",
                           font='modern 18',
                           bgcolor=(1, 1, 0.75, 1),
                          )
        plot.overlays.append(label4)
        tool4 = DataLabelTool(label4, drag_button="right", auto_arrow_root=True)
        label4.tools.append(tool4)

        label5 = DataLabel(component=plot, data_point=(x[65], y[65]),
                           border_padding=10,
                           marker_color="green",
                           marker_size=4,
                           show_label_coords=False,
                           label_style='bubble',
                           label_position=(25, 5),
                           label_text="Label with\narrow_min_length=20",
                           border_visible=False,
                           arrow_min_length=20,
                           font='modern 14',
                           bgcolor=(0.75, 0.75, 0.75, 1),
                          )
        plot.overlays.append(label5)
        tool5 = DataLabelTool(label5, drag_button="right", auto_arrow_root=True)
        label5.tools.append(tool5)

        container.add(plot)

        return container

demo = PlotExample()

if __name__ == "__main__":
    demo.configure_traits()
