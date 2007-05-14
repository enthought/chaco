#!/usr/bin/env python
"""
This demonstrates how to create a plot offscreen and save it to an image
file on disk.
"""

# Major library imports
from numpy import arange, fabs, pi, sin
from scipy.special import jn

# Enthought library imports
from enthought.kiva.backend_image import GraphicsContext
from enthought.traits.api import false, RGBAColor

# Chaco imports
from enthought.chaco2.api import OverlayPlotContainer, create_line_plot, \
                                 add_default_axes, add_default_grids

def create_plot():
    container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                     bgcolor = "lightgray")

    numpoints = 100
    low = -5
    high = 15.0
    x = arange(low, high+0.001, (high-low)/numpoints)
    
    # Plot some bessel functions
    value_mapper = None
    index_mapper = None
    for i in range(10):
        y = jn(i, x)
        plot = create_line_plot((x,y), color=(1.0-i/10.0,i/10.0,0,1), width=2.0,
                                index_sort="ascending")
        if i == 0:
            value_mapper = plot.value_mapper
            index_mapper = plot.index_mapper
            add_default_axes(plot)
            add_default_grids(plot)
        else:
            plot.value_mapper = value_mapper
            value_mapper.range.add(plot.value)
            plot.index_mapper = index_mapper
            index_mapper.range.add(plot.index)
        
        if i%2 == 1:
            plot.line_style = "dash"
        container.add(plot)

    return container


def draw_plot(filename, size=(800,600)):
    container = create_plot()
    container.bounds = list(size)
    container.do_layout(force=True)
    gc = GraphicsContext((size[0]+1, size[1]+1))
    container.draw(gc)
    gc.save(filename)
    return

if __name__ == "__main__":
    draw_plot("foo.png")

# EOF
