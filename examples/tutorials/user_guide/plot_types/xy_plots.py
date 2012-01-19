"""Create examples of all XY plots in Chaco for the user guide.

Relies on sklearn for the datasets.
"""
from functools import partial
from chaco.array_data_source import ArrayDataSource
from chaco.axis import PlotAxis
from chaco.data_range_1d import DataRange1D
from chaco.jitterplot import JitterPlot
from chaco.lineplot import LinePlot
from chaco.plot_graphics_context import PlotGraphicsContext
from chaco.scatterplot import ScatterPlot

import scipy.stats
import numpy as np
import sklearn.datasets as datasets

from chaco.linear_mapper import LinearMapper
from chaco.candle_plot import CandlePlot
from chaco.colormapped_scatterplot import ColormappedScatterPlot

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

    import chaco.default_colormaps as dc

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



all_examples = {
    'line': get_line_plot_connected,
    'line_hold': get_line_plot_hold,
    'line_connectedhold': get_line_plot_connectedhold,
    'scatter': get_scatter_plot,
    'cmap_scatter': get_cmap_scatter_plot,
    'jitter': get_jitter_plot,
    'candle': get_candle_plot,
}


if __name__ == '__main__':
    name = 'cmap_scatter'

    factory_func = all_examples[name]
    plot = factory_func()

    window = PlotWindow(plot=plot)
    ui = window.edit_traits()

    filename = '{}_plot.png'.format(name)
    save_plot(window.container, filename)


