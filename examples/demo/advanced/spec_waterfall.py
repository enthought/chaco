"""
This plot displays the audio spectrum from the microphone.

Based on updating_plot.py
"""
# Major library imports
import pyaudio
from numpy import zeros, linspace, short, fromstring, transpose, array
from scipy import fft

# Enthought library imports
from enable.api import Window, Component, ComponentEditor
from traits.api import HasTraits, Instance, List
from traitsui.api import Item, Group, View, Handler
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import (
    Plot,
    ArrayPlotData,
    HPlotContainer,
    VPlotContainer,
    AbstractMapper,
    LinePlot,
    LinearMapper,
    DataRange1D,
)

NUM_SAMPLES = 1024
SAMPLING_RATE = 11025
SPECTROGRAM_LENGTH = 50


class WaterfallRenderer(LinePlot):

    # numpy arrays of the same length
    values = List(args=[])

    # Maps each array in values into a contrained, short screen space
    y2_mapper = Instance(AbstractMapper)

    _cached_data_pts = List()
    _cached_screen_pts = List()

    def _gather_points(self):
        if not self._cache_valid:
            if not self.index or len(self.values) == 0:
                return

            index = self.index.get_data()
            values = self.values

            numindex = len(index)
            if (
                numindex == 0
                or all(len(v) == 0 for v in values)
                or all(numindex != len(v) for v in values)
            ):
                self._cached_data_pts = []
                self._cache_valid = True

            self._cached_data_pts = [
                transpose(array((index, v))) for v in values
            ]
            self._cache_value = True

    def get_screen_points(self):
        self._gather_points()
        return [
            self.map_screen(pts, i)
            for i, pts in enumerate(self._cached_data_pts)
        ]

    def map_screen(self, data_array, data_offset=None):
        """data_offset, if provided, is a float that will be mapped
        into screen space using self.value_mapper and then added to
        mapping data_array with y2_mapper.  If data_offset is not
        provided, then y2_mapper is used.
        """
        if len(data_array) == 0:
            return []
        x_ary, y_ary = transpose(data_array)
        sx = self.index_mapper.map_screen(x_ary)
        if data_offset is not None:
            dy = self.value_mapper.map_screen(data_offset)
            sy = self.y2_mapper.map_screen(y_ary) + dy
        else:
            sy = self.value_mapper.map_screen(y_ary)

        if self.orientation == "h":
            return transpose(array((sx, sy)))
        else:
            return transpose(array((sy, sx)))


# ============================================================================
# Create the Chaco plot.
# ============================================================================


def _create_plot_component(obj):
    # Setup the spectrum plot
    frequencies = linspace(0.0, float(SAMPLING_RATE) / 2, num=NUM_SAMPLES / 2)
    obj.spectrum_data = ArrayPlotData(frequency=frequencies)
    empty_amplitude = zeros(NUM_SAMPLES / 2)
    obj.spectrum_data.set_data("amplitude", empty_amplitude)

    obj.spectrum_plot = Plot(obj.spectrum_data)
    spec_renderer = obj.spectrum_plot.plot(
        ("frequency", "amplitude"), name="Spectrum", color="red"
    )[0]
    obj.spectrum_plot.padding = 50
    obj.spectrum_plot.title = "Spectrum"
    plot_rends = list(obj.spectrum_plot.plots.values())
    spec_range = plot_rends[0][0].value_mapper.range
    spec_range.low = 0.0
    spec_range.high = 5.0
    obj.spectrum_plot.index_axis.title = "Frequency (hz)"
    obj.spectrum_plot.value_axis.title = "Amplitude"

    # Time Series plot
    times = linspace(0.0, float(NUM_SAMPLES) / SAMPLING_RATE, num=NUM_SAMPLES)
    obj.time_data = ArrayPlotData(time=times)
    empty_amplitude = zeros(NUM_SAMPLES)
    obj.time_data.set_data("amplitude", empty_amplitude)

    obj.time_plot = Plot(obj.time_data)
    obj.time_plot.plot(("time", "amplitude"), name="Time", color="blue")
    obj.time_plot.padding = 50
    obj.time_plot.title = "Time"
    obj.time_plot.index_axis.title = "Time (seconds)"
    obj.time_plot.value_axis.title = "Amplitude"
    time_range = list(obj.time_plot.plots.values())[0][0].value_mapper.range
    time_range.low = -0.2
    time_range.high = 0.2

    # Spectrogram plot
    values = [zeros(NUM_SAMPLES / 2) for i in range(SPECTROGRAM_LENGTH)]
    p = WaterfallRenderer(
        index=spec_renderer.index,
        values=values,
        index_mapper=LinearMapper(range=obj.spectrum_plot.index_mapper.range),
        value_mapper=LinearMapper(
            range=DataRange1D(low=0, high=SPECTROGRAM_LENGTH)
        ),
        y2_mapper=LinearMapper(
            low_pos=0, high_pos=8, range=DataRange1D(low=0, high=15)
        ),
    )
    spectrogram_plot = p
    obj.spectrogram_plot = p
    dummy = Plot()
    dummy.padding = 50
    dummy.index_axis.mapper.range = p.index_mapper.range
    dummy.index_axis.title = "Frequency (hz)"
    dummy.add(p)

    container = HPlotContainer()
    container.add(obj.spectrum_plot)
    container.add(obj.time_plot)

    c2 = VPlotContainer()
    c2.add(dummy)
    c2.add(container)

    return c2


def get_audio_data():
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLING_RATE,
        input=True,
        frames_per_buffer=NUM_SAMPLES,
    )
    audio_data = fromstring(stream.read(NUM_SAMPLES), dtype=short)
    stream.close()
    normalized_data = audio_data / 32768.0
    return (abs(fft(normalized_data))[: NUM_SAMPLES / 2], normalized_data)


# HasTraits class that supplies the callable for the timer event.
class TimerController(HasTraits):
    def onTimer(self, *args):
        spectrum, time = get_audio_data()
        self.spectrum_data.set_data("amplitude", spectrum)
        self.time_data.set_data("amplitude", time)
        spec_data = self.spectrogram_plot.values[1:] + [spectrum]
        self.spectrogram_plot.values = spec_data
        self.spectrum_plot.request_redraw()


# ============================================================================
# Attributes to use for the plot view.
size = (900, 850)
title = "Audio Spectrum Waterfall"

# ============================================================================
# Demo class that is used by the demo.py application.
# ============================================================================


class DemoHandler(Handler):
    def closed(self, info, is_ok):
        """Handles a dialog-based user interface being closed by the user.
        Overridden here to stop the timer once the window is destroyed.
        """

        info.object.timer.Stop()


class Demo(HasTraits):

    plot = Instance(Component)

    controller = Instance(TimerController, ())

    timer = Instance(Timer)

    traits_view = View(
        Group(
            Item("plot", editor=ComponentEditor(size=size), show_label=False),
            orientation="vertical",
        ),
        resizable=True,
        title=title,
        width=size[0],
        height=size[1] + 25,
        handler=DemoHandler,
    )

    def __init__(self, **traits):
        super(Demo, self).__init__(**traits)
        self.plot = _create_plot_component(self.controller)

    def edit_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(20, self.controller.onTimer)
        return super(Demo, self).edit_traits(*args, **kws)

    def configure_traits(self, *args, **kws):
        # Start up the timer! We should do this only when the demo actually
        # starts and not when the demo object is created.
        self.timer = Timer(20, self.controller.onTimer)
        return super(Demo, self).configure_traits(*args, **kws)


popup = Demo()

if __name__ == "__main__":
    popup.configure_traits()
