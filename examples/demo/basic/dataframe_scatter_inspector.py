""" Overlay to display the data attached to a scatter point hovered over.
"""
import pandas as pd
import numpy as np

from traits.api import Callable, Enum, HasTraits, Instance, on_trait_change, \
    Str
from traitsui.api import View, Item
from enable.api import ComponentEditor
from chaco.api import Plot, ArrayPlotData, ScatterInspectorOverlay
from chaco.tools.api import ScatterInspector
from chaco.overlays.api import DataFrameScatterOverlay, TextBoxOverlay


def _create_plot_component():
    # Create a fake dataset from which 2 dimensions will be displayed in a
    # scatter plot:
    x = np.random.uniform(0.0, 10.0, 50)
    y = np.random.uniform(0.0, 5.0, 50)
    data = pd.DataFrame({"x": x, "y": y,
                         "dataset": np.random.choice(list("abcdefg"), 50)})
    plot_data = ArrayPlotData(x=x, y=y)
    plot = Plot(plot_data)
    scatter = plot.plot(("x", "y"), type="scatter")[0]

    # Attach the inspector and its overlays
    inspector = ScatterInspector(component=scatter)
    scatter.tools.append(inspector)

    text_overlay = DataframeScatterOverlay(component=plot,
                                           inspector=inspector,
                                           source_df=data,
                                           bgcolor="black", alpha=0.6,
                                           text_color="white",
                                           border_color='none')
    plot.overlays.append(text_overlay)

    # Optional: add an overlay on the point to confirm what is hovered over
    # Note that this overlay magically knows about hovered points by
    # listening to renderer events rather than inspector events:
    point_overlay = ScatterInspectorOverlay(component=scatter,
                                            hover_color="red",
                                            hover_marker_size=6)
    scatter.overlays.append(point_overlay)
    return plot


# =============================================================================
# Demo class that is used by the demo.py application.
# =============================================================================

size = (900, 500)
title = "Tooltip demo"


class Demo(HasTraits):
    plot = Instance(Plot)

    traits_view = View(
        Item('plot', editor=ComponentEditor(size=size), show_label=False),
        resizable=True, title=title
    )

    def _plot_default(self):
        return _create_plot_component()


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
