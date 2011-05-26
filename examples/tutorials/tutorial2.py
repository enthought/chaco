"""Tutorial 2. Creating a plot in window.

Using a traitsui view, a plot can be placed as a configurable item that is
viewed when configure_traits is called.
"""

from enthought.enable.api import ComponentEditor
from enthought.traits.api import HasTraits
from enthought.traits.ui.api import Item, View


from tutorial1 import myplot

class PlotExample(HasTraits):
    plot = myplot

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       title="Chaco Tutorial")

demo = PlotExample()

if __name__ == "__main__":
    demo.configure_traits()
