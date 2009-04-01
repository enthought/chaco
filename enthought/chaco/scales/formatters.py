"""
Classes for formatting labels for values or times.
"""

from math import ceil, floor, fmod, log10
from numpy import abs, all, array, asarray, amax, amin
from safetime import strftime, time
from time import localtime


__all__ = ['NullFormatter', 'BasicFormatter', 'IntegerFormatter',
    'OffsetFormatter', 'TimeFormatter']

class NullFormatter(object):
    """ Formatter for empty labels.
    """
    def format(ticks, numlabels=None, char_width=None):
        """ Returns a list containing an empty label for each item in *ticks*.
        """
        return [""] * len(ticks)

    def estimate_width(start, end, numlabels=None, char_width=None):
        """ Returns 0 for width and 0 for number of labels.
        """
        return 0, 0
    

class BasicFormatter(object):
    """ Formatter for numeric labels.
    """
    # This is a class-level default that is related to the algorithm in format()
    avg_label_width = 7.0

    # Toggles whether or not to use scientific notation when the values exceed
    # scientific_limits
    use_scientific = True
    
    # Any number smaller than 10 ** limits[0] or larger than 10 ** limits[1]
    # will be represented using scientific notiation.
    scientific_limits = (-3, 5)

    def __init__(self, **kwds):
        # Allow the user to override the class-level defaults.
        self.__dict__.update(kwds)

    def oldformat(self, ticks, numlabels=None, char_width=None):
        """ This function is adapted from matplotlib's "OldScalarFormatter".
        
        Parameters
        ----------
        ticks : array of numbers
            The tick values to be formatted.
        numlabels
            Not used.
        char_width
            Not used.
            
        Returns
        -------
        List of formatted labels.
        """
        labels = []
        if len(ticks) == 0:
            return []
        
        d = abs(ticks[-1] - ticks[0])
        for x in ticks:
            if abs(x)<1e4 and x==int(x):
                labels.append('%d' % x)
                continue

            if d < 1e-2: fmt = '%1.3e'
            elif d < 1e-1: fmt = '%1.3f'
            elif d > 1e5: fmt = '%1.1e'
            elif d > 10 : fmt = '%1.1f'
            elif d > 1 : fmt = '%1.2f'
            else: fmt = '%1.3f'
            s =  fmt % x
            tup = s.split('e')
            if len(tup)==2:
                mantissa = tup[0].rstrip('0').rstrip('.')
                sign = tup[1][0].replace('+', '')
                exponent = tup[1][1:].lstrip('0')
                if sign or exponent:
                    s = '%se%s%s' %(mantissa, sign, exponent)
                else:
                    s = mantissa
            else:
                s = s.rstrip('0').rstrip('.')
            labels.append(s)
        return labels

    def format(self, ticks, numlabels=None, char_width=None, fill_ratio=0.3):
        """ Does "nice" formatting of floating-point numbers.  *numlabels* is
        ignored in this method.
        """
        if len(ticks) == 0:
            return []

        ticks = asarray(ticks)
        if self.use_scientific:
            scientific = (((ticks % 10 ** self.scientific_limits[1]) == 0) | 
                          (abs(ticks) <= 10 ** self.scientific_limits[0])).all()
        else:
            scientific = False
        
        if scientific:
            if char_width is not None:
                # We need to determine how many digits we can use in the
                # mantissa based on the order of magnitude of the exponent.
                chars_per_label = int(char_width * fill_ratio / len(ticks))
                maxtick = amax(abs(ticks))
                if maxtick > 0:
                    exp_oom = str(int(floor(log10(maxtick))))
                else:
                    exp_oom = "0"
                emax = len(exp_oom)

                if chars_per_label < emax:
                    # We're sort of hosed.  Use a minimum 3 chars for the mantissa.
                    mmax = 3
                else:
                    mmax = chars_per_label - emax - 1
            else:
                mmax = -1
            labels = [self._nice_sci(x, mmax) for x in ticks]

        else:
            # For decimal mode, 
            if not (ticks % 1).any():
                labels = map(str, ticks.astype(int))
            else:
                labels = map(str, ticks)

        return labels

    def _nice_sci(self, val, mdigits, force_sign=False):
        """ Formats *val* nicely using scientific notation.  *mdigits* is the
        max number of digits to use for the mantissa.  If *force_sign* is True,
        then always show the sign of the mantissa, otherwise only show the sign
        if *val* is negative.
        """
        if val != 0:
            e = int(floor(log10(abs(val))))
        else:
            e = 0
        m = val / float(10**e)
        m_str = str(m)

        # Safely truncating the mantissa is somewhat tricky.  The minimum
        # length of the mantissa is everything up to (but not including) the
        # period.  If the m_str doesn't have a decimal point, then we have to
        # ignore mdigits.
        if mdigits > 0 and "." in m_str:
            max_len = max(m_str.index("."), mdigits)
            m_str = m_str[:max_len]
        
            # Strip off a trailing decimal 
            if m_str[-1] == ".":
                m_str = m_str[:-1]
            
            # It's not sufficient just to truncate the string; we need to
            # handle proper rounding

        else:
            # Always strip off a trailing decimal
            if m_str[-1] == ".":
                m_str = m_str[:-1]
        
        if force_sign and not m_str.startswith("-"):
            m_str = "+" + m_str

        if e != 0:
            # Clean up the exponent
            e_str = str(e)
            
            if e_str.startswith("+") and not force_sign:
                e_str = e_str[1:]
            m_str += "e" + e_str

        return m_str


    def estimate_width(self, start, end, numlabels=None, char_width=None,
                       fill_ratio=0.3, ticker=None):
        """ Returns an estimate of the total number of characters used by the
        the labels for the given set of inputs, as well as the number of labels.
        
        Parameters
        ----------
        start : number
            The beginning of the interval.
        end : number
            The end of the interval.
        numlabels : number
            The ideal number of labels to generate on the interval. 
        char_width : number
            The total character width available for labelling the interval.
        fill_ratio : 0.0 < float <= 1.0
            Ratio of the available width that will be occupied by label text.
        ticker : AbstractScale object
            Object that can calculate the number of labels needed.

        Returns
        -------
        (numlabels, total label width)
        """
        if numlabels == 0 or char_width == 0:
            return 0, 0
        
        # use the start and end points as ticks and average their label sizes
        labelsizes = map(len, self.format([start, end]))
        avg_size = sum(labelsizes) / 2.0

        if ticker:
            if numlabels:
                initial_estimate = numlabels
            elif char_width:
                initial_estimate = round(fill_ratio * char_width / avg_size)

            est_ticks = ticker.num_ticks(start, end, initial_estimate)

        elif numlabels:
            est_ticks = numlabels
        
        elif char_width:
            est_ticks = round(fill_ratio * char_width / avg_size)

        return est_ticks, est_ticks * avg_size


class IntegerFormatter(BasicFormatter):
    """ Format integer tick labels as integers.
    """

    def format(self, ticks, numlabels=None, char_width=None, fill_ratio=0.3):
        """ Formats integer tick labels.
        """
        return map(str, map(int, ticks))


class OffsetFormatter(BasicFormatter):
    """ This formatter is like BasicFormatter, but it supports formatting
    ticks using an offset.  This is useful for viewing small ranges within
    big numbers.
    """

    # Whether or not to use offsets when labelling the ticks.  Note that
    # even if this is true, offset are only used when the ratio of the data
    # range to the average data value is smaller than a threshold.
    use_offset = False

    # The threshold ratio of the data range to the average data value, below
    # which "offset" display mode will be used if use_offset is True.
    offset_threshold = 1e-3
    
    # Determines which ticks to display the offset value at.  Can be "all",
    # "firstlast", or "none".
    offset_display = "firstlast"

    # Determines which format to use to display the end labels.  Can be
    # "offset" or "sci".
    end_label_format = "offset"

    # Specifies the threshold values 
    offset_limits = (-3, 4)

    # There are two possible formats for the offset.
    #
    # "sci"
    #     uses scientific notation for the offset
    # "decimal"
    #     pads with zeroes left or right until the decimal
    #
    # The following table shows some example ranges and how an intermediate
    # tick will be displayed.  These all assume an offset_display value of
    # "none" or "firstlast".
    # 
    #  ============     ==========       =========      =========
    #     start            end             sci          decimal  
    #  ============     ==========       =========      =========
    #    90.0004         90.0008         5.0e-4          .0005   
    #    90.0004         90.0015         1.2e-3          .0012   
    #   -1200015        -1200003           12              12    
    #    2300015000     2300015030       1.502e4         15020   
    #  ============     ==========       =========      =========
    #
    offset_format = "sci"

    # The offset generated by the last call to format()
    offset = None


    def _compute_offset(self, ticks):
        first, last = ticks[0], ticks[-1]
        data_range = ticks[-1] - ticks[0]
        range_oom = int(ceil(log10(data_range)))
        pow_of_ten = 10 ** range_oom
        if all(asarray(ticks) < 0):
            return ceil(amax(ticks) / pow_of_ten) * pow_of_ten
        else:
            return floor(amin(ticks) / pow_of_ten) * pow_of_ten
        

    def format(self, ticks, numlabels=None, char_width=None):
        if len(ticks) == 0:
            return []
        
        data_range = ticks[-1] - ticks[0]
        avg_data = sum(abs(ticks)) / len(ticks)
        if self.use_offset and data_range/avg_data < self.offset_threshold:
            offset = self._compute_offset(ticks)
            intermed_ticks = asarray(ticks) - offset

            if self.offset_format == "sci":
                labels = BasicFormatter.format(self, intermed_ticks)
            else:
                # have to decide between %d and %f here.  also have to
                # strip trailing "0"s.. test with %g.
                labels = ["%g" % i for i in intermed_ticks]

            if offset > 0:
                sign = "+"
            else:
                sign = ""
            offset_str = BasicFormatter.format(self, [offset])[0] + sign
            if self.offset_display == "firstlast":
                if self.end_label_format == "offset":
                    labels[0] = offset_str + labels[0]
                    labels[-1] = offset_str + labels[-1]
                else:
                    labels[0] = BasicFormatter.format(self, [ticks[0]])[0]
                    labels[-1] = BasicFormatter.format(self, [ticks[-1]])[0]

            elif self.offset_display == "all":
                labels = [offset_str + label for label in labels]
            
            return labels
        else:
            return BasicFormatter.format(self, ticks, numlabels, char_width)
    
    def estimate_width(self, start, end, numlabels=None, char_width=None,
                       fill_ratio=0.3, ticker=None):
        if numlabels == 0 or char_width == 0:
            return (0, 0)

        if ticker:
            if numlabels:
                initial_estimate = numlabels
            elif char_width:
                avg_size = len("%g%g" % (start, end)) / 2.0
                initial_estimate = round(fill_ratio * char_width / avg_size)
            est_ticks = int(ticker.num_ticks(start, end, initial_estimate))

        elif numlabels:
            est_ticks = numlabels

        elif char_width:
            est_ticks = round(fill_ratio * char_width / avg_size)
        
        start, mid, end = map(len, self.format([start, (start+end)/2.0, end]))
        if est_ticks > 2:
            size = start + end + (est_ticks-2) * mid
        else:
            size = start + end

        return est_ticks, size


def strftimeEx(fmt, t, timetuple=None):
    """
    Extends time.strftime() to format milliseconds and microseconds.
    
    Expects input to be a floating-point number of seconds since epoch.
    The formats are:
        
    - ``%(ms)``:  milliseconds
    - ``%(us)``:  microseconds
    """

    if "%(ms)" in fmt:
        ms = round(fmod(t, 1) * 1000)
        fmt = fmt.replace("%(ms)", "%03d" % ms)

    if "%(us)" in fmt:
        us = round(fmod(t, 1e-3) * 1000000)
        fmt = fmt.replace("%(us)", "%03d" % us)

    if not timetuple:
        timetuple = localtime(t)
    return strftime(fmt, timetuple)
    

class TimeFormatter(object):
    """ Formatter for time values.
    """
    # This table of format is convert into the 'formats' dict.  Each tuple of
    # formats must be ordered from shortest to longest.  Use %T for milliseconds.
    _formats = {
        'microseconds': ('%(us)us', '%(ms).%(us)'),
        'milliseconds': ('%(ms)ms', '%S.%(ms)s'),
        'seconds': (':%S', '%Ss'),
        'minsec': ('%M:%S',), # '%Mm%S', '%Mm%Ss'),
        'minutes': ('%Mm',),
        'hourmin': ('%H:%M',), #'%Hh%M', '%Hh%Mm', '%H:%M:%S','%Hh %Mm %Ss'),
        'hours': ('%Hh', '%H:%M'),
        'days': ('%m/%d', '%a%d',),
        'months': ('%m/%Y', '%b%y'),
        'years': ("'%y", '%Y')
        }

    # Labels of time units, from finest to coarsest.
    format_order = ['microseconds', 'milliseconds', 'seconds', 'minsec', 'minutes',
                    'hourmin', 'hours', 'days', 'months', 'years']
     
    # A dict whose are keys are the strings in **format_order**; each value is
    # two arrays, (widths, format strings).
    formats = {}

    # Whether or not to strip the leading zeros on tick labels.
    strip_leading_zeros = True

    def __init__(self, **kwds):
        self.__dict__.update(kwds)
        self._compute_format_weights()

    def _compute_format_weights(self):
        if self.formats:
            return
        
        for fmt_name, fmt_strings in self._formats.items():
            sizes = []
            tmptime = time()
            for s in fmt_strings:
                size = len(strftimeEx(s, tmptime))
                sizes.append(size)
            self.formats[fmt_name] = (array(sizes), fmt_strings)
        return

    def _get_resolution(self, resolution, interval):
        r = resolution
        span = interval
        if r < 5e-4:
            resol = "microseconds"
        elif r < 0.5:
            resol = "milliseconds"
        elif r < 60:
            if span > 60:
                resol = "minsec"
            else:
                resol = "seconds"
        elif r < 3600:
            if span > 3600:
                resol = "hourmin"
            else:
                resol = "minutes"
        elif r < 24*3600:
            resol = "hours"
        elif r < 30*24*3600:
            resol = "days"
        elif r < 365*24*3600:
            resol = "months"
        else:
            resol = "years"
        return resol
        
    def format(self, ticks, numlabels=None, char_width=None, fill_ratio = 0.3,
               ticker=None):
        """ Formats a set of time values.
                
        Parameters
        ----------
        ticks : array of numbers
            The tick values to be formatted
        numlabels
            Not used.
        char_width : number
            The total character width available for labelling the interval.
        fill_ratio : 0.0 < float <= 1.0
            Ratio of the available width that will be occupied by label text.
        ticker : AbstractScale object
            Object that can calculate the number of labels needed.
            
        Returns
        -------
        List of formatted labels.

        """
        # In order to pick the right set of labels, we need to determine
        # the resolution of the ticks.  We can do this using a ticker if
        # it's provided, or by computing the resolution from the actual
        # ticks we've been given.
        if len(ticks) == 0:
            return []

        span = abs(ticks[-1] - ticks[0])
        if ticker:
            r = ticker.resolution
        else:
            r = span / (len(ticks) - 1)
        resol = self._get_resolution(r, span)

        widths, formats = self.formats[resol]
        format = formats[0]
        if char_width:
            # If a width is provided, then we pick the most appropriate scale,
            # otherwise just use the widest format
            good_formats = array(formats)[widths * len(ticks) < fill_ratio * char_width]
            if len(good_formats) > 0:
                format = good_formats[-1]

        # Apply the format to the tick values
        labels = []
        resol_ndx = self.format_order.index(resol)

        # This dictionary maps the name of a time resolution (in self.format_order)
        # to its index in a time.localtime() timetuple.  The default is to map
        # everything to index 0, which is year.  This is not ideal; it might cause
        # a problem with the tick at midnight, january 1st, 0 a.d. being incorrectly
        # promoted at certain tick resolutions.
        time_tuple_ndx_for_resol = dict.fromkeys(self.format_order, 0)
        time_tuple_ndx_for_resol.update( {
                "seconds" : 5,
                "minsec" : 4,
                "minutes" : 4,
                "hourmin" : 3,
                "hours" : 3,
                })

        # As we format each tick, check to see if we are at a boundary of the
        # next higher unit of time.  If so, replace the current format with one
        # from that resolution.  This is not the best heuristic in the world,
        # but it works!  There is some trickiness here due to having to deal
        # with hybrid formats in a reasonable manner.
        for t in ticks:
            tm = localtime(t)
            s = strftimeEx(format, t, tm)

            hybrid_handled = False
            next_ndx = resol_ndx

            # The way to check that we are at the boundary of the next unit of
            # time is by checking that we have 0 units of the resolution, i.e.
            # we are at zero minutes, so display hours, or we are at zero seconds,
            # so display minutes (and if that is zero as well, then display hours).
            while tm[ time_tuple_ndx_for_resol[self.format_order[next_ndx]] ] == 0:
                next_ndx += 1
                if next_ndx == len(self.format_order):
                    break
                if resol in ("minsec", "hourmin") and not hybrid_handled:
                    if (resol == "minsec" and tm.tm_min == 0 and tm.tm_sec != 0) or \
                        (resol == "hourmin" and tm.tm_hour == 0 and tm.tm_min != 0):
                        next_format = self.formats[self.format_order[resol_ndx-1]][1][0]
                        s = strftimeEx(next_format, t, tm)
                        break
                    else:
                        hybrid_handled = True

                next_format = self.formats[self.format_order[next_ndx]][1][0]
                s = strftimeEx(next_format, t, tm)

            if self.strip_leading_zeros:
                labels.append(s.lstrip("0"))
            else:
                labels.append(s)
            
        return labels

    def estimate_width(self, start, end, numlabels=None, char_width=None,
                       fill_ratio = 0.2, ticker=None):
        """ Returns an estimate of the total number of characters used by the
        the labels for the given set of inputs, as well as the number of labels.
        
        Parameters
        ----------
        start : number
            The beginning of the interval.
        end : number
            The end of the interval.
        numlabels : number
            The ideal number of labels to generate on the interval. 
        char_width : number
            The total character width available for labelling the interval.
        fill_ratio : 0.0 < float <= 1.0
            Ratio of the available width that will be occupied by label text.
        ticker : AbstractScale object
            Object that can calculate the number of labels needed.

        Returns
        -------
        (numlabels, total label width)
        """
        if numlabels == 0 or char_width == 0:
            return 0, 0

        if ticker is None or not hasattr(ticker, "unit"):
            raise ValueError("TimeFormatter requires a scale.")

        if not numlabels:
            numlabels = ticker.num_ticks(start, end)

        span = abs(end - start)
        if ticker:
            r = ticker.resolution
        else:
            r = span / numlabels
        unit = self._get_resolution(r, span)

        if unit == "milliseconds":
            return numlabels, numlabels * 6

        widths, strings = self.formats[unit]
        
        if char_width:
            # Find an appropriate resolution in self.formats and pick between
            # the various format strings
            good_widths = widths[widths * numlabels < fill_ratio * char_width]
            if len(good_widths) == 0:
                # All too big, pick the first label
                width = widths[0]
            else:
                # Pick the largest label that fits
                width = good_widths[-1]
            width *= numlabels
        else:
            # Just pick the middle of the pack of format widths
            width = widths[ int(len(widths) / 2) ] * numlabels
        
        return numlabels, width
    
        
