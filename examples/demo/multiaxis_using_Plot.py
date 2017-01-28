#!/usr/bin/env python
"""
Draws some x-y line and scatter plots. On the left hand plot:
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from chaco.example_support import COLOR_PALETTE
# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import BroadcasterTool, PanTool, ZoomTool
from chaco.api import create_line_plot, add_default_axes

from traits.api import List
from chaco.tools.api import SelectedZoomState
import numpy

class CaeZoomTool(ZoomTool):
    zoom_tools = List


    def _end_select(self, event):
        """ Ends selection of the zoom region, adds the new zoom range to
        the zoom stack, and does the zoom.
        """
        self._screen_end = (event.x, event.y)

        start = numpy.array(self._screen_start)
        end = numpy.array(self._screen_end)

        if sum(abs(end - start)) < self.minimum_screen_delta:
            self._end_selecting(event)
            event.handled = True
            return
        self.do_zoom(self._screen_start, self._screen_end)

        for zoom_tool in self.zoom_tools:
            zoom_tool.do_zoom(self._screen_start, self._screen_end)
        self._end_selecting(event)
        event.handled = True


    def do_zoom(self, screen_start, screen_end):
        low, high = self._map_coordinate_box(screen_start, screen_end)

        x_range = self._get_x_mapper().range
        y_range = self._get_y_mapper().range

        prev = (x_range.low, x_range.high, y_range.low, y_range.high)

        if self.tool_mode == 'range':
            axis = self._determine_axis()
            if axis == 1:
                # vertical
                next = (x_range.low, x_range.high, low[1], high[1])
            else:
                # horizontal
                next = (low[0], high[0], y_range.low, y_range.high)

        else:
            next = (low[0], high[0], low[1], high[1])

        zoom_state = SelectedZoomState(prev, next)
        zoom_state.apply(self)
        self._append_state(zoom_state)
        return

#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index = x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i,x))

    # Create some line plots of some of the data
    plot1 = Plot(pd)
    plot1.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")

    # Tweak some of the plot properties
    plot1.title = "My First Line Plot"
    plot1.padding = 50
    plot1.padding_top = 75
    plot1.legend.visible = True

    x = linspace(-5, 15.0, 100)
    y = jn(5, x)
    foreign_plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[0]), width=2.0)
    left, bottom = add_default_axes(foreign_plot)
    left.orientation = "right"
    bottom.orientation = "top"
    plot1.add(foreign_plot)

    # Attach some tools to the plot
    broadcaster = BroadcasterTool()
    broadcaster.tools.append(PanTool(plot1))
    broadcaster.tools.append(PanTool(foreign_plot))
    broad_caster = None

    for c in (plot1, foreign_plot):
        zoom = CaeZoomTool(component=c, tool_mode="box", always_on=False)
        c.overlays.append(zoom)
        if broad_caster is None:
            print("OWNER", zoom)
            broad_caster = zoom
        else:
            print("WADDUP", zoom)
            broad_caster.zoom_tools.append(zoom)

    plot1.tools.append(broadcaster)

    return plot1

#===============================================================================
# Attributes to use for the plot view.
size=(900,500)
title="Multi-Y plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title,
                    width=size[0], height=size[1]
                    )

    def _plot_default(self):
         return _create_plot_component()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
