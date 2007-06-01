"""
A scale for time and calendar intervals.
"""

from datetime import datetime, timedelta
from math import floor
from time import mktime

from scales import AbstractScale, DefaultScale, ScaleSystem, frange, heckbert_interval
from formatters import TimeFormatter


datetime_scale = ["microsecond", "second", "minute", "hour", "day", "month", "year"]
datetime_zeros = zip(datetime_scale, [0, 0, 0, 0, 1, 1, 1])


__all__ = ["TimeScale", "CalendarScaleSystem", "HMSScales", "MDYScales",
           "trange", "tfrac", "dt_to_sec"]


def td_to_sec(td):
    "Returns the floating point number of seconds in a timedelta object"
    return td.days*24*3600 + td.seconds + td.microseconds*1e-6
     

def dt_to_sec(t):
    """ Returns the floating point number of seconds since UNIX epoch
    corresponding to the given datetime instance.  This is more accurate than
    mktime(t.timetuple()) because it preserves milliseconds.
    """
    tup = t.timetuple()
    try:
        return mktime(tup) + t.microsecond*1e-6
    except OverflowError:
        # Kludge working in PDT only.
        if tup[:6] == (1969, 12, 31, 15, 59, 59):
            return -1 + t.microsecond*1e-6


def tfrac(t, **time_unit):
    """ Performs a calendar-aware split of a time into (aligned_time, frac)
    over an interval that is a multiple of one of the following time units:

        "milliseconds", "seconds", "minutes", "hours", "days", "years"

    Settings of milliseconds..hours are truncated towards 0, days are counted
    from January 1st of their respective year, and years are counted from 1 AD.
    This may lead to unexpected rounding if multi-day or multi-year intervals
    are used.

    For example:
    If it is currently 4:15pm on January 3rd, 2007, calling
        tfrac(time.time(), hours=3)
    returns the UNIX number of seconds corresponding to "January 3rd, 2007 15:00:00"
    as the aligned time and the number of seconds in 1 hour and 15 minutes as the
    fractional part.
    
    Parameters
    ==========
    t: float; time in seconds
    **time_unit: a dict with a single (interval=value) item

    Returns
    =======
    (aligned time as UNIX time, remainder in seconds)
    """
    unit, period = time_unit.items()[0]
    if unit == "milliseconds":
        unit = "microsecond"
        period *= 1000
    else:
        unit = unit[:-1]  # strip off the 's'

    # Find the nearest round date
    dt = datetime.fromtimestamp(t)
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


def trange(start, end, **time_unit):
    """ Like range(), but for times, and with "natural" alignment dependeing on
    the interval.  Example:

        t_range(time.time(), time.time()+76*3600, days=2)
        t_range(start, end, months=3)

    Parameters
    ==========
    start, end: float; time in seconds.  end should be later than start.
    time_unit: a single (key, int_value) pair where key is in the list:
    
                  milliseconds, seconds, minutes, hours, days

    Returns
    =======
    A list of times that nicely span the interval, or an empty list if start
    and end fall within the same interval
    """

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

    unit, period = time_unit.items()[0]
    delta = td_to_sec(timedelta(**time_unit))
    count = (end_whole - start_whole) / delta
               
    ticks = [start_whole + i*delta for i in range(int(round(count))+1)]
    return ticks[first_tick_ndx:]



class TimeScale(AbstractScale):
    """ A scale based on time intervals and calendar dates. The valid
    intervals are:

    Natural time:
        milliseconds, seconds, minutes, hours, days, years
    Calendar time:
        day_of_month, month_of_year

    for calendar times, a list of hours/days/months is set.
    By default, intervals are aligned to January 1st.
    """

    # This is used to compute an approximate resolution for each type of scale
    SECS_PER_UNIT = {"milliseconds": 1e-3,
                     "seconds": 1,
                     "minutes": 60,
                     "hours": 3600,
                     "days": 24*3600,
                     "day_of_month": 30*24*3600,
                     "month_of_year": 365*24*3600 }

    CALENDAR_UNITS = ("day_of_month", "month_of_year")

    def __init__(self, **kw_interval):
        """ Defines the time period that this scale uses.  See the class docstring
        for valid intervals.
        """
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
        self.formatter = kw_interval.get("formatter", TimeFormatter())
        return
    
    def num_ticks(self, start, end, desired_ticks=None):
        # This is only approximate, but puts us in the ballpark
        if self.unit == "milliseconds":
            ticks = self.ticks(start, end, desired_ticks=8)
            coarsest_scale_count = (end - start) / 0.500
            return max(len(ticks), coarsest_scale_count)
        else:
            return (end - start) / self.resolution

    def ticks(self, start, end, desired_ticks=None):
        """ Start and end are floating-point seconds since the epoch. """
        
        if self.unit in self.CALENDAR_UNITS:
            return self.cal_ticks(start, end)
        elif self.unit == "milliseconds":
            if start == end:
                return [start]
            start *= 1000
            end *= 1000
            min, max, delta = heckbert_interval(start, end, desired_ticks, enclose=True)
            min /= 1000
            max /= 1000
            delta /= 1000
            return frange(min, max, delta)
        else:
            return trange(start, end, **{self.unit: self.val})

    def cal_ticks(self, start, end):
        start = datetime.fromtimestamp(start)
        end = datetime.fromtimestamp(end)

        if self.unit == "day_of_month":
            s = start.year + 1/12.0 * start.month
            e = end.year + 1/12.0 * end.month
            num_months = int(round((e - s) * 12)) + 1   # add 1 for fencepost
            start_year = start.year
            start_month = start.month
            ym = [divmod(i, 12) for i in range(start_month-1, start_month-1+num_months)]
            months = [start.replace(year=start_year+y, month=m+1, day=1) for (y,m) in ym]
            ticks = [dt.replace(day=i) for dt in months for i in self.vals]

        elif self.unit == "month_of_year":
            years = [start.replace(year=newyear, day=1) for newyear in range(start.year, end.year+1)]
            ticks = [dt.replace(month=i, day=1) for dt in years for i in self.vals]
            
        else:
            raise ValueError("Unknown calendar unit '%s'" % self.unit)

        if len(ticks) > 0:
            # Find the first and last index in all_ticks that falls within (start,end)
            for start_ndx in range(len(ticks)):
                if ticks[start_ndx] >= start:
                    break
            for end_ndx in range(len(ticks)-1, 0, -1):
                if ticks[end_ndx] <= end:
                    break
            ticks = ticks[start_ndx : end_ndx+1]

        return map(dt_to_sec, ticks)

    def labels(self, start, end, numlabels=None, char_width=None):
        ticks = self.ticks(start, end, numlabels)
        labels = self.formatter.format(ticks, numlabels, char_width, ticker=self)
        return zip(ticks, labels)

    def label_width(self, start, end, numlabels=None, char_width=None):
        """ Returns an estimate of total number of characters used by the
        the labels that this scale will produce for the given set of
        inputs, as well as the number of labels.

        Returns: (numlabels, total label width)
        """
        return self.formatter.estimate_width(start, end, numlabels, char_width,
                                             ticker=self)


# Declare some default scale systems

HMSScales = [TimeScale(milliseconds=1)] + \
            [TimeScale(seconds=dt) for dt in (1, 5, 15, 30)] + \
            [TimeScale(minutes=dt) for dt in (1, 5, 15, 30)] + \
            [TimeScale(hours=dt) for dt in (1, 2, 3, 4, 6, 12, 24)]

MDYScales = [TimeScale(day_of_month=range(1,31,3)),
             TimeScale(day_of_month=(1,8,15,22)),
             TimeScale(day_of_month=(1,15)),
             TimeScale(month_of_year=range(1,13)),
             TimeScale(month_of_year=range(1,13,3)),
             TimeScale(month_of_year=(1,7)),
             TimeScale(month_of_year=(1,))]

class CalendarScaleSystem(ScaleSystem):
    """ Scale system for calendars.  Has a pre-defined set of nice "time points"
    to use for ticking and labelling.
    """

    def __init__(self, *scales, **kw):
        """ Creates a new CalendarScaleSystem.

        If scales are not provided, then defaults to HMSScales and MDYScales.
        """
        if len(scales) == 0:
            scales = HMSScales + MDYScales
        super(CalendarScaleSystem, self).__init__(*scales, **kw)
        self.default_scale = None

    def _get_scale(self, start, end, numticks):
        if len(self.scales) == 0:
            if self.default_scale is not None:
                closest_scale = self.default_scale
            else:
                raise ValueError("CalendarScaleSystem has not be configured with any scales.")
        else:
            closest_scale = self._get_scale_np(start, end, numticks)
            if list(self.scales).index(closest_scale) in (0, len(self.scales)-1) and \
                   self.default_scale is not None:
                # Handle the edge cases and see if there is a major discrepancy between
                # what the scales offer and the desired number of ticks; if so, revert
                # to using the default scale
                approx_ticks = closest_scale.num_ticks(start, end, numticks)
                if (approx_ticks == 0) or (numticks == 0) or \
                       (abs(approx_ticks - numticks) / numticks > 1.5) or \
                       (abs(numticks - approx_ticks) / approx_ticks > 1.5):
                    closest_scale = self.default_scale
        return closest_scale
