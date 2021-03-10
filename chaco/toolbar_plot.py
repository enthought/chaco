from chaco.plot import Plot
from chaco.tools.toolbars.plot_toolbar import PlotToolbar
from traits.api import Type, DelegatesTo, Instance, Enum, \
        on_trait_change

class ToolbarPlot(Plot):
    #: Should we turn on the auto-hide feature on the toolbar?
    auto_hide = DelegatesTo('toolbar')

    toolbar = Instance(PlotToolbar)

    toolbar_class = Type(PlotToolbar)
    toolbar_added = False

    #: Location of the default toolbar that is created if a toolbar
    #: is not specified with the :attr:`toolbar` attribute.  Changing this
    #: attribute after the ToolbarPlot instance is created has no effect;
    #: use obj.toolbar.location to dynamically change toolbar's location.
    toolbar_location = Enum('top', 'right', 'bottom', 'left')

    def __init__(self, *args, **kw):

        # initialize the toolbar class before super() has a chance to create
        # the default using the default class. This can happen because of
        # ordering issues

        if "toolbar_class" in kw:
            self.toolbar_class = kw.pop("toolbar_class")

        super(ToolbarPlot, self).__init__(*args, **kw)

        self.toolbar.component = self
        self.add_toolbar()

    def _toolbar_default(self):
        return self.toolbar_class(self, location=self.toolbar_location)

    def add_toolbar(self):
        if not self.toolbar_added:
            self.overlays.append(self.toolbar)
            self.toolbar_added = True
            self.request_redraw()

    def remove_toolbar(self):
        if self.toolbar_added and self.auto_hide:
            self.overlays.remove(self.toolbar)
            self.toolbar_added = False
            self.request_redraw()

    def _bounds_changed(self, old, new):
        self.toolbar.do_layout(force=True)
        super(ToolbarPlot, self)._bounds_changed(old, new)

    @on_trait_change('toolbar')
    def _toolbar_changed(self, name, obj, old, new):
        if self.toolbar_added:
            # fixup the new toolbar's component to match the old one
            new.component = old.component

            self.overlays.remove(old)
            self.toolbar_added = False
            self.add_toolbar()
