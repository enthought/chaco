"""
Implementation of a plot using a custom overlay and tool
"""


import numpy

from traits.api import HasTraits, Instance, Enum
from traitsui.api import View, Item
from enable.api import ComponentEditor
from chaco.api import Plot, ArrayPlotData, AbstractOverlay
from enable.api import BaseTool
from enable.markers import DOT_MARKER, DotMarker


class BoxSelectTool(BaseTool):
    """Tool for selecting all points within a box

    There are 2 states for this tool, normal and selecting. While the
    left mouse button is down the metadata on the datasources will be
    updated with the current selected bounds.

    Note that the tool does not actually store the selected point, but the
    bounds of the box.
    """

    event_state = Enum("normal", "selecting")

    def normal_left_down(self, event):
        self.event_state = "selecting"
        self.selecting_mouse_move(event)

    def selecting_left_up(self, event):
        self.event_state = "normal"

    def selecting_mouse_move(self, event):
        x1, y1 = self.map_to_data(event.x - 25, event.y - 25)
        x2, y2 = self.map_to_data(event.x + 25, event.y + 25)

        index_datasource = self.component.index
        index_datasource.metadata["selections"] = (x1, x2)

        value_datasource = self.component.value
        value_datasource.metadata["selections"] = (y1, y2)

        self.component.request_redraw()

    def map_to_data(self, x, y):
        """Returns the data space coordinates of the given x and y.

        Takes into account orientation of the plot and the axis setting.
        """

        plot = self.component
        if plot.orientation == "h":
            index = plot.x_mapper.map_data(x)
            value = plot.y_mapper.map_data(y)
        else:
            index = plot.y_mapper.map_data(y)
            value = plot.x_mapper.map_data(x)

        return index, value


class XRayOverlay(AbstractOverlay):
    """Overlay which draws scatter markers on top of plot data points.

    This overlay should be combined with a tool which updates the
    datasources metadata with selection bounds.
    """

    marker = DotMarker()

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        x_range = self._get_selection_index_screen_range()
        y_range = self._get_selection_value_screen_range()

        if len(x_range) == 0:
            return

        x1, x2 = x_range
        y1, y2 = y_range

        with gc:
            gc.set_alpha(0.8)
            gc.set_fill_color((1.0, 1.0, 1.0))
            gc.rect(x1, y1, x2 - x1, y2 - y1)
            gc.draw_path()

        pts = self._get_selected_points()
        if len(pts) == 0:
            return
        screen_pts = self.component.map_screen(pts)
        if hasattr(gc, "draw_marker_at_points"):
            gc.draw_marker_at_points(screen_pts, 3, DOT_MARKER)
        else:
            gc.save_state()
            for sx, sy in screen_pts:
                gc.translate_ctm(sx, sy)
                gc.begin_path()
                self.marker.add_to_path(gc, 3)
                gc.draw_path(self.marker.draw_mode)
                gc.translate_ctm(-sx, -sy)
            gc.restore_state()

    def _get_selected_points(self):
        """gets all the points within the bounds defined in the datasources
        metadata
        """
        index_datasource = self.component.index
        index_selection = index_datasource.metadata["selections"]
        index = index_datasource.get_data()

        value_datasource = self.component.value
        value_selection = value_datasource.metadata["selections"]
        value = value_datasource.get_data()

        x_indices = numpy.where(
            (index > index_selection[0]) & (index < index_selection[-1])
        )
        y_indices = numpy.where(
            (value > value_selection[0]) & (value < value_selection[-1])
        )

        indices = list(set(x_indices[0]) & set(y_indices[0]))

        sel_index = index[indices]
        sel_value = value[indices]

        return list(zip(sel_index, sel_value))

    def _get_selection_index_screen_range(self):
        """maps the selected bounds which were set by the tool into screen
        space. The screen space points can be used for drawing the overlay
        """
        index_datasource = self.component.index
        index_mapper = self.component.index_mapper
        index_selection = index_datasource.metadata["selections"]
        return tuple(index_mapper.map_screen(numpy.array(index_selection)))

    def _get_selection_value_screen_range(self):
        """maps the selected bounds which were set by the tool into screen
        space. The screen space points can be used for drawing the overlay
        """
        value_datasource = self.component.value
        value_mapper = self.component.value_mapper
        value_selection = value_datasource.metadata["selections"]
        return tuple(value_mapper.map_screen(numpy.array(value_selection)))


class PlotExample(HasTraits):

    plot = Instance(Plot)

    traits_view = View(
        Item("plot", editor=ComponentEditor()), width=600, height=600
    )

    def __init__(self, index, value, *args, **kw):
        super(PlotExample, self).__init__(*args, **kw)

        plot_data = ArrayPlotData(index=index)
        plot_data.set_data("value", value)

        self.plot = Plot(plot_data)
        line = self.plot.plot(("index", "value"))[0]

        line.overlays.append(XRayOverlay(line))
        line.tools.append(BoxSelectTool(line))


index = numpy.arange(0, 25, 0.25)
value = numpy.sin(index) + numpy.arange(0, 10, 0.1)

example = PlotExample(index, value)
example.configure_traits()
