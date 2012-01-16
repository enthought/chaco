
.. highlight:: python
   :linenothreshold: 10

*********************
Containers and Layout
*********************

Overview
========

It is quite common to need to display data side by side. In order to arrange
multiple plots and other components (e.g., colorbars) in a single panel,
Chaco uses *containers* to organize the layout.

 * Rendering order
 * Event dispatch
 * Layout and sizing

Chaco containers
================

Chaco implements 4 different containers:
:ref:`hv-plot-container`,
:ref:`grid-plot-container`, and :ref:`overlay-plot-container`.

All containers are derived from the base class
:class:`~chaco.base_plot_container.​BasePlotContainer`, and share
a common interface:

* ``__init__(*components, **parameters)`` (constructor of the container object):
  The constructor of a plot container takes a sequence of
  components, which are added to the container itself,
  and a set of keyword arguments, which are used to initialize the
  parameters of the container. For example::

      container = HPlotContainer(scatter_plot, line_plot, spacing=100)

  creates a container with horizontal layout containing two plots
  (``scatter_plot`` and ``line_plot``), with a spacing of 100 pixels between
  them.

* ``add(*components)``: Append ore or more plots to the ones already present in the
  container. For example, this is equivalent to the code above::

      container = HPlotContainer(spacing=100)
      container.add(line_plot, scatter_plot)

* ``remove(self, *components)``: Remove a sequence of components from the
  container

* ``insert(index, component)``: Inserts a component at a specific position
  in the components list

**Note:** **Each plot can have only one container**, so adding the same plot to
a second container will remove it from the first one. In the same way,
adding the same plot multiple times will not have create multiple
copies. Instead, one should create multiple plots objects.
E.g., this code::

        # Create a vertical container containing two horizontal containers
        h_container1 = HPlotContainer()
        h_container2 = HPlotContainer()
        outer_container = VPlotContainer(h_container1, h_container2,
                                         stack_order="top_to_bottom")

        # Add the two plots to the first container
        h_container1.add(scatter_plot, line_plot1, line_plot2)

        # Now add the first line plot to the second container => it is removed
        # from the first, as each plot can only have one container
        h_container2.add(line_plot1)

results in this layout:

  .. image:: images/user_guide/one_container_per_plot.png
      :height: 200pt




.. _hv-plot-container:

HPlotContainer and VPlotContainer
---------------------------------

:class:`~chaco.base_plot_container.HPlotContainer` and
:class:`~chaco.base_plot_container.VPlotContainer` display a set of components
in an horizontal and vertical stack, respectively, as shown in these simple
examples:

.. image:: images/hplotcontainer.png
    :height: 200pt

.. image:: images/vplotcontainer.png
    :height: 200pt

In both cases, a series of line plots and scatter plots is added to an
:class:`~chaco.base_plot_container.HPlotContainer` or a
:class:`~chaco.base_plot_container.VPlotContainer`::

        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)

        # Create a scatter plot
        scatter_plot = Plot(plotdata)
        scatter_plot.plot(("x", "y"), type="scatter", color="blue")

        # Create a line plot
        line_plot = Plot(plotdata)
        line_plot.plot(("x", "y"), type="line", color="blue")

        # Create a horizontal container and put the two plots inside it
        container = HPlotContainer(line_plot, scatter_plot)
        self.plot = container


:class:`~chaco.base_plot_container.HPlotContainer` is also used quite often to
display a colorbar or legend to the side of a plot, e.g.

.. image:: images/user_guide/h_container_colorbar.png
  :height: 200pt

was created using a color-mapped scatter plot and a colorbar inside a
horizontal container::

        # Create the plot
        plot = Plot(data)
        plot.plot(("index", "value", "color"), type="cmap_scatter",
                  color_mapper=jet)

        # Create the colorbar, handing in the appropriate range and colormap
        colormap = plot.color_mapper
        colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                            color_mapper=colormap,
                            orientation='v',
                            resizable='v',
                            width=30,
                            padding=20)

        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom

        # Create a container to position the plot and the colorbar side-by-side
        container = HPlotContainer(plot, colorbar)


HPlot

    # The order in which components in the plot container are laid out.
    stack_order = Enum("left_to_right", "right_to_left")

    # The amount of space to put between components.
    spacing = Float(0.0)

    # The vertical alignment of objects that don't span the full height.
    valign = Enum("bottom", "top", "center")

container = HPlotContainer(use_backbuffer = True)

also use to layout colorbar

VPlot


    # The horizontal alignment of objects that don't span the full width.
    halign = Enum("left", "right", "center")

    # The order in which components in the plot container are laid out.
    stack_order = Enum("bottom_to_top", "top_to_bottom")

    # The amount of space to put between components.
    spacing = Float(0.0)

VPlotContainer(bgcolor = "lightblue",
                               spacing = 20,
                               padding = 50,
                               fill_padding=False)


.. seealso::

    **HPlotContainer and VPlotContainer in action.** See ``demo/financial_plot.py``,
    ``demo/two_plots.py``, ``demo/advanced/scalar_image_function_inspector.py``,
    and ``demo/basc/cmap_scatter.py``
    in the Chaco examples directory.


.. _grid-plot-container:

GridPlotContainer
-----------------

*content here*


.. _overlay-plot-container:

OverlayPlotContainer
--------------------

*content here*
