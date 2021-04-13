from chaco.shell.scaly_plot import ScalyPlot
from enable.api import ComponentEditor
from pyface.workbench.api import TraitsUIEditor
from traits.api import Any, Enum, HasTraits, Property, Str
from traitsui.api import Item, View


class PlotUI(HasTraits):
    """Simple TraitsUI proxy for a Chaco plot."""

    # The plot.
    component = Any()

    traits_view = View(
        Item("component", editor=ComponentEditor(), show_label=False),
        resizable=True,
    )


class PlotEditor(TraitsUIEditor):
    """A Workbench Editor showing a Chaco plot for the shell interface."""

    bgcolor = Str("white")
    image_default_origin = Enum(
        "bottom left", "top left", "bottom right", "top right"
    )

    # The plot.
    component = Property(Any)
    container = Property(Any)

    # The PlotData.
    data = Any()

    # The PlotSession of which we are a part.  We need to know this in order
    # to notify it of our being closed, etc.
    session = Any()

    def __init__(
        self,
        is_image=False,
        bgcolor="white",
        image_default_origin="top left",
        *args,
        **kw
    ):

        super(TraitsUIEditor, self).__init__(**kw)

        # Some defaults which should be overridden by preferences.
        self.bgcolor = bgcolor
        self.image_default_origin = image_default_origin

        # Create an empty top-level container
        if is_image:
            top_container = self._create_top_img_container()
        else:
            top_container = self._create_top_container()

        self.obj = PlotUI(component=top_container)

    #### PlotWindow interface ##################################################

    def get_container(self):
        return self.obj.component

    def set_container(self, container):
        self.obj.component = container

    def iconize(self, iconize):
        """Iconizes the window if *iconize* is True.

        Do nothing in this implementation.
        """

    def maximize(self, maximize):
        """If *maximize* is True, maximizes the window size; restores if False.

        Do nothing in this implementation.
        """

    def set_size(self, width, height):
        pass

    def set_title(self, title):
        self.name = title

    def raise_window(self):
        self.window.activate_editor(self)

    #### Editor interface ######################################################

    def destroy_control(self):
        """Destroy the toolkit-specific control that represents the part."""
        self._on_window_close()
        super(TraitsUIEditor, self).destroy_control()

    #### Private interface #####################################################

    def _get_container(self):
        return self.obj.component

    def _set_container(self, value):
        self.obj.component = value

    def _get_component(self):
        return self.obj.component

    def _set_component(self, value):
        self.obj.component = value

    def _create_top_container(self):
        plot = ScalyPlot(
            padding=50,
            fill_padding=True,
            bgcolor=self.bgcolor,
            use_backbuffer=True,
        )
        return plot

    def _create_top_img_container(self):
        plot = ScalyPlot(
            padding=50,
            fill_padding=True,
            bgcolor=self.bgcolor,
            use_backbuffer=True,
            default_origin=self.image_default_origin,
        )
        return plot

    def _on_window_close(self):
        if self.session:
            try:
                ndx = self.session.windows.index(self)
                self.session.del_window(ndx)
            except ValueError:
                pass
