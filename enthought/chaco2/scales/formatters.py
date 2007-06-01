"""
Code for formatting labels given values/times.
"""

from math import modf
from numpy import array
from time import localtime, strftime

class NullFormatter(object):

    def format(ticks, numlabels=None, char_width=None):
        return [""] * len(ticks)

    def estimate_width(start, end, numlabels=None, char_width=None):
        return 0, 0
    

class BasicFormatter(object):

    # This is a class-level default that is related to the algorithm in format()
    avg_label_width = 7.0
    
    def format(self, ticks, numlabels=None, char_width=None):
        """ This function is adapted from matplotlib's "OldScalarFormatter" """
        labels = []
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
                s = '%se%s%s' %(mantissa, sign, exponent)
            else:
                s = s.rstrip('0').rstrip('.')
            labels.append(s)
        return labels

    def estimate_width(self, start, end, numlabels=None, char_width=None,
                       fill_ratio=0.3, ticker=None):
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


class TimeFormatter(object):

    # This table of format is convert into the 'formats' dict.  Each tuple of
    # formats should be ordered from shortest to longest.  Use %T for milliseconds.
    _formats = {
        'seconds': (':%S',), # '%Ss'),
        'minsec': ('%Mm%S',), # '%Mm%S', '%Mm%Ss'),
        'minutes': ('%Mm',),
        'hourmin': ('%Hh%M',), #'%Hh%M', '%Hh%Mm', '%H:%M:%S','%Hh %Mm %Ss'),
        'hours': ('%Hh',),
        'days': ('%m/%d', '%a%d',),
        'months': ('%m/%Y', '%b%y'),
        'years': ("'%y", '%Y')
        }

    format_order = ['milliseconds', 'seconds', 'minsec', 'minutes', 'hourmin',
                    'hours', 'days', 'months', 'years']
                     
    # A dict mapping each of the keys in _formats to a value of two arrays
    # (widths, format strings)
    formats = {}


    def __init__(self):
        self._compute_format_weights()

    def _compute_format_weights(self):
        if self.formats:
            return
        
        for fmt_name, fmt_strings in self._formats.items():
            sizes = []
            tmptime = localtime()
            for s in fmt_strings:
                size = len(strftime(s, tmptime))
                sizes.append(size)
            self.formats[fmt_name] = (array(sizes), fmt_strings)
        return

    def _get_resolution(self, resolution, interval):
        r = resolution
        span = interval
        if r < 0.5:
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

        if resol == "milliseconds":
            # manually format milliseconds
            labels = []
            for t in ticks:
                ms, s = modf(t)
                sec = int(s % 60)
                ms = int(ms * 1000)
                if sec > 0:
                    if ms > 0:
                        s = "%d.%03ds" % (sec, ms)
                    else:
                        s = "%ds" % sec
                else:
                    # this should go through a full format promotion like below,
                    # but for now this is good enough.
                    if ms > 0:
                        s = "0.%03ds" % ms
                    else:
                        tm = localtime(t)
                        if tm.tm_min > 0:
                            fmt = self.formats["minutes"][1][0]
                        elif tm.tm_hour > 0:
                            fmt = self.formats["hours"][1][0]
                        else:
                            fmt = self.formats["days"][1][0]
                        s = strftime(fmt, tm)
                    
                labels.append(s)

        else:
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
            for t in ticks:
                tm = localtime(t)
                s = strftime(format, tm)

                # Check to see if we are at a boundary of the next higher unit
                # of time.  If so, replace the current format with one from
                # that resolution.  This is not the best heuristic in the
                # world, but it works!  There is some trickiness here due to
                # having to deal with hybrid formats in a reasonable manner.
                hybrid_handled = False
                next_ndx = resol_ndx
                while s.startswith(":00") or s.startswith("00"):
                    next_ndx += 1
                    if next_ndx == len(self.format_order):
                        break
                    if resol in ("minsec", "hourmin") and not hybrid_handled:
                        if (resol == "minsec" and tm.tm_min == 0 and tm.tm_sec != 0) or \
                           (resol == "hourmin" and tm.tm_hour == 0 and tm.tm_min != 0):
                            next_format = self.formats[self.format_order[resol_ndx-1]][1][0]
                            s = strftime(next_format, tm)
                            break
                        else:
                            hybrid_handled = True

                    next_format = self.formats[self.format_order[next_ndx]][1][0]
                    s = strftime(next_format, tm)

                labels.append(s.lstrip("0"))
            
        return labels

    def estimate_width(self, start, end, numlabels=None, char_width=None,
                       fill_ratio = 0.2, ticker=None):
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
    
        
