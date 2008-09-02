
.. _tutorial_1:

###############################
Interactive Plotting with Chaco
###############################

Overview
========

This tutorial is an introduction to Chaco.  We're going to build several mini-applications
of increasing capability and complexity.  Chaco was designed to be primarily used by
scientific programmers, and this tutorial only requires basic familiarity with Python.

Knowledge of numpy can be helpful for certain parts of the tutorial.  Knowledge of
GUI programming concepts such as widgets, windows, and events will be helpful for
the last portion of the tutorial, but it is not required.

This tutorial will demonstrate using Chaco with Traits UI, so knowledge of the Traits
framework will also be helpful.  We don't use very many sophisticated aspects of
Traits or Traits UI, and it is entirely possible to pick it up as you go through
the tutorial.

It's also worth pointing out that you don't *have* to use Traits UI in order to
use Chaco - you can integrate Chaco directly with Qt or wxPython - but for this
tutorial, we will be using Traits UI to make things easier.

.. contents::


Goals
=====

By the end of this tutorial, you will have learned how to:

    - create Chaco plots of various types
    - arrange plots of data items in various layouts
    - configure and interact with your plots using Traits UI
    - create a custom plot overlay
    - create a custom tool that interacts with the mouse


Introduction
============

Chaco is a *plotting application toolkit*.  This means that it is used to build
both statis plots as well as dynamic data visualizations that let you interactively
explore your data.  Here are four basic examples of Chaco plots:

.. image:: images/tornado.png

This plot shows a static "tornado plot" with a categorical Y axis and continuous
X axis.  The plot is resizable, but the user cannot interact or explore the data
in any way.

.. image:: images/simple_line.png

This is an overlaid composition of line and scatter plots with a legend.  Unlike
the previous plot, the user can pan and zoom this plot, exploring the relationship
between data curves in areas that appear densely overlapping.  Furthermore, the user
can move the legend to an arbitrary position on the plot, and as they resize the plot,
the legend will maintain the same screen-space separation relative to its closest
corner.

.. image:: images/regression.png

This example starts to demonstrate interacting with the dataset in an
exploratory way.  Whereas interactivity in the previous example was limited to
basic pan and zoom (which are fairly common in most plotting libraries), this is
an example of a more advanced interaction that allows a level of data exploration
beyond the standard view manipuations.

With this example, the user can select a region of data space, and a simple
line fit is applied to the selected points.  The equation of the line is
then displayed in a text label.

The lasso selection tool and regression overlay are both built in to Chaco,
but they also serve a dual purpose of demonstrating how one can build complex
data-centric interactions and displays on top of the Chaco framework.

.. image:: images/scalar_function.png

(TODO)

Script-oriented Plotting
========================

We distinguish between "static" plots and "interactive visualizations"
because these different applications of a library affect the structure
of how the library is written, as well as the code you write to use the
library.

Here is a simple example of the "script-oriented" approach for building up
a static plot.  This will be familiar to anyone who has used Gnuplot,
MATLAB, or Matplotlib::

    from numpy import *
    from enthought.chaco.shell import *

    x = linspace(-2*pi, 2*pi, 100)
    y = sin(x)

    plot(x, y, "r-")
    title("First plot")
    ytitle("sin(x)")
    show()

.. image::images/script_oriented.png

The basic structure is that we generate some data, then we call functions to plot the data and configure the plot.  There is a global concept of "the active plot", and the functions do high-level manipulations on it.  The generated plot is then
usually saved to disk for inclusion in a journal article or presentation slides.

Now, as it so happens, this particular example uses the chaco.shell script plotting package, so when you run this script, the plot that Chaco pops up does have some basic interactivity.  You can pan and zoom, and even move forwards and backwards through your zoom history.  But ultimately it's a pretty static view into the data.


Application-oriented Plotting
=============================

The second approach to plotting can be thought of as "application-oriented", for
lack of a better term.  There is definitely a bit more code, and the plot initially doesn't look much different, but it sets us up to do more interesting things, as you'll see later on::

    class LinePlot(HasTraits):
        plot = Instance(Plot)
        traits_view = View(
            Item('plot',editor=ComponentEditor(),
                 show_label=False), 
            width=500, height=500,
            resizable=True,
            title="Chaco Plot")

        def __init__(self):
            x = linspace(-14, 14, 100)
            y = sin(x) * x**3
            plotdata = ArrayPlotData(x = x, y = y)
            plot = Plot(plotdata)
            plot.plot(("x", "y"), type="line",
                      color="blue")
            plot.title = "sin(x) * x^3"
            self.plot = plot

    if __name__ == "__main__":
        LinePlot().configure_traits()

This produces a plot similar to the previous script-oriented code snippet:

.. image::images/first_plot.png

So, this is our first "real" Chaco plot, and we'll walk through this code and
look at what each bit does.  This example serves as the basis for many of the
later examples.

Understanding the First Plot
============================

We'll start with the basics.  First, we declare a class to represent our
class, called "LinePlot"::

    class LinePlot(HasTraits):
        plot = Instance(Plot)

This class uses the Enthought Traits package, so we subclass from 
:class:`HasTraits`. 


