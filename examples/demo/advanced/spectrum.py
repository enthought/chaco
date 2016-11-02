#!/usr/bin/env python
"""
This plot displays the audio waveform, spectrum, and spectrogram from the
microphone.

Based on updating_plot.py
"""
import sys

# Major library imports
try:
    import pyaudio
except ImportError:
    sys.exit('You need pyaudio installed to run this demo.')

from numpy import zeros, linspace, short, fromstring, hstack, transpose
from scipy import fft

# Enthought library imports
from chaco.default_colormaps import hot
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View, Handler
from pyface.timer.api import Timer

# Chaco imports
from chaco.api import Plot, ArrayPlotData, HPlotContainer

NUM_SAMPLES = 1024
SAMPLING_RATE = 11025
SPECTROGRAM_LENGTH = 100

#============================================================================
# Create the Chaco plot.
#============================================================================

def _create_plot_component(obj):
    # Setup the spectrum plot
    frequencies = linspace(0.0, float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)
    obj.spectrum_data = ArrayPlotData(frequency=frequencies)
    empty_amplitude = zeros(NUM_SAMPLES/2)
    obj.spectrum_data.set_data('amplitude', empty_amplitude)

    obj.spectrum_plot = Plot(obj.spectrum_data)
    obj.spectrum_plot.plot(("frequency", "amplitude"), name="Spectrum",
                           color="red")
    obj.spectrum_plot.padding = 50
    obj.spectrum_plot.title = "Spectrum"
    spec_range = list(obj.spectrum_plot.plots.values())[0][0].value_mapper.range
    spec_range.low = 0.0
    spec_range.high = 5.0
    obj.spectrum_plot.index_axis.title = 'Frequency (Hz)'
    obj.spectrum_plot.value_axis.title = 'Amplitude'

    # Time Series plot
    times = linspace(0.0, float(NUM_SAMPLES)/SAMPLING_RATE, num=NUM_SAMPLES)
    obj.time_data = ArrayPlotData(time=times)
    empty_amplitude = zeros(NUM_SAMPLES)
    obj.time_data.set_data('amplitude', empty_amplitude)

    obj.time_plot = Plot(obj.time_data)
    obj.time_plot.plot(("time", "amplitude"), name="Time", color="blue")
    obj.time_plot.padding = 50
    obj.time_plot.title = "Time"
    obj.time_plot.index_axis.title = 'Time (seconds)'
    obj.time_plot.value_axis.title = 'Amplitude'
    time_range = list(obj.time_plot.plots.values())[0][0].value_mapper.range
    time_range.low = -0.2
    time_range.high = 0.2

    # Spectrogram plot
    spectrogram_data = zeros(( NUM_SAMPLES/2, SPECTROGRAM_LENGTH))
    obj.spectrogram_plotdata = ArrayPlotData()
    obj.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
    spectrogram_plot = Plot(obj.spectrogram_plotdata)
    max_time = float(SPECTROGRAM_LENGTH * NUM_SAMPLES) / SAMPLING_RATE
    max_freq = float(SAMPLING_RATE / 2)
    spectrogram_plot.img_plot('imagedata',
                              name='Spectrogram',
                              xbounds=(0, max_time),
                              ybounds=(0, max_freq),
                              colormap=hot,
                              )
    range_obj = spectrogram_plot.plots['Spectrogram'][0].value_mapper.range
    range_obj.high = 5
    range_obj.low = 0.0
    spectrogram_plot.title = 'Spectrogram'
    obj.spectrogram_plot = spectrogram_plot

    container = HPlotContainer()
    container.add(obj.spectrum_plot)
    container.add(obj.time_plot)
    container.add(spectrogram_plot)

    return container

_stream = None
def get_audio_data():
    global _stream
    if _stream is None:
        pa = pyaudio.PyAudio()
        _stream = pa.open(format=pyaudio.paInt16, channels=1, rate=SAMPLING_RATE,
                     input=True, frames_per_buffer=NUM_SAMPLES)
    try:
        audio_data  = fromstring(_stream.read(NUM_SAMPLES), dtype=short)
    except IOError as e:
        # Workaround "Input overflowed" issue on OS X, by restarting stream
        if e.errno != "Input overflowed":
            raise
        audio_data = zeros((NUM_SAMPLES,))
        _stream.stop_stream()
        _stream.close()
        _stream = None
    normalized_data = audio_data / 32768.0
    return (abs(fft(normalized_data))[:NUM_SAMPLES/2], normalized_data)


# HasTraits class that supplies the callable for the timer event.
class TimerController(HasTraits):

    def onTimer(self, *args):
        spectrum, time = get_audio_data()
        self.spectrum_data.set_data('amplitude', spectrum)
        self.time_data.set_data('amplitude', time)
        spectrogram_data = self.spectrogram_plotdata.get_data('imagedata')
        spectrogram_data = hstack((spectrogram_data[:,1:],
                                   transpose([spectrum])))

        self.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
        self.spectrum_plot.request_redraw()
        return

#============================================================================
# Attributes to use for the plot view.
size = (900,500)
title = "Audio Spectrum"

#============================================================================
# Demo class that is used by the demo.py application.
#============================================================================

class DemoHandler(Handler):

    def closed(self, info, is_ok):
        """ Handles a dialog-based user interface being closed by the user.
        Overridden here to stop the timer once the window is destroyed.
        """

        info.object.timer.Stop()
        return

class Demo(HasTraits):

    plot = Instance(Component)

    controller = Instance(TimerController, ())

    timer = Instance(Timer)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title,
                    width=size[0], height=size[1],
                    handler=DemoHandler
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
    try:
        popup.configure_traits()
    finally:
        if _stream is not None:
            _stream.close()
