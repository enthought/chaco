#!/usr/bin/env python
"""
This demonstrates how to create a plot offscreen and save it to an image
file on disk.
"""
# Standard library imports
import os, sys

# Major library imports
from numpy import fabs, linspace, pi, sin
from scipy.special import jn

# Enthought library imports
from enthought.traits.api import false

# Chaco imports
from enthought.chaco2.api import ArrayPlotData, Plot, PlotGraphicsContext
from enthought.chaco2.example_support import COLOR_PALETTE

DPI = 72.0

# This is a bit of a hack, to work around the fact that line widths don't scale
# with the GraphicsContext's CTM.
dpi_scale = DPI / 72.0

def create_plot():
    numpoints = 100
    low = -5
    high = 15.0
    x = linspace(low, high, numpoints)
    pd = ArrayPlotData(index=x)
    p = Plot(pd, bgcolor="lightgray", padding=50, border_visible=True)
    for i in range(10):
        pd.set_data("y" + str(i), jn(i,x))
        p.plot(("index", "y" + str(i)), color=tuple(COLOR_PALETTE[i]),
               width = 2.0 * dpi_scale)
    p.x_grid.visible = True
    p.x_grid.line_width *= dpi_scale
    p.y_grid.visible = True
    p.y_grid.line_width *= dpi_scale
    p.legend.visible = True
    return p

def draw_plot(filename, size=(800,600)):
    container = create_plot()
    container.outer_bounds = list(size)
    container.do_layout(force=True)
    gc = PlotGraphicsContext(size, dpi=DPI)
    gc.render_component(container)
    gc.save(filename)
    return

def draw_pdf(filename, size=(800,600)):
    from enthought.chaco2.pdf_graphics_context import PdfPlotGraphicsContext
    container = create_plot()
    container.bounds = list(size)
    container.do_layout(force=True)
    gc = PdfPlotGraphicsContext(filename=filename, dest_box = (0.5, 0.5, 5.0, 5.0))
    gc.render_component(container)
    gc.save()
    
def get_directory(filename):
    print 'Please enter a path in which to place generated plots.'
    print 'Press <ENTER> to generate in the current directory.'
    path = raw_input('Path: ').strip()
    
    if len(path) > 0 and not os.path.exists(path):
        print 'The given path does not exist.'
        sys.exit()
        
    if not os.path.isabs(path):
        print 'Creating image: ' + os.path.join(os.getcwd(), path, filename)
    else:
        print 'Creating image: ' + os.path.join(path, filename)
            
    return os.path.join(path, filename)
        

if __name__ == "__main__":
    draw_plot(get_directory('noninteractive.png'), size=(800, 600))
    
    # If you have ReportLab installed, you can uncomment the following:
    #draw_pdf(get_directory('noninteractive.pdf'))

# EOF
