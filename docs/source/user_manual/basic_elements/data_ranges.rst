===========
Data ranges
===========

A data range expresses bounds on *data space* of some dimensionality.
For example, the simplest
data range is just a set of two scalars representing (low, high) bounds in 1-D.
Data ranges are commonly used in plots to determine the range of plot axes.

Data ranges are typically associated to a data source, with their bounds set
to ``auto``, which means that they automatically scale to fit the
data source bounds. Each data source can be associated with multiple ranges,
and each data range can be associated with multiple data sources.

Interface
---------

The basic interface for data sources is defined in
:class:`~chaco.abstract_data_range.AbstractDataRange`
and
:class:`~chaco.base_data_range.BaseDataRange`.

This is a summary of the most important attributes and methods
(see the docstrings of this class for more details):

**Attributes**

    :attr:`~chaco.abstract_data_range.AbstractDataRange.sources`

      A list of data sources associated to the data range. Concrete implementation
      of data range listen to the event
      :attr:`~chaco.abstract_data_source.AbstractDataSource.data_changed`
      and refresh their bounds as appropriate (e.g., when the bounds are
      set to ``auto``).

    :attr:`~chaco.abstract_data_range.AbstractDataRange.low`

      The actual value of the lower bounds of the range. The correct way
      to set it is to use the :attr:`low_setting` attribute.

    :attr:`~chaco.abstract_data_range.AbstractDataRange.high`

      The actual value of the upper bounds of the range. The correct way
      to set it is to use the :attr:`high_setting` attribute.

    :attr:`~chaco.abstract_data_range.AbstractDataRange.low_setting`

      Setting for the lower bound of the range. This can either be a valid
      lower bound value, or ``auto`` (default), in which case the
      lower bound is set automatically from the associated data sources.

    :attr:`~chaco.abstract_data_range.AbstractDataRange.high_setting`

      Setting for the upper bound of the range. This can either be a valid
      upper bound value, or ``auto`` (default), in which case the
      upper bound is set automatically from the associated data sources.


**Methods**

    :attr:`~chaco.base_data_range.BaseDataRange.add(*datasources)`

      Convenience method to associate one ore more data sources to the range.
      The method avoids adding the same data source twice.

    :attr:`~chaco.base_data_range.BaseDataRange.remove(*datasources)`

      Convenience method to remove one ore more data sources from the range.
      If one of the data sources is not associated with the range,
      it is ignored.

    :attr:`~chaco.abstract_data_range.AbstractDataRange.clip_data(data)`

      Given an array of data values of the same dimensionality as the range,
      return a list of data values that are inside the range.

    :attr:`~chaco.abstract_data_range.AbstractDataRange.mask_data(data)`

        Given an array of data values of the same dimensionality as the range,
        this method returns a mask array of the same length as data, filled
        with 1s and 0s corresponding to whether the data value at that index
        is inside or outside the range.

    :attr:`~chaco.abstract_data_range.AbstractDataRange.bound_data(data)`

        Given an array of *monotonic* data values of the same dimensionality
        as the range,
        returns a tuple of indices (start, end) corresponding to the first and
        last elements that fall within the range.


Events
------

The basic data range interface defines a single event,
:attr:`~chaco.abstract_data_range.AbstractDataRange.updated`,
which is fired when the bound values change.
The value of the event is a tuple ``(low_bound, high_bound)``.

List of Chaco data ranges
--------------------------

There are two data range implementations in Chaco, one for 1D and one
for 2D ranges:

:class:`~chaco.data_range_1d.DataRange1D`

  :class:`~chaco.data_range_1d.DataRange1D` represents a 1D data range. This
  subclass adds several more ways to control the bound of the range given
  the associated data sources.

  First of all, a new parameter,
  :attr:`~chaco.data_range_1d.DataRange1D.tight_bounds`, controls whether
  the bounds should fit exactly the range of the associated data sources
  (the default is True). If it is False, the range adds some padding
  on either side of the data, controlled by
  :attr:`~chaco.data_range_1d.DataRange1D.margin`, which is expressed
  as a precentage of the full data width.

  Second, :class:`~chaco.data_range_1d.DataRange1D`
  defines a new setting, ``track`` for :attr:`low_setting` and
  :attr:`high_setting`. When one of the bounds is set to ``track``, it
  follows the other bound by the amount set in
  :attr:`~chaco.data_range_1d.DataRange1D.tracking_amount`.

  Third, bounds can be computed using a user-supplied function specified
  in :attr:`~chaco.data_range_1d.DataRange1D.bounds_func`. The function
  takes the arguments
  ``(data_low, data_high, margin, tight_bounds)``, where ``data_low``
  and ``data_high`` are the bounds computed *after* taking into
  account the ``auto`` or ``track`` settings, and
  :attr:`margin` and :attr:`tight_bounds` are defined as above.

  The logic of computing the bounds is implemented in the
  function :func:`calc_bounds` in :mod:`chaco.data_range_1d`.


:class:`~chaco.data_range_2d.DataRange2D`

  :class:`~chaco.data_range_2d.DataRange2D` represents a 2D data range.
  Under the hood, it is implemented using two
  :class:`~chaco.data_range_1d.DataRange1D` objects,
  one for each dimension,
  which are stored in the
  :attr:`~chaco.data_range_2d.DataRange2D.x_range` and
  :attr:`~chaco.data_range_2d.DataRange2D.y_range` attributes. These
  can be accessed directly if one wants to use the full flexibility
  of the :class:`~chaco.data_range_1d.DataRange1D` class.

  The data range bounds, :attr:`low` and :attr:`high`,
  return 2-elements tuples containing the bounds for  for the two dimensions.
