
import unittest

import numpy as np
from numpy.testing.utils import assert_almost_equal
from chaco.shell.plot_maker import make_data_sources

class MakeDataSourcesTestCase(unittest.TestCase):

    def test_1D_single(self):
        session = None
        ary = np.array([3.0, 2.1, 1.3, 1.8, 5.7])
        sources = make_data_sources(session, "none", ary)
        assert_almost_equal(sources[0][0].get_data(), np.arange(len(ary)))
        assert_almost_equal(sources[0][1].get_data(), ary)
        return

    def test_1d_multiple(self):
        session = None
        index = np.arange(-np.pi, np.pi, np.pi/30.0)
        s = np.sin(index)
        c = np.cos(index)
        t = np.tan(index)
        sources = make_data_sources(session, "ascending", index, s, c, t)
        assert_almost_equal(sources[0][0].get_data(), index)
        self.assert_(sources[0][0] == sources[1][0])
        self.assert_(sources[0][0] == sources[2][0])
        assert_almost_equal(sources[0][1].get_data(), s)
        assert_almost_equal(sources[1][1].get_data(), c)
        assert_almost_equal(sources[2][1].get_data(), t)
        return


if __name__ == "__main__":
    unittest.main()

# EOF
