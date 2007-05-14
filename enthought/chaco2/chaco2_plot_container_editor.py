#-------------------------------------------------------------------------------
#  Traits editor for editing (displaying, really) a ChacoPlotContainer
#  Written by: David C. Morrill
#  Date: 01/26/2007
#  (c) Copyright 2007 by Enthought, Inc.
#----------------------------------------------------------------------------


from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.basic_editor_factory import BasicEditorFactory
from enthought.enable2.wx_backend.api import Window

class _PlotContainerEditor( Editor ):

    #---------------------------------------------------------------------------
    #  Trait definitions:     
    #---------------------------------------------------------------------------

    # Indicate that the plot editor is scrollable (default override):
    scrollable = True

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
    def init( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self._window       = Window( parent, component=self.value )
        self.control       = self._window.control

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
    def update_editor( self ):
        """ Updates the editor when the object trait changes external to the
        editor.
        """
        pass


class PlotContainerEditor( BasicEditorFactory ):

    #---------------------------------------------------------------------------
    #  Trait definitions:     
    #---------------------------------------------------------------------------

    # Class used to create all editor styles (override):
    klass = _PlotContainerEditor

