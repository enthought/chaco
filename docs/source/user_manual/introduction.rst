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

The classes that define these basic concept are decribes in the next sections.

Data sources
============

A data source is a wrapper object for the actual data that the plot will be
handling.
It provides methods for retrieving data, estimating a size of the dataset,
indications about the dimensionality of the data, a place for metadata
(such as selections and annotations), and events that fire when the data gets
changed.

There are two primary reasons for a data source class:

* It provides a way for different plotting objects to reference the same data.

* It defines the interface to expose data from existing applications to Chaco.

In most cases, the standard :class:`~chaco.array_data_source.ArrayDataSource`
will suffice.

Interface
---------

The basic interface for data sources is defined in
:class:`~chaco.abstract_data_source.AbstractDataSource`.
Here is a summary of the most important attributes and methods:

:attr:`~chaco.abstract_data_source.AbstractDataSource.value_dimension`

  The dimensionality of the data value at each point. It is defined
  as a :class:`DimensionTrait`, i.e., one of
  "scalar", "point", "image", or "cube". For example,
  a :class:`GridDataSource` represents data in a 2D array and thus its
  :attr:`value_dimension` is "scalar".

:attr:`~chaco.abstract_data_source.AbstractDataSource.index_dimension`

  The dimensionality of the data value at each point. It is defined
  as a :class:`DimensionTrait`, i.e., one of
  "scalar", "point", "image", or "cube". For example,
  a :class:`GridDataSource` represents data in a 2D array and thus its
  :attr:`index_dimension` is "image".

:attr:`~chaco.abstract_data_source.AbstractDataSource.metadata`

  A dictionary that maps strings to arbitrary data. Usually, the mapped
  data is a set of indices, as in the case of selections and annotations.
  By default, :attr:`metadata` contains the keys "selections" (representing
  indices that are currently selected by some tool)
  and "annotations", both mapping to an empty list.

:attr:`~chaco.abstract_data_source.AbstractDataSource.persist_data`

  If True (default), the data that this data source refers to is serialized
  when the data source is.

:attr:`~chaco.abstract_data_source.AbstractDataSource.get_data()`

  Returns a data array containing the data referred to by the data source.

:attr:`~chaco.abstract_data_source.AbstractDataSource.`
:attr:`~chaco.abstract_data_source.AbstractDataSource.`

Events
------

:class:`~chaco.abstract_data_source.AbstractDataSource` defines three events
that can be used in Traits applications to react to changes in the data source:

:attr:`~chaco.abstract_data_source.AbstractDataSource.data_changes`

  Fired when the data values change.

:attr:`~chaco.abstract_data_source.AbstractDataSource.bounds_changes`

  Fired when the data bounds change.

:attr:`~chaco.abstract_data_source.AbstractDataSource.metadata_changed`
  Fired when the content of :attr:`metadata` changes (both the
  :attr:`metadata` dictionary object or any of its items).


Subclasses
----------

chaco.array_data_source.ArrayDataSource

  A data source representing a single, continuous array of numerical data.

chaco.function_data_source.FunctionDataSource

chaco.grid_data_source.GridDataSource

chaco.multi_array_data_source.MultiArrayDataSource

  A data source representing a single, continuous array of numerical data
  of potentially more than one dimension.

chaco.point_data_source.PointDataSource

  A data source representing a (possibly unordered) set of (X,Y) points.

chaco.image_data.ImageData

  Represents a grid of data to be plotted.

Data range
==========

Mappers
=======

 mappers

Plots
=====

 plots (plot types)

basic plot properties:

index, value
index_mapper
value_mapper

origin

bgcolor

resizable

index_range
value_range

orientation

Plot types described on separate page.

Layers
======

 underlays and overlays

DEFAULT_DRAWING_ORDER = ["background", "image", "underlay", "plot",
 "selection", "border", "annotation", "overlay"]

Axes
====

 axes

Tools
=====

 tools


===================
Plotting with Chaco
===================

The Plot class
==============

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



