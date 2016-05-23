

import datetime
import os
import contextlib

import numpy as np

from chaco.scales.time_scale import (
    tfrac, trange, TimeScale, CalendarScaleSystem)
from chaco.scales.api import TimeFormatter

# Note on testing:
# Chaco assumes times are in UTC seconds since Posix Epoch but does ticking
# in whatever the local time is on the host machine.  This is problematic for
# testing, because correct responses depend on current state of the test
# machine, and will vary by location and time of year.  For hour/day/year
# testing, where TZ matter, we select 3 timezones to test in:
#
# * UTC, because it's easy to reason about what the answer should be
# * Australia/North (ie. Alice Springs, Darwin) which is UTC+9:30 and with no
#   daylight savings time shifts, which should hopefully reveal bugs with
#   non-integer hour offsets.
# * Pacific/Honolulu which is UTC-10:00 and with no daylight savings time
#   shifts, which should hopefully reveal bugs with previous-day or -year
#   baselines.
#
# Note that this isn't quite bullet-proof, as things will break if Hawaii or
# the Northern Territory ever change their timezones (eg. by introducing
# daylight savings).  We also rely on os.environ['TZ'] working to run the
# tests, but at the time of writing it remains to be seen if this works for
# Windows.

#----------------------------------------------------------------
# Utilities
#----------------------------------------------------------------

# Interesting timezone offsets
UTC = 0.0
ALICE_SPRINGS = 9.5*3600
HONOLULU = -10.0*3600


@contextlib.contextmanager
def set_timezone(tz):
    """ Temporarily select the timezone to use

    Parameters
    ----------
    tz : str or number
        Either a standard tz offset
    """
    import chaco.scales.safetime
    import chaco.scales.time_scale

    new_epoch = datetime.datetime.utcfromtimestamp(tz)
    old_epoch = chaco.scales.safetime.EPOCH

    # set module global EPOCHs based on new timezone
    chaco.scales.safetime.EPOCH = new_epoch
    chaco.scales.time_scale.EPOCH = new_epoch
    try:
        yield
    finally:
        # restore module global EPOCHs
        chaco.scales.safetime.EPOCH = old_epoch
        chaco.scales.time_scale.EPOCH = old_epoch


#----------------------------------------------------------------
# tfrac tests
#----------------------------------------------------------------

def test_tfrac_years_01():
    with set_timezone(UTC):
        t = 3601
        (base, frac) = tfrac(t, years=1)
        assert base == 0
        assert frac == 3601

def test_tfrac_years_01_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3601
        (base, frac) = tfrac(t, years=1)
        assert base == 3600 * -9.5  # Alice Springs year start UTC timestamp
        assert frac == 3600 * 10.5 + 1  # 10:30:01 in the morning Jan 1

def test_tfrac_years_01_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        t = 3601
        (base, frac) = tfrac(t, years=1)
        assert base == 3600 * (-365*24 + 10)  # previous Honolulu year start UTC timestamp
        assert frac == 3600 * (364*24 + 15) + 1  # 15:00:01 in the afternoon, Dec 31

def test_tfrac_years_02():
    with set_timezone(UTC):
        t = 3601
        (base, frac) = tfrac(t, years=10)
        assert base == 0
        assert frac == 3601

def test_tfrac_years_02_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3601
        (base, frac) = tfrac(t, years=10)
        assert base == 3600 * -9.5  # Alice Springs decade start UTC timestamp
        assert frac == 3600 * 10.5 + 1  # 10:30:01 in the morning Jan 1

def test_tfrac_years_02_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        t = 3601
        (base, frac) = tfrac(t, years=10)
        # previous Honolulu decade start UTC timestamp (including leap years)
        assert base == 3600 * (-(365*10 + 3)*24 + 10)
        # 15:00:01 in the afternoon, Dec 31, 9 years into decade
        assert frac == 3600 * ((365*9+3 + 364)*24 + 15) + 1

def test_tfrac_days_01():
    with set_timezone(UTC):
        t = 3601
        (base, frac) = tfrac(t, days=1)
        assert base == 0
        assert frac == 3601

def test_tfrac_days_01_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3601
        (base, frac) = tfrac(t, days=1)
        assert base == 3600 * -9.5  # Alice Springs day start UTC timestamp
        assert frac == 3600 * 10.5 + 1  # 10:30:01 in the morning

def test_tfrac_days_01_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        t = 3601
        (base, frac) = tfrac(t, days=1)
        assert base == 3600 * (-24 + 10)  # previous Honolulu day start UTC timestamp
        assert frac == 3600 * 15 + 1  # 15:00:01 in the afternoon

def test_tfrac_days_02():
    with set_timezone(UTC):
        t = 3*24.0*3600 + 1000.0
        (base, frac) = tfrac(t, days=1)
        assert base == 3600 * 24 * 3
        assert frac == 1000

def test_tfrac_days_02_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3*24.0*3600 + 1000.0
        (base, frac) = tfrac(t, days=1)
        assert base == 3600 * (24 * 3 - 9.5)
        assert frac == 3600 * 9.5 + 1000

def test_tfrac_days_02_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        t = 3*24.0*3600 + 1000.0
        (base, frac) = tfrac(t, days=1)
        assert base == 3600 * (24 * 2 + 10)
        assert frac == 3600 * (24 - 10) + 1000

def test_tfrac_hours_01():
    with set_timezone(UTC):
        t = 3601
        (base, frac) = tfrac(t, hours=1)
        assert base == 3600
        assert frac == 1

def test_tfrac_hours_01_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3601
        (base, frac) = tfrac(t, hours=1)
        assert base == 1800
        assert frac == 1801

def test_tfrac_hours_02():
    with set_timezone(UTC):
        t = 3601
        (base, frac) = tfrac(t, hours=2)
        assert base == 0
        assert frac == 3601

def test_tfrac_hours_02_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3601
        (base, frac) = tfrac(t, hours=2)
        assert base == 1800
        assert frac == 1801

def test_tfrac_hours_03():
    with set_timezone(UTC):
        t = 3600 * 5.5
        (base, frac) = tfrac(t, hours=2)
        assert base == 3600 * 4
        assert frac == 3600 * 1.5

def test_tfrac_hours_03_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3600 * 5.5
        (base, frac) = tfrac(t, hours=2)
        assert base == 3600 * 4.5
        assert frac == 3600 * 1

def test_tfrac_hours_04():
    with set_timezone(UTC):
        t = 3600 * 5.5
        (base, frac) = tfrac(t, hours=3)
        assert base == 3600 * 3.0
        assert frac == 3600 * 2.5

def test_tfrac_hours_04_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3600 * 5.5
        (base, frac) = tfrac(t, hours=3)
        assert base == 3600 * 5.5
        assert frac == 3600 * 0

def test_tfrac_hours_05():
    with set_timezone(UTC):
        t = 3600 * 15.5
        (base, frac) = tfrac(t, hours=6)
        assert base == 3600 * 12.0
        assert frac == 3600 *  3.5

def test_tfrac_hours_05_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        t = 3600 * 15.5
        (base, frac) = tfrac(t, hours=6)
        assert base == 3600 * 14.5
        assert frac == 3600 *  1.0

def test_tfrac_minutes_01():
    t = 3601
    (base, frac) = tfrac(t, minutes=1)
    assert base == 3600
    assert frac == 1

def test_tfrac_minutes_02():
    t = 123.5
    (base, frac) = tfrac(t, minutes=1)
    assert base == 120
    assert frac == 3.5

def test_tfrac_seconds_01():
    t = 3601
    (base, frac) = tfrac(t, seconds=1)
    assert base == 3601
    assert frac == 0

def test_tfrac_seconds_02():
    t = 1.75
    (base, frac) = tfrac(t, seconds=1)
    assert base == 1
    assert frac == 0.75

def test_tfrac_milliseconds_01():
    t = 123.5
    (base, frac) = tfrac(t, milliseconds=1)
    assert base == 123.5
    assert frac == 0.0

def test_tfrac_milliseconds_02():
    t = 10.0625
    (base, frac) = tfrac(t, milliseconds=1)
    assert base == 10.062
    assert frac ==  0.0005

def test_tfrac_milliseconds_03():
    t = 10.0625
    (base, frac) = tfrac(t, milliseconds=10)
    assert base == 10.06
    assert frac ==  0.0025

def test_tfrac_milliseconds_04():
    t = 1.0078121
    # Note that the last digit is lost due to rounding to microsecond scale.
    (base, frac) = tfrac(t, milliseconds=1)
    assert base == 1.007
    assert frac == 0.000812

def test_tfrac_milliseconds_05():
    t = 1.0078056
    # Note that the last digit is lost due to rounding to microsecond scale.
    (base, frac) = tfrac(t, milliseconds=1)
    assert base == 1.007
    assert frac == 0.000806


#----------------------------------------------------------------
# trange tests
#----------------------------------------------------------------

def test_trange_hours_01():
    with set_timezone(UTC):
        r = trange(0, 1, hours=1)
        assert r == []

def test_trange_hours_01_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        r = trange(0, 1, hours=1)
        assert r == []

def test_trange_hours_01_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        r = trange(0, 1, hours=1)
        assert r == []

def test_trange_hours_02():
    with set_timezone(UTC):
        r = trange(-1, 1, hours=1)
        assert r == [0.0]

def test_trange_hours_02_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        r = trange(-1, 1, hours=1)
        assert r == []

def test_trange_hours_02_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        r = trange(-1, 1, hours=1)
        assert r == [0.0]

def test_trange_hours_03():
    with set_timezone(UTC):
        r = trange(0, 3600, hours=1)
        assert r == [0.0, 3600.0]

def test_trange_hours_03_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        r = trange(0, 3600, hours=1)
        assert r == [1800.0]

def test_trange_hours_03_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        r = trange(0, 3600, hours=1)
        assert r == [0.0, 3600.0]

def test_trange_hours_04():
    with set_timezone(UTC):
        r = trange(-3600, 3600, hours=1)
        assert r == [-3600.0, 0.0, 3600.0]

def test_trange_hours_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        r = trange(-3600, 3600, hours=1)
        assert r == [-1800.0, 1800.0]

def test_trange_hours_04_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        r = trange(-3600, 3600, hours=1)
        assert r == [-3600.0, 0.0, 3600.0]

def test_trange_hours_05():
    with set_timezone(UTC):
        r = trange(-10, 3610, hours=1)
        assert r == [0.0, 3600.0]

def test_trange_hours_06():
    with set_timezone(UTC):
        r = trange(-10, 7210, hours=1)
        assert r == [0.0, 3600.0, 7200.0]

def test_trange_hours_07():
    with set_timezone(UTC):
        r = trange(-10, 7210, hours=2)
        assert r == [0.0, 7200.0]

def test_trange_hours_07_Alice_Springs():
    # Australia/North (UTC+09:30, never DST)
    with set_timezone(ALICE_SPRINGS):
        r = trange(-10, 7210, hours=2)
        assert r == [1800.0]

def test_trange_hours_07_Honolulu():
    # Pacific/Honolulu (UTC-10:00, never DST)
    with set_timezone(HONOLULU):
        r = trange(-10, 7210, hours=2)
        assert r == [0.0, 7200.0]

def test_trange_seconds_01():
    r = trange(0, 1, seconds=1)
    assert r == [0.0, 1.0]

def test_trange_seconds_02():
    r = trange(0, 10, seconds=1)
    assert r == range(11)

def test_trange_seconds_03():
    r = trange(0, 1.5, seconds=1)
    assert r == [0.0, 1.0]

def test_trange_milliseconds_01():
    r = trange(0, 0.1, milliseconds=1)
    assert np.allclose(np.array(r), np.linspace(0.0, 0.1, 101))

def test_trange_milliseconds_02():
    r = trange(-0.002, 0.001, milliseconds=1)
    assert np.allclose(np.array(r), np.linspace(-0.002, 0.001, 4))


#----------------------------------------------------------------
# TimeScale tests
#----------------------------------------------------------------

# Could use more tests here... --WW

def test_time_scale_seconds_01():
    ts = TimeScale(seconds=1)
    ticks = ts.ticks(0, 10)
    assert (np.array(ticks) == np.linspace(0.0, 10.0, 11)).all()

def test_time_scale_seconds_02():
    ts = TimeScale(seconds=2)
    ticks = ts.ticks(0, 10)
    assert (np.array(ticks) == np.linspace(0.0, 10.0, 6)).all()

def test_time_scale_milliseconds_01():
    ts = TimeScale(milliseconds=1)
    ticks = ts.ticks(0, 0.1)
    assert len(ticks) == 11
    assert (np.array(ticks) == np.linspace(0.0, 0.1, 11)).all()

def test_time_scale_with_formatter():
    """ Regression test for TimeScale() with formatter keyword.

    Using the formatter keyword in the constructor of TimeScale
    could raise a KeyError.  This test passes if no exception is
    raised.
    """
    ts = TimeScale(seconds=1, formatter=TimeFormatter())
    ts = TimeScale(minutes=1, formatter=TimeFormatter())


#----------------------------------------------------------------
# CalendarScaleSystem tests
#----------------------------------------------------------------

def test_calendar_scale_system_01():
    css = CalendarScaleSystem()
    ticks = css.ticks(0,10)
    assert len(ticks) == 11
    assert (np.array(ticks) == np.linspace(0,10,11)).all()


# TODO: Add more tests of the ticks() and labels() methods of
# the CalendarScaleSystem.
#
# Determine why the format switches from '##s' to ':##'
# as in the following, and create appropriate tests:
#
# In [145]: css.labels(71010,71021, numlabels=8, char_width=130)
# Out[145]:
# [(71010.0, '30s'),
#  (71011.0, '31s'),
#  (71012.0, '32s'),
#  (71013.0, '33s'),
#  (71014.0, '34s'),
#  (71015.0, '35s'),
#  (71016.0, '36s'),
#  (71017.0, '37s'),
#  (71018.0, '38s'),
#  (71019.0, '39s'),
#  (71020.0, '40s'),
#  (71021.0, '41s')]
#
# In [146]: css.labels(71010,71022, numlabels=8, char_width=130)
# Out[146]:
# [(71010.0, ':30'),
#  (71011.0, ':31'),
#  (71012.0, ':32'),
#  (71013.0, ':33'),
#  (71014.0, ':34'),
#  (71015.0, ':35'),
#  (71016.0, ':36'),
#  (71017.0, ':37'),
#  (71018.0, ':38'),
#  (71019.0, ':39'),
#  (71020.0, ':40'),
#  (71021.0, ':41'),
#  (71022.0, ':42')]
#
# In [147]:
