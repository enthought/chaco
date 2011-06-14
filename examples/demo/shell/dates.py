
# Mayor Library imports
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

# Set the plot's horizontal axis to be a time scale
curplot().x_axis.tick_generator.scale = CalendarScaleSystem()

#This command is only necessary if running from command line
show()

