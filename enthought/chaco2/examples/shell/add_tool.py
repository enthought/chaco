# Like pcolor.py, except demonstrates how a chaco2.shell plot object ca
# be customized by adding a tool and overlay.

# imports
from numpy import *
from enthought.chaco2.shell import *
from enthought.chaco2.default_colormaps import *

# Crate some scalar data
xs = linspace(0,10,200); 
ys = linspace(0,20,400); 
x,y=meshgrid(xs,ys); 
z = sin(x)*y

# Create a pseudo-color-map
pcolor(x,y,z)

#change the color mapping
colormap(jet)

# Add some titles
title("pseudo colormap image plot")

# Add a custom tool - in this case, an ImageInspector
from enthought.chaco2.tools.api import ImageInspectorTool, ImageInspectorOverlay
img_plot = curplot().plots.values()[0][0]
tool = ImageInspectorTool(img_plot)
img_plot.tools.append(tool)
overlay = ImageInspectorOverlay(img_plot, image_inspector=tool,
                                bgcolor="white", border_visible=True)
img_plot.overlays.append(overlay)

#This command is only necessary if running from command line
show()
