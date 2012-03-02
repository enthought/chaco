Mappers
=======

Mappers perform the job of mapping a data space region to screen space,
and vice versa. They are used by plots to transform their data sources
to pixel coordinates on the screen. While most of the time this is
a relatively simple rescaling operation, mapper can also be used
for non-linear transformations, most notably to map a data source
to logarithmic coordinates on screen.

Interface
---------

The general interface for mappers is defined in
:class:`~chaco.abstract_mapper.AbstractMapper` and defines only a few
methods:

    :attr:`~chaco.abstract_mapper.AbstractMapper.map_screen(data_value)`,
    :attr:`~chaco.abstract_mapper.AbstractMapper.map_data(screen_value)`

      Maps a vector of data coordinates to screen coordinates, and vice versa.

    :attr:`~chaco.abstract_mapper.AbstractMapper.map_data_array(screen_value_array)`

      Maps an array of points in data coordinates to screen coordinates.
      By default, this method just loops over the points, calling :attr:`map_data()`
      on each one.  For vectorizable mapping functions, this
      implementation is overridden with a faster one.

Mappers for 1D data have a slightly larger interface, defined in
:class:`~chaco.base_1d_mapper.Base1DMapper`. These mappers rely
on a :class:`~chaco.data_range_1d.DataRange1D` object to find the
bounds on the data domain.

    :attr:`~chaco.abstract_mapper.AbstractMapper.range`

      A :class:`~chaco.data_range_1d.DataRange1D` instance to define the
      data-space bounds of the mapper. The mapper listens to the
      :attr:`updated` event of the range and re-fires it as its
      own :attr:`updated` event (see below).

    :attr:`~chaco.abstract_mapper.AbstractMapper.low_pos`,
    :attr:`~chaco.abstract_mapper.AbstractMapper.high_pos`,
    :attr:`~chaco.abstract_mapper.AbstractMapper.screen_bounds`,

      The screen space position of the lower/upper bound of the data space.
      :attr:`screen_bounds` is a convenience property to set/get the screen
      bounds with a single attribute.

    :attr:`~chaco.abstract_mapper.AbstractMapper.stretch_data`

      When the screen bounds change (in response, for instance, to the
      window resizing) one could either fit more data space on the screen, or
      stretch the data space to the new bounds.
      If :attr:`stretch_data` is True (default), the data is stretched;
      if it is False, the mapper preserves the screen-to-data ratio.


Events
------

The :class:`~chaco.abstract_mapper.AbstractMapper` interface defines a single
generic event,
:attr:`~chaco.abstract_mapper.AbstractMapper.updated`,
which is fired when the bound values change.

For subclasses of :class:`~chaco.base_1d_mapper.Base1DMapper`, the
:attr:`updated` event is also fired in response to an :attr:`updated` event
fired by the underlying data range.
The value of the new event is the tuple ``(low_bound, high_bound)`` contained
in the triggering event.


List of Chaco data mappers
--------------------------

:class:`~chaco.linear_mapper.LinearMapper` (subclass of :class:`~chaco.base_1d_mapper.Base1DMapper`)

  This mapper transforms a 1D data space range linearly to a fixed 1D range
  in screen space.

:class:`~chaco.log_mapper.LogMapper` (subclass of :class:`~chaco.base_1d_mapper.Base1DMapper`)

  Maps a 1D data space range to a 1D range in screen space through a
  logarithmic transform. Data values
  smaller than or equal to 0.0 are
  substituted by :attr:`~chaco.log_mapper.LogMapper.fill_value`
  (default is 1.0) before the logarithmic transformation.

:class:`~chaco.grid_mapper.GridMapper`

  Same as :class:`~chaco.linear_mapper.LinearMapper` for 2D ranges. This class
  replaces the :class:`Base1DMapper` attributes with analogous ones:

      :attr:`~chaco.grid_mapper.GridMapper.range`

          A :class:`~chaco.data_range_2d.DataRange2D` instance to define the
          data-space bounds of the mapper.

      :attr:`~chaco.grid_mapper.GridMapper.x_low_pos`,
      :attr:`~chaco.grid_mapper.GridMapper.y_low_pos`,
      :attr:`~chaco.grid_mapper.GridMapper.x_high_pos`,
      :attr:`~chaco.grid_mapper.GridMapper.y_high_pos`

        Screen space positions for the lower and upper bounds of the x and
        y axes.

      :attr:`~chaco.grid_mapper.GridMapper.screen_bounds`

        Convenience property to set/get the screen bounds with a single attribute.
        The value of this attribute a 4-elements tuple
        ``(x_low_pos, x_high_pos, y_low_pos, y_high_pos)``.

  :class:`~chaco.grid_mapper.GridMapper` uses two
  :class:`~chaco.base_1d_mapper.Base1DMapper` instances to define mappers for
  the two axes (accessible from the two private attributes
  :attr:`_xmapper` and :attr:`_ymapper`.
  It thus possible to set them to be linear or
  logarithmic mappers. This is best made using the class constructor, which has
  this signature:

    :class:`~chaco.grid_mapper.GridMapper(x_type="linear", y_type="linear", range=None, **kwargs)`

  ``x_type`` and ``y_type`` can be either 'linear' or 'log', which will
  create a corresponding :class:`LinearMapper` or :class:`LogMapper` classes.


:class:`~chaco.polar_mapper.PolarMapper`

  This class should map data polar coordinates to screen cartesian coordinates,
  to use for example with a :class:`~chaco.polar_line_renderer.PolarLineRenderer`,
  but at the moment it is a copy of :class:`~chaco.linear_mapper.LinearMapper`.

  .. warning::

    The implementation of this mapper is under construction.

