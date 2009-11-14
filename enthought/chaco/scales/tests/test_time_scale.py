

import time

import numpy as np

from enthought.chaco.scales.time_scale import tfrac, trange, \
        TimeScale, CalendarScaleSystem

#----------------------------------------------------------------
# tfrac tests
#----------------------------------------------------------------

def test_tfrac_days_01():
    # Not sure this test is useful. --WW
    t = time.mktime(time.gmtime(0))
    (base, frac) = tfrac(t, days=1)
    assert base == t
    assert frac == 0.0

def test_tfrac_days_02():
    # Not sure this test is useful. --WW
    t = time.mktime(time.gmtime(0)) + 3*24.0*3600 + 1000.0
    (base, frac) = tfrac(t, days=1)
    assert base == t - 1000.0
    assert frac == 1000.0

def test_tfrac_hours_01():
    t = 3601
    (base, frac) = tfrac(t, hours=1)
    assert base == 3600
    assert frac == 1

def test_tfrac_hours_02():
    t = 3601
    (base, frac) = tfrac(t, hours=2)
    assert base == 0
    assert frac == 3601

def test_tfrac_hours_03():
    t = 3600 * 5.5
    (base, frac) = tfrac(t, hours=2)
    assert base == 3600 * 4
    assert frac == 3600 * 1.5

def test_tfrac_hours_04():
    t = 3600 * 5.5
    (base, frac) = tfrac(t, hours=3)
    assert base == 3600 * 3.0
    assert frac == 3600 * 2.5

def test_tfrac_hours_05():
    t = 3600 * 15.5
    (base, frac) = tfrac(t, hours=6)
    assert base == 3600 * 12.0
    assert frac == 3600 *  3.5

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
    print base, frac
    assert base == 1.007
    assert frac == 0.000812

def test_tfrac_milliseconds_05():
    t = 1.0078056
    # Note that the last digit is lost due to rounding to microsecond scale.
    (base, frac) = tfrac(t, milliseconds=1)
    print base, frac
    assert base == 1.007
    assert frac == 0.000806


#----------------------------------------------------------------
# trange tests
#----------------------------------------------------------------

def test_trange_hours_01():
    r = trange(0, 1, hours=1)
    assert r == []

def test_trange_hours_02():
    r = trange(-1, 1, hours=1)
    assert r == [0.0]

def test_trange_hours_03():
    r = trange(0, 3600, hours=1)
    assert r == [0.0, 3600.0]

def test_trange_hours_04():
    r = trange(-3600, 3600, hours=1)
    assert r == [-3600.0, 0.0, 3600.0]

def test_trange_hours_05():
    r = trange(-10, 3610, hours=1)
    assert r == [0.0, 3600.0]

def test_trange_hours_06():
    r = trange(-10, 7210, hours=1)
    assert r == [0.0, 3600.0, 7200.0]

def test_trange_hours_07():
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
    assert np.allclose(np.array(r), np.linspace(0.0, 0.1, 101)).all()

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
