==================================
Overlays: axis, legend, grid, etc.
==================================

Overlays are elements that decorate plots, like for example
axes, legends, grids, etc.

Overlays are very similar to regular plot elements, and share most
of their interface with :ref:`plot renderers <plot_renderers>`
(both are subclasses of :class:`chaco.plot_component.PlotComponent`).

In addition, they have a lightweight interface defined in
:class:`chaco.abstract_overlay.AbstractOverlay`: the additional
features are that 1) they keep a reference to the plot they are decorating in
:attr:`~chaco.abstract_overlay.AbstractOverlay.component`;
2) the background color
:attr:`~chaco.abstract_overlay.AbstractOverlay.bgcolor`
is 'trasparent' by default;
3) they plot :ref:`on the 'overlay' layer <plot_layers>` by default.


TODO: explain how to attach an overlay to an existing plot renderer


There are three important classes of overlays defined in Chaco:
:ref:`axes <axis>`, :ref:`legends <legend>`, and :ref:`grids <grid>`.

.. _axis:

Axes
====

The Chaco overlay representing a plot axis is defined in the class
:class:`~chaco.axis.PlotAxis`.

A new axis is created by passing a
mapper, usually the mapper defined for the corresponding plot data coordinate.
:class:`~chaco.axis.PlotAxis` also defines a range of attributes to customize
the appearance of labels, ticks, and other axis elements. For example,
given an X-Y plot renderer, ``plot``, we can define a new x-axis as: ::

    AXIS_DEFAULTS = {
        'axis_line_weight': 2,
        'tick_weight': 2,
        'tick_label_font': 'modern 16',
        'title_font': 'modern 20',
    }

    x_axis = PlotAxis(orientation='bottom',
                      title='My x axis',
                      mapper=plot.x_mapper,
                      component=plot,
                      **AXIS_DEFAULTS)

The newly created axis can then be attached to the plot renderer by
appending it to its underlays layer: ::

    plot.underlays.append(x_axis)

Attributes
----------

This attributes control the appearance of the axis:

:attr:`~chaco.axis.PlotAxis.title`,
:attr:`~chaco.axis.PlotAxis.title_font`,
:attr:`~chaco.axis.PlotAxis.title_color`,
:attr:`~chaco.axis.PlotAxis.title_spacing`

  Define the axis label. :attr:`title` is a string or unicode object
  that is rendered using the given font and color. :attr:`title_font` is
  a string describing a font (e.g. '12 pt bold italic"
  'swiss family Arial' or 'default 12'; see
  :class:`~kiva.kiva_font_trait.TraitKivaFont` for details).
  Finally, :attr:`title_spacing` is the space between the axis line and the
  title (either the number of pixels or 'auto', default).

:attr:`~chaco.axis.PlotAxis.tick_interval`,
:attr:`~chaco.axis.PlotAxis.tick_generator`,


:attr:`~chaco.axis.PlotAxis.tick_weight`,
:attr:`~chaco.axis.PlotAxis.tick_color`,
:attr:`~chaco.axis.PlotAxis.tick_in`,
:attr:`~chaco.axis.PlotAxis.tick_out`,
:attr:`~chaco.axis.PlotAxis.tick_visible`,


:attr:`~chaco.axis.PlotAxis.tick_label_font`
:attr:`~chaco.axis.PlotAxis.tick_label_color`
:attr:`~chaco.axis.PlotAxis.tick_label_rotate_angle`
:attr:`~chaco.axis.PlotAxis.tick_label_alignment`
:attr:`~chaco.axis.PlotAxis.tick_label_margin`
:attr:`~chaco.axis.PlotAxis.tick_label_offset`
:attr:`~chaco.axis.PlotAxis.tick_label_position`
:attr:`~chaco.axis.PlotAxis.tick_label_formatter`

:attr:`~chaco.axis.PlotAxis.`
:attr:`~chaco.axis.PlotAxis.`

Events
------

updated

Fired when the axis's range bounds change.

.. _legend:

Legend
======

.. _grid:

Grid
====

