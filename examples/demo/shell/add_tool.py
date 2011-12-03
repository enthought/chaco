"""This example demonstrates customizing a plot object with a plot tool
using the chaco.shell subpackage.

The functions in the chaco.shell package allow us to quickly generate plots
with some basic interactivity without using the object-oriented core of Chaco.
"""

# Major library imports
from numpy import linspace, meshgrid, sin

# Enthought library imports
from chaco.shell import show, title, pcolor, colormap, curplot
from chaco.default_colormaps import jet

# Crate some scalar data
xs = linspace(0,10,200)
ys = linspace(0,20,400)
x,y = meshgrid(xs,ys)
z = sin(x)*y

# Create a pseudo-color-map
pcolor(x, y, z, name='sin_x_times_y')

# Change the color mapping
colormap(jet)

# Add some titles
title("pseudo colormap image plot")


# From the current plot object, grab the first plot
img_plot = curplot().plots['sin_x_times_y'][0]

# Add a custom tool - in this case, an ImageInspector
from chaco.tools.api import ImageInspectorTool, ImageInspectorOverlay

tool = ImageInspectorTool(img_plot)
img_plot.tools.append(tool)
overlay = ImageInspectorOverlay(img_plot, image_inspector=tool,
                                bgcolor="white", border_visible=True)
img_plot.overlays.append(overlay)


# If running this from the command line and outside of a wxPython
# application or process, the show() command is necessary to keep
# the plot from disappearing instantly.  If a wxPython mainloop
# is already running, then this command is not necessary.
show()
