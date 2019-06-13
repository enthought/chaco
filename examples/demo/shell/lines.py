"""
This example displays some line plots in different colors and styles using
the chaco.shell subpackage.

The functions in the chaco.shell package allow us to quickly generate plots
with some basic interactivity without using the object-oriented core of Chaco.
"""

from numpy import linspace, pi, sin, cos
from chaco.shell import plot, hold, title, show

# Create some data
x = linspace(-2*pi, 2*pi, 100)
y1 = sin(x)
y2 = cos(x)

# Create some line plots using the plot() command and using
# Matlab-style format specifiers
plot(x, y1, "b-", bgcolor="white")
hold()
plot(x, y2, "g-.", marker_size=2)

# Set the plot title
title("simple line plots")

# If running this from the command line and outside of a wxPython
# application or process, the show() command is necessary to keep
# the plot from disappearing instantly.  If a wxPython mainloop
# is already running, then this command is not necessary.
show()
