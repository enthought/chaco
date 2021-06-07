"""
Example application for exploring Van der Waal's Equation
"""
import numpy as np

from chaco.api import ArrayPlotData, Plot
from enable.api import ComponentEditor
from traits.api import (
    Array,
    Enum,
    Float,
    HasTraits,
    Instance,
    observe,
    Property,
    Range,
)
from traitsui.api import Item, UItem, View


class Data(HasTraits):

    volume = Array()

    pressure = Property(
        Array, observe=['temperature', 'attraction', 'tot_volume']
    )

    attraction = Range(low=-50.0, high=50.0, value=0.0)

    tot_volume = Range(low=.01, high=100.0, value=0.01)

    temperature = Range(low=-50.0, high=50.0, value=50.0)

    r_constant = Float(8.314472)

    plot_type = Enum("line", "scatter")

    plot = Instance(Plot)

    def _plot_default(self):
        self.plotdata = ArrayPlotData(x=self.volume, y=self.pressure)
        plot = Plot(self.plotdata)
        plot.title = 'Pressure vs. Volume'
        plot.x_axis.title = "Volume"
        plot.y_axis.title = "Pressure"
        plot.range2d.set_bounds((-10, -2000), (120, 4000))
        plot.padding_left = 80

        plot.plot(
            ("x", "y"), type=self.plot_type, name=self.plot_type, color="blue"
        )

        return plot

    def _volume_default(self):
        """ Default handler for volume Trait Array. """
        return np.arange(.1, 100)

    def _get_pressure(self):
        """Recalculate when a trait the property observes changes."""
        return (
            (self.r_constant*self.temperature)/(self.volume - self.tot_volume)
            - self.attraction/(self.volume*self.volume)
        )

    @observe("pressure")
    def _update_plot(self, event):
        self.plotdata.set_data("y", self.pressure)

    @observe("plot_type")
    def _update_plot_type(self, event):
        old_plot_type, new_plot_type = event.old, event.new

        self.plot.delplot(old_plot_type)
        self.plot.plot(
            ("x", "y"), type=new_plot_type, name=new_plot_type, color="blue"
        )
        self.plot.invalidate_and_redraw()

    traits_view = View(
        UItem(
            "plot",
            editor=ComponentEditor(),
            resizable=True
        ),
        Item(name='attraction'),
        Item(name='tot_volume'),
        Item(name='temperature'),
        Item(name='r_constant', style='readonly'),
        Item(name='plot_type'),
        resizable=True,
        buttons=["OK"],
        title='Van der Waal Equation',
        width=900,
        height=800,
    )


popup = Data()


if __name__ == '__main__':
    popup.configure_traits()
