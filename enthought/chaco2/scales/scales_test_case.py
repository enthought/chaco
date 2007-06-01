
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


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(ScalesTestCase, "test_"))
    suites.append(unittest.makeSuite(ScaleSystemTestCase, "test_"))
    suites.append(unittest.makeSuite(BasicFormatterTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()
