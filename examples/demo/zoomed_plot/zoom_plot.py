"""
The main executable file for the zoom_plot demo.

Right-click and drag on the upper plot to select a region to view in detail
in the lower plot.  The selected region can be moved around by dragging,
or resized by clicking on one of its edges and dragging.
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
from chaco.api import VPlotContainer
from chaco.tools.api import RangeSelection

# Relative imports
from grid_plot_factory import create_gridded_line_plot
from zoom_overlay import ZoomOverlay

sample_path = os.path.join('examples','data','sample.wav')
alt_path = os.path.join('..','data','sample.wav')
fname = find_resource('Chaco', sample_path, alt_path=alt_path,
    return_path=True)
numpts = 3000

def read_music_data():
    from wav_to_numeric import wav_to_numeric
    index, data = wav_to_numeric(fname)
    return index[:numpts], data[:numpts]

def create_zoomed_plot():
    try:
        x,y = read_music_data()
    except:
        x = linspace(-10*pi, 10*pi, numpts)
        y = sin(x)

    main_plot = create_gridded_line_plot(x,y)
    zoom_plot = create_gridded_line_plot(x,y)

    outer_container = VPlotContainer(padding=30,
                                     fill_padding=True,
                                     spacing=50,
                                     stack_order='top_to_bottom',
                                     bgcolor='lightgray',
                                     use_backbuffer=True)

    outer_container.add(main_plot)
    outer_container.add(zoom_plot)

    main_plot.controller = RangeSelection(main_plot)

    zoom_overlay = ZoomOverlay(source=main_plot, destination=zoom_plot)
    outer_container.overlays.append(zoom_overlay)

    return outer_container

#===============================================================================
# Attributes to use for the plot view.
size = (800, 600)
title = fname

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
         return create_zoomed_plot()

demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()

#--EOF---
