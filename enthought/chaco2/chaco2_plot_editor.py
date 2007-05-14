"""
Traits UI editor for WX based on the chaco1 PlotEditor in traits/ui/wx/plot_editor.py
"""

# Major library imports
import wx
from numpy import arange

# Enthought library imports
from enthought.traits.api import Enum, false, List, Str, true, Range, Tuple, \
                                 RGBAColor, Bool, KivaFont, Trait, Int, Any, \
                                 Property
from enthought.traits.ui.api import View, Item, EnableRGBAColorEditor                             
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.editor_factory import EditorFactory

from enthought.enable2.api import black_color_trait, LineStyle, ColorTrait, white_color_trait
from enthought.enable2.wx_backend.api import Window


# Local relative imports
from plot_containers import OverlayPlotContainer
from plot_factory import create_line_plot, create_scatter_plot, \
                         add_default_grids, add_default_axes
from plot_label import PlotLabel
from scatter_markers import marker_trait

# Somewhat unorthodox...
from enthought.chaco2.tools.api import PanTool, SimpleZoom


#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------

WindowColor = "lightgray"

#-------------------------------------------------------------------------------
#  Trait definitions:  
#-------------------------------------------------------------------------------

# Range of values for an axis:
AxisRange =  Tuple( ( 0.0, 1.0, 0.01 ), 
                    labels = [ 'Low', 'High', 'Step' ],
                    cols   = 3 )
                    
# Minimum/Maximum axis bounds:                    
AxisBounds = Tuple( ( 0.0, 1.0 ),
                    labels = [ 'Min', 'Max' ],
                    cols   = 2 )

# Height/Width range for the plot widget:                    
PlotSize = Range( 50, 1000, 180 )

# Range of plot line weights:
LineWeight = Range( 1, 9, 3 )

# Defines the color editor to use for various color traits:
color_editor = EnableRGBAColorEditor( auto_set = False )


USE_DATA_UPDATE = 1


class Chaco2PlotItem(Item):
    index = Str
    value = Str
    title = Str("Plot Editor")
    
    x_bounds = AxisBounds
    x_auto = Bool(True)
    y_bounds = AxisBounds
    y_auto = Bool(True)

    # If "h", then the index is horizontal (x) and
    orientation = Enum("h", "v")

    # If these are None, then the index/value trait names are used
    x_label = Trait(None, None, Str)
    x_label_font = KivaFont("modern 10")
    x_label_color = black_color_trait
    y_label = Trait(None, None, Str)
    y_label_font = KivaFont("modern 10")
    y_label_color = black_color_trait
    
    # General plot properties
    color = ColorTrait("blue")
    bgcolor = white_color_trait
    bg_color = Property   # backwards compatibility; deprecated
    padding_bg_color = ColorTrait(WindowColor)
    
    # Border properties
    border_width = Int(1)
    border_visible = false
    border_dash = LineStyle
    border_color = black_color_trait
    
    # the type of the plot
    type = Enum("line", "scatter")
    type_trait = Str
    
    # plot-specific properties.  These might not apply to all plot types.
    marker = marker_trait
    marker_size = Int(4)
    outline_color = black_color_trait
    
    def __init__(self, index, value, type="line", **traits):
        self.index = index
        self.value = value
        self.type = type
        self.name = "Plot"
        super(Chaco2PlotItem, self).__init__(**traits)
        
        self.editor = Chaco2EditorFactory()
        
        self.editor.plotitem = self
        
        return

    def _set_bg_color(self, val):
        self.bgcolor = val
    
    def _get_bg_color(self):
        return self.bgcolor


class Chaco2EditorFactory ( EditorFactory ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    width    = PlotSize     # Width of the plot editor
    height   = PlotSize     # Height of the plot editor
    plotitem = Any

    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return Chaco2PlotEditor( parent,
                                 factory     = self, 
                                 ui          = ui, 
                                 object      = object, 
                                 name        = name, 
                                 description = description )
    
    def text_editor ( self, ui, object, name, description, parent ):
        return Chaco2PlotEditor( parent,
                                 factory     = self, 
                                 ui          = ui, 
                                 object      = object, 
                                 name        = name, 
                                 description = description )
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return Chaco2PlotEditor( parent,
                                 factory     = self, 
                                 ui          = ui, 
                                 object      = object, 
                                 name        = name, 
                                 description = description )


class Chaco2PlotEditor ( Editor ):
    
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        plotitem = factory.plotitem
        
        container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                         bgcolor = plotitem.padding_bg_color,
                                         use_backbuffer=True)
        
        if plotitem.title != '':
            container.overlays.append(PlotLabel(plotitem.title, component=container,
                                                overlay_position="top"))
        
        self._container = container
        window = Window(parent, component = container)
        self.control = control = window.control
        control.SetSize((factory.width, factory.height))
        object = self.object

        if USE_DATA_UPDATE == 1:
            for name in (plotitem.index, plotitem.value):
                object.on_trait_change( self._update_data, name)
        for name in (plotitem.type_trait,):
            object.on_trait_change( self._update_editor, name)
        return
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
    
    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        object = self.object
        plotitem = self.factory.plotitem
        
        if USE_DATA_UPDATE == 1:
            for name in (plotitem.index, plotitem.value):
                object.on_trait_change( self._update_data, name, remove = True )
        for name in (plotitem.type_trait,):
            object.on_trait_change( self._update_editor, name, remove = True )
        self._destroy_plot()
        super(Chaco2PlotEditor, self).dispose()
    
    def _destroy_plot(self):
        if self._container and self._plot:
            plot = self._plot
            del plot.index._data
            del plot.index._cached_mask
            del plot.value._data
            del plot.value._cached_mask
            self._container.remove(plot)
            self._plot = None
            plot.index = None
            plot.value = None
        return
    
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
    
    def update_editor(self):
        """ Updates the editor when the object trait changes external to the 
            editor.
        """
        
        factory  = self.factory
        plotitem = factory.plotitem
        
        # Remove the old plot
        if self._plot is not None:
            self._destroy_plot()
        
        try:
            x_values = getattr(self.object, plotitem.index)
            y_values = getattr(self.object, plotitem.value)
        except:
            self._container.request_redraw()
            return
        
        if plotitem.type_trait != "":
            plot_type = getattr(self.object, plotitem.type_trait)
        else:
            plot_type = plotitem.type
        
        if plotitem.x_auto == True:
            index_bounds = None
        else:
            index_bounds = plotitem.x_bounds

        if plotitem.y_auto == True:
            value_bounds = None
        else:
            value_bounds = plotitem.y_bounds
        
        # Class-level attribute mapping different plot_type strings to methods for
        # creating different types of plots
        plot_creator_map = { "line": self._create_line_plot,
                             "scatter": self._create_scatter_plot }
        
        if plot_type in plot_creator_map.keys():
            plot = plot_creator_map[plot_type](plotitem, (x_values, y_values),
                                                index_bounds = index_bounds,
                                                value_bounds = value_bounds,
                                                orientation = plotitem.orientation)
        else:
            raise RuntimeError, "Unknown plot type '%s' in Chaco2PlotEditor." % plot_type
        
        self._set_basic_properties(plot, plotitem)
        
        self._add_axis_grids(plot, plotitem)
        
        self._plot = plot
        self._container.add(plot)
        self._container.request_redraw()
        return

    def _update_data(self):
        """ Updates the editor when the object trait changes external to the 
            editor.
        """
        if self._plot is None:
            self.update_editor()
        else:            
            x_values = getattr(self.object, self.factory.plotitem.index)
            y_values = getattr(self.object, self.factory.plotitem.value)
            self._plot.index.set_data(x_values)
            self._plot.value.set_data(y_values)

            
    def _set_basic_properties(self, plot, plotitem):
        for attr in ("color", "bgcolor", "border_visible", "border_width",
                     "border_dash", "border_color"):
            setattr(plot, attr, getattr(plotitem, attr))
        return

    def _create_line_plot(self, plotitem, values, **kwargs):
        plot = create_line_plot(values, **kwargs)
        return plot
    
    def _create_scatter_plot(self, plotitem, values, **kwargs):
        plot = create_scatter_plot(values, **kwargs)
        for attr in ("marker", "marker_size", "outline_color"):
            setattr(plot, attr, getattr(plotitem, attr))
        return plot
    
    def _add_axis_grids(self, new_plot, plotitem):
        if plotitem.x_label is not None:
            htitle = plotitem.x_label
        else:
            htitle = plotitem.index
        
        if plotitem.y_label is not None:
            vtitle = plotitem.y_label
        else:
            vtitle = plotitem.value
            
        if plotitem.orientation == "v":
            htitle, vtitle = vtitle, htitle
        
        value_axis, index_axis = add_default_axes(new_plot, htitle=htitle, vtitle=vtitle,
                                        orientation=plotitem.orientation)
        index_axis.title_font = plotitem.x_label_font
        index_axis.title_color = plotitem.x_label_color
        value_axis.title_font = plotitem.y_label_font
        value_axis.title_color = plotitem.y_label_color
        
        add_default_grids(new_plot)
        new_plot.tools.append(PanTool(new_plot))
        zoom = SimpleZoom(component=new_plot, tool_mode="box", always_on=False)
        new_plot.overlays.append(zoom)
        return


# EOF
