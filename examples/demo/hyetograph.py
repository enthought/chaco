from chaco.api import ArrayPlotData, Plot
from enable.api import ComponentEditor
from traits.api import (
    HasTraits,
    Instance,
    Int,
    Range,
    Array,
    Enum,
    observe,
)
from traitsui.api import Item, View

COUNTIES = {'Brazos': 0, 'Dallas': 3, 'El Paso': 6, 'Harris': 9}
YEARS = {
    2: [65, 8, .806, 54, 8.3, .791, 24, 9.5, .797, 68, 7.9, .800],
    10: [80, 8.5, .763, 78, 8.7, .777, 42, 12., .795, 81, 7.7, .753],
    25: [89, 8.5, .754, 90, 8.7, .774, 60, 12., .843, 81, 7.7, .724],
    100: [96, 8., .730, 106, 8.3, .762, 65, 9.5, .825, 91, 7.9, .706]
}


class Hyetograph(HasTraits):
    """ Creates a simple hyetograph demo. """

    timeline = Array()

    intensity = Array()

    nrcs = Array()

    duration = Int(12, desc='In Hours')

    year_storm = Enum(2, 10, 25, 100)

    county = Enum('Brazos', 'Dallas', 'El Paso', 'Harris')

    curve_number = Range(70, 100)

    plot_type = Enum('line', 'scatter')

    intensity_plot = Instance(Plot)

    nrcs_plot = Instance(Plot)

    def _intensity_plot_default(self):
        intensity_plot = Plot(ArrayPlotData(x=self.timeline, y=self.intensity))
        intensity_plot.x_axis.title = "Time (hr)"
        intensity_plot.y_axis.title = "Intensity (in/hr)"
        intensity_plot.plot(
            ("x", "y"), type=self.plot_type, name=self.plot_type, color="blue"
        )
        return intensity_plot

    def _nrcs_plot_default(self):
        nrcs_plot = Plot(ArrayPlotData(x=self.timeline, y=self.nrcs))
        nrcs_plot.x_axis.title = "Time"
        nrcs_plot.y_axis.title = "Intensity"
        nrcs_plot.plot(
            ("x", "y"), type=self.plot_type, name=self.plot_type, color="blue"
        )
        return nrcs_plot

    def calculate_intensity(self):
        """ The Hyetograph calculations. """
        # Assigning A, B, and C values based on year, storm, and county
        year = YEARS[self.year_storm]
        value = COUNTIES[self.county]
        a, b, c = year[value], year[value+1], year[value+2]

        self.timeline = [i for i in range(2, self.duration + 1, 2)]
        intensity = a / (self.timeline * 60 + b)**c
        cumulative_depth = intensity * self.timeline

        temp = cumulative_depth[0]
        result = []
        for i in cumulative_depth[1:]:
            result.append(i-temp)
            temp = i
        result.insert(0, cumulative_depth[0])

        # Alternating block method implementation.
        result.reverse()
        switch = True
        o, e = [], []
        for i in result:
            if switch:
                o.append(i)
            else:
                e.append(i)
            switch = not switch
        e.reverse()
        result = o + e
        self.intensity = result

    def calculate_runoff(self):
        """ NRCS method to get run-off based on permeability of ground. """
        s = (1000 / self.curve_number) - 10
        a = self.intensity - (.2 * s)
        vr = a**2 / (self.intensity + (.8 * s))
        # There's no such thing as negative run-off.
        for i in range(0, len(a)):
            if a[i] <= 0:
                vr[i] = 0
        self.nrcs = vr

    @observe('duration, year_storm, county, curve_number')
    def _perform_calculations(self, event=None):
        self.calculate_intensity()
        self.calculate_runoff()
        self.intensity_plot.data.set_data("y", self.intensity)
        self.nrcs_plot.data.set_data("y", self.nrcs)

    @observe("plot_type")
    def _update_polt_type(self, event):
        old_plot_type, new_plot_type = event.old, event.new

        self.intensity_plot.delplot(old_plot_type)
        self.nrcs_plot.delplot(old_plot_type)
        self.intensity_plot.plot(
            ("x", "y"), type=new_plot_type, name=new_plot_type, color="blue"
        )
        self.nrcs_plot.plot(
            ("x", "y"), type=new_plot_type, name=new_plot_type, color="blue"
        )
        self.intensity_plot.invalidate_and_redraw()
        self.nrcs_plot.invalidate_and_redraw()

    def start(self):
        self._perform_calculations()
        self.configure_traits()

    traits_view = View(
        Item('plot_type'),
        Item("intensity_plot", editor=ComponentEditor()),
        Item(name='duration'),
        Item(name='year_storm'),
        Item(name='county'),
        Item("nrcs_plot", editor=ComponentEditor()),
        Item('curve_number'),
        resizable=True,
        width=800,
        height=800,
    )


if __name__ == "__main__":
    hyetograph = Hyetograph()
    hyetograph.start()
