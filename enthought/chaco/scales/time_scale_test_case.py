
from itertools import starmap
from datetime import datetime as DT

from scales import ScaleSystem
from time_scale import dt_to_sec, trange, TimeScale, HMSScales
from formatters import TimeFormatter

from scales_test_case import TicksTestCase


def DTS(*args, **kw):
    """ Returns a unix-timestamp-like time """
    return dt_to_sec(DT(*args, **kw))

def sec_from_hms(start, *times):
    """ Returns a list of times based on adding each offset tuple in times
    to the start time (which should be in seconds).  Offset tuples can be
    in any of the forms: (hours), (hours,minutes), or (hours,minutes,seconds).
    """
    ret = []
    for t in times:
        cur = 0
        if len(t) > 0:
            cur += t[0] * 3600
        if len(t) > 1:
            cur += t[1] * 60
        if len(t) > 2:
            cur += t[2]
        ret.append(start+cur)
    return ret


class TRangeTestCase(TicksTestCase):

    def test_null_ranges(self):
        ranges = (
            ((2005,3,15,10,23,15), (2005,3,15,10,23,45), {"minutes":1}),
            ((2005,3,15,10,23), (2005,3,15,10,47), {"hours":1}),
            ((2005,3,15,5,23), (2005,3,15,18,43), {"days":1}),
            ((2005,3,15,10,30), (2005,12,25,18,30), {"years":1})
            )
        for start, end, kw in ranges:
            self.assert_empty(trange(DTS(*start), DTS(*end), **kw))
        return

    def test_microseconds(self):
        base = DTS(2005, 3, 15, 10, 45, 10)
        start = base + 0.0000027
        end = base + 0.0000088
        ticks = trange(start, end, microseconds=1)
        desired = [base+i for i in (3e-6, 4e-6, 5e-6, 6e-6, 7e-6, 8e-6)]
        self.check_ticks(ticks, desired)

    def test_milliseconds(self):
        base = DTS(2005, 3, 15, 10, 45, 10)
        start = base + 0.0028
        end = base + 0.0075
        ticks = trange(start, end, milliseconds=1)
        desired = [base + i for i in (0.003, 0.004, 0.005, 0.006, 0.007)]
        self.check_ticks(ticks, desired)
        ticks = trange(start, end, milliseconds=2)
        self.check_ticks(ticks, (base+0.004, base+0.006))

    def test_daily(self):
        base = DTS(2005, 1, 1)
        secs_per_day = 24*3600
        ticks = trange(base, base + secs_per_day*5, days=1)
        self.check_ticks(ticks, [base+i*secs_per_day for i in range(5)])

    def test_daily_leap(self):
        start = DTS(2004, 2, 27)
        end = DTS(2004, 3, 2)
        ticks = trange(start, end, days=1)
        desired = [start + i*24*3600 for i in range(5)]
        self.check_ticks(ticks, desired)

    def test_hourly(self):
        # test between Feb 29,2004 10:15pm and Mar 1st 3:15am
        ticks = trange(DTS(2004,2,29,22,15), DTS(2004,3,1,3,15), hours=1)
        start = DTS(2004,2,29,23)
        desired = [start + i*3600 for i in range(5)]
        self.check_ticks(ticks, desired)

    def test_multiday_increment(self):
        start = DTS(2005, 1, 1)
        ticks = trange(start, start + 9*24*3600, days=3)
        self.check_ticks(ticks, [start+i*3*24*3600 for i in range(3)])



class TimeScaleTestCase(TicksTestCase):
    """ This exercises a single TimeScale set at various resolutions """

    def test_hourly(self):
        ts = TimeScale(hours=1)
        start = DTS(2005, 3, 15, 10, 30)
        end = DTS(2005, 3, 15, 16, 59)
        desired_start = DTS(2005, 3, 15)
        desired = [desired_start + i*3600 for i in (11, 12, 13, 14, 15, 16)]
        self.check_ticks(ts.ticks(start, end), desired)

    def test_minutes(self):
        ts = TimeScale(minutes=15)
        start = DTS(2005, 3, 15, 10, 20)
        end = DTS(2005, 3, 15, 11, 55)
        dstart = DTS(2005, 3, 15)
        desired = ((10,30), (10,45), (11,00), (11,15), (11,30), (11,45))
        self.check_ticks(ts.ticks(start, end),
                                sec_from_hms(dstart, *desired))

    def test_day_of_month(self):
        ts = TimeScale(day_of_month=(1,8,15,22))
        start = DTS(2005,3,12)
        end = DTS(2005,5,3)
        desired = list(starmap(DTS, ((2005,3,15), (2005,3,22), (2005,4,1), (2005,4,8),
                                (2005,4,15), (2005,4,22), (2005,5,1))))
        self.check_ticks(ts.ticks(start,end), desired)

        # test adjacent months
        start = DTS(2005, 3, 12)
        end = DTS(2005, 4, 10)
        desired = list(starmap(DTS, ((2005,3,15), (2005,3,22), (2005,4,1), (2005,4,8))))
        self.check_ticks(ts.ticks(start,end), desired)


    def test_month_of_year(self):
        ts = TimeScale(month_of_year=(1,4,8))
        start = DTS(2005,1,1)
        end = DTS(2006,5,1)
        desired = list(starmap(DTS, ((2005,1,1), (2005,4,1), (2005,8,1), (2006,1,1), (2006,4,1))))
        self.check_ticks(ts.ticks(start,end), desired)

    def test_microsecond(self):
        ts = TimeScale(microseconds=1)
        base = DTS(1975, 3, 15, 10, 45, 10)
        start = base + 2.8e-6
        end = start + 9.2e-6
        desired = [base+i for i in (3e-6, 4e-6, 5e-6, 6e-6, 7e-6, 8e-6, 9e-6)]
        self.check_ticks(ts.ticks(start, end), desired)
        


class CalendarScaleSystemTestCase(TicksTestCase):
    """ This exercises the ability of multiple TimeScale objects to play well
    within a single ScaleSystem.
    """
    
    def test_hourly_scales(self):
        scales = [TimeScale(seconds=dt) for dt in (1, 5, 15, 30)] + \
                 [TimeScale(minutes=dt) for dt in (1, 5, 15, 30)] + \
                 [TimeScale(hours=dt) for dt in (1, 2, 3, 4, 6, 12)]

    def test_yearly_scales(self):
        ticker = ScaleSystem(TimeScale(month_of_year=1), default_scale=None)
        ticks = ticker.ticks(DTS(2000,1,1), DTS(2007,1,1), 10)
        desired = list(starmap(DTS, ((2000,1,1), (2001,1,1), (2002,1,1), (2003,1,1),
                                (2004,1,1), (2005,1,1), (2006,1,1), (2007,1,1))))
        self.check_ticks(ticks, desired)


class TimeFormatterTestCase(TicksTestCase):

    def test_widths(self):
        fmt = TimeFormatter()
        scale = TimeScale(minutes = 5)
        test_intervals = ([(2005,3,15,10,30), (2005,3,15,10,50), 50],
                          )
        print
        for start, end, width in test_intervals:
            est_width = scale.label_width(DTS(*start), DTS(*end), char_width=width)
            print start, end,
            print " avail:", width, "est:", est_width[1], "numlabels:", est_width[0]
        return

    def test_labels(self):
        fmt = TimeFormatter()
        scale = ScaleSystem(*HMSScales)

        test_intervals = ([(2005,3,15,10,30), (2005,3,15,10,50), 150],
                          )
        print
        for start, end, width in test_intervals:
            labels = scale.labels(DTS(*start), DTS(*end), char_width=width)
            print start, end, " avail:", width,
            print " used:", sum([len(x[1]) for x in labels]),
            print labels
        return


if __name__ == "__main__":
    import nose
    nose.run()
