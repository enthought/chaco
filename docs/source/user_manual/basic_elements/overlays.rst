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

.. _axes:

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
  a string describing a font (e.g. '12 pt bold italic',
  'swiss family Arial' or 'default 12'; see
  :class:`~kiva.kiva_font_trait.TraitKivaFont` for details).
  Finally, :attr:`title_spacing` is the space between the axis line and the
  title (either the number of pixels or 'auto', default).


:attr:`~chaco.axis.PlotAxis.tick_weight`,
:attr:`~chaco.axis.PlotAxis.tick_color`,
:attr:`~chaco.axis.PlotAxis.tick_in`,
:attr:`~chaco.axis.PlotAxis.tick_out`,
:attr:`~chaco.axis.PlotAxis.tick_visible`,

  These attributes control the aspect of the ticks on the axis.
  If :attr:`tick_visible` is True, ticks are represented as lines of
  color :attr:`tick_color` (default is black) and thickness
  :attr:`tick_weight` (in pixels, default is 1). Each line extends into the
  plot area by :attr:`tick_in` pixels and into the label area by
  :attr:`tick_out` pixels (default is 5).


:attr:`~chaco.axis.PlotAxis.tick_label_font`,
:attr:`~chaco.axis.PlotAxis.tick_label_color`,
:attr:`~chaco.axis.PlotAxis.tick_label_rotate_angle`,
:attr:`~chaco.axis.PlotAxis.tick_label_alignment`,
:attr:`~chaco.axis.PlotAxis.tick_label_margin`,
:attr:`~chaco.axis.PlotAxis.tick_label_offset`,
:attr:`~chaco.axis.PlotAxis.tick_label_position`,

  The attributes allow to fine-tune the aspect of the tick labels:
  first of all, the font (e.g. '12 pt bold italic') and color of the
  labels. The position and orientation of the label can be also be
  closely controlled: :attr:`tick_label_rotate_angle` give the rotation
  angle (only multiples of 90 degrees are supported);
  :attr:`tick_label_alignment` selects whether the corner ('corner') or center
  ('edge', default) of the label are aligned to the corresponding tick
  ('corner' is better for 45 degrees rotation); :attr:`tick_label_margin`
  and :attr:`tick_label_offset` control the margin around the
  tick labels, and their distance from the axis; finally,
  :attr:`tick_label_position` can be set to either 'outside' (default)
  or 'inside' depending on whether the labels should be displayed inside
  or outside the plot area.


:attr:`~chaco.axis.PlotAxis.tick_label_formatter`

  By default, tick labels are assumed to be floating point numbers, and are
  displayed as such after removing trailing zeros and the decimal dot if
  necessary (e.g., '10.000' will be displayed as '10', and '21.10' as '21.1').
  The default behavior can be changed by setting :attr:`tick_label_formatter`
  to a callable that takes the value of the tick label and returns a
  formatted string.


:attr:`~chaco.axis.PlotAxis.tick_interval`,
:attr:`~chaco.axis.PlotAxis.tick_generator`,

  Locations and distances of ticks are controlled by the attribute
  :attr:`tick_generator`

  Default is chaco.ticks.auto_ticks or chaco.ticks.log_auto_ticks

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

