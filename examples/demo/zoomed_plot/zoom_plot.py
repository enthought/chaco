"""
The main executable file for the zoom_plot demo.

Right-click and drag on the upper plot to select a region to view in detail
in the lower plot.  The selected region can be moved around by dragging,
or resized by clicking on one of its edges and dragging. The ZoomPlot class
encapsulates the creation of a zoom plot and exposes some of the attributes and
methods necessary for deep interaction with the plot.
"""
# Standard library imports
import os

# Major library imports
from numpy import sin, pi, linspace

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View
from traits.util.resource import find_resource

# Chaco imports
from chaco.api import VPlotContainer, ArrayPlotData, Plot, PlotGrid, PlotAxis
from chaco.tools.api import RangeSelection

# Relative imports
from .zoom_overlay import ZoomOverlay

sample_path = os.path.join("examples", "data", "sample.wav")
alt_path = os.path.join("..", "data", "sample.wav")
fname = find_resource(
    "Chaco", sample_path, alt_path=alt_path, return_path=True
)
numpts = 3000


def read_music_data():
    from .wav_to_numeric import wav_to_numeric

    index, data = wav_to_numeric(fname)
    return index[:numpts], data[:numpts]


class ZoomPlot(HasTraits):
    """Encapsulation of the zoom plot concept.

    This class organzies the data, plot container and ZoomOverlay required for
    a zoom plot. ZoomPlot represents the first step towards a reusable and
    extensible generalization of the zoom plot.

    """

    data = Instance(ArrayPlotData)

    plot = Instance(Component)

    def update_data(self, x, y):
        """Update the data in the plot windows"""
        # FIXME: This isn't forcing the update, so the crufty code below is used.
        # self.plot.data['x'] = x
        # self.plot.data['y'] = y
        self.plot.components[0].index.set_data(x)
        self.plot.components[0].value.set_data(y)
        self.plot.components[1].index.set_data(x)
        self.plot.components[1].value.set_data(y)

    def _data_default(self):
        x = linspace(0, 4 * pi, 1201)
        y = sin(x ** 2)

        data = ArrayPlotData(x=x, y=y)

        return data

    def _plot_default(self):
        plotter = Plot(data=self.data)
        main_plot = plotter.plot(["x", "y"])[0]
        self.configure_plot(main_plot, xlabel="")

        plotter2 = Plot(data=self.data)
        zoom_plot = plotter2.plot(["x", "y"])[0]
        self.configure_plot(zoom_plot)

        outer_container = VPlotContainer(
            padding=20,
            fill_padding=True,
            spacing=0,
            stack_order="top_to_bottom",
            bgcolor="lightgray",
            use_backbuffer=True,
        )

        outer_container.add(main_plot)
        outer_container.add(zoom_plot)
        # FIXME: This is set to the windows bg color.  Should get from the system.
        # outer_container.bgcolor = (236/255., 233/255., 216/255., 1.0)

        main_plot.controller = RangeSelection(main_plot)

        zoom_overlay = ZoomOverlay(source=main_plot, destination=zoom_plot)
        outer_container.overlays.append(zoom_overlay)

        return outer_container

    @staticmethod
    def configure_plot(plot, xlabel="Time (s)"):
        """Set up colors, grids, etc. on plot objects."""
        plot.bgcolor = "white"
        plot.border_visible = True
        plot.padding = [40, 15, 15, 20]
        plot.color = "darkred"
        plot.line_width = 1.1

        vertical_grid = PlotGrid(
            component=plot,
            mapper=plot.index_mapper,
            orientation="vertical",
            line_color="gray",
            line_style="dot",
        )

        horizontal_grid = PlotGrid(
            component=plot,
            mapper=plot.value_mapper,
            orientation="horizontal",
            line_color="gray",
            line_style="dot",
        )

        vertical_axis = PlotAxis(orientation="left", mapper=plot.value_mapper)

        horizontal_axis = PlotAxis(
            orientation="bottom",
            title=xlabel,
            mapper=plot.index_mapper,
        )

        plot.underlays.append(vertical_grid)
        plot.underlays.append(horizontal_grid)

        # Have to add axes to overlays because we are backbuffering the main plot,
        # and only overlays get to render in addition to the backbuffer.
        plot.overlays.append(vertical_axis)
        plot.overlays.append(horizontal_axis)


# ===============================================================================
# Attributes to use for the plot view.
size = (800, 600)
title = fname

# ===============================================================================
# # Demo class that is used by the demo.py application.
# ===============================================================================
class ZoomPlotView(HasTraits):

    zoom_plot = Instance(ZoomPlot, ())

    traits_view = View(
        Group(
            Item(
                "object.zoom_plot.plot",
                editor=ComponentEditor(size=size),
                show_label=False,
            ),
            orientation="vertical",
        ),
        resizable=True,
        title="Zoom Plot",
        width=size[0],
        height=size[1],
    )


demo = ZoomPlotView()
# Configure the zoom plot by giving it data
try:
    x, y = read_music_data()
    demo.zoom_plot.update_data(x, y)
except:
    # Use the defaults
    pass

if __name__ == "__main__":
    demo.configure_traits()
