
# Local relative imports
from chaco.api import ArrayDataSource, DataRange1D, LinearMapper, LinePlot, \
                                 ScatterPlot, PlotAxis, PlotGrid


def create_gridded_line_plot(x, y, orientation="h", color="red", width=1.0,
                             dash="solid", value_mapper_class=LinearMapper,
                             padding=30):

    assert len(x) == len(y)

    # If you know it is monotonically increasing, sort_order can
    # be set to 'ascending'
    index = ArrayDataSource(x,sort_order='none')
    value = ArrayDataSource(y, sort_order="none")

    index_range = DataRange1D(tight_bounds = False)
    index_range.add(index)
    index_mapper = LinearMapper(range=index_range)

    value_range = DataRange1D(tight_bounds = False)
    value_range.add(value)
    value_mapper = value_mapper_class(range=value_range)

    plot = LinePlot(index=index, value=value,
                    index_mapper = index_mapper,
                    value_mapper = value_mapper,
                    orientation = orientation,
                    color = color,
                    line_width = width,
                    line_style = dash,
                    padding = [40, 15, 15, 20],   # left, right, top, bottom
                    border_visible = True,
                    border_width = 1,
                    bgcolor = "white",
                    use_backbuffer = True,
                    backbuffer_padding = False,
                    unified_draw = True,
                    draw_layer = "plot",
                    overlay_border = True)

    vertical_grid = PlotGrid(component = plot,
                             mapper=index_mapper,
                             orientation='vertical',
                             line_color="gray",
                             line_style='dot',
                             use_draw_order = True)

    horizontal_grid = PlotGrid(component = plot,
                               mapper=value_mapper,
                               orientation='horizontal',
                               line_color="gray",
                               line_style='dot',
                               use_draw_order = True)

    vertical_axis = PlotAxis(orientation='left',
                             mapper=plot.value_mapper,
                             use_draw_order = True)

    horizontal_axis = PlotAxis(orientation='bottom',
                               title='Time (s)',
                               mapper=plot.index_mapper,
                               use_draw_order = True)

    plot.underlays.append(vertical_grid)
    plot.underlays.append(horizontal_grid)

    # Have to add axes to overlays because we are backbuffering the main plot,
    # and only overlays get to render in addition to the backbuffer.
    plot.overlays.append(vertical_axis)
    plot.overlays.append(horizontal_axis)
    return plot

def create_gridded_scatter_plot(x, y, orientation="h", color="red", width=1.0,
                                fill_color="red", marker="square", marker_size=2,
                                value_mapper_class=LinearMapper, padding=30):

    assert len(x) == len(y)

    # If you know it is monotonically increasing, sort_order can
    # be set to 'ascending'
    index = ArrayDataSource(x,sort_order='none')
    value = ArrayDataSource(y, sort_order="none")

    index_range = DataRange1D(tight_bounds = False)
    index_range.add(index)
    index_mapper = LinearMapper(range=index_range)

    value_range = DataRange1D(tight_bounds = False)
    value_range.add(value)
    value_mapper = value_mapper_class(range=value_range)

    plot = ScatterPlot(index=index, value=value,
                        index_mapper = index_mapper,
                        value_mapper = value_mapper,
                        orientation = orientation,
                        color = color,
                        fill_color=fill_color,
                        marker=marker,
                        marker_size=marker_size,
                        padding = [40, 15, 15, 20],   # left, right, top, bottom
                        border_visible = True,
                        border_width = 1,
                        bgcolor = "white",
                        use_backbuffer = True,
                        backbuffer_padding = False,
                        unified_draw = True,
                        draw_layer = "plot",
                        overlay_border = True)

    vertical_grid = PlotGrid(component = plot,
                             mapper=index_mapper,
                             orientation='vertical',
                             line_color="gray",
                             line_style='dot',
                             use_draw_order = True)

    horizontal_grid = PlotGrid(component = plot,
                               mapper=value_mapper,
                               orientation='horizontal',
                               line_color="gray",
                               line_style='dot',
                               use_draw_order = True)

    vertical_axis = PlotAxis(orientation='left',
                             mapper=plot.value_mapper,
                             use_draw_order = True)

    horizontal_axis = PlotAxis(orientation='bottom',
                               title='Time (s)',
                               mapper=plot.index_mapper,
                               use_draw_order = True)

    plot.underlays.append(vertical_grid)
    plot.underlays.append(horizontal_grid)

    # Have to add axes to overlays because we are backbuffering the main plot,
    # and only overlays get to render in addition to the backbuffer.
    plot.overlays.append(vertical_axis)
    plot.overlays.append(horizontal_axis)
    return plot



