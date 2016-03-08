import unittest2 as unittest

from chaco.ticks import DefaultTickGenerator, auto_interval


class TestDefaultTickGenerator(unittest.TestCase):

    def setUp(self):
        self.tick_generator = DefaultTickGenerator()

    def test_minor_tick_generator(self):

        high = 1.
        low = 0.
        interval = 0.1
        ticks = self.tick_generator.get_ticks(
            data_low=0,
            data_high=1,
            bounds_low=low,
            bounds_high=high,
            interval=interval,
        )
        expected_num_ticks = (high - low) / interval + 1
        self.assertEqual(len(ticks), expected_num_ticks)


class TestAutoInterval(unittest.TestCase):
    def test_default_auto_interval(self):
        """test default interval computation range orders of magnitude

        By default, the interval tries to pick eye-friendly intervals so that
        there are between 2 and 8 tick marks.
        """
        data_low = 0.
        for i in range(30):
            data_high = 10. ** (i / 10.)
            interval = auto_interval(data_low=data_low, data_high=data_high)
            num_ticks = int((data_high - data_low) / interval)
            self.assertGreaterEqual(num_ticks, 3)
            self.assertLessEqual(num_ticks, 8)

    def test_auto_interval_max_ticks(self):
        data_low = 0.
        data_high = 100.
        for max_ticks in range(4, 11):
            interval = auto_interval(data_low=data_low, data_high=data_high,
                                     max_ticks=max_ticks)
            num_ticks = int((data_high - data_low) / interval)
            self.assertGreaterEqual(num_ticks, 3)
            self.assertLessEqual(num_ticks, max_ticks)

if __name__ == "__main__":
    unittest.main()
