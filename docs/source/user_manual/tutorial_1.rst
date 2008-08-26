
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

.. image:: images/scalar_function.png

