"""
The main executable file for the zoom_plot demo.

Right-click and drag on the upper plot to select a region to view in detail
in the lower plot.  The selected region can be moved around by dragging,
or resized by clicking on one of its edges and dragging.
"""

# Major library imports
from numpy import amin, amax, arange, searchsorted, sin, pi, linspace

from enthought.enable2.example_support import DemoFrame, demo_main

# Enthought imports
from enthought.enable2.api import Window

# Chaco imports
from enthought.chaco2.api import SimplePlotFrame, VPlotContainer
from enthought.chaco2.tools.api import RangeSelection

# Relative imports
from grid_plot_factory import create_gridded_line_plot
from zoom_overlay import ZoomOverlay

fname = r"Chaco\examples\data\sample.wav"
numpts = 54000

def read_music_data():
    from wav_to_numeric import wav_to_numeric
    index, data = wav_to_numeric(fname)
    return index[:numpts], data[:numpts]

def create_zoomed_plot():
    try:
        x,y = read_music_data()
    except:
        x = linspace(-10*pi, 10*pi, numpts)
        y = sin(x)

    main_plot = create_gridded_line_plot(x,y)
    zoom_plot = create_gridded_line_plot(x,y)

    outer_container = VPlotContainer(padding=30,
                                     fill_padding=True,
                                     spacing=50,
                                     stack_order='top_to_bottom',
                                     bgcolor='lightgray',
                                     use_backbuffer=True)

    outer_container.add(main_plot)
    outer_container.add(zoom_plot)
    
    main_plot.controller = RangeSelection(main_plot)
    
    zoom_overlay = ZoomOverlay(source=main_plot, destination=zoom_plot)
    outer_container.overlays.append(zoom_overlay)

    return outer_container
    
class MyFrame(DemoFrame):
    def _create_window(self):
        return Window(self, -1, component=create_zoomed_plot())


if __name__ == "__main__":
    demo_main(MyFrame, size=(800,600), title=fname)

# EOF

