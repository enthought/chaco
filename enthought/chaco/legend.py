""" Defines the Legend, AbstractCompositeIconRenderer, and
CompositeIconRenderer classes.
"""
from numpy import array, zeros_like

from enthought.enable.api import white_color_trait
from enthought.kiva import font_metrics_provider
from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api import Any, Dict, Enum, Bool, HasTraits, Int, \
                                 Instance, List, CList, Float

# Local relative imports
from abstract_overlay import AbstractOverlay
from label import Label
from lineplot import LinePlot
from plot_component import PlotComponent
from scatterplot import ScatterPlot


class AbstractCompositeIconRenderer(HasTraits):
    """ Abstract class for an icon renderer.
    """
    def render_icon(self, plots, gc, x, y, width, height):
        """ Renders an icon representing the given list of plots onto the
        graphics context, using the given dimensions and at the specified
        position.
        """
        raise NotImplementedError



class CompositeIconRenderer(AbstractCompositeIconRenderer):
    """ Renderer for composite icons.
    """
    def render_icon(self, plots, *render_args):
        """ Renders an icon for a list of plots. """
        types = set(map(type, plots))
        if types == set([ScatterPlot]):
            self._render_scatterplots(plots, *render_args)
        elif types == set([LinePlot]):
            self._render_lineplots(plots, *render_args)
        elif types == set([ScatterPlot, LinePlot]):
            self._render_line_scatter(plots, *render_args)
        else:
            raise ValueError("Don't know how to render combination plot with " +\
                             "renderers " + str(types))
        return

    def _render_scatterplots(self, plots, gc, x, y, width, height):
        # Don't support this for now
        pass

    def _render_lineplots(self, plots, gc, x, y, width, height):
        # Assume they are all the same color/appearance and use the first one
        plots[0]._render_icon(gc, x, y, width, height)

    def _render_line_scatter(self, plots, gc, x, y, width, height):
        # Separate plots into line and scatter renderers; render one of each
        scatter = [p for p in plots if type(p) == ScatterPlot]
        line = [p for p in plots if type(p) == LinePlot]
        line[0]._render_icon(gc, x, y, width, height)
        scatter[0]._render_icon(gc, x, y, width, height)



class Legend(AbstractOverlay):
    """ A legend for a plot.
    """
    # The font to use for the legend text.
    font = KivaFont("modern 12")

    # The amount of space between the content of the legend and the border.
    border_padding = Int(10)

    # The border is visible (overrides Enable Component).
    border_visible = True

    # The background color of the legend (overrides AbstractOverlay).
    bgcolor = white_color_trait

    # The position of the legend with respect to its overlaid component.  (This
    # attribute applies only if the legend is used as an overlay.)
    #
    # * ur = Upper Right
    # * ul = Upper Left
    # * ll = Lower Left
    # * lr = Lower Right
    align = Enum("ur", "ul", "ll", "lr")

    # The amount of space between legend items.
    line_spacing = Int(3)

    # The size of the icon or marker area drawn next to the label.
    icon_bounds = List([24, 24])

    # Amount of spacing between each label and its icon.
    icon_spacing = Int(5)

    # Map of labels (strings) to plot instances or lists of plot instances.  The
    # Legend determines the appropriate rendering of each plot's marker/line.
    plots = Dict

    # The list of labels to show and the order to show them in.  If this
    # list is blank, then the keys of self.plots is used and displayed in
    # alphabetical order.  Otherwise, only the items in the **labels**
    # list are drawn in the legend.  Labels are ordered from top to bottom.
    labels = List

    # Whether or not to hide plots that are not visible.  (This is checked during
    # layout.)  This option *will* filter out the items in **labels** above, so
    # if you absolutely, positively want to set the items that will always
    # display in the legend, regardless of anything else, then you should turn
    # this option off.  Otherwise, it usually makes sense that a plot renderer
    # that is not visible will also not be in the legend.
    hide_invisible_plots = Bool(True)

    # If hide_invisible_plots is False, we can still choose to render the names
    # of invisible plots with an alpha.
    invisible_plot_alpha = Float(0.33)

    # The renderer that draws the icons for the legend.
    composite_icon_renderer = Instance(AbstractCompositeIconRenderer)

    # Action that the legend takes when it encounters a plot whose icon it
    # cannot render:
    #
    # * 'skip': skip it altogether and don't render its name
    # * 'blank': render the name but leave the icon blank (color=self.bgcolor)
    # * 'questionmark': render a "question mark" icon
    error_icon = Enum("skip", "blank", "questionmark")

    # Should the legend clip to the bounds it needs, or to its parent?
    clip_to_component = Bool(False)

    # The legend is not resizable (overrides PlotComponent).
    resizable = "hv" 

    # The legend draws itself as in one pass when its parent is drawing
    # the **draw_layer** (overrides PlotComponent).
    unified_draw = True
    # The legend is drawn on the overlay layer of its parent (overrides
    # PlotComponent).
    draw_layer = "overlay"

    #------------------------------------------------------------------------
    # Private Traits
    #------------------------------------------------------------------------

    # A cached list of Label instances
    _cached_labels = List
    
    # A cached array of label sizes.
    _cached_label_sizes = Any
    
    # A cached list of label names.
    _cached_label_names = CList

    # A list of the visible plots.  Each plot corresponds to the label at
    # the same index in _cached_label_names.  This list does not necessarily
    # correspond to self.plots.value() because it is sorted according to
    # the plot name and it potentially excludes invisible plots.
    _cached_visible_plots = CList

    # A cached array of label positions relative to the legend's origin
    _cached_label_positions = Any


    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.
        
        Implements AbstractOverlay.
        """
        self.do_layout()
        valign, halign = self.align
        if valign == "u":
            y = component.y2 - self.outer_height
        else:
            y = component.y
        if halign == "r":
            x = component.x2 - self.outer_width
        else:
            x = component.x
        self.outer_position = [x, y]
        if self.clip_to_component:
            c = self.component
            gc.save_state()
            gc.clip_to_rect(c.x, c.y, c.width, c.height)
        PlotComponent._draw(self, gc, view_bounds, mode)
        if self.clip_to_component:
            gc.restore_state()
        return

    # The following two methods implement the functionality of the Legend
    # to act as a first-class component instead of merely as an overlay.
    # The make the Legend use the normal PlotComponent render methods when
    # it does not have a .component attribute, so that it can have its own
    # overlays (e.g. a PlotLabel).
    # 
    # The core legend rendering method is named _draw_as_overlay() so that
    # it can be called from _draw_plot() when the Legend is not an overlay,
    # and from _draw_overlay() when the Legend is an overlay.

    def _draw_plot(self, gc, view_bounds=None, mode="normal"):
        if self.component is None:
            self._draw_as_overlay(gc, view_bounds, mode)
        return

    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        if self.component is not None:
            self._draw_as_overlay(gc, view_bounds, mode)
        else:
            PlotComponent._draw_overlay(self, gc, view_bounds, mode)
        return

    def _draw_as_overlay(self, gc, view_bounds=None, mode="normal"):
        """ Draws the overlay layer of a component.
        
        Overrides PlotComponent.
        """
        # Determine the position we are going to draw at from our alignment
        # corner and the corresponding outer_padding parameters.  (Position
        # refers to the lower-left corner of our border.)

        # First draw the border, if necesssary.  This sort of duplicates
        # the code in PlotComponent._draw_overlay, which is unfortunate;
        # on the other hand, overlays of overlays seem like a rather obscure
        # feature.

        gc.save_state()
        try:
            gc.clip_to_rect(self.x, self.y, self.width, self.height)
            edge_space = self.border_width + self.border_padding
            icon_width, icon_height = self.icon_bounds

            icon_x = self.x + edge_space
            text_x = icon_x + icon_width + self.icon_spacing
            y = self.y2 - edge_space

            if self._cached_label_positions is not None:
                if len(self._cached_label_positions) > 0:
                    self._cached_label_positions[:,0] = icon_x

            for i, label_name in enumerate(self._cached_label_names):
                # Compute the current label's position
                label_height = self._cached_label_sizes[i][1]
                y -= label_height
                self._cached_label_positions[i][1] = y

                # Try to render the icon
                icon_y = y + (label_height - icon_height) / 2
                #plots = self.plots[label_name]
                plots = self._cached_visible_plots[i]
                render_args = (gc, icon_x, icon_y, icon_width, icon_height)

                try:
                    if isinstance(plots, list) or isinstance(plots, tuple):
                        # TODO: How do we determine if a *group* of plots is
                        # visible or not?  For now, just look at the first one
                        # and assume that applies to all of them
                        if not plots[0].visible:
                            # TODO: the get_alpha() method isn't supported on the Mac kiva backend
                            #old_alpha = gc.get_alpha()
                            old_alpha = 1.0
                            gc.set_alpha(self.invisible_plot_alpha)
                        else:
                            old_alpha = None
                        if len(plots) == 1:
                            plots[0]._render_icon(*render_args)
                        else:
                            self.composite_icon_renderer.render_icon(plots, *render_args)
                    else:
                        # Single plot
                        if not plots.visible:
                            #old_alpha = gc.get_alpha()
                            old_alpha = 1.0
                            gc.set_alpha(self.invisible_plot_alpha)
                        else:
                            old_alpha = None
                        plots._render_icon(*render_args)

                    icon_drawn = True
                except:
                    icon_drawn = self._render_error(*render_args)

                if icon_drawn:
                    # Render the text
                    gc.translate_ctm(text_x, y)
                    gc.set_antialias(0)
                    self._cached_labels[i].draw(gc)
                    gc.set_antialias(1)
                    gc.translate_ctm(-text_x, -y)

                    # Advance y to the next label's baseline
                    y -= self.line_spacing
                if old_alpha is not None:
                    gc.set_alpha(old_alpha)

        finally:
            gc.restore_state()

        return

    def _render_error(self, gc, icon_x, icon_y, icon_width, icon_height):
        """ Renders an error icon or performs some other action when a
        plot is unable to render its icon.  
        
        Returns True if something was actually drawn (and hence the legend 
        needs to advance the line) or False if nothing was drawn.
        """
        if self.error_icon == "skip":
            return False
        elif self.error_icon == "blank" or self.error_icon == "questionmark":
            gc.save_state()
            gc.set_fill_color(self.bgcolor_)
            gc.rect(icon_x, icon_y, icon_width, icon_height)
            gc.fill_path()
            gc.restore_state()
            return True
        else:
            return False

    def get_preferred_size(self):
        """
        Computes the size and position of the legend based on the maximum size of
        the labels, the alignment, and position of the component to overlay.
        """
        # Gather the names of all the labels we will create
        if len(self.plots) == 0:
            return [0, 0]

        plot_names, visible_plots = zip(*sorted(self.plots.items()))
        label_names = self.labels
        if len(label_names) == 0:
            if len(self.plots) > 0:
                label_names = plot_names
            else:
                self._cached_labels = []
                self._cached_label_sizes = []
                self._cached_label_names = []
                self._cached_visible_plots = []
                self.outer_bounds = [0, 0]
                return [0, 0]

        if self.hide_invisible_plots:
            visible_labels = []
            visible_plots = []
            for i, name in enumerate(label_names):
                val = self.plots[plot_names[i]]
                # Rather than checking for a list/TraitListObject/etc., we just check
                # for the attribute first
                if hasattr(val, 'visible'):
                    if val.visible:
                        visible_labels.append(name)
                        visible_plots.append(val)
                else:
                    # If we have a list of renderers, add the name if any of them are
                    # visible
                    for renderer in val:
                        if renderer.visible:
                            visible_labels.append(name)
                            visible_plots.append(val)
                            break
            label_names = visible_labels

        # Create the labels
        labels = [self._create_label(text) for text in label_names]

        # We need a dummy GC in order to get font metrics
        dummy_gc = font_metrics_provider()
        label_sizes = array([label.get_width_height(dummy_gc) for label in labels])

        if len(label_sizes) > 0:
            max_label_width = max(label_sizes[:, 0])
            total_label_height = sum(label_sizes[:, 1]) + (len(label_sizes)-1)*self.line_spacing
        else:
            max_label_width = 0
            total_label_height = 0
        
        legend_width = max_label_width + self.icon_spacing + self.icon_bounds[0] \
                        + self.hpadding + 2*self.border_padding
        legend_height = total_label_height + self.vpadding + 2*self.border_padding

        self._cached_labels = labels
        self._cached_label_sizes = label_sizes
        self._cached_label_positions = zeros_like(label_sizes)
        self._cached_label_names = label_names
        self._cached_visible_plots = visible_plots

        if "h" not in self.resizable:
            legend_width = self.outer_width
        if "v" not in self.resizable:
            legend_height = self.outer_height
        return [legend_width, legend_height]

    def get_label_at(self, x, y):
        """ Returns the label object at (x,y) """
        for i, pos in enumerate(self._cached_label_positions):
            size = self._cached_label_sizes[i]
            corner = pos + size
            if (pos[0] <= x <= corner[0]) and (pos[1] <= y <= corner[1]):
                return self._cached_labels[i]
        else:
            return None

    def _do_layout(self):
        if self.component is not None or len(self._cached_labels) == 0 or \
                self._cached_label_sizes is None or len(self._cached_label_names) == 0:
            width, height = self.get_preferred_size()
            self.outer_bounds = [width, height]
        return

    def _create_label(self, text):
        """ Returns a new Label instance for the given text.  Subclasses can
        override this method to customize the creation of labels.
        """
        return Label(text=text, font=self.font, margin=0, bgcolor="transparent",
                     border_width=0) 

    def _composite_icon_renderer_default(self):
        return CompositeIconRenderer()

    def _anytrait_changed(self, name, old, new):
        if name in ("font", "border_padding", "padding", "line_spacing", "icon_bounds",
                    "icon_spacing", "labels", "plots", "plots_items", "labels_items",
                    "border_width", "align", "position", "position_items", "bounds",
                    "bounds_items"):
            self._layout_needed = True
        return




# EOF
