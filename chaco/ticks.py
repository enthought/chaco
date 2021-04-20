# -------------------------------------------------------------------------------
#
#
#  Written by: David C. Morrill (based on similar routines written by Eric Jones)
#
#  Date: 2007-05-01
#
#  (c) Copyright 2002-7 by Enthought, Inc.
#
# -------------------------------------------------------------------------------
""" Tick generator classes and helper functions for calculating axis
tick-related values (i.e., bounds and intervals).

"""
# Major library imports

from numpy import (
    arange,
    argsort,
    array,
    ceil,
    concatenate,
    equal,
    finfo,
    float64,
    floor,
    isnan,
    linspace,
    log10,
    minimum,
    ndarray,
    newaxis,
    putmask,
    shape,
)

# Enthought library imports
from traits.api import HasTraits, Any


class AbstractTickGenerator(HasTraits):
    """Abstract class for tick generators."""

    def get_ticks(
        self,
        data_low,
        data_high,
        bounds_low,
        bounds_high,
        interval,
        use_endpoints=False,
        scale="linear",
    ):
        """Returns a list of ticks points in data space.

        Parameters
        ----------
        data_low, data_high : float
            The actual minimum and maximum of index values of the entire
            dataset.
        bounds_low, bounds_high : "auto", "fit", float
            The range for which ticks should be generated.
        interval : "auto", float
            If the value is a positive number, it specifies the length
            of the tick interval; a negative integer specifies the
            number of tick intervals; 'auto' specifies that the number and
            length of the tick intervals are automatically calculated, based
            on the range of the axis.
        use_endpoints : Boolean
            If True, the lower and upper bounds of the data are used as the
            lower and upper end points of the axis. If False, the end points
            might not fall exactly on the bounds.
        scale : 'linear' or 'log'
            The type of scale the ticks are for.

        Returns
        -------
        tick_list : array of floats
            Where ticks are to be placed.


        Example
        -------
        If the range of x-values in a line plot span from -15.0 to +15.0, but
        the plot is currently displaying only the region from 3.1 to 6.83, and
        the user wants the interval to be automatically computed to be some
        nice value, then call get_ticks() thusly::

            get_ticks(-15.0, 15.0, 3.1, 6.83, "auto")

        A reasonable return value in this case would be::

            [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]
        """

        raise NotImplementedError


class DefaultTickGenerator(AbstractTickGenerator):
    """An implementation of AbstractTickGenerator that simply uses the
    auto_ticks() and log_auto_ticks() functions.
    """

    def get_ticks(
        self,
        data_low,
        data_high,
        bounds_low,
        bounds_high,
        interval,
        use_endpoints=False,
        scale="linear",
    ):
        if scale == "linear":
            return array(
                auto_ticks(
                    data_low,
                    data_high,
                    bounds_low,
                    bounds_high,
                    interval,
                    use_endpoints=False,
                ),
                float64,
            )
        elif scale == "log":
            return array(
                log_auto_ticks(
                    data_low,
                    data_high,
                    bounds_low,
                    bounds_high,
                    interval,
                    use_endpoints=False,
                ),
                float64,
            )


class ShowAllTickGenerator(AbstractTickGenerator):
    """Uses the abstract interface, but returns all "positions" instead
    of decimating the ticks.

    You must provide a sequence of values as a *positions* keyword argument
    to the constructor.
    """

    # A sequence of positions for ticks.
    positions = Any

    def get_ticks(
        self,
        data_low,
        data_high,
        bounds_low,
        bounds_high,
        interval,
        use_endpoints=False,
        scale="linear",
    ):
        """Returns an array based on **positions**."""
        # ignore all the high, low, etc. data and just return every position
        return array(self.positions, float64)


class MinorTickGenerator(DefaultTickGenerator):
    """An implementation of AbstractTickGenerator that extends DefaultTickGenerator,
    but sets the tick interval to a smaller length.
    """

    def get_ticks(
        self,
        data_low,
        data_high,
        bounds_low,
        bounds_high,
        interval,
        use_endpoints=False,
        scale="linear",
    ):
        if interval == "auto":
            # for the default interval, generate a smaller tick interval
            interval = auto_interval(
                0, auto_interval(data_low, data_high), max_ticks=5
            )

        return super().get_ticks(
            data_low,
            data_high,
            bounds_low,
            bounds_high,
            interval,
            use_endpoints,
            scale,
        )


# -------------------------------------------------------------------------------
#  Code imported from plt/plot_utility.py:
# -------------------------------------------------------------------------------


def auto_ticks(
    data_low,
    data_high,
    bound_low,
    bound_high,
    tick_interval,
    use_endpoints=True,
):
    """Finds locations for axis tick marks.

    Calculates the locations for tick marks on an axis. The *bound_low*,
    *bound_high*, and *tick_interval* parameters specify how the axis end
    points and tick interval are calculated.

    Parameters
    ----------

    data_low, data_high : number
        The minimum and maximum values of the data along this axis.
        If any of the bound settings are 'auto' or 'fit', the axis
        traits are calculated automatically from these values.
    bound_low, bound_high : 'auto', 'fit', or a number.
        The lower and upper bounds of the axis. If the value is a number,
        that value is used for the corresponding end point. If the value is
        'auto', then the end point is calculated automatically. If the
        value is 'fit', then the axis bound is set to the corresponding
        *data_low* or *data_high* value.
    tick_interval : can be 'auto' or a number
        If the value is a positive number, it specifies the length
        of the tick interval; a negative integer specifies the
        number of tick intervals; 'auto' specifies that the number and
        length of the tick intervals are automatically calculated, based
        on the range of the axis.
    use_endpoints : Boolean
        If True, the lower and upper bounds of the data are used as the
        lower and upper end points of the axis. If False, the end points
        might not fall exactly on the bounds.

    Returns
    -------
    An array of tick mark locations. The first and last tick entries are the
    axis end points.
    """
    # if a NaN makes it here, we cant determine tick mark locations. Return
    # empty list to prevent crash. Motivated by enthought/chaco#529
    if isnan([data_low, data_high, bound_low, bound_high]).any():
        return []

    is_auto_low = bound_low == "auto"
    is_auto_high = bound_high == "auto"

    if isinstance(bound_low, str):
        lower = data_low
    else:
        lower = float(bound_low)

    if isinstance(bound_high, str):
        upper = data_high
    else:
        upper = float(bound_high)

    if (tick_interval == "auto") or (tick_interval == 0.0):
        rng = abs(upper - lower)

        if rng == 0.0:
            tick_interval = 0.5
            lower = data_low - 0.5
            upper = data_high + 0.5
        else:
            tick_interval = auto_interval(lower, upper)
    elif tick_interval < 0:
        intervals = -tick_interval
        tick_interval = tick_intervals(lower, upper, intervals)
        if is_auto_low and is_auto_high:
            is_auto_low = is_auto_high = False
            lower = tick_interval * floor(lower / tick_interval)
            while (abs(lower) >= tick_interval) and (
                (lower + tick_interval * (intervals - 1)) >= upper
            ):
                lower -= tick_interval
            upper = lower + tick_interval * intervals

    # If the lower or upper bound are set to 'auto',
    # calculate them based on the newly chosen tick_interval:
    if is_auto_low or is_auto_high:
        delta = 0.01 * tick_interval * (data_low == data_high)
        auto_lower, auto_upper = auto_bounds(
            data_low - delta, data_high + delta, tick_interval
        )
        if is_auto_low:
            lower = auto_lower
        if is_auto_high:
            upper = auto_upper

    # Compute the range of ticks values:
    start = floor(lower / tick_interval) * tick_interval
    end = floor(upper / tick_interval) * tick_interval
    # If we return the same value for the upper bound and lower bound, the
    # layout code will not be able to lay out the tick marks (divide by zero).
    if start == end:
        lower = start = start - tick_interval
        upper = end = start - tick_interval

    if upper > end:
        end += tick_interval
    ticks = arange(start, end + (tick_interval / 2.0), tick_interval)

    if len(ticks) < 2:
        ticks = array(((lower - lower * 1.0e-7), lower))
    if (not is_auto_low) and use_endpoints:
        ticks[0] = lower
    if (not is_auto_high) and use_endpoints:
        ticks[-1] = upper

    return [tick for tick in ticks if tick >= bound_low and tick <= bound_high]


# --------------------------------------------------------------------------------
#  Compute the best tick interval for a specified data range:
# --------------------------------------------------------------------------------


def heckbert_interval(data_low, data_high, numticks=8):
    """
    Returns a "nice" range and interval for a given data range and a preferred
    number of ticks.  From Paul Heckbert's algorithm in Graphics Gems.
    """
    range = _nice(data_high - data_low)
    d = _nice(range / (numticks - 1), round=True)
    graphmin = floor(data_low / d) * d
    graphmax = ceil(data_high / d) * d
    # nfrac = max(-floor(log10(d)), 0)
    return graphmin, graphmax, d


def _nice(x, round=False):
    """ if round is False, then use ceil(range) """
    expv = floor(log10(x))
    f = x / pow(10, expv)
    if round:
        if f < 1.5:
            nf = 1.0
        elif f < 3.0:
            nf = 2.0
        elif f < 7.0:
            nf = 5.0
        else:
            nf = 10.0
    else:
        if f <= 1.0:
            nf = 1.0
        elif f <= 2.0:
            nf = 2.0
        elif f <= 5.0:
            nf = 5.0
        else:
            nf = 10.0
    return nf * pow(10, expv)


def auto_interval(data_low, data_high, max_ticks=9):
    """Calculates the tick interval for a range.

    The boundaries for the data to be plotted on the axis are::

        data_bounds = (data_low,data_high)

    The function chooses the number of tick marks, which can be between
    3 and max_ticks marks (including end points), and chooses tick intervals at
    1, 2, 2.5, 5, 10, 20, ...

    Returns
    -------
    interval : float
        tick mark interval for axis
    """
    range = float(data_high) - float(data_low)

    # We'll choose from between 2 and 8 tick marks.
    # Preference is given to more ticks:
    #   Note reverse order and see kludge below...
    divisions = arange(
        max_ticks - 1, 2.0, -1.0
    )  # for max_ticks=9, ( 7, 6, ..., 3 )

    # Calculate the intervals for the divisions:
    candidate_intervals = range / divisions

    # Get magnitudes and mantissas for each candidate:
    magnitudes = 10.0 ** floor(log10(candidate_intervals))
    mantissas = candidate_intervals / magnitudes

    # List of "pleasing" intervals between ticks on graph.
    # Only the first magnitude are listed, higher mags others are inferred:
    magic_intervals = array((1.0, 2.0, 2.5, 5.0, 10.0))

    # Calculate the absolute differences between the candidates
    # (with magnitude removed) and the magic intervals:
    differences = abs(magic_intervals[:, newaxis] - mantissas)

    # Find the division and magic interval combo that produce the
    # smallest differences:

    # KLUDGE: 'argsort' doesn't preserve the order of equal values,
    # so we subtract a small, index dependent amount from each difference
    # to force correct ordering.
    sh = shape(differences)
    small = 2.2e-16 * arange(sh[1]) * arange(sh[0])[:, newaxis]
    small = small[::-1, ::-1]  # reverse the order
    differences = differences - small

    # ? Numeric should allow keyword "axis" ? comment out for now
    # best_mantissa = minimum.reduce(differences,axis=0)
    # best_magic = minimum.reduce(differences,axis=-1)
    best_mantissa = minimum.reduce(differences, 0)
    best_magic = minimum.reduce(differences, -1)
    magic_index = argsort(best_magic)[0]
    mantissa_index = argsort(best_mantissa)[0]

    # The best interval is the magic_interval multiplied by the magnitude
    # of the best mantissa:
    interval = magic_intervals[magic_index]
    magnitude = magnitudes[mantissa_index]
    result = interval * magnitude
    if result == 0.0:
        result = finfo(float).eps
    return result


# --------------------------------------------------------------------------------
#  Compute the best tick interval length to achieve a specified number of tick
#  intervals:
# --------------------------------------------------------------------------------


def tick_intervals(data_low, data_high, intervals):
    """Computes the best tick interval length to achieve a specified number of
    tick intervals.

    Parameters
    ----------
    data_low, data_high : number
        The minimum and maximum values of the data along this axis.
        If any of the bound settings are 'auto' or 'fit', the axis
        traits are calculated automatically from these values.
    intervals : number
        The desired number of intervals

    Returns
    -------
    Returns a float indicating the tick interval length.
    """
    range = float(data_high - data_low)
    if range == 0.0:
        range = 1.0
    interval = range / intervals
    factor = 10.0 ** floor(log10(interval))
    interval /= factor

    if interval < 2.0:
        interval = 2.0
        index = 0
    elif interval < 2.5:
        interval = 2.5
        index = 1
    elif interval < 5.0:
        interval = 5.0
        index = 2
    else:
        interval = 10.0
        index = 3

    while True:
        result = interval * factor
        if (floor(data_low / result) * result) + (
            intervals * result
        ) >= data_high:
            return result
        index = (index + 1) % 4
        interval *= (2.0, 1.25, 2.0, 2.0)[index]


def log_auto_ticks(
    data_low,
    data_high,
    bound_low,
    bound_high,
    tick_interval,
    use_endpoints=True,
):
    """Like auto_ticks(), but for log scales."""
    tick_goal = 15
    magic_numbers = [1, 2, 5]
    explicit_ticks = False

    if data_low <= 0.0:
        return []

    if tick_interval != "auto":
        if tick_interval < 0:
            tick_goal = -tick_interval
        else:
            magic_numbers = [tick_interval]
            explicit_ticks = True

    if data_low > data_high:
        data_low, data_high = data_high, data_low

    log_low = log10(data_low)
    log_high = log10(data_high)
    log_interval = log_high - log_low

    if log_interval < 1.0:
        # If less than a factor of 10 separates the data, just use the normal
        # linear approach
        return auto_ticks(
            data_low,
            data_high,
            bound_low,
            bound_high,
            tick_interval,
            use_endpoints=False,
        )

    elif log_interval < (tick_goal + 1) / 2 or explicit_ticks:
        # If there's enough space, try to put lines at the magic number multipliers
        # inside each power of ten

        # Try each interval to see how many ticks we get
        for interval in magic_numbers:
            ticklist = []
            for exp in range(int(floor(log_low)), int(ceil(log_high))):
                for multiplier in linspace(
                    interval, 10.0, round(10.0 / interval), endpoint=1
                ):
                    tick = 10 ** exp * multiplier
                    if tick >= data_low and tick <= data_high:
                        ticklist.append(tick)
            if len(ticklist) < tick_goal + 3 or explicit_ticks:
                return ticklist
    else:
        # We put lines at every power of ten or less
        startlog = ceil(log_low)
        endlog = floor(log_high)
        interval = ceil((endlog - startlog) / 9.0)
        expticks = arange(startlog, endlog, interval)
        # There's no function that is like arange but inclusive, so
        # we have to check whether the endpoint should be included.
        if (endlog - startlog) % interval == 0.0:
            expticks = concatenate([expticks, [endlog]])
        return 10 ** expticks


# -------------------------------------------------------------------------------
#  Compute the best lower and upper axis bounds for a range of data:
# -------------------------------------------------------------------------------


def auto_bounds(data_low, data_high, tick_interval):
    """Calculates appropriate upper and lower bounds for the axis from
    the data bounds and the given axis interval.

    The boundaries  hit either exactly on the lower and upper values
    or on the tick mark just beyond the lower and upper values.
    """
    return (
        calc_bound(data_low, tick_interval, False),
        calc_bound(data_high, tick_interval, True),
    )


# -------------------------------------------------------------------------------
#  Compute the best axis endpoint for a specified data value:
# -------------------------------------------------------------------------------


def calc_bound(end_point, tick_interval, is_upper):
    """Finds an axis end point that includes the value *end_point*.

    If the tick mark interval results in a tick mark hitting directly on the
    end point, *end_point* is returned.  Otherwise, the location of the tick
    mark just past *end_point* is returned. The *is_upper* parameter
    specifies whether *end_point* is at the upper (True) or lower (False)
    end of the axis.
    """
    quotient, remainder = divmod(end_point, tick_interval)
    if (remainder == 0.0) or (
        ((tick_interval - remainder) / tick_interval) < 0.00001
    ):
        return end_point

    c1 = (quotient + 1.0) * tick_interval
    c2 = quotient * tick_interval
    if is_upper:
        return max(c1, c2)
    return min(c1, c2)
