from enthought.enable.tools.hover_tool import HoverTool
from enthought.chaco.api import Plot
from enthought.chaco.tools.toolbars.plot_toolbar import PlotToolbar
from enthought.traits.api import Type, Bool, Instance, Enum, on_trait_change

class ToolbarPlot(Plot):
    # Should we turn on the auto-hide feature on the toolbar?
    auto_hide = Bool(False)

    # Hover Tool - used when auto-hide is True
    hovertool = Instance(HoverTool)
    hovertool_added = False

    # Hover Toolbar - is always visible when auto-hide is False
    toolbar = Instance(PlotToolbar)

    toolbar_class = Type(PlotToolbar)
    toolbar_added = False

    # Location of the default toolbar that is created if a toolbar
    # is not specified with the `toolbar` attribute.  Changing this
    # attribute after the ToolbarPlot instance is created has no effect;
    # use obj.toolbar.location to dynamically change the location of the
    # instance `obj`s toolbar.
    toolbar_location = Enum('top', 'right', 'bottom', 'left')

    def __init__(self, *args, **kw):
        toolbar = kw.pop("toolbar", None)
        super(ToolbarPlot, self).__init__(*args, **kw)

        self.hovertool = HoverTool(self, area_type="top",
                                   callback=self.add_toolbar)
        self.tools.append(self.hovertool)

        if toolbar is None:
            self.toolbar = self.toolbar_class(self, location=self.toolbar_location)
        else:
            self.toolbar = toolbar
            toolbar.component = self
        self.add_toolbar()

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

    def add_hovertool(self):
        if not self.hovertool_added:
            self.tools.append(self.hovertool)
            self.hovertool_added = True

    def remove_hovertool(self):
        if self.hovertool_added:
            self.tools.remove(self.hovertool)
            self.hovertool_added = False

    def _auto_hide_changed(self, old, new):
        if self.auto_hide:
            self.remove_toolbar()
            self.add_hovertool()
        else:
            self.remove_hovertool()
            self.add_toolbar()

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
