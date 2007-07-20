""" Defines a Traits editor for "editing" (really displaying) a Chaco 
plot container.
"""
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

    # The plot editor is scrollable (overrides Traits UI Editor).
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
    #  Updates the editor when the object trait changes externally to the editor:
    #---------------------------------------------------------------------------
    def update_editor( self ):
        """ Updates the editor when the object trait changes externally to the
        editor.
        """
        pass


class PlotContainerEditor( BasicEditorFactory ):
    """ wxPython editor factory for Chaco2 plot containers. 
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:     
    #---------------------------------------------------------------------------

    # The class used to create all editor styles (overrides BasicEditorFactory).
    klass = _PlotContainerEditor

