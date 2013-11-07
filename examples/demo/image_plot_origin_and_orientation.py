"""
Demonstration of altering a plot's origin and orientation.

The origin parameter sets a plot's default origin to the specified corner
of the plot window. These positions has the following behavior:
    * 'left' : index increases left to right
    * 'right' : index increases right to left
    * 'top' : index increases top to bottom
    * 'bottom' : index increases bottom to top

The orientation parameter switches the x- and y-axes. Alternatively, you can
think of this as a transpose about the origin.
"""

# Major library imports
from scipy.misc import lena

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import UItem, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, GridContainer, Plot
from chaco.tools.api import PanTool, ZoomTool


class Demo(HasTraits):
    plot = Instance(Component)

    traits_view = View(
        Group(
            UItem('plot', editor=ComponentEditor(size=(1000, 500))),
            orientation = "vertical"
        ),
        resizable=True, title="Demo of image origin and orientation"
    )

    def _plot_default(self):
        # Create a GridContainer to hold all of our plots: 2 rows, 4 columns:
        container = GridContainer(fill_padding=True,
                                  bgcolor="lightgray", use_backbuffer=True,
                                  shape=(2, 4))

        arrangements = [('top left', 'h'),
                        ('top right', 'h'),
                        ('top left', 'v'),
                        ('top right', 'v'),
                        ('bottom left', 'h'),
                        ('bottom right', 'h'),
                        ('bottom left', 'v'),
                        ('bottom right', 'v')]
        orientation_name = {'h': 'horizontal', 'v': 'vertical'}

        pd = ArrayPlotData(image=lena())
        # Plot some bessel functions and add the plots to our container
        for origin, orientation in arrangements:
            plot = Plot(pd, default_origin=origin, orientation=orientation)
            plot.img_plot('image')

            # Attach some tools to the plot
            plot.tools.append(PanTool(plot))
            zoom = ZoomTool(plot, tool_mode="box", always_on=False)
            plot.overlays.append(zoom)

            title = '{}, {}'
            plot.title = title.format(orientation_name[orientation],
                                      origin.replace(' ', '-'))

            # Add to the grid container
            container.add(plot)

        return container


demo = Demo()

if __name__ == "__main__":
    demo.configure_traits()
