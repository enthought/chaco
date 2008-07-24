
# Mayor Library imports
from numpy import linspace, random, pi

# Enthought library imports
from enthought.chaco2.shell import plot, hold, title, show


# Create some data
x = linspace(-2*pi, 2*pi, 100)
y1 = random.random(100)
y2 = random.random(100)

# Create some scatter plots
plot(x, y1, "b.")
hold()
plot(x, y2, "g+", marker_size=2)

# Add some titles
title("simple scatter plots")

# This command is only necessary if running from command line
show()

