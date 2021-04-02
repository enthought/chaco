"""
Perform expensive calculations based on user interactions while keeping the GUI
responsive. This makes use of asynchronous programming tools in the encore
package.

Move the slider to blur the image. Note the slider stays responsive even though
the blurring may lag the slider. Uncheck "Asynchronous" and note that the
slider movement is no longer responsive - the blurring occurs on the main
thread and interrupts the movement of the slider.
"""
# Major library imports
from numpy import ogrid, pi, sin

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import (
    Array, Bool, DelegatesTo, HasTraits, Instance, Range, observe
)
from traits.trait_notifiers import ui_dispatch
from traitsui.api import Item, Group, View

try:
    from encore.concurrent.futures.enhanced_thread_pool_executor import \
        EnhancedThreadPoolExecutor
    from encore.concurrent.futures.asynchronizer import Asynchronizer
except ImportError:
    import sys
    sys.exit('You need futures and encore installed to run this demo.')

# Chaco imports
from chaco.api import ArrayPlotData, Plot, VPlotContainer, gray


class BlurPlotController(HasTraits):
    """ Plot controller class for an image plot and its blurred output """

    #==========================================================================
    # Synchronization logic
    #==========================================================================

    # Flag indicating whether updates are asynchronous.
    asynchronous = Bool(True)

    # The executor. This provides a thread pool on which to process operations.
    _executor = Instance(EnhancedThreadPoolExecutor)

    # The asynchronizer. This dispatches calls to the executor while dropping
    # calls that cannot be handled fast enough.
    _asynchronizer = Instance(Asynchronizer)

    def __executor_default(self):
        # TIP: The executor should be 'shutdown' when no longer needed to avoid
        # creating multiple idle threads. This is not necessary in a small
        # demo.
        return EnhancedThreadPoolExecutor(max_workers=1)

    def __asynchronizer_default(self):
        # TIP: Multiple Asynchronizers can share the same executor.  If you
        # have multiple calls that need to be "asynchronized", each should have
        # its own asynchronizer.
        return Asynchronizer(self._executor)

    @observe('blur_level, image', post_init=True)
    def _recalculate_blurred_image(self, event):
        """ Blur the image either synchronously or with the asynchronizer """
        image = self.image
        blur_level = self.blur_level

        if self.asynchronous:
            # The 'submit' call is non-blocking, and returns almost
            # immediately.  The asynchronizer will pass
            # self._blur_and_notify_plot and its arguments (the "job") to the
            # executor to be run on one of the executor's worker threads when
            # the asynchronizer's current job (if any) is complete. If another
            # job (presumably with a different blur_level) comes in before this
            # happens, this job will never be executed.
            self._asynchronizer.submit(self._blur_and_notify_plot, image,
                                       blur_level)
        else:
            # This happens on the calling thread, which is the GUI thread when
            # a change in 'blur_level' comes from the GUI (as in this demo).
            # The GUI must wait for these calls to complete before it can
            # process further user input.  If the calls are slow, the GUI will
            # become unresponsive.
            self.blurred_image = blur_image(image, blur_level)
            self.plot_data.set_data("blurred_image", self.blurred_image)

    def _blur_and_notify_plot(self, image, blur_level):
        """ Do the work of blurring the image and notifying the plot """
        self.blurred_image = blur_image(image, blur_level)

        # Calling 'self.plot_data.set_data' will update the blurred plot.  In
        # general, it is not safe to send visual updates when not on the GUI
        # thread. Since this call is being executed on one of the executor's
        # worker threads, we must re-dispatch the data update to the UI thread
        # or suffer undefined consequences (possibly crashes).
        ui_dispatch(self.plot_data.set_data, "blurred_image",
                    self.blurred_image)

    #==========================================================================
    # Visualization logic - useful, but not the point of the demo
    #==========================================================================

    # An image array to display
    image = Array

    # The blurred image to display
    blurred_image = Array

    # The level of blurring to apply
    blur_level = Range(low=0, high=5)

    # The plot data
    plot_data = Instance(ArrayPlotData)

    # The plot component
    component = Instance(Component)

    def _image_default(self):
        x, y = ogrid[-pi:pi:1024j, 0:2*pi:1024j]
        z = (sin(11*x**2)**2 * sin(5*y**2))**2
        return z

    def _blurred_image_default(self):
        return self.image

    def _plot_data_default(self):
        pd = ArrayPlotData()
        pd.set_data("image", self.image)
        pd.set_data("blurred_image", self.blurred_image)
        return pd

    def _component_default(self):
        padding = (25, 5, 5, 25)
        image_plot = Plot(self.plot_data, padding=padding)
        image_plot.img_plot("image",
                            origin="top left",
                            xbounds=(-pi, pi),
                            ybounds=(-pi, pi),
                            colormap=gray)

        blurred_image_plot = Plot(self.plot_data, padding=padding)
        blurred_image_plot.img_plot("blurred_image",
                                    origin="top left",
                                    xbounds=(-pi, pi),
                                    ybounds=(-pi, pi),
                                    colormap=gray)

        container = VPlotContainer()
        container.add(blurred_image_plot)
        container.add(image_plot)
        return container


def blur_image(image, blur_level):
    """ Blur the image using a potentially time-consuming algorithm """

    blurred_image = image.copy()
    for _ in range(blur_level**2):
        blurred_image[1:-1, 1:-1] += (
            blurred_image[:-2, 1:-1] +  # top
            blurred_image[2:, 1:-1] +  # bottom
            blurred_image[1:-1, :-2] +  # left
            blurred_image[1:-1, 2:] +  # right
            blurred_image[:-2, :-2] +  # top-left
            blurred_image[:-2, 2:] +  # top-right
            blurred_image[2:, :-2] +  # bottom-left
            blurred_image[2:, 2:]  # bottom-right
        )
        blurred_image /= 9

    return blurred_image


#==============================================================================
# Attributes to use for the plot view.
#==============================================================================
size = (800, 600)
title = "Image with asynchronous blurring"


#==============================================================================
# Demo class that is used by the demo.py application.
#==============================================================================
class Demo(HasTraits):

    plot_controller = Instance(BlurPlotController, ())

    component = DelegatesTo('plot_controller')

    blur_level = DelegatesTo('plot_controller')

    asynchronous = DelegatesTo('plot_controller')

    traits_view = View(
        Group(
            Item(
                'component',
                editor=ComponentEditor(size=size),
                show_label=False
            ),
            Group(
                Item('asynchronous'),
                Item('blur_level'),
                orientation="horizontal"
            ),
            orientation="vertical"
        ),
        resizable=True,
        title=title
    )


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
