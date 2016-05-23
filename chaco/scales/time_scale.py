"""
A scale for time and calendar intervals.
"""

from math import floor

from scales import AbstractScale, ScaleSystem, frange, heckbert_interval
from formatters import TimeFormatter
from safetime import (safe_fromtimestamp, datetime, timedelta, EPOCH,
                      MINYEAR, MAXYEAR)

# Labels for date and time units.
datetime_scale = ["microsecond", "second", "minute", "hour",
                  "day", "month", "year"]
datetime_zeros = zip(datetime_scale, [0, 0, 0, 0, 1, 1, 1])


__all__ = ["TimeScale", "CalendarScaleSystem", "HMSScales", "MDYScales",
           "trange", "tfrac", "td_to_sec", "dt_to_sec"]


def td_to_sec(td):
    """ Returns the floating point number of seconds in a timedelta object.
    """
    return td.days * 24 * 3600 + td.seconds + td.microseconds * 1e-6


def dt_to_sec(t):
    """ Returns the floating point number of seconds since the UNIX epoch
    corresponding to the given datetime instance.

    This value is more accurate than mktime(t.timetuple()) because it
    preserves milliseconds.
    """
    return td_to_sec(t - EPOCH)


def tfrac(t, **time_unit):
    """ Performs a calendar-aware split of a time into (aligned_time, frac)
    over an interval that is a multiple of one of the following time units:

        "microseconds" "milliseconds", "seconds", "minutes", "hours", "days", "years"

    Settings of milliseconds..hours are truncated towards 0, days are counted
    from January 1st of their respective year, and years are counted from 1 AD.
    This may lead to unexpected rounding if multi-day or multi-year intervals
    are used.

    For example:

    If it is currently 4:15pm on January 3rd, 2007, calling:
    ``tfrac(time.time(), hours=3)``
    returns the UNIX number of seconds corresponding to
    "January 3rd, 2007 15:00:00"
    as the aligned time, and the number of seconds in 1 hour and 15 minutes as
    the fractional part.

    Parameters
    ==========
    t : float
        time in seconds
    ``**time_unit`` : dict
        a single (interval=value) item

    Returns
    =======
    A tuple: (aligned time as UNIX time, remainder in seconds)
    """
    unit, period = time_unit.items()[0]
    if unit == "milliseconds":
        unit = "microsecond"
        period *= 1000
    else:
        unit = unit[:-1]  # strip off the 's'

    # Find the nearest round date
    dt = safe_fromtimestamp(t)
    amt = getattr(dt, unit)
    ndx = datetime_scale.index(unit)
    closest_multiple = int(floor(amt / period) * period)
    if closest_multiple == 0 and unit in ("day", "year"):
        # TODO: this isn't really quite right for intervals of days > 1...
        closest_multiple = 1
    whole = dt.replace(**{unit: closest_multiple})
    whole = whole.replace(**dict(datetime_zeros[:ndx]))
    frac = td_to_sec(dt - whole)

    return dt_to_sec(whole), frac

def _advance_month(dt, months):
    """ Advance a datetime object by a given number of months.
    """
    new_month = dt.month + months
    years, extra_months = divmod(new_month-1, 12)
    new_month = extra_months + 1
    return dt.replace(year=dt.year+years, month=new_month)

def trange_months(start, end, months):
    """ Create a range of timestamps separated by a given number of months.

    The start of the iteration is always aligned to Jan 1 2000.
    """
    dt_start = safe_fromtimestamp(start)
    dt_end = safe_fromtimestamp(end)
    dmonths = (12 * (dt_start.year - 2000) + dt_start.month - 1) % months
    dt = _advance_month(dt_start.replace(day=1, hour=0, minute=0, second=0,
        microsecond=0), -dmonths)
    while dt < dt_start:
        dt = _advance_month(dt, months)
    timestamps = []
    while dt <= dt_end:
        timestamps.append(dt_to_sec(dt))
        dt = _advance_month(dt, months)
    return timestamps

def _advance_years(dt, years):
    """ Advance a datetime object by a given number of years.
    """
    return dt.replace(year=dt.year+years)

def trange_years(start, end, years):
    """ Create a range of timestamps separated by a given number of years.

    The start of the iteration is aligned to Jan 1 2000.
    """
    dt_start = safe_fromtimestamp(start)
    dt_end = safe_fromtimestamp(end)
    dyears = (dt_start.year - 2000) % years
    if dyears < 0:
        dyears += years
    dt = datetime(dt_start.year-dyears, 1, 1, 0, 0, 0, 0)
    while dt < dt_start:
        dt = _advance_years(dt, years)
    timestamps = []
    while dt <= dt_end:
        timestamps.append(dt_to_sec(dt))
        dt = _advance_years(dt, years)
    return timestamps

def trange(start, end, **time_unit):
    """ Like range(), but for times, and with "natural" alignment depending on
    the interval.

    For example::

        t_range(time.time(), time.time()+76*3600, days=2)
        t_range(start, end, months=3)

    Parameters
    ==========
    start, end : float
        Time in seconds.  *end* must be later than *start*.
    time_unit : a single (key, int_value) pair
        The units to use. *key* must be in the list: "milliseconds", "seconds",
        "minutes", "hours", "days", "months", "years".  Months are treated as
        30 days, and years are treated as 365 days.

    Returns
    =======
    A list of times that nicely span the interval, or an empty list if *start*
    and *end* fall within the same interval.
    """
    if len(time_unit) > 1:
        raise ValueError("trange() only takes one keyword argument, got %d" % len(time_unit))

    # Months and years are non-uniform, so we special-case them.
    unit, value = time_unit.items()[0]
    if unit == 'months':
        return trange_months(start, end, value)
    elif unit == 'years':
        return trange_years(start, end, value)

    # Express start and end ticks as (date, frac) where date is calendar-aligned
    # with the interval in time_unit.
    start_whole, start_frac = tfrac(start, **time_unit)
    end_whole, end_frac = tfrac(end, **time_unit)

    # Handle some corner-cases
    if start_whole == end_whole:
        return []

    if start_frac < 1e-6:
        first_tick_ndx = 0
    else:
        first_tick_ndx = 1

    # Convert months and years into days
    time_unit["days"] = time_unit.setdefault("days", 0) + \
                            365 * time_unit.pop("years", 0) + \
                            30 * time_unit.pop("months", 0)
    delta = td_to_sec(timedelta(**time_unit))
    count = (end_whole - start_whole) / delta

    ticks = [start_whole + i*delta for i in range(int(round(count))+1)]
    return ticks[first_tick_ndx:]


class TimeScale(AbstractScale):
    """ A scale based on time intervals and calendar dates. The valid
    intervals are:

    Natural time:
        microseconds, milliseconds, seconds, minutes, hours, days, years
    Calendar time:
        day_of_month, month_of_year

    For calendar times, a list of hours/days/months is set.
    By default, intervals are aligned to January 1st.
    """

    # This is used to compute an approximate resolution for each type of scale.
    SECS_PER_UNIT = {"microseconds": 1e-6,
                     "milliseconds": 1e-3,
                     "seconds": 1,
                     "minutes": 60,
                     "hours": 3600,
                     "days": 24*3600,
                     "day_of_month": 30*24*3600,
                     "month_of_year": 365*24*3600,
                     "years": 365*24*3600,
                     }

    CALENDAR_UNITS = ("day_of_month", "month_of_year")

    def __init__(self, **kw_interval):
        """ Defines the time period that this scale uses.
        """
        self.formatter = kw_interval.pop("formatter", TimeFormatter())
        unit, val = kw_interval.items()[0]
        self.unit = unit
        if "_of_" in unit:
            # Calendar time interval - divide by the number of ticks per larger
            # unit of time to get an average resolution
            if type(val) in (int, float):
                val = [val]
            self.vals = val
            self.resolution = self.SECS_PER_UNIT[unit] / float(len(val))
        else:
            self.val = val
            self.resolution = val * self.SECS_PER_UNIT[unit]
        return

    def num_ticks(self, start, end, desired_ticks=None):
        """ Returns an approximate number of ticks that this scale
        produces for the given interval.

        Implements AbstractScale.
        """
        # This is only approximate, but puts us in the ballpark
        if self.unit in ("milliseconds", "microseconds"):
            ticks = self.ticks(start, end, desired_ticks=8)
            coarsest_scale_count = (end - start) / (500 * self.SECS_PER_UNIT[self.unit])
            return max(len(ticks), coarsest_scale_count)
        else:
            return (end - start) / self.resolution

    def ticks(self, start, end, desired_ticks=None):
        """ Returns the set of "nice" positions on this scale that enclose and
        fall inside the interval (*start*,*end*).

        Implements AbstractScale. The *start* and *end* parameters are
        floating-point seconds since the epoch.
        """

        if self.unit in self.CALENDAR_UNITS:
            return self.cal_ticks(start, end)
        elif self.unit in ("milliseconds", "microseconds"):
            if start == end or (end - start) < self.SECS_PER_UNIT[self.unit]:
                return [start]
            secs_per_unit = self.SECS_PER_UNIT[self.unit]
            start /= secs_per_unit
            end /= secs_per_unit
            if desired_ticks is None:
                min, max, delta = heckbert_interval(start, end, enclose=True)
            else:
                min, max, delta = heckbert_interval(start, end, desired_ticks,
                                                    enclose=True)
            min *= secs_per_unit
            max *= secs_per_unit
            delta *= secs_per_unit
            return frange(min, max, delta)
        else:
            return trange(start, end, **{self.unit: self.val})

    def cal_ticks(self, start, end):
        """ ticks() method for calendar-based intervals """

        # start and end are in seconds since Epoch, get naive datetimes
        try:
            start_dt = datetime.fromtimestamp(start)
        except ValueError:
            start_dt = datetime(MINYEAR, 1, 1, 0, 0, 0)
        try:
            end_dt = datetime.fromtimestamp(end)
        except ValueError:
            end_dt = datetime(MAXYEAR, 1, 1, 0, 0, 0)

        # get range of years of interest
        # add 2 because of python ranges + guard against timezone shifts
        # eg. if 20000101 -> 19991231 because of local timezone, end is 1999+2
        years = range(start_dt.year, min(end_dt.year+2, MAXYEAR+1))
        if self.unit == "day_of_month":
            # get naive datetimes for start of each day of each month
            # in range of years.  Excess will be discarded later.
            months = range(1, 13)
            dates = [datetime(year, month, i)
                     for year in years for month in months for i in self.vals]

        elif self.unit == "month_of_year":
            # get naive datetimes for start of each month in range of years
            dates = [datetime(year, month, 1)
                     for year in years for month in self.vals]
        else:
            raise ValueError("Unknown calendar unit '%s'" % self.unit)

        # safely convert to seconds since epoch
        ticks = [dt_to_sec(date) for date in dates]

        # trim excess timestamps
        ticks = [t for t in ticks if start <= t <= end]

        return ticks

    def labels(self, start, end, numlabels=None, char_width=None):
        """ Returns a series of ticks and corresponding strings for labels
        that fall inside the interval (*start*,*end*).

        Overrides AbstractScale.
        """
        ticks = self.ticks(start, end, numlabels)
        labels = self.formatter.format(ticks, numlabels, char_width, ticker=self)
        return zip(ticks, labels)

    def label_width(self, start, end, numlabels=None, char_width=None):
        """ Returns an estimate of total number of characters used by the
        the labels that this scale will produce for the given set of
        inputs, as well as the number of labels.

        Overrides AbstractScale.
        """
        return self.formatter.estimate_width(start, end, numlabels, char_width,
                                             ticker=self)


# Declare some default scale systems

# Default time scale for hours, minutes, seconds, and milliseconds.
HMSScales = [TimeScale(microseconds=1), TimeScale(milliseconds=1)] + \
            [TimeScale(seconds=dt) for dt in (1, 5, 15, 30)] + \
            [TimeScale(minutes=dt) for dt in (1, 5, 15, 30)] + \
            [TimeScale(hours=dt) for dt in (1, 2, 3, 4, 6, 12, 24)]

# Default time scale for months, days, and years.
MDYScales = [TimeScale(day_of_month=range(1,31,3)),
             TimeScale(day_of_month=(1,8,15,22)),
             TimeScale(day_of_month=(1,15)),
             TimeScale(month_of_year=range(1,13)),
             TimeScale(month_of_year=range(1,13,3)),
             TimeScale(month_of_year=(1,7)),
             TimeScale(month_of_year=(1,)),] + \
            [TimeScale(years=dt) for dt in (1,2,5,10)]

class CalendarScaleSystem(ScaleSystem):
    """ Scale system for calendars.

    This class has a pre-defined set of nice "time points" to use for ticking
    and labelling.
    """

    def __init__(self, *scales, **kw):
        """ Creates a new CalendarScaleSystem.

        If scales are not provided, then it defaults to HMSScales and MDYScales.
        """
        if len(scales) == 0:
            scales = HMSScales + MDYScales
        super(CalendarScaleSystem, self).__init__(*scales, **kw)

    def _get_scale(self, start, end, numticks):
        if len(self.scales) == 0:
            if self.default_scale is not None:
                closest_scale = self.default_scale
            else:
                raise ValueError("CalendarScaleSystem has not be configured "
                                 "with any scales.")
        elif end - start < 1e-6 or end - start > 1e5 * 365 * 24 * 3600:
            closest_scale = self.default_scale
        else:
            closest_scale = self._get_scale_np(start, end, numticks)

        return closest_scale
