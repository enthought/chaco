"""
Functions and classes that compute ticks and labels for graph axes, with 
special handling of time and calendar axes.
"""

from bisect import bisect
from math import ceil, floor, log10
from numpy import abs, argmin, array, isnan, linspace

# Local imports
from formatters import BasicFormatter


__all__ = ["AbstractScale", "DefaultScale", "FixedScale", "Pow10Scale",
           "LogScale", "ScaleSystem", "heckbert_interval", "frange"]

def frange(min, max, delta):
    """ Floating point range. """
    count = int(round((max - min) / delta)) + 1
    return [min + i*delta for i in range(count)]

class AbstractScale(object):
    """ Defines the general interface for scales. """

    DEFAULT_NUM_TICKS = 8

    def ticks(self, start, end, desired_ticks=None):
        """ Returns the set of "nice" positions on this scale that enclose and
        fall inside the interval (*start*,*end*). 
        
        Parameters
        ----------
        start : number
            The beginning of the scale interval.
        end : number
            The end of the scale interval.
        desired_ticks : integer
            Number of ticks that the caller would like to get
        
        """
        raise NotImplementedError

    def num_ticks(self, start, end, desired_ticks=None):
        """ Returns an approximate number of ticks that this scale 
        produces for the given interval.  
        
        This method is used by the scale system to determine whether this is 
        the appropriate scale to use for an interval; the returned number of
        ticks does not have to be exactly the same as what ticks() returns.

        Parameters
        ----------
        start : number
            The beginning of the scale interval.
        end : number
            The end of the scale interval.
        desired_ticks : integer
            Number of ticks that the caller would like to get
        
        Returns
        -------
        A float or an integer.
        """
        raise NotImplementedError

    def labels(self, start, end, numlabels=None, char_width=None):
        """ Returns a series of ticks and corresponding strings for labels
        that fall inside the interval (*start*,*end*).

        Parameters
        ----------
        start : number
            The beginning of the scale interval.
        end : number
            The end of the scale interval.
        numlabels : number
            The ideal number of labels to generate on the interval. 
        char_width : number
            The total character width available for labelling the interval.  
            
        One of *numlabels* or *char_width* must be provided. If both are 
        provided, then both are considered when picking label density and format.
        """
        ticks = self.ticks(start, end, numlabels)
        labels = self.formatter.format(ticks, numlabels, char_width)
        return zip(ticks, labels)

    def label_width(self, start, end, numlabels=None, char_width=None):
        """ Returns an estimate of the total number of characters used by the
        the labels that this scale produces for the given set of
        inputs, as well as the number of labels.
        
        Parameters
        ----------
        start : number
            The beginning of the scale interval.
        end : number
            The end of the scale interval.
        numlabels : number
            The ideal number of labels to generate on the interval. 
        char_width : number
            The total character width available for labelling the interval.  

        Returns
        -------
        (numlabels, total label width)
        """
        return self.formatter.estimate_width(start, end, numlabels, char_width,
                                             ticker=self)

        
class FixedScale(AbstractScale):
    """ A scale with fixed resolution, and "nice" points that line up at
    multiples of the resolution.  An optional zero value can be defined
    that offsets the "nice" points to (N*resolution+zero).
    """
    def __init__(self, resolution, zero=0.0, formatter=None):
        self.resolution = resolution
        self.zero = zero
        if formatter is None:
            formatter = BasicFormatter()
        self.formatter = formatter
        
    def ticks(self, start, end, desired_ticks=None):
        """ For FixedScale, *desired_ticks* is ignored. 
        
        Overrides AbstractScale.
        """
        if start == end or isnan(start) or isnan(end):
            return []
        res = self.resolution
        start -= self.zero
        end -= self.zero
        start_tick = int(ceil(start / res))
        end_tick = int(floor(end / res))
        ticks = [i*res for i in range(start_tick, end_tick+1)]
        return ticks

    def num_ticks(self, start, end, desired_ticks=None):
        """ For FixedScale, *desired_ticks* is ignored. 
        
        Overrides AbstractScale.
        """
        if self.resolution is None or self.resolution == 0.0:
            return 0
        else:
            return (end - start) / self.resolution

def _nice(x, round=False):
    """ Returns a bracketing interval around interval *x*, whose endpoints fall
    on "nice" values.  If *round* is False, then it uses ceil(range)
    
    This function is adapted from the original in Graphics Gems; the boundaries
    have been changed to use (1, 2.5, 5, 10) as the nice values instead of
    (1, 2, 5, 10).
    """

    expv = floor(log10(x))
    f = x / pow(10, expv)
    if round:
        if f < 1.75:
            nf = 1.0
        elif f < 3.75:
            nf = 2.5
        elif f < 7.0:
            nf = 5.0;
        else:
            nf = 10.0
    else:
        if f <= 1.0:
            nf = 1.0
        elif f <= 2.5:
            nf = 2.5
        elif f <= 5.0:
            nf = 5.0
        else:
            nf = 10.0
    return nf * pow(10, expv)

def heckbert_interval(data_low, data_high, numticks=8, nicefunc=_nice, enclose=False):
    """ Returns a "nice" range and resolution for an interval and a preferred
    number of ticks, using Paul Heckbert's algorithm in Graphics Gems.

    If *enclose* is True, then the function returns a min and a max that fall
    inside *data_low* and *data_high*; if *enclose* is False, the nice interval
    can be larger than the input interval.
    """
    if data_high == data_low:
        return data_high, data_low, 0
    if numticks == 0:
        numticks = 1

    range = nicefunc(data_high - data_low)
    if numticks > 1:
        numticks -= 1
    d = nicefunc(range / numticks, round=True)
    if enclose:
        graphmin = ceil(data_low / d) * d
        graphmax = floor(data_high / d) * d
    else:
        graphmin = floor(data_low / d) * d
        graphmax = ceil(data_high / d) * d
    return graphmin, graphmax, d


class DefaultScale(AbstractScale):
    """ A dynamic scale that tries to place ticks at nice numbers (1, 2, 5, 10)
    so that ticks don't "pop" as the resolution changes.
    """
    def __init__(self, formatter=None):
        if formatter is None:
            formatter = BasicFormatter()
        self.formatter = formatter
        
    def ticks(self, start, end, desired_ticks=8):
        """ Returns the set of "nice" positions on this scale that enclose and
        fall inside the interval (*start*,*end*). 
        
        Implements AbstractScale.
        """
        if start == end or isnan(start) or isnan(end):
            return [start]
        min, max, delta = heckbert_interval(start, end, desired_ticks, enclose=True)
        return frange(min, max, delta)

    def num_ticks(self, start, end, desired_ticks=8):
        """ Returns an approximate number of ticks that this scale 
        produces for the given interval.  
        
        Implements AbstractScale.
        """
        return len(self.ticks(start, end, desired_ticks))


class Pow10Scale(AbstractScale):
    """ A dynamic scale that shows only whole multiples of powers of 10 
    (including powers < 1).
    """

    def __init__(self, formatter=None):
        if formatter is None:
            formatter = BasicFormatter()
        self.formatter = formatter

    def ticks(self, start, end, desired_ticks=8):
        """ Returns the set of "nice" positions on this scale that enclose and
        fall inside the interval (*start*,*end*). 

        Implements AbstractScale.
        """
        if start == end or isnan(start) or isnan(end):
            return [start]
        min, max, delta = heckbert_interval(start, end, desired_ticks,
                                            nicefunc=self._nice_pow10,
                                            enclose = True)
        return frange(min, max, delta)
    
    def num_ticks(self, start, end, desired_ticks=8):
        """ Returns an approximate number of ticks that this scale 
        produces for the given interval.  
        
        Implements AbstractScale.
        """
        return len(self.ticks(start, end, desired_ticks))

    def _nice_pow10(self, x, round=False):
        return pow(10, floor(log10(x)))


class LogScale(AbstractScale):
    """ A dynamic scale that only produces ticks and labels that work well when
    plotting data on a logarithmic scale.
    """
    def __init__(self, formatter=None):
        if formatter is None:
            formatter = BasicFormatter()
        self.formatter = formatter

    def ticks(self, start, end, desired_ticks=8):

        magic_numbers = [1, 2, 5]
        
        if start > end:
            start, end = end, start

        if start == 0.0:
            # Whoever calls us with a value of 0.0 puts themselves at our mercy
            log_start = 1e-9
        else:
            log_start = log10(start)

        if end == 0.0:
            log_end = 1e-9
        else:
            log_end = log10(end)
        log_interval = log_end - log_start

        if log_interval < 1.0:
            # If the data is spaced by less than a factor of 10, then use
            # regular/linear ticking
            min, max, delta = heckbert_interval(start, end, desired_ticks,
                                                                enclose=True)
            return frange(min, max, delta)

        elif log_interval < desired_ticks:
            for interval in magic_numbers:
                ticklist = []
                for exp in range(int(floor(log_start)),
                                    int(ceil(log_end))+(interval==1)):
                    for multiplier in linspace(interval, 10.0,
                                               round(10.0/interval)-(interval==1),
                                               endpoint=(interval != 1)):
                        tick = 10**exp * multiplier
                        if start <= tick <= end:
                            ticklist.append(tick)
                        elif tick > end:
                            break
                if len(ticklist) < desired_ticks * 1.5:
                    return ticklist
            return ticklist
        
        else:
            # Put lines at every power of ten
            startlog = ceil(log_start)
            endlog = floor(log_end)
            expticks = linspace(startlog, endlog, endlog - startlog + 1)
            return 10**expticks

    def num_ticks(self, start, end, desired_ticks=8):
        """ Returns an approximate number of ticks that this scale 
        produces for the given interval.  
        
        Implements AbstractScale.
        """
        return len(self.ticks(start, end, desired_ticks))

##############################################################################
#
# ScaleSystem
#
##############################################################################

class ScaleSystem(object):
    """ Represents a collection of scales over some range of resolutions.  
    
    This class has settings for a default scale that is used when ticking an 
    interval that is smaller than the finest resolution scale or larger than
    the coarsest resolution scale.
    """

    def __init__(self, *scales, **kw):
        """ Creates a ScaleSystem

        Usage::
            
            ScaleSystem(scale1, .., scaleN, default_scale = DefaultScale())

        If *default_scale* is not specified, then an instance of DefaultScale()
        is created.  If no *default_scale* is needed, then set it to None.
        """
        self.scales = scales
        self.default_scale = kw.get("default_scale", DefaultScale())

        # Heuristics for picking labels
        # The ratio of total label character count to the available character width
        self.fill_ratio = 0.3
        self.default_numticks = 8


    def ticks(self, start, end, numticks=None):
        """ Computes nice locations for tick marks.

        Parameters
        ==========
        start, end : number
            The start and end values of the data.
        numticks : number
            The desired number of ticks to produce.
        scales : a list of tuples of (min_interval, Scale) 
            Scales to use, in order from fine resolution to coarse.  
            If the end-start interval is less than a particular scale's 
            *min_interval*, then the previous scale is used.

        Returns
        =======
        A list of positions where the ticks are to be placed.
        """

        if numticks == 0:
            return []
        elif start == end or isnan(start) or isnan(end):
            return []
        elif numticks is None:
            numticks = self.default_numticks

        scale = self._get_scale(start, end, numticks)
        ticks = scale.ticks(start, end, numticks)
        return ticks

    def labels(self, start, end, numlabels=None, char_width=None):
        """ Computes position and labels for an interval

        Parameters
        ----------
        start : number
            The beginning of the scale interval.
        end : number
            The end of the scale interval.
        numlabels : number
            The ideal number of labels to generate on the interval. 
        char_width : number
            The total character width available for labelling the interval.  
        
        One of *numlabels* or *char_width* must be provided.  If both are
        provided, then both are considered when picking label density and format.

        Returns
        -------
        A list of (tick position, string) tuples.
        """
        if numlabels == 0 or char_width == 0 or isnan(start) or isnan(end):
            return []

        # There are three cases:
        #   1. we are given numlabels but not char_width
        #   2. we are given char_width and not numlabels
        #   3. we are given both
        #
        # Case 1: Use numlabels to find the closest scale purely on tick count.
        # Case 2: Query all scales for their approximate label_width, pick the
        #         closest one to char_width * self.fill_ratio
        # Case 3: Use numlabels to find the closest scale based on tick count.

        if numlabels and not char_width:
            scale = self._get_scale(start, end, numlabels)
            labels = scale.labels(start, end, numlabels)

        elif char_width:
            if numlabels:
                scale = self._get_scale(start, end, numlabels)
                try:
                    ndx = list(self.scales).index(scale)
                    low = max(0, ndx - 1)
                    high = min(len(self.scales), ndx + 1)
                    scales = self.scales[low:high]
                except ValueError:
                    scales = [scale]
            else:
                if len(self.scales) == 0:
                    scales = [self.default_scale]
                else:
                    scales = self.scales

            counts, widths = zip(*[s.label_width(start, end, char_width=char_width) \
                                      for s in scales])
            widths = array(widths)
            closest = argmin(abs(widths - char_width*self.fill_ratio))
            if numlabels is None:
                numlabels = scales[closest].num_ticks(start, end, counts[closest])
            labels = scales[closest].labels(start, end, numlabels,
                                            char_width=char_width)

        return labels
            

    def _get_scale(self, start, end, numticks):
        if len(self.scales) == 0:
            closest_scale = self.default_scale
        else:
            closest_scale = self._get_scale_np(start, end, numticks)

            if self.default_scale is not None:
                # Handle the edge cases and see if there is a major discrepancy between
                # what the scales offer and the desired number of ticks; if so, revert
                # to using the default scale
                approx_ticks = closest_scale.num_ticks(start, end, numticks)
                if (approx_ticks == 0) or (numticks == 0) or \
                       (abs(approx_ticks - numticks) / numticks > 1.2) or \
                       (abs(numticks - approx_ticks) / approx_ticks > 1.2):
                    closest_scale = self.default_scale
        return closest_scale

    def _get_scale_bisect(self, start, end, numticks):
        scale_intervals = [s.num_ticks(start, end, numticks) for s in self.scales]
        sorted_scales = sorted(zip(scale_intervals, self.scales))
        ndx = bisect(sorted_scales, numticks, lo=0, hi=len(self.scales))
        if ndx == len(self.scales):
            ndx -= 1
        return sorted_scales[ndx][1]

    def _get_scale_np(self, start, end, numticks):
        # Extract the intervals from the scales we were given
        scale_intervals = array([s.num_ticks(start, end, numticks) for s in self.scales])
        closest = argmin(abs(scale_intervals - numticks))
        return self.scales[closest]

