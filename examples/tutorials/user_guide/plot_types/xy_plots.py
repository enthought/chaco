"""Create examples of all XY plots in Chaco for the user guide.

Relies on sklearn for the datasets.
"""

from functools import partial

from chaco.array_data_source import ArrayDataSource
from chaco.axis import PlotAxis
from chaco.cmap_image_plot import CMapImagePlot
from chaco.contour_line_plot import ContourLinePlot
from chaco.contour_poly_plot import ContourPolyPlot
from chaco.data_range_1d import DataRange1D
from chaco.data_range_2d import DataRange2D
from chaco.jitterplot import JitterPlot
from chaco.lineplot import LinePlot
from chaco.plot_graphics_context import PlotGraphicsContext
from chaco.scatterplot import ScatterPlot
from chaco.linear_mapper import LinearMapper
from chaco.candle_plot import CandlePlot
from chaco.colormapped_scatterplot import ColormappedScatterPlot
from chaco.variable_size_scatterplot import VariableSizeScatterPlot
import chaco.default_colormaps as dc

import scipy.stats
import scipy.stats
import numpy as np
import sklearn.datasets as datasets
from chaco.errorbar_plot import ErrorBarPlot
from chaco.filled_line_plot import FilledLinePlot
from chaco.image_plot import ImagePlot
from chaco.grid_data_source import GridDataSource
from chaco.grid_mapper import GridMapper
from chaco.image_data import ImageData
from plot_window import PlotWindow


AXIS_WIDTH = 2

PLOT_DEFAULTS = {
    'color': 'blue',
    'line_width': 3.0,
    'border_visible': True,
    'border_width': AXIS_WIDTH
}

AXIS_DEFAULTS = {
    'axis_line_weight': AXIS_WIDTH,
    'tick_weight': AXIS_WIDTH,
    'tick_label_font': 'modern 16',
    'title_font': 'modern 20',
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


def add_axes(plot, x_label='', y_label=''):
    y_axis = PlotAxis(orientation='left',
                      title=y_label,
                      mapper=plot.y_mapper,
                      component=plot,
                      **AXIS_DEFAULTS)

    x_axis = PlotAxis(orientation='bottom',
                      title=x_label,
                      mapper=plot.x_mapper,
                      component=plot,
                      **AXIS_DEFAULTS)

    plot.underlays.append(x_axis)
    plot.underlays.append(y_axis)


def save_plot(plot, filename):
    width, height = plot.outer_bounds
    plot.do_layout(force=True)

    gc = PlotGraphicsContext((width, height), dpi=72.0*2)
    gc.render_component(plot)

    gc.save(filename)


# ---- factories for example plots

def get_line_plot(render_style):
    prices = datasets.fetch_mldata('regression-datasets stock')

    x, y = get_data_sources(y=prices['data'][:70,0])
    x_mapper, y_mapper = get_mappers(x, y)

    line_plot = LinePlot(
        index=x, value=y,
        index_mapper=x_mapper, value_mapper=y_mapper,
        render_style=render_style,
        **PLOT_DEFAULTS
    )

    add_axes(line_plot, x_label='Days', y_label='Stock price')

    return line_plot

get_line_plot_connected = partial(get_line_plot, "connectedpoints")
get_line_plot_hold = partial(get_line_plot, "hold")
get_line_plot_connectedhold = partial(get_line_plot, "connectedhold")


def get_scatter_plot():
    boston = datasets.load_boston()
    prices = boston['target']
    lower_status = boston['data'][:,-1]

    x, y = get_data_sources(x=lower_status, y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    scatter_plot = ScatterPlot(
        index=x, value=y,
        index_mapper=x_mapper, value_mapper=y_mapper,
        marker='circle',
        **PLOT_DEFAULTS
    )
    scatter_plot.line_width = 1.0

    add_axes(scatter_plot, x_label='Percent lower status in the population',
             y_label='Median house prices')

    return scatter_plot


def get_cmap_scatter_plot():
    boston = datasets.load_boston()
    prices = boston['target']
    lower_status = boston['data'][:,-1]
    tax = boston['data'][:,9]

    x, y = get_data_sources(x=lower_status, y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    color_source = ArrayDataSource(tax)
    color_mapper = dc.RdYlGn(DataRange1D(low=tax.min(), high=tax.max()))

    scatter_plot = ColormappedScatterPlot(
        index=x, value=y,
        index_mapper=x_mapper, value_mapper=y_mapper,
        color_data=color_source,
        color_mapper=color_mapper,
        marker='circle',
        title='Colors represent property-tax rate',
        render_method='bruteforce',
        **PLOT_DEFAULTS
    )

    add_axes(scatter_plot, x_label='Percent lower status in the population',
             y_label='Median house prices')

    return scatter_plot


def get_variable_size_scatter_plot():
    boston = datasets.load_boston()
    prices = boston['target']
    lower_status = boston['data'][:,-1]
    tax = boston['data'][:,9]

    x, y = get_data_sources(x=lower_status, y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    # normalize between 0 and 30
    marker_size = tax / tax.max() * 10.

    print zip(lower_status, tax)

    scatter_plot = VariableSizeScatterPlot(
        index=x, value=y,
        index_mapper=x_mapper, value_mapper=y_mapper,
        marker_size=marker_size,
        marker='circle',
        title='Colors represent property-tax rate',
        render_method='bruteforce',
        **PLOT_DEFAULTS
    )
    scatter_plot.color = (0.0, 1.0, 0.3, 0.4)


    add_axes(scatter_plot, x_label='Percent lower status in the population',
             y_label='Median house prices')

    return scatter_plot


def get_jitter_plot():
    boston = datasets.load_boston()
    prices = boston['target']

    x, y = get_data_sources(y=prices)
    x_mapper, y_mapper = get_mappers(x, y)

    jitter_plot = JitterPlot(
        index=y,
        mapper=y_mapper,
        marker='circle',
        jitter_width=100,
        **PLOT_DEFAULTS
    )
    jitter_plot.line_width = 1.

    x_axis = PlotAxis(orientation='bottom',
                      title='Median house prices',
                      mapper=jitter_plot.mapper,
                      component=jitter_plot,
                      **AXIS_DEFAULTS)

    jitter_plot.underlays.append(x_axis)

    return jitter_plot


def get_candle_plot():
    means = np.array([0.2, 0.8, 0.5])
    stds =  np.array([1.0, 0.3, 0.5])
    data = scipy.stats.norm(loc=means, scale=stds).rvs((100, 3))

    x = ArrayDataSource(np.arange(3))
    center = ArrayDataSource(data.mean(0))
    bar_min = ArrayDataSource(data.mean(0)-data.std(0))
    bar_max = ArrayDataSource(data.mean(0)+data.std(0))
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
        center_color='yellow',
        bar_color='orange',
        **PLOT_DEFAULTS
    )

    add_axes(candle_plot, x_label='Items', y_label='Values')

    return candle_plot


def get_errorbar_plot():
    x = np.linspace(1., 5., 10)
    y = 3.2 * x**2 + 4.0
    y_with_noise = (y[None,:]
                    + scipy.stats.norm(loc=0, scale=2.8).rvs((10, 1)))

    means = y_with_noise.mean(0)
    stds = y_with_noise.std(0)

    x, y = get_data_sources(x=x, y=means)

    low = ArrayDataSource(means - stds)
    high = ArrayDataSource(means + stds)

    x_range = DataRange1D(low=0, high=6)
    y_range = DataRange1D(tight_bounds=False)
    y_range.add(y, low, high)

    errorbar_plot = ErrorBarPlot(
        index=x, value=y,
        index_mapper=LinearMapper(range=x_range),
        value_mapper=LinearMapper(range=y_range),
        value_low=low,
        value_high=high,
        endcap_size=11.,
        **PLOT_DEFAULTS
    )

    add_axes(errorbar_plot, x_label='Test values', y_label='Measured')

    return errorbar_plot


def get_filled_line_plot():
    prices = datasets.fetch_mldata('regression-datasets stock')

    x, y = get_data_sources(y=prices['data'][:70,0])
    x_mapper, y_mapper = get_mappers(x, y)

    line_plot = FilledLinePlot(
        index=x, value=y,
        index_mapper=x_mapper, value_mapper=y_mapper,
        fill_color='lightgreen',
        edge_width=3.0,
        **PLOT_DEFAULTS
    )

    add_axes(line_plot, x_label='Days', y_label='Stock price')

    return line_plot


def get_image_plot():
    # Create some RGBA image data
    image = np.zeros((200,400,4), dtype=np.uint8)
    image[:,0:40,0] += 255     # Vertical red stripe
    image[0:25,:,1] += 255     # Horizontal green stripe; also yellow square
    image[-80:,-160:,2] += 255 # Blue square
    image[:,:,3] = 255

    index = GridDataSource(np.linspace(0, 4., 400), np.linspace(-1, 1., 200))
    index_mapper = GridMapper(range=DataRange2D(low=(0,-1), high=(4.,1.)))

    image_source = ImageData(data=image, value_depth=4)

    image_plot = ImagePlot(
        index=index,
        value=image_source,
        index_mapper=index_mapper,
        **PLOT_DEFAULTS
    )

    add_axes(image_plot, x_label='x', y_label='y')

    return image_plot


def get_image_from_file():
    import os.path
    filename = os.path.join('..', '..', '..',
                            'demo','basic','capitol.jpg')
    image_source = ImageData.fromfile(filename)

    w, h = image_source.get_width(), image_source.get_height()
    index = GridDataSource(np.arange(w), np.arange(h))
    index_mapper = GridMapper(range=DataRange2D(low=(0, 0),
                                                high=(w-1, h-1)))

    image_plot = ImagePlot(
        index=index,
        value=image_source,
        index_mapper=index_mapper,
        origin='top left',
        **PLOT_DEFAULTS
    )

    add_axes(image_plot, x_label='x', y_label='y')

    return image_plot


def get_cmap_image_plot():
    # Create a scalar field to colormap
    NPOINTS = 200

    xs = np.linspace(-2 * np.pi, +2 * np.pi, NPOINTS)
    ys = np.linspace(-1.5*np.pi, +1.5*np.pi, NPOINTS)
    x, y = np.meshgrid(xs, ys)
    z = scipy.special.jn(2, x)*y*x

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

    add_axes(cmap_plot, x_label='x', y_label='y')

    return cmap_plot


def get_contour_line_plot():
    NPOINTS_X, NPOINTS_Y = 600, 300

    # Create a scalar field to contour
    xs = np.linspace(-2 * np.pi, +2 * np.pi, NPOINTS_X)
    ys = np.linspace(-1.5*np.pi, +1.5*np.pi, NPOINTS_Y)
    x, y = np.meshgrid(xs, ys)
    z = scipy.special.jn(2, x)*y*x

    # FIXME: we have set the xbounds and ybounds manually to work around
    # a bug in CountourLinePlot, see comment in contour_line_plot.py at
    # line 112 (the workaround is the +1 at the end)
    xs_bounds = np.linspace(xs[0], xs[-1], z.shape[1]+1)
    ys_bounds = np.linspace(ys[0], ys[-1], z.shape[0]+1)
    index = GridDataSource(xdata=xs_bounds, ydata=ys_bounds)
    index_mapper = GridMapper(range=DataRange2D(index))

    value = ImageData(data=z, value_depth=1)
    color_mapper = dc.Blues(DataRange1D(value))

    contour_plot = ContourLinePlot(
        index = index,
        index_mapper = index_mapper,
        value = value,
        colors = color_mapper,
        widths = range(1, 11),
        **PLOT_DEFAULTS
    )

    add_axes(contour_plot, x_label='x', y_label='y')

    return contour_plot


def get_contour_poly_plot():
    NPOINTS_X, NPOINTS_Y = 600, 300

    # Create a scalar field to contour
    xs = np.linspace(-2 * np.pi, +2 * np.pi, NPOINTS_X)
    ys = np.linspace(-1.5*np.pi, +1.5*np.pi, NPOINTS_Y)
    x, y = np.meshgrid(xs, ys)
    z = scipy.special.jn(2, x)*y*x

    # FIXME: we have set the xbounds and ybounds manually to work around
    # a bug in CountourLinePlot, see comment in contour_line_plot.py at
    # line 112 (the workaround is the +1 at the end)
    xs_bounds = np.linspace(xs[0], xs[-1], z.shape[1]+1)
    ys_bounds = np.linspace(ys[0], ys[-1], z.shape[0]+1)
    index = GridDataSource(xdata=xs_bounds, ydata=ys_bounds)
    index_mapper = GridMapper(range=DataRange2D(index))

    value = ImageData(data=z, value_depth=1)
    color_mapper = dc.Blues(DataRange1D(value))

    contour_plot = ContourPolyPlot(
        index = index,
        index_mapper = index_mapper,
        value = value,
        colors = color_mapper,
        **PLOT_DEFAULTS
    )

    add_axes(contour_plot, x_label='x', y_label='y')

    return contour_plot


all_examples = {
    'line': get_line_plot_connected,
    'line_hold': get_line_plot_hold,
    'line_connectedhold': get_line_plot_connectedhold,
    'scatter': get_scatter_plot,
    'cmap_scatter': get_cmap_scatter_plot,
    'vsize_scatter': get_variable_size_scatter_plot,
    'jitter': get_jitter_plot,
    'candle': get_candle_plot,
    'errorbar': get_errorbar_plot,
    'filled_line': get_filled_line_plot,
    'image': get_image_plot,
    'image_from_file': get_image_from_file,
    'cmap_image': get_cmap_image_plot,
    'contour_line': get_contour_line_plot,
    'contour_poly': get_contour_poly_plot
}


if __name__ == '__main__':
    name = 'contour_poly'

    factory_func = all_examples[name]
    plot = factory_func()

    window = PlotWindow(plot=plot)
    ui = window.edit_traits()

    filename = '{}_plot.png'.format(name)
    save_plot(window.container, filename)


