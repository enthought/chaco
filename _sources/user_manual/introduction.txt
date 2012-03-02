************
Introduction
************

==============
What is Chaco?
==============

Chaco is a 2D plotting library that is part of and integrates with
the Enthought Tools Suite.

The strong points of Chaco are

1. it can be :ref:`embedded <embedding>` in any wx, Qt, or TraitsUI application

2. it is designed for building interactive plotting applications, rather than
   static 2D plots

3. Chaco classes can be easily extended to create new plot types,
   interactive tools, and plot containers


At the lowest level, Chaco is a hierarchy of classes that defines
2D plotting elements: plots, containers, interactive tools, color bars, etc.
In principle, applications can create instances of these elements and lay them
out in a container to define components that can be :ref:`embedded in one
of several of graphical back ends <embedding>`. Working at this level allows the
maximum flexibility, but requires understanding
:ref:`Chaco's basic elements <basic_elements>`.

Chaco defines two abstraction layers that allow a more high-level
(albeit less flexible) plotting experience. First, Chaco contains a
:class:`~chaco.plot.Plot`
class that defines several methods that create a complete plot given one or
more data sets. In other words, :class:`~chaco.plot.Plot` knows how to
package data for the most common kinds of plots. Second, Chaco has a
:mod:`shell` module that defines high-level plotting functions. This module
allows using Chaco as an interactive plotting tool that will be familiar
to users of matplotlib.

.. _basic_elements:

==============
Basic elements
==============

To venture deeper in Chaco's architecture it is useful to understand a few
basic ideas on which Chaco is based:

* **Plots are compositions of visual components**

  Each plot is composed by a number of graphical widgets:
  the plot graphics, axes, labels, legend, colorbar, etc.
  Everything you see in a plot is an individual component
  with position, shape, and appearance attributes, and with an
  opportunity to respond to events.

* **Data and screen space are separated**

  Although everything in a plot eventually ends up rendering into a common
  visual area, there are aspects of the plot which are intrinsically
  screen-space, and some which are fundamentally data-space. For example,
  data about the height of college students lives in data space (meters),
  but needs to be rendered in screen space (pixels). Chaco uses the
  concept of *mapper* to translate one into the other.
  Preserving the distinction between these two domains allows us to think about
  visualizations in a structured way.

* **Layers**

  Plot components are split into several layers, which are usually plotted
  in sequence. For example, axes and labels are usually plotted on the
  "underlay" layer, plot data on the "plot" layer, and legends and other
  plot annotations on the "overlay" layer. In this way one can define
  interactive tools that add graphical elements to a plot without
  having to modify the drawing logic.


The next sections describe in detail the basic building blocks of
Chaco plots, and the classes that implement them:

.. toctree::
  :maxdepth: 1

  basic_elements/data_sources.rst
  basic_elements/data_ranges.rst
  basic_elements/mappers.rst
  basic_elements/plot_renderers.rst



TODO: to see how these elements collaborate to build an interactive plot,
give complete low-level example of line plot with simple tool and
describe the exchange of information


Axes
====

 axes

Tools
=====

 tools, overlays


===================
Plotting with Chaco
===================

The Plot class
==============

Plot and PlotData

chaco.shell
===========

========================
Low-level Chaco plotting
========================

1) create instances of PlotRenderer and add them to a Container.
   There are factory functions in
   plot_factory that make it simpler

2) Create a Plot instance, use methods to create new plots of different kinds.
   This automatizes 1) with an OverlayPlotContainer, i.e., it
   plots multiple curves on the same element

Plots can be rendered in a traitsui, wx, or qt window




.. _embedding:

=====================
Embedding Chaco plots
=====================

Traits UI
=========

WxPython
========

Qt/PyQt
=======



