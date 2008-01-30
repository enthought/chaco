#!/usr/bin/env python
"""
Allows editing of a line plot.

Left-dragging a point will move its position.

Right-drag pans the plot.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow and
alt-right-arrow moves you forwards and backwards through the "zoom history".
"""

# Major library imports
from numpy import linspace
from scipy.special import jn

from enthought.chaco2.example_support import DemoFrame, demo_main, COLOR_PALETTE

# Enthought library imports
from enthought.enable2.api import Window
from enthought.enable2.tools.api import DragTool
from enthought.traits.api import Instance, Int, Tuple

# Chaco imports
from enthought.chaco2.api import add_default_axes, add_default_grids, \
        OverlayPlotContainer, PlotLabel, ScatterPlot, create_line_plot, \
        PlotComponent
from enthought.chaco2.tools.api import PanTool, SimpleZoom



class PointDraggingTool(DragTool):
    
    component = Instance(PlotComponent)

    # The pixel distance from a point that the cursor is still considered
    # to be 'on' the point
    threshold = Int(5)

    # The index of the point being dragged
    _drag_index = Int(-1)

    # The original dataspace values of the index and value datasources
    # corresponding to _drag_index
    _orig_value = Tuple

    def is_draggable(self, x, y):
        # Check to see if (x,y) are over one of the points in self.component
        if self._lookup_point(x, y) is not None:
            return True
        else:
            return False

    def normal_mouse_move(self, event):
        plot = self.component
        
        ndx = plot.map_index((event.x, event.y), self.threshold)
        if ndx is None:
            if plot.index.metadata.has_key('selections'):
                del plot.index.metadata['selections']
        else:
            plot.index.metadata['selections'] = [ndx]

        plot.invalidate_draw()
        plot.request_redraw()


    def drag_start(self, event):
        plot = self.component
        ndx = plot.map_index((event.x, event.y), self.threshold)
        if ndx is None:
            return
        self._drag_index = ndx
        self._orig_value = (plot.index.get_data()[ndx], plot.value.get_data()[ndx])

    def dragging(self, event):
        plot = self.component

        data_x, data_y = plot.map_data((event.x, event.y))

        plot.index._data[self._drag_index] = data_x
        plot.value._data[self._drag_index] = data_y
        plot.index.data_changed = True
        plot.value.data_changed = True
        plot.request_redraw()

    def drag_cancel(self, event):
        plot = self.component
        plot.index._data[self._drag_index] = self._orig_value[0]
        plot.value._data[self._drag_index] = self._orig_value[1]
        plot.index.data_changed = True
        plot.value.data_changed = True
        plot.request_redraw()

    def drag_end(self, event):
        plot = self.component
        if plot.index.metadata.has_key('selections'):
            del plot.index.metadata['selections']
        plot.invalidate_draw()
        plot.request_redraw()

    def _lookup_point(self, x, y):
        """ Finds the point closest to a screen point if it is within self.threshold
        
        Parameters
        ==========
        x : float
            screen x-coordinate
        y : float
            screen y-coordinate

        Returns
        =======
        (screen_x, screen_y, distance) of datapoint nearest to the input *(x,y)*.
        If no data points are within *self.threshold* of *(x,y)*, returns None.
        """

        if hasattr(self.component, 'get_closest_point'):
            # This is on BaseXYPlots
            return self.component.get_closest_point((x,y), threshold=self.threshold)

        return None



class PlotFrame(DemoFrame):
    def _create_window(self):
        container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                         bgcolor = "lightgray", use_backbuffer=True)
        self.container = container

        # Create the initial X-series of data
        numpoints = 30
        low = -5
        high = 15.0
        x = linspace(low, high, numpoints)
        y = jn(0, x)

        lineplot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[0]), width=2.0)
        lineplot.selected_color = "none"
        scatter = ScatterPlot(index = lineplot.index,
                           value = lineplot.value,
                           index_mapper = lineplot.index_mapper,
                           value_mapper = lineplot.value_mapper,
                           color = tuple(COLOR_PALETTE[0]),
                           marker_size = 5)
        scatter.index.sort_order = "ascending"

        scatter.bgcolor = "white"
        scatter.border_visible = True
        
        add_default_grids(scatter)
        add_default_axes(scatter)

        scatter.tools.append(PanTool(scatter, drag_button="right"))
        
        # The SimpleZoom tool is stateful and allows drawing a zoom
        # box to select a zoom region.
        zoom = SimpleZoom(scatter, tool_mode="box", always_on=False, drag_button=None)
        scatter.overlays.append(zoom)

        scatter.tools.append(PointDraggingTool(scatter))

        container.add(lineplot)
        container.add(scatter)

        # Add the title at the top
        container.overlays.append(PlotLabel("Bessel functions",
                                  component=container,
                                  font = "swiss 16",
                                  overlay_position="top"))

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,700), title="Simple line plot")

# EOF
