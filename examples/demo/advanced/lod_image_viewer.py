import numpy as np

try:
    import zarr
except ImportError:
    import sys
    sys.exit('You need zarr installed to run this demo')

from enable.api import ComponentEditor, Container, Scrolled
from traits.api import Dict, HasTraits, Instance
from traitsui.api import Item, View

try:
    from encore.concurrent.futures.enhanced_thread_pool_executor import \
        EnhancedThreadPoolExecutor
    from encore.concurrent.futures.asynchronizer import Asynchronizer
except ImportError:
    import sys
    sys.exit('You need futures and encore installed to run this demo.')

from chaco.api import (
    DataRange2D, GridDataSource, GridMapper, HPlotContainer, LODDataBase,
    LODImagePlot, LODImageSource
)

LOD_PATH = "LOD_{}"


def mandelbrot_set(xmin, xmax, ymin, ymax, xn, yn, maxiter, horizon):
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


class SampleLOD(LODDataBase):

    data_entry = Dict

    def get_lod_image(self, lod):
        return self.data_entry[LOD_PATH.format(lod)]


def _create_lod_plot():
    z = SampleLOD(data_entry=sample_big_data())
    zps = LODImageSource(data=z)
    h = zps.get_height()
    w = zps.get_width()
    index = GridDataSource(np.arange(h), np.arange(w))
    index_mapper = GridMapper(
        range=DataRange2D(low=(0, 0), high=(h-1, w-1))
    )
    renderer = LODImagePlot(
        value=zps,
        index=index,
        index_mapper=index_mapper,
        maximum_lod=5,
        executor=EnhancedThreadPoolExecutor(name='ImageCacheComputation',
                                            max_workers=1),
    )
    container = HPlotContainer(bounds=(1200, 1000))
    container.add(renderer)
    return container


class LODImageDemo(HasTraits):

    plot_container = Instance(Container)

    scrolled = Instance(Scrolled)

    traits_view = View(
        Item(
            'scrolled',
            editor=ComponentEditor(size=(500, 500)),
            show_label=False,
        ),
        resizable=True,
    )

    def _scrolled_default(self):
        c = Scrolled(
            self.plot_container,
        )
        return c


if __name__ == "__main__":
    plot_component = _create_lod_plot()
    lod_demo = LODImageDemo(plot_container=plot_component)
    lod_demo.configure_traits()
