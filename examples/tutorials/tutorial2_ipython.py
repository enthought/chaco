#!/usr/bin/env python

"""
Tutorial 2 (IPython) - Getting at our first plot using IPython


This addendum to Tutorial 2 demonstrates the dynamic nature of the various
components in Chaco.

To run this tutorial, change to the directory where this file is located,
then invoke IPython:

  ipython -wthread

Then just run this tutorial:

  run tutorial2_ipython.py

Once this executes, you will have a Chaco plot window open, and all of the
functions defined in this file will be available at the IPython prompt.
(The "frame" and "plot" variables will also be defined.)

You can configure some aspects of your plot by using the functions.
"""

from tutorial2 import PlotFrame

# Create the frame with no parent and a default size
frame = PlotFrame(None)

# Grab a reference to the plot object and expose it as a module-wide global.
plot = frame.plot_window.component


def xtitle(text):
    plot.x_axis.title = text
    plot.request_redraw()

def ytitle(text):
    plot.y_axis.title = text
    plot.request_redraw()

def xrange(low, high):
    plot.x_mapper.range.low = low
    plot.x_mapper.range.high = high
    plot.request_redraw()

def yrange(low, high):
    plot.y_mapper.range.low = low
    plot.y_mapper.range.high = high
    plot.request_redraw()


