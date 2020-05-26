"""
This example demonstrates using dates as labels for the axis ticks using
the chaco shell subpackage.

Try zooming in and out using the mouse wheel and see the resolution of
the dates gradually changing from days to years.
"""

# Major library imports
from numpy import linspace, pi, sin

# Enthought library imports
from chaco.shell import show, plot, title, curplot
from chaco.scales.api import CalendarScaleSystem

# Create some data
numpoints = 100
x = linspace(-2*pi, 2*pi, numpoints)
y1 = sin(x)

# Create the dates
import time
now = time.time()
dt = 24 * 3600    # data points are spaced by 1 day
dates = linspace(now, now + numpoints*dt, numpoints)

# Create some line plots
plot(dates, y1, "b-", bgcolor="white")

# Add some titles
title("Plotting Dates")

current_plot = curplot()
# Set the plot's horizontal axis to be a time scale
current_plot.x_axis.tick_generator.scale = CalendarScaleSystem()
zoom_tool = current_plot.overlays[2]
pan_tool = current_plot.tools[0]
zoom_tool.x_min_zoom_factor = float(1e-3)
pan_tool.restrict_to_data = True


# This command is only necessary if running from command line
show()

