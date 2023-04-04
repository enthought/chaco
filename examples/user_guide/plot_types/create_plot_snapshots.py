"""Create examples of all XY plots in Chaco for the user guide.

Relies on sklearn for the datasets.
"""


import argparse
from functools import partial

from chaco.api import (
    ArrayDataSource,
    BarPlot,
    CandlePlot,
    CMapImagePlot,
    ColormappedScatterPlot,
    ContourLinePlot,
    ContourPolyPlot,
    DataRange1D,
    DataRange2D,
    ErrorBarPlot,
    FilledLinePlot,
    GridDataSource,
    GridMapper,
    ImageData,
    ImagePlot,
    JitterPlot,
    LinePlot,
    LinearMapper,
    MultiArrayDataSource,
    MultiLinePlot,
    PlotAxis,
    PlotGraphicsContext,
    PlotGrid,
    PolarLineRenderer,
    PolygonPlot,
    QuiverPlot,
    ScatterPlot,
)
from chaco.polar_mapper import PolarMapper
import chaco.default_colormaps as dc
from enable.api import color_table

import scipy.stats
import numpy as np
import sklearn.datasets as datasets

from plot_window import PlotWindow


AXIS_WIDTH = 2

PLOT_DEFAULTS = {
    "color": "blue",
    "line_width": 3.0,
    "border_visible": True,
    "border_width": AXIS_WIDTH,
}

AXIS_DEFAULTS = {
    "axis_line_weight": AXIS_WIDTH,
    "tick_weight": AXIS_WIDTH,
    "tick_label_font": "modern 16",
    "title_font": "modern 20",
}


def get_data_sources(x=None, y=None):
    y = np.asarray(y)

    if x is None:
        x = np.arange(len(y))
    else:
        x = np.asarray(x)

    y_source = ArrayDataSource(y)
    x_source = ArrayDataSource(x)

    return x_source, y_source


def get_mappers(x_source, y_source):
    def _1D_mapper(source):
        data_range = DataRange1D()
        data_range.add(source)
        return LinearMapper(range=data_range)

    return _1D_mapper(x_source), _1D_mapper(y_source)


def add_axes(plot, x_label="", y_label=""):
    y_axis = PlotAxis(
        orientation="left",
        title=y_label,
        mapper=plot.y_mapper,
        component=plot,
        **AXIS_DEFAULTS
    )

    x_axis = PlotAxis(
        orientation="bottom",
        title=x_label,
        mapper=plot.x_mapper,
        component=plot,
        **AXIS_DEFAULTS
    )

    plot.underlays.append(x_axis)
    plot.underlays.append(y_axis)


def save_plot(plot, filename):
    width, height = plot.outer_bounds
    plot.do_layout(force=True)

    gc = PlotGraphicsContext((width, height), dpi=72.0 * 2)
    gc.render_component(plot)

    gc.save(filename)


# ---- factories for example plots


def get_line_plot(render_style):
    prng = np.random.RandomState(seed=1234)
    x_data = np.linspace(0, 10, 50)
    y_data = x_data ** 2 + prng.randn(50)

    x, y = get_data_sources(x=x_data, y=y_data)
    x_mapper, y_mapper = get_mappers(x, y)

    line_plot = LinePlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        render_style=render_style,
        **PLOT_DEFAULTS
    )

    add_axes(line_plot, x_label="x", y_label="y")

    return line_plot


get_line_plot_connected = partial(get_line_plot, "connectedpoints")
get_line_plot_hold = partial(get_line_plot, "hold")
get_line_plot_connectedhold = partial(get_line_plot, "connectedhold")


def get_scatter_plot():
    boston = datasets.load_boston()
    prices = boston["target"]
    lower_status = boston["data"][:, -1]

    x, y = get_data_sources(x=lower_status, y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    scatter_plot = ScatterPlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        marker="circle",
        **PLOT_DEFAULTS
    )
    scatter_plot.line_width = 1.0

    add_axes(
        scatter_plot,
        x_label="Percent lower status in the population",
        y_label="Median house prices",
    )

    return scatter_plot


def get_cmap_scatter_plot():
    boston = datasets.load_boston()
    prices = boston["target"]
    lower_status = boston["data"][:, -1]
    nox = boston["data"][:, 4]

    x, y = get_data_sources(x=lower_status, y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    color_source = ArrayDataSource(nox)
    color_mapper = dc.reverse(dc.RdYlGn)(
        DataRange1D(low=nox.min(), high=nox.max())
    )

    scatter_plot = ColormappedScatterPlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        color_data=color_source,
        color_mapper=color_mapper,
        marker="circle",
        title="Color represents nitric oxides concentration",
        render_method="bruteforce",
        **PLOT_DEFAULTS
    )

    add_axes(
        scatter_plot,
        x_label="Percent lower status in the population",
        y_label="Median house prices",
    )

    return scatter_plot


def get_4d_scatter_plot():
    boston = datasets.load_boston()
    prices = boston["target"]
    lower_status = boston["data"][:, -1]
    tax = boston["data"][:, 9]
    nox = boston["data"][:, 4]

    x, y = get_data_sources(x=lower_status, y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    color_source = ArrayDataSource(nox)
    color_mapper = dc.reverse(dc.RdYlGn)(
        DataRange1D(low=nox.min(), high=nox.max())
    )

    # normalize between 0 and 10
    marker_size = tax / tax.max() * 10.0

    scatter_plot = ColormappedScatterPlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        color_data=color_source,
        color_mapper=color_mapper,
        fill_alpha=0.8,
        marker="circle",
        marker_size=marker_size,
        title="Size represents property-tax rate, "
        "color nitric oxides concentration",
        render_method="bruteforce",
        **PLOT_DEFAULTS
    )

    add_axes(
        scatter_plot,
        x_label="Percent lower status in the population",
        y_label="Median house prices",
    )

    return scatter_plot


def get_variable_size_scatter_plot():
    boston = datasets.load_boston()
    prices = boston["target"]
    lower_status = boston["data"][:, -1]
    tax = boston["data"][:, 9]

    x, y = get_data_sources(x=lower_status, y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    # normalize between 0 and 10
    marker_size = tax / tax.max() * 10.0

    scatter_plot = ScatterPlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        marker="circle",
        marker_size=marker_size,
        title="Size represents property-tax rate",
        **PLOT_DEFAULTS
    )
    scatter_plot.color = (0.0, 1.0, 0.3, 0.4)

    add_axes(
        scatter_plot,
        x_label="Percent lower status in the population",
        y_label="Median house prices",
    )

    return scatter_plot


def get_jitter_plot():
    boston = datasets.load_boston()
    prices = boston["target"]

    x, y = get_data_sources(y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    jitter_plot = JitterPlot(
        index=y,
        index_mapper=y_mapper,
        orientation="h",
        marker="circle",
        jitter_width=100,
        **PLOT_DEFAULTS
    )
    jitter_plot.line_width = 1.0

    x_axis = PlotAxis(
        orientation="bottom",
        title="Median house prices",
        mapper=jitter_plot.index_mapper,
        component=jitter_plot,
        **AXIS_DEFAULTS
    )

    jitter_plot.underlays.append(x_axis)

    return jitter_plot


def get_candle_plot():
    means = np.array([0.2, 0.8, 0.5])
    stds = np.array([1.0, 0.3, 0.5])
    data = scipy.stats.norm(loc=means, scale=stds).rvs((100, 3))

    x = ArrayDataSource(np.arange(3))
    center = ArrayDataSource(data.mean(0))
    bar_min = ArrayDataSource(data.mean(0) - data.std(0))
    bar_max = ArrayDataSource(data.mean(0) + data.std(0))
    stem_min = ArrayDataSource(data.min(0))
    stem_max = ArrayDataSource(data.max(0))

    x_range = DataRange1D(low=-1, high=3)
    y_range = DataRange1D(tight_bounds=False)
    y_range.add(center, bar_min, bar_max, stem_min, stem_max)

    candle_plot = CandlePlot(
        index=x,
        index_mapper=LinearMapper(range=x_range),
        value_mapper=LinearMapper(range=y_range),
        center_values=center,
        bar_min=bar_min,
        bar_max=bar_max,
        min_values=stem_min,
        max_values=stem_max,
        center_color="yellow",
        bar_color="orange",
        **PLOT_DEFAULTS
    )

    add_axes(candle_plot, x_label="Items", y_label="Values")

    return candle_plot


def get_errorbar_plot():
    x = np.linspace(1.0, 5.0, 10)
    y = 3.2 * x ** 2 + 4.0
    y_with_noise = y[None, :] + scipy.stats.norm(loc=0, scale=2.8).rvs((10, 1))

    means = y_with_noise.mean(0)
    stds = y_with_noise.std(0)

    x, y = get_data_sources(x=x, y=means)

    low = ArrayDataSource(means - stds)
    high = ArrayDataSource(means + stds)

    x_range = DataRange1D(low=0, high=6)
    y_range = DataRange1D(tight_bounds=False)
    y_range.add(y, low, high)

    errorbar_plot = ErrorBarPlot(
        index=x,
        value=y,
        index_mapper=LinearMapper(range=x_range),
        value_mapper=LinearMapper(range=y_range),
        value_low=low,
        value_high=high,
        endcap_size=11.0,
        **PLOT_DEFAULTS
    )

    add_axes(errorbar_plot, x_label="Test values", y_label="Measured")

    return errorbar_plot


def get_filled_line_plot():
    prng = np.random.RandomState(seed=1234)
    x_data = np.linspace(0, 10, 50)
    y_data = x_data ** 2 + prng.randn(50)

    x, y = get_data_sources(x=x_data, y=y_data)
    x_mapper, y_mapper = get_mappers(x, y)

    line_plot = FilledLinePlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        fill_color="lightgreen",
        edge_width=3.0,
        **PLOT_DEFAULTS
    )

    add_axes(line_plot, x_label="x", y_label="y")

    return line_plot


def get_image_plot():
    # Create some RGBA image data
    image = np.zeros((200, 400, 4), dtype=np.uint8)
    image[:, 0:40, 0] += 255  # Vertical red stripe
    image[0:25, :, 1] += 255  # Horizontal green stripe; also yellow square
    image[-80:, -160:, 2] += 255  # Blue square
    image[:, :, 3] = 255

    index = GridDataSource(np.linspace(0, 4.0, 400), np.linspace(-1, 1.0, 200))
    index_mapper = GridMapper(range=DataRange2D(low=(0, -1), high=(4.0, 1.0)))

    image_source = ImageData(data=image, value_depth=4)

    image_plot = ImagePlot(
        index=index,
        value=image_source,
        index_mapper=index_mapper,
        **PLOT_DEFAULTS
    )

    add_axes(image_plot, x_label="x", y_label="y")

    return image_plot


def get_image_from_file():
    import os.path

    filename = os.path.join("..", "..", "demo", "basic", "capitol.jpg")
    image_source = ImageData.fromfile(filename)

    w, h = image_source.get_width(), image_source.get_height()
    index = GridDataSource(np.arange(w), np.arange(h))
    index_mapper = GridMapper(
        range=DataRange2D(low=(0, 0), high=(w - 1, h - 1))
    )

    image_plot = ImagePlot(
        index=index,
        value=image_source,
        index_mapper=index_mapper,
        origin="top left",
        **PLOT_DEFAULTS
    )

    add_axes(image_plot, x_label="x", y_label="y")

    return image_plot


def get_cmap_image_plot():
    # Create a scalar field to colormap
    NPOINTS = 200

    xs = np.linspace(-2 * np.pi, +2 * np.pi, NPOINTS)
    ys = np.linspace(-1.5 * np.pi, +1.5 * np.pi, NPOINTS)
    x, y = np.meshgrid(xs, ys)
    z = scipy.special.jn(2, x) * y * x

    index = GridDataSource(xdata=xs, ydata=ys)
    index_mapper = GridMapper(range=DataRange2D(index))

    color_source = ImageData(data=z, value_depth=1)
    color_mapper = dc.Spectral(DataRange1D(color_source))

    cmap_plot = CMapImagePlot(
        index=index,
        index_mapper=index_mapper,
        value=color_source,
        value_mapper=color_mapper,
        **PLOT_DEFAULTS
    )

    add_axes(cmap_plot, x_label="x", y_label="y")

    return cmap_plot


def get_contour_line_plot():
    NPOINTS_X, NPOINTS_Y = 600, 300

    # Create a scalar field to contour
    xs = np.linspace(-2 * np.pi, +2 * np.pi, NPOINTS_X)
    ys = np.linspace(-1.5 * np.pi, +1.5 * np.pi, NPOINTS_Y)
    x, y = np.meshgrid(xs, ys)
    z = scipy.special.jn(2, x) * y * x

    index = GridDataSource(xdata=xs, ydata=ys)
    index_mapper = GridMapper(range=DataRange2D(index))

    value = ImageData(data=z, value_depth=1)
    color_mapper = dc.Blues(DataRange1D(value))

    contour_plot = ContourLinePlot(
        index=index,
        index_mapper=index_mapper,
        value=value,
        colors=color_mapper,
        widths=list(range(1, 11)),
        **PLOT_DEFAULTS
    )

    add_axes(contour_plot, x_label="x", y_label="y")

    return contour_plot


def get_contour_poly_plot():
    NPOINTS_X, NPOINTS_Y = 600, 300

    # Create a scalar field to contour
    xs = np.linspace(-2 * np.pi, +2 * np.pi, NPOINTS_X)
    ys = np.linspace(-1.5 * np.pi, +1.5 * np.pi, NPOINTS_Y)
    x, y = np.meshgrid(xs, ys)
    z = scipy.special.jn(2, x) * y * x

    index = GridDataSource(xdata=xs, ydata=ys)
    index_mapper = GridMapper(range=DataRange2D(index))

    value = ImageData(data=z, value_depth=1)
    color_mapper = dc.Blues(DataRange1D(value))

    contour_plot = ContourPolyPlot(
        index=index,
        index_mapper=index_mapper,
        value=value,
        colors=color_mapper,
        **PLOT_DEFAULTS
    )

    add_axes(contour_plot, x_label="x", y_label="y")

    return contour_plot


def get_polygon_plot():
    xs = np.array([0.5, 2.0, 4.0, 5.5, 4.0, 1.5, 0.5, 0.0])
    ys = np.array([0.0, 0.8, 0.5, 3.0, 3.5, 2.0, 3.0, 0.5])

    x, y = get_data_sources(xs, ys)
    x_mapper, y_mapper = get_mappers(x, y)

    polygon_plot = PolygonPlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        edge_width=4.0,
        face_color="orange",
        **PLOT_DEFAULTS
    )

    add_axes(polygon_plot, x_label="x", y_label="y")

    return polygon_plot


def get_bar_plot():
    boston = datasets.load_boston()
    prices = boston["target"]

    ys, bin_edges = np.histogram(prices, bins=10)
    ys = ys.astype("d") / ys.sum()
    xs = (bin_edges[:-1] + bin_edges[1:]) / 2.0

    x, y = get_data_sources(x=xs, y=ys)
    x_mapper, y_mapper = get_mappers(x, y)

    # we need to make the range of the x coordinate a bit larger, otherwise
    # half of the first and last bar are cut
    delta = bin_edges[1] - bin_edges[0]
    x_mapper.range.low = xs[0] - delta / 2.0
    x_mapper.range.high = xs[-1] + delta / 2.0

    y_mapper.range.high += 0.02

    bar_plot = BarPlot(
        index=x,
        value=y,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        fill_color="blue",
        bar_width=3.0,
        **PLOT_DEFAULTS
    )

    add_axes(bar_plot, x_label="Median house prices", y_label="Frequency")

    return bar_plot


def get_quiver_plot():
    NPOINTS = 250

    # points are distributed uniformly between -1 and 1
    xs = np.random.uniform(low=-1.0, high=1.0, size=(NPOINTS,))
    ys = np.random.uniform(low=-1.0, high=1.0, size=(NPOINTS,))

    x, y = get_data_sources(x=xs, y=ys)
    x_mapper, y_mapper = get_mappers(x, y)

    # vectors are tangent to a circle centered in (0, 0) and the size depends
    # on the radius
    r = np.sqrt(xs * xs + ys * ys) * 20.0
    v = r * np.array([-np.sin(np.arctan2(ys, xs)), np.cos(np.arctan2(ys, xs))])
    v_source = MultiArrayDataSource(v.T)

    quiver_plot = QuiverPlot(
        index=x,
        value=y,
        vectors=v_source,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
        aspect_ratio=1.0,
    )

    add_axes(quiver_plot, x_label="x", y_label="y")

    return quiver_plot


def get_polar_plot():
    # Create theta
    N_POINTS = 5000
    low, high = 0, np.pi
    theta = np.arange(low, high, (high - low) / N_POINTS)

    # Create the radius data
    radius = np.cos(3 * theta)

    # FIXME: at the moment PolarMapper does not actually do anything, so
    # we need to transform to Cartesian coordinates by hand
    xs = radius * np.cos(theta)
    ys = radius * np.sin(theta)

    x, y = get_data_sources(xs, ys)
    index_mapper = PolarMapper(range=DataRange1D(x))
    value_mapper = PolarMapper(range=DataRange1D(y))

    polar_plot = PolarLineRenderer(
        index=x,
        value=y,
        index_mapper=index_mapper,
        value_mapper=value_mapper,
        aspect_ratio=1.0,
        **PLOT_DEFAULTS
    )
    polar_plot.border_visible = False

    return polar_plot


def get_multiline_plot():
    prng = np.random.RandomState(seed=1234)

    x = np.linspace(0, 10, 50)
    y_data = np.column_stack(
        [
            x ** 2,
            50 * np.sin(x),
            50 * np.cos(x),
            0.5 * x ** 2 + 2 * prng.randn(50),
            0.7 * x ** 2 + prng.randn(50),
        ]
    )

    # data sources for the two axes
    xs = ArrayDataSource(np.arange(50))
    ys = ArrayDataSource(np.arange(y_data.shape[1]))
    y_range = DataRange1D(low=-0.5, high=y_data.shape[1] - 0.5)
    y_mapper = LinearMapper(range=y_range)

    # data source for the multiple lines
    lines_source = MultiArrayDataSource(data=y_data.T)

    colors = ["blue", "green", "yellow", "orange", "red"]

    def color_generator(color_idx):
        return color_table[colors[color_idx]]

    multiline_plot = MultiLinePlot(
        index=xs,
        yindex=ys,
        index_mapper=LinearMapper(range=DataRange1D(xs)),
        value_mapper=y_mapper,
        value=lines_source,
        normalized_amplitude=1.0,
        use_global_bounds=False,
        color_func=color_generator,
        **PLOT_DEFAULTS
    )

    add_axes(multiline_plot, x_label="Days", y_label="Stock price changes")

    y_grid = PlotGrid(
        mapper=y_mapper,
        orientation="horizontal",
        line_style="dot",
        component=multiline_plot,
    )
    multiline_plot.overlays.append(y_grid)

    return multiline_plot


all_examples = {
    "line": get_line_plot_connected,
    "line_hold": get_line_plot_hold,
    "line_connectedhold": get_line_plot_connectedhold,
    "scatter": get_scatter_plot,
    "cmap_scatter": get_cmap_scatter_plot,
    "4d_scatter": get_4d_scatter_plot,
    "vsize_scatter": get_variable_size_scatter_plot,
    "jitter": get_jitter_plot,
    "candle": get_candle_plot,
    "errorbar": get_errorbar_plot,
    "filled_line": get_filled_line_plot,
    "image": get_image_plot,
    "image_from_file": get_image_from_file,
    "cmap_image": get_cmap_image_plot,
    "contour_line": get_contour_line_plot,
    "contour_poly": get_contour_poly_plot,
    "polygon": get_polygon_plot,
    "bar": get_bar_plot,
    "quiver": get_quiver_plot,
    "polar": get_polar_plot,
    "multiline": get_multiline_plot,
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "-n",
        "--name",
        help=(
            "Name of the plot snapshot to create. If this is omitted, all "
            "snapshots are created."
        ),
    )
    name = p.parse_args().name
    if name is None:
        names = all_examples.keys()
    else:
        names = [name]

    create_plot_types(names)


def create_plot_types(names):
    for name in names:
        fname = "{}_plot.png".format(name)
        print("*** creating figure {!r} for type {!r} ***".format(fname, name))
        plot = all_examples[name]()

        window = PlotWindow(plot=plot)
        window.edit_traits()

        save_plot(window.container, fname)


if __name__ == "__main__":
    main()
