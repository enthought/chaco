import numpy
from traits.api import HasTraits, Instance, List, Str, Array, Enum, File, \
    Int, Button, Property, DelegatesTo, cached_property, on_trait_change
from traitsui.api import View, Group, VGroup, HGroup, Item, spring, CheckListEditor, InstanceEditor, TabularEditor
from pyface.api import MessageDialog
from enable.api import ComponentEditor
from chaco.api import ArrayPlotData, Plot, ScatterInspectorOverlay, marker_trait, jet
from chaco.tools.api import PanTool, ZoomTool, DragZoom, ScatterInspector



iris_dtype = numpy.dtype([
    ('sepal length', float),
    ('sepal width', float),
    ('petal length', float),
    ('petal width', float),
    ('species', 'O')])

#class IrisAdapter(TabularAdapter):
#    """ This is an adapter that maps the iris dtype to the TabularEditor columns
#    and also knows how to get the value of the cell.
#    """
#    columns = ['sepal length', 'sepal width', 'petal length', 'petal width', 'species']
#    
#    def get_text(self, object, trait, row, column):
#        return getattr(object, trait)[row][column]
    
class IrisDataset(HasTraits):
    """ A dataset loaded from a file, displayed in a Tabular editor.
    """
    filename = File
            
    data = Property(Array(dtype=iris_dtype), depends_on='filename')
    
    selection = List(Int)
    
    def _open_file_changed(self):
        dlg = FileDialog()
        if dlg.open():
            self.filename = dlg.path
    
    @cached_property
    def _get_data(self):
        """ The filename has changed, so try to read in a new dataset.
        
        Note that we can display the array directly.
        """
        if not self.filename:
            return numpy.array([], dtype=iris_dtype)
        try:
            # load into an array
            return numpy.loadtxt(self.filename, iris_dtype, delimiter=',')
        except Exception, exc:
            dlg = MessageDialog(title='Could not open file %s' % self.filename,
                message=str(exc))
            dlg.open()
            return numpy.array([], dtype=iris_dtype)
    
    traits_view = View(
        VGroup(
            HGroup(
                Item('open_file'),
                Item('filename', style='readonly', springy=True),
                Item('update'),
                show_labels=False,
            ),
            show_labels=False,
        ),
        height=600,
        width=400,
        resizable=True,
    )
