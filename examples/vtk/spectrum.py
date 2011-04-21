#!/usr/bin/env python
"""
This plot displays the audio spectrum from the microphone.

Based on updating_plot.py
"""

# Major library imports
import pyaudio
from numpy import zeros, linspace, short, fromstring, hstack, transpose
from scipy import fft

# Enthought library imports
from enthought.chaco.default_colormaps import jet
from traits.api import HasTraits, Instance, Any

# Chaco imports
from enthought.chaco.api import Plot, ArrayPlotData, HPlotContainer, \
        OverlayPlotContainer
from enthought.chaco.tools.api import MoveTool, PanTool, ZoomTool

NUM_SAMPLES = 1024
SAMPLING_RATE = 11025
SPECTROGRAM_LENGTH = 100

def create_plot_component(obj):
    # Setup the spectrum plot
    frequencies = linspace(0., float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)
    obj.spectrum_data = ArrayPlotData(frequency=frequencies)
    empty_amplitude = zeros(NUM_SAMPLES/2)
    obj.spectrum_data.set_data('amplitude', empty_amplitude)

    obj.spectrum_plot = Plot(obj.spectrum_data)
    obj.spectrum_plot.plot(("frequency", "amplitude"), name="Spectrum",
                           color="red")
    obj.spectrum_plot.padding = 50
    obj.spectrum_plot.title = "Spectrum"
    spec_range = obj.spectrum_plot.plots.values()[0][0].value_mapper.range
    spec_range.low = 0.0
    spec_range.high = 5.0
    obj.spectrum_plot.index_axis.title = 'Frequency (hz)'
    obj.spectrum_plot.value_axis.title = 'Amplitude'

    # Time Series plot
    times = linspace(0., float(NUM_SAMPLES)/SAMPLING_RATE, num=NUM_SAMPLES)
    obj.time_data = ArrayPlotData(time=times)
    empty_amplitude = zeros(NUM_SAMPLES)
    obj.time_data.set_data('amplitude', empty_amplitude)

    obj.time_plot = Plot(obj.time_data)
    obj.time_plot.plot(("time", "amplitude"), name="Time", color="blue")
    obj.time_plot.padding = 50
    obj.time_plot.title = "Time"
    obj.time_plot.index_axis.title = 'Time (seconds)'
    obj.time_plot.value_axis.title = 'Amplitude'
    time_range = obj.time_plot.plots.values()[0][0].value_mapper.range
    time_range.low = -0.2
    time_range.high = 0.2

    # Spectrogram plot
    spectrogram_data = zeros(( NUM_SAMPLES/2, SPECTROGRAM_LENGTH))
    obj.spectrogram_plotdata = ArrayPlotData()
    obj.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
    spectrogram_plot = Plot(obj.spectrogram_plotdata)
    spectrogram_time = linspace(
        0.0, float(SPECTROGRAM_LENGTH*NUM_SAMPLES)/float(SAMPLING_RATE),
        num=SPECTROGRAM_LENGTH)
    spectrogram_freq = linspace(0.0, float(SAMPLING_RATE/2), num=NUM_SAMPLES/2)
    spectrogram_plot.img_plot('imagedata',
                              name='Spectrogram',
                              xbounds=spectrogram_time,
                              ybounds=spectrogram_freq,
                              colormap=jet,
                              )
    range_obj = spectrogram_plot.plots['Spectrogram'][0].value_mapper.range
    range_obj.high = 5
    range_obj.low = 0.0
    spectrogram_plot.title = 'Spectrogram'
    obj.spectrogram_plot = spectrogram_plot

    return obj.spectrum_plot, obj.time_plot, obj.spectrogram_plot

_stream = None
def get_audio_data():
    global _stream
    if _stream is None:
        # The audio stream is opened the first time this function gets called.
        # The stream is always closed (if it was opened) in a try finally
        # block at the end of this file,
        pa = pyaudio.PyAudio()
        _stream = pa.open(format=pyaudio.paInt16, channels=1,
                          rate=SAMPLING_RATE,
                          input=True, frames_per_buffer=NUM_SAMPLES)

    audio_data  = fromstring(_stream.read(NUM_SAMPLES), dtype=short)
    normalized_data = audio_data / 32768.0
    return (abs(fft(normalized_data))[:NUM_SAMPLES/2], normalized_data)

class TimerController(HasTraits):
    interactor = Any()
    timer_id = Any()

    def on_timer(self, vtk_obj=None, eventname=""):
        try:
            spectrum, time = get_audio_data()
        except IOError:
            return
        self.spectrum_data.set_data('amplitude', spectrum)
        self.time_data.set_data('amplitude', time)
        spectrogram_data = self.spectrogram_plotdata.get_data('imagedata')
        spectrogram_data = hstack((spectrogram_data[:,1:],
                                   transpose([spectrum])))

        self.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
        self.spectrum_plot.request_redraw()
        return

def main():
    from enthought.tvtk.api import tvtk
    from enthought.mayavi import mlab
    from enthought.enable.vtk_backend.vtk_window import EnableVTKWindow
    f = mlab.figure(size=(900,850))
    m = mlab.test_mesh()
    scene = mlab.gcf().scene
    render_window = scene.render_window
    renderer = scene.renderer
    rwi = scene.interactor

    # Create the plot
    timer_controller = TimerController()
    plots = create_plot_component(timer_controller)
    specplot, timeplot, spectrogram = plots

    for i, p in enumerate(plots):
        p.set(resizable = "", bounds = [200,200], outer_x = 0,
                bgcolor = "transparent",
                )
        p.outer_y = i*250
        p.tools.append(MoveTool(p, drag_button="right"))
        p.tools.append(PanTool(p))
        p.tools.append(ZoomTool(p))

    spectrogram.tools[-1].set(tool_mode="range", axis="value")
    spectrogram.tools[-2].set(constrain=True, constrain_direction="y")

    container = OverlayPlotContainer(bgcolor = "transparent",
                    fit_window = True)
    container.add(*plots)
    container.timer_callback = timer_controller.on_timer

    window = EnableVTKWindow(rwi, renderer,
            component = container,
            istyle_class = tvtk.InteractorStyleTrackballCamera,
            bgcolor = "transparent",
            event_passthrough = True,
            )

    mlab.show()

if __name__ == "__main__":
    main()

