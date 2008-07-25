
# Mayor Library imports
from numpy import linspace, pi, sin, cos

# Enthought library imports
from enthought.chaco.shell import plot, hold, title, show


# Create some data
x = linspace(-2*pi, 2*pi, 100)
y1 = sin(x)
y2 = cos(x)

# Create some line plots
plot(x, y1, "b-", bgcolor="white")
hold()
plot(x, y2, "g-.", marker_size=2)

# Add some titles
title("simple line plots")

#This command is only necessary if running from command line
show()

