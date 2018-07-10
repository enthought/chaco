import unittest

import six.moves as sm

from chaco.api import create_scatter_plot, PlotGraphicsContext, DataLabel


class DataLabelTestCase(unittest.TestCase):

    def test_data_label_arrow_not_visible(self):
        # Regression test for https://github.com/enthought/chaco/issues/281
        # Before the problem was fixed, this test (specifically, using
        # arrow_visible=False in the DataLabel constructor) would raise an
        # exception because of an undefined reference.
        size = (50, 50)
        plot = create_scatter_plot(data=[list(sm.xrange(10)),
                                         list(sm.xrange(10))])
        label = DataLabel(component=plot,
                          data_point=(4, 4),
                          marker_color="red",
                          marker_size=3,
                          label_position=(20, 50),
                          label_style='bubble',
                          label_text="Something interesting",
                          label_format="at x=%(x).2f, y=%(y).2f",
                          arrow_visible=False)
        plot.overlays.append(label)
        plot.outer_bounds = list(size)
        gc = PlotGraphicsContext(size)
        gc.render_component(plot)


if __name__ == "__main__":
    unittest.main()
