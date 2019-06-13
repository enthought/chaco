
import unittest

from numpy import alltrue, array, ravel, zeros, isinf, linspace

#from chaco import _speedups as speedups
#from chaco import _speedups_fallback as fallback


def assert_close(desired,actual):
    diff_allowed = 1e-5
    diff = abs(ravel(actual) - ravel(desired))
    for d in diff:
        if not isinf(d):
            assert alltrue(d <= diff_allowed)
            return

class GatherPointsBase(object):

    # The module to look for the gather_points function in; subclasses
    # should override this.
    module = None

    def test_basic(self):
        index = linspace(0.0, 20.0, 21)
        value = linspace(0.0, 1.0, 21)
        points, selection = self.func(index, 4.5, 14.5, value, -1.0, 2.4)
        desired = array([[5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            [0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.8]]).T
        self.assertTrue(selection == None)
        assert_close(desired, points)

    def test_masked(self):
        index = linspace(0.0, 10.0, 11)
        value = linspace(0.0, 1.0, 11)
        index_mask = zeros(11, dtype=bool)
        index_mask[2:6] = 1
        value_mask = zeros(11, dtype=bool)
        value_mask[4:8] = 1

        points, selection = self.func(index, 0, 10, value, 0, 1,
                                index_mask = index_mask)
        desired = array([[2, 3, 4, 5], [0.2, 0.3, 0.4, 0.5]]).T
        assert_close(desired, points)

        points, selection = self.func(index, 0, 10, value, 0, 1,
                                index_mask = index_mask,
                                value_mask = value_mask)
        desired = array([[4, 0.4], [5, 0.5]])
        assert_close(desired, points)


    def test_selection(self):
        pass

    def test_selection_range(self):
        pass

    def _get_func(self):
        return self.module.scatterplot_gather_points
    func = property(_get_func)


#class SpeedupsTestCase(GatherPointsBase, unittest.TestCase):
#    module = speedups


#class SpeedupsFallbackTestCase(SpeedupsTestCase):
#    module = fallback


#def timing_test_gather_points():
#    import time
#    from numpy import sin, pi

#    numpoints = 10000
#    numruns = 10

#    x = linspace(-8*pi, 8*pi, numpoints)
#    y = sin(x)
#    args = (x, -30, 30, y, -0.5, 0.5)

#    funcs = {"Fallback": fallback.scatterplot_gather_points,
#             "C-based": speedups.scatterplot_gather_points}
#
#    for name, func in funcs.items():
#        now = time.time()
#        for i in range(numruns):
#            points, selection = func(*args)
#        print "%s (%d pts, %d runs):" % (name, numpoints, numruns), (time.time() - now)
#    return


