""" Overlay to display the data attached to a scatter point hovered over.
"""
import pandas as pd
import numpy as np

from traits.api import Callable, Enum, HasTraits, Instance, observe, Str
from traitsui.api import View, Item
from enable.api import ComponentEditor
from chaco.api import Plot, ArrayPlotData, ScatterInspectorOverlay, \
    TextBoxOverlay
from chaco.api import DataFramePlotData
from chaco.tools.api import ScatterInspector


class DataframeScatterInspector(ScatterInspector):
    #: Data structure to gather all data to display neatly
    data = Instance(pd.DataFrame)


class DataframeScatterOverlay(TextBoxOverlay):
    """ Overlay for displaying hovered data point information.
    """
    #: The inspector tool which has hover information
    inspector = Instance(ScatterInspector)

    #: Function which takes and index and returns an info string.
    message_for_data = Callable

    @observe('inspector:inspector_event')
    def scatter_point_found(self, event):
        inspector_event = event.new 
        data_idx = inspector_event.event_index
        if data_idx is not None:
            self.text = self.message_for_data(data_idx)
        else:
            self.text = ""

        self.visible = len(self.text) > 0
        self.component.request_redraw()

    def _message_for_data_default(self):
        def show_data(data_idx):
            data = self.inspector.data.iloc[data_idx]
            elements = ["idx: {}".format(data_idx)]
            for col in data.index:
                elements.append("{}: {}".format(col, data[col]))
            text = "\n".join(elements)
            return text

        return show_data


if __name__ == "__main__":

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
        inspector = DataframeScatterInspector(
            component=scatter, data=data
        )
        scatter.tools.append(inspector)

        text_overlay = DataframeScatterOverlay(component=plot,
                                               inspector=inspector,
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
