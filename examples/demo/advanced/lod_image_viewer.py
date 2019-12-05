"""
Renders high resolution image based on user interactions while keeping the GUI
responsive.

Move the scrollbar to move around the image. Note the scrollbar stays
responsive even though the high resolution image may take longer to load.
"""
import numpy as np

from enable.api import ComponentEditor, Container
from traits.api import HasTraits, Instance
from traitsui.api import Item, View

from chaco.api import (
    DataRange2D, GridDataSource, GridMapper, HPlotContainer,
    ImageData, ImagePlot
)
from chaco.tools.api import PanTool, ZoomTool


LOD_PATH = "LOD_{}"


def mandelbrot_set(xmin, xmax, ymin, ymax, xn, yn, maxiter, horizon):
    """ Generates Mandelbrot dataset. """
    X = np.linspace(xmin, xmax, xn).astype(np.float32)
    Y = np.linspace(ymin, ymax, yn).astype(np.float32)
    C = X + Y[:, None] * 1j
    N = np.zeros_like(C, dtype=int)
    Z = np.zeros_like(C)
    for n in range(maxiter):
        I = abs(Z) < horizon
        N[I] = n
        Z[I] = Z[I]**2 + C[I]
    N[N == maxiter-1] = 0
    return Z, N


def sample_big_data():
    """ Generates the Mandelbrot fractal with different resolutions stored as
    multiple LOD images
    Ref: https://matplotlib.org/examples/showcase/mandelbrot.html
    """
    xmin, xmax = -2.25, +0.75
    ymin, ymax = -1.25, +1.25
    maxiter = 200
    horizon = 2.0 ** 40
    log_horizon = np.log2(np.log(horizon))

    xn = 3000
    yn = 2500
    sample = {}

    for lod in range(10):
        Z, N = mandelbrot_set(xmin, xmax, ymin, ymax,
                              xn // (2 ** lod), yn // (2 ** lod),
                              maxiter, horizon)
        with np.errstate(invalid='ignore'):
            M = np.nan_to_num(N + 1 - np.log2(np.log(abs(Z))) + log_horizon)

        sample[LOD_PATH.format(lod)] = np.stack(
            [M/2, M, M/4], axis=2).astype('uint8')

    return sample


def _create_lod_plot():
    sample = sample_big_data()
    sample_image_data = ImageData(data=sample[LOD_PATH.format(5)],
                                  support_downsampling=True,
                                  lod_data_entry=sample,
                                  lod_key_pattern=LOD_PATH,
                                  transposed=False)

    h = sample_image_data.get_height(lod=0)
    w = sample_image_data.get_width(lod=0)
    index = GridDataSource(np.arange(h), np.arange(w))
    index_mapper = GridMapper(
        range=DataRange2D(low=(0, 0), high=(h-1, w-1))
    )
    renderer = ImagePlot(
        value=sample_image_data,
        index=index,
        index_mapper=index_mapper,
        use_downsampling=True,
    )

    container = HPlotContainer(bounds=(1200, 1000))
    container.add(renderer)
    renderer.tools.append(PanTool(renderer, constrain_key="shift"))
    renderer.overlays.append(ZoomTool(component=renderer,
                                      tool_mode="box", always_on=False))
    return container


class LODImageDemo(HasTraits):

    plot_container = Instance(Container)

    traits_view = View(
        Item(
            'plot_container',
            editor=ComponentEditor(size=(600, 500)),
            show_label=False,
        ),
        resizable=True,
    )


if __name__ == "__main__":
    lod_demo = LODImageDemo(plot_container=_create_lod_plot())
    lod_demo.configure_traits()
