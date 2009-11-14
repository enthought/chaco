
from enthought.chaco.scales.formatters import strftimeEx, TimeFormatter


#----------------------------------------------------------------
# strftimeEx tests
#----------------------------------------------------------------

def test_strftimeEx_01():
    t = 0.123
    fmt = "%(ms)"
    result = strftimeEx(fmt, t)
    assert result == "123"

def test_strftimeEx_02():
    t = 0.123456
    fmt = "%(us)"
    result = strftimeEx(fmt, t)
    assert result == "456"

def test_strftimeEx_03():
    t = 0.678910
    fmt = "%(ms)"
    # According to the code, the number that replaces (ms) is *rounded*,
    # so this formt should give "679".  
    result = strftimeEx(fmt, t)
    assert result == "679"

def test_strftimeEx_04():
    t = 0.678910
    fmt = "%(ms).%(us)ms"
    # According to the code, the number that replaces (ms) is *rounded*,
    # so this formt should give "679.910ms".  (See the next test case for the
    # correct way to do this.) 
    result = strftimeEx(fmt, t)
    assert result == "679.910ms"

def test_strftimeEx_04():
    t = 0.678910
    fmt = "%(ms_).%(us)ms"
    # The format "%(ms_)" uses floor().
    result = strftimeEx(fmt, t)
    print result
    assert result == "678.910ms"

#----------------------------------------------------------------
# TimeFormatter tests
#----------------------------------------------------------------

def test_time_formatter_01():
    tf = TimeFormatter()
    ticks = [10.005, 10.0053, 10.0056]
    labels = tf.format(ticks, char_width=130)
    expected = ["5.000ms", "5.300ms", "5.600ms"]
    assert labels == expected
