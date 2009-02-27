import numpy
from enthought.chaco.api import Plot, ArrayPlotData
from enthought.chaco.overlays.status_overlay import StatusOverlay, \
        ErrorOverlay, WarningOverlay
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance, Button
from enthought.traits.ui.api import Item, View, HGroup

class MyPlot(HasTraits):
    plot = Instance(Plot)
    status_overlay = Instance(StatusOverlay)
    
    error_button = Button('error')
    warn_button = Button('warning')
    no_problem_button = Button('No problem')

    traits_view = View( HGroup(Item('error_button', show_label=False),
                               Item('warn_button', show_label=False),
                               Item('no_problem_button', show_label=False)),
                        Item('plot', editor=ComponentEditor(), show_label=False))

    def __init__(self, index, data_series, **kw):
        super(MyPlot, self).__init__(**kw)

        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('data_series', data_series)
        self.plot = Plot(plot_data)
        self.plot.plot(('index', 'data_series'))
        
    def _error_button_fired(self, event):
        if self.status_overlay is not None:
            self.status_overlay.fade_out()
        self.status_overlay = ErrorOverlay(component=self.plot)
        self.plot.overlays.append(self.status_overlay)
        self.plot.request_redraw()
         
    def _warn_button_fired(self, event):
        if self.status_overlay is not None:
            self.status_overlay.fade_out()
        self.status_overlay = WarningOverlay(component=self.plot)
        self.plot.overlays.append(self.status_overlay)
        self.plot.request_redraw()

    def _no_problem_button_fired(self, event):
        if self.status_overlay is not None:
            self.status_overlay.fade_out()
        self.plot.request_redraw()

index = numpy.array([1,2,3,4,5])
data_series = index**2

my_plot = MyPlot(index, data_series)
my_plot.configure_traits()
