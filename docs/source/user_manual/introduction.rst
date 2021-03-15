************
Introduction
************

This guide is designed to act as a conceptual guide to Chaco, an open-source
data visualization library built and maintained by Enthought, Inc.  Chaco is
a set of interactive visualization tools built on top of the Enable and Kiva
2D drawing libraries and designed to complement other Enthought rapid
application development tools including Traits and TraitsUI.  This guide
discusses many, but not all of the features of Chaco.  For complete details
of the Chaco API, refer to the Chaco API documentation.

==============
What is Chaco?
==============

Chaco is a 2D plotting library that is part of and integrates with
the Enthought Tools Suite.

The strong points of Chaco are

1. it can be :ref:`embedded <embedding>` in any Wx, Qt, or TraitsUI application

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

Chaco defines two abstraction layers that allow a more high-level (albeit
less flexible) plotting experience. First, Chaco contains a
:class:`~chaco.plot.Plot` class that defines several methods that create a
complete plot given one or more data sets. In other words,
:class:`~chaco.plot.Plot` knows how to package data for the most common kinds
of plots. Second, Chaco has a :mod:`shell` module that defines high-level
plotting functions. This module allows using Chaco as an interactive plotting
tool that will be familiar to users of matplotlib.

.. _basic_elements:

==========
Core Ideas
==========

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

* **Modular design and extensible classes**

  Chaco is meant to be used for writing tools and applications, and code
  reuse and good class design are important. We use the math behind the
  data and visualizations to give us architectural direction and conceptual
  modularity. The Traits framework allows us to use events to couple
  disjoint components at another level of modularity.

  Also, rather than building super-flexible core objects with myriad
  configuration attributes, Chaco's classes are written with subclassing in
  mind.  While they are certainly configurable, the classes themselves are
  written in a modular way so that subclasses can easily customize
  particular aspects of a visual component's appearance or a tool's
  behavior.

These pages describe in detail the basic building blocks of
Chaco plots, and the classes that implement them:

.. toctree::
  :maxdepth: 1

  basic_elements/data_sources.rst
  basic_elements/data_ranges.rst
  basic_elements/mappers.rst
  basic_elements/plot_renderers.rst
  basic_elements/tools.rst
  basic_elements/overlays.rst
  plot_types.rst


.. comment: TODO: find out how the selection features are organized

.. comment: TODO: to see how these elements collaborate to build an interactive 
   plot, give complete low-level example of line plot with simple tool and
   describe the exchange of information
