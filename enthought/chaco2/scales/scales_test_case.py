
import pdb, unittest

from scales import *


class TicksTestCase(unittest.TestCase):
    """ Base class for scale and scale system unit tests """
    def assert_empty(self, arg):
        self.assert_(len(arg) == 0)

    def check_ticks(self, ticks1, ticks2):
        for t1, t2 in zip(ticks1, ticks2):
            self.assertAlmostEqual(t1, t2, 6)

    def check_labels(self, labels1, labels2):
        for t1, t2, in zip(labels1, labels2):
            self.assert_(t1 == t2)
        

class ScalesTestCase(TicksTestCase):

    def test_pow10(self):
        scale = Pow10Scale()
        ticks = scale.ticks(5,15,8)
        self.check_ticks(ticks, frange(5, 15, 1.0))
        ticks = scale.ticks(5,105,8)
        self.check_ticks(ticks, frange(10, 100, 10.0))

    def test_log_scale(self):
        scale = LogScale()
        ticks = scale.ticks(0.1, 10.0)
        self.check_ticks(ticks, array((0.2, 0.4, 0.6, 0.8, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0)))

        ticks = scale.ticks(10.0, 1000.0)
        self.check_ticks(ticks, array((20.0, 40.0, 60.0, 80.0, 100.0,
                                       200.0, 400.0, 600.0, 800.0, 1000.0)))

        ticks = scale.ticks(5.0, 4300)
        self.check_ticks(ticks, array((5, 10, 50, 100, 500, 1000)))
        

class ScaleSystemTestCase(TicksTestCase):

    def test_defaults(self):
        ticker = ScaleSystem()
        ticks = ticker.ticks(5, 30, 10)
        self.check_ticks(ticks, frange(5.0, 30.0, 2.5))

    def test_fixed_scales(self):
        scales = [FixedScale(resolution = 1.0),
                  FixedScale(resolution = 10.0),
                  FixedScale(resolution = 100.0)]
        ticker = ScaleSystem(default_scale=None, *scales)
        self.check_ticks(ticker.ticks(5, 35, 3), (10.0, 20.0, 30.0))
        self.check_ticks(ticker.ticks(5, 35, 20), frange(5.0, 30.0, 1.0))
        self.check_ticks(ticker.ticks(5, 614, 10), (100, 200, 300, 400, 500, 600))

    def test_revert_to_default(self):
        scales = [FixedScale(resolution = 1.0),
                  FixedScale(resolution = 10.0),
                  FixedScale(resolution = 100.0)]
        ticker = ScaleSystem(*scales)
        ticks = ticker.ticks(2.0, 3.0, 10)
        self.check_ticks(ticks, frange(2.0, 3.0, 0.1))

    def test_translation(self):
        pass


from formatters import *

class BasicFormatterTestCase(TicksTestCase):

    def test_format(self):
        fmt = BasicFormatter()

        # test with a fixed scale
        scale = FixedScale(resolution = 1.0)
        start, end = 12.0, 18.0
        numlabels = 8
        
        ticks = scale.ticks(start, end, numlabels)
        labels = fmt.format(ticks, numlabels, None)
        desired = map(str, range(12, 19))
        self.check_labels(labels, desired)

        # test with small numbers
        scale = FixedScale(resolution = 1e-4)
        start, end = 5e-5, 8.5e-4
        ticks = scale.ticks(start, end, numlabels)
        labels = fmt.format(ticks, numlabels, None)
        desired = [str(i)+"e-4" for i in range(1, 9)]
        self.check_labels(labels, desired)

    def test2_nice_sci(self):
      
        # The table of numerical values and their proper representation
        # given a certain number of mantissa digits
        vals = [ (3.14159e10, (2, "3e10"), (3, '3.1e10'), (5, '3.141e10')),
                 (123456789, (3, '1.2e8'), (5, '1.234e8')),
                 (-123456, (2, "-1e5"), (3, "-1e5"), (4, "-1.2e5")),
                 (123, (2, "1e2"), (3, "1.2e2"), (4, "1.23e2")),
                 (1.234, (2, "1"), (3, "1.2"), (4, "1.23")),
                 ]
        fmt = BasicFormatter()
        for lst in vals:
            val = lst[0]
            for mdigits, desired in lst[1:]:
                s = fmt._nice_sci(val, mdigits)
                if s != desired:
                    print "Mismatch for", val, "; desired:", desired, "actual:", s


    def test_estimate_default_scale(self):
        fmt = BasicFormatter()
        scale = DefaultScale()

        # Test using numlabels
        test_intervals = ((12., 18., 8),
                          (-4., 16., 10),
                          (5e-5, 8.5e-4, 8),
                          (3e8, 6e8, 8),
                          )
        for start, end, numlabels in test_intervals:
            estimate = fmt.estimate_width(start, end, numlabels, ticker=scale)[1]
            ticks = scale.ticks(start, end, numlabels)
            labels = fmt.format(ticks, numlabels, None)
            actual = sum(map(len, labels))
            self.assert_( abs(estimate-actual) / actual < 0.4 )
        return

    def test_width_based_default_scale(self):
        scale = ScaleSystem()

        test_intervals = ((1, 100, 80),
                          (1, 100, 40),
                          (1, 100, 20),)
        print
        for start, end, width in test_intervals:
            labels = scale.labels(start, end, char_width=width)
            print "(%d,%d)" % (start,end), " avail:", width,
            print " used:", sum([len(x[1]) for x in labels])
        return

    def test_scale_system(self):
        scale = ScaleSystem(FixedScale(resolution = 1.0),
                            FixedScale(resolution = 2.5),
                            FixedScale(resolution = 5.0),
                            FixedScale(resolution = 10.0),
                            FixedScale(resolution = 20.0),
                            FixedScale(resolution = 100.0))

        test_intervals = ((1,100,200),
                          (1, 100, 80),
                          (1, 100, 40),
                          (1, 100, 20),
                          (1, 100, 5),
                          (1, 10, 100),
                          (1, 10, 50),
                          (1, 10, 20),)
        print
        for start, end, width in test_intervals:
            labels = scale.labels(start, end, char_width=width)
            print "(%d,%d)" % (start,end), " avail:", width,
            print " used:", sum([len(x[1]) for x in labels]),
            print zip(*labels)[1]
        return

class OffsetFormatterTestCase(TicksTestCase):


    def test_format(self):

        test_ranges = [(12003, 12015, 1.0),
                       (1.2003, 1.2015, 1e-4),
                       (-1.2015, -1.2003, 1e-4)]

        for start, end, resol in test_ranges:
            fmt = OffsetFormatter()
            fmt.use_offset=True
            fmt.offset_format = "decimal"
            fmt.end_label_format = "sci"

            scale = FixedScale(resolution = resol)
            numlabels = 12
            ticks = scale.ticks(start, end, numlabels)
            print "range:", start, end
            labels = fmt.format(ticks, numlabels, None)
            print "Labels:", labels, "\n"
            print "estimated width:", fmt.estimate_width(start, end, numlabels)
            print "actual width:", sum(map(len, labels))



def test_suite(level=1):
    suites = []
##     suites.append(unittest.makeSuite(ScalesTestCase, "test_"))
##     suites.append(unittest.makeSuite(ScaleSystemTestCase, "test_"))
    suites.append(unittest.makeSuite(BasicFormatterTestCase, "test2_"))
    #suites.append(unittest.makeSuite(OffsetFormatterTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()
