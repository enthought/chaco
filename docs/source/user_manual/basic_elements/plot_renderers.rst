==============
Plot renderers
==============

Plot renderers are the classes that actually draw the different kinds of plots,
or plot-like elements as for instance color bars.

This section describes the concepts that are common to all kind of plots.
A separate page  contains an exhaustive
:ref:`list of all plot types <plot_types>` defined in Chaco.

Common interface
================

The base interface is defined in the abstract class
:class:`~chaco.abstract_plot_renderer.AbstractPlotRenderer`, and provides
attributes and methods to set size, position, and aspect of the
plotting area.

Two more specialized interface are used by most concrete implementations,
namely :class:`~chaco.base_xy_plot.BaseXYPlot`, which is the interface
for :ref:`X-vs-Y plots <xy_plots>`, and
:class:`~chaco.base_2d_plot.Base2DPlot`, which is the interface for
:ref:`2D plots <2d_plots>` (e.g., :ref:`image plots <image_plot>` or
:ref:`contour plots <contour_plot>`).

The base interface inherits from a deep hierarchy of classes generating
from the ``enable`` package, starting with
:class:`enable.coordinate_box.CoordinateBox` (representing a box in screen
space) and :class:`enable.interactor.Interactor` (which allows plot
components to react to mouse and keyboard events), and down through
:class:`enable.component.Component` and :class:`chaco.plot_component.PlotComponent`
(follow :ref:`this link for a description of the relationship between Chaco and enable) <chaco_enable_kiva>`).
The class were most of the functionality is defined is
:class:`enable.component.Component`.

Here we give a summary of all the important properties exposed in
:class:`~chaco.abstract_plot_renderer.AbstractPlotRenderer`, without
worrying too much about their origin. Also, to avoid unnecessary cluttering
of the page, attributes and methods that are of secondary importance are not
listed.
Please refer to the API documentation for more details.


Box properties
--------------

All plot renderers are ``enable`` graphical components, and thus correspond
to a rectangular area in screen space. The renderer keeps track of two
area: an inner box that only contains the plot, and an outer box
that includes the padding and border area.
The properties of the boxes are controlled by
these attributes:

    :attr:`position`

      Position of the internal box relative to its container,
      given as a list [x,y].
      If there is no container, this is set to [0, 0].
      "Absolute" coordinates of point (i.e., relative to top-level parent
      :class:`Window` object) can be obtained using
      :attr:`get_absolute_coords(*coords)`.

    :attr:`x`, :attr:`y`, :attr:`x2`, :attr:`y2`

      Coordinates of the lower-left (x,y) and upper-right (x2,y2)
      pixel of the internal box, relative to its container.

    :attr:`bounds`,
    :attr:`width`, :attr:`height`

      Bounds of the internal box, in pixels.
      :attr:`bounds` is a list [width, height].


    :attr:`outer_position`,
    :attr:`outer_x`, :attr:`outer_y`, :attr:`outer_x2`, :attr:`outer_y2`,
    :attr:`outer_bounds`,
    :attr:`outer_width`, :attr:`outer_height`,
    :attr:`set_outer_position(index, value)`,
    :attr:`set_outer_bounds(index, value)`

      Attributes for the outer box equivalent to those defined above for the
      inner box. Modifying the outer position attributes is
      the right way to move the plot without changing its padding or bounds.
      Similarly, modifying the outer bounds attributes leaves the
      lower-left position and the padding unchanged.


    :attr:`resizable`,
    :attr:`fixed_preferred_size`

      String that defines in which dimensions the component is resizable.
      One of '' (not resizable), 'v' (resizable vertically), 'h'
      (resizable horizontally), 'hv' (resizable in both directions, default).
      If the component is resizable, :attr:`fixed_preferred_size`
      can be used to specify the
      amount of space that the component would like to get in each dimension,
      as a tuple (width, height). In this case, width and height have to be
      understood as relative sized: if one component in a container
      specifies, say, a fixed preferred width of 50 and another one
      specifies a fixed preferred width of 100, then the latter component will
      always be twice as wide as the former.

    :attr:`aspect_ratio`,
    :attr:`auto_center`

      Ratio of the components's width to its heights. This is used to maintain
      a fixed ratio between bounds when thet are changed independently,
      for example when resizing the window. :attr:`auto_center`
      specifies if the component should center itself in any space
      that is left empty (default is True).

    :attr:`padding_left`,
    :attr:`padding_right`,
    :attr:`padding_top`,
    :attr:`padding_bottom`,
    :attr:`padding`,
    :attr:`hpadding`,
    :attr:`vpadding`

      Padding space (in pixels). :attr:`padding` is a convenience property
      that returns a tuple of (left, right, top, bottom) padding. It can
      also be set to a single integer, in which case all four padding
      attributes are set to the same value.

      :attr:`hpadding` and :attr:`vpadding` are read-only property that return
      the total amount of horizontal and vertical padding (including
      the border width if the border is visible).

    :attr:`get_absolute_coords(*coords)`

      Transform coordinates relative to this component's origin to
      "absolute" coordinates, relative to top-level container.

Aspect properties
-----------------

These attributes control the aspect (e.g. color) of padding, backroung,
and borders:

    :attr:`bgcolor`

      The background color of this component (default is white). This can be
      set to "transparent" or "none" if the component should be see-through.
      The color can be specified as a string or as and RGB or RGBa tuple.

    :attr:`fill_padding`

      If True (default), fill the padding area with the background color.

    :attr:`border_visible`

      Determines if the border is visible (default is False).

    :attr:`border_width`

      Thickness of the border around the component in pixels (default is 1).

    :attr:`border_dash`

      Style of the lines tracing the border. One of 'solid' (default),
      'dot dash', 'dash', 'dot', or 'long dash'.

    :attr:`border_color`

      Color of the border.
      The color can be specified as a string or as and RGB or RGBa tuple.


Layers
------

Each plot is rendered in a sequence of layers so that different components
can plot at different time. For example, a line plot is drawn *before*
its legend, but *after* the axes and background grid.

The default drawing order is defined in
:attr:`~chaco.plot_component.PlotComponent.draw_order` as a list
of the names of the layers. The definition of the layers is as follows:

  1. 'background': Background image, shading, and borders
  2. 'image': A special layer for plots that render as images.  This is in
        a separate layer since these plots must all render before non-image
        plots
  3. 'underlay': Axes and grids
  4. 'plot': The main plot area itself
  5. 'annotation': Lines and text that are conceptually part of the "plot" but
        need to be rendered on top of everything else in the plot.
  5. 'selection': Selected content are rendered above normal plot elements
        to make them stand out. This can be disabled by setting
        :attr:`use_selection` to False (default).
  6. 'border': Plot borders
  7. 'annotation': Lines and text that are conceptually part of the "plot"
        but need to be rendered on top of everything else in the plot
  8. 'overlay': Legends, selection regions, and other tool-drawn visual
        elements

Concrete plot renderers set their default draw layer in
:attr:`~chaco.plot_component.PlotComponent.draw_layer` (default is 'plot').
Note that if this component is placed in a container, in most cases
the container's draw order is used, since the container calls
each of its contained components for each rendering pass.

One can add new elements to a plot by appending them to the
:attr:`underlays` or :attr:`overlays` lists. Components in these lists
are drawn underneath/above the plots as part of the 'underlay'/'overlay'
layers. They also receive mouse and keyboard events.

Interaction
-----------

Plot renderers also inherit from :class:`enable.interactor.Interactor`, and
as such are able to react to keyboard and mouse events. However, interactions
are usually defined as tools and overlays. Therefore, this part of the
interface is described at those pages.

TODO: add reference to interaction interface

Context
-------

Since plot renderers take care of displaying graphics, they keep references
to the larger graphical context:

    :attr:`container`

      Reference to a container object (None if no container is defined).
      The renderer defines its position relative to this.

    :attr:`window`

      Reference to the top-level enable Window.

    :attr:`viewports`

      List of viewport that are viewing this component

Others
------

    :attr:`use_backbuffer`

      If True, the polt renders itself to an
      offscreen buffer that is cached for later use. If False, (default) then
      the component will *never* render itself back-buffered, even if asked
      to do so.

    :attr:`invalidate_and_redraw()`

      Convenience method to invalidate our contents and request redraw.
      This method is sometimes useful when modifying a Chaco plot in an
      ipython shell.


X-Y Plots interface
===================

2D Plots interface
==================

TODO: explain that you need to provide index, value, and mappers

TODO: grids

TODO: hittest

TODO: selected

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
