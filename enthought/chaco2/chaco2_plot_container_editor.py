""" Defines a Traits editor for "editing" (really displaying) a Chaco 
plot container.
"""
#-------------------------------------------------------------------------------
#  Traits editor for editing (displaying, really) a ChacoPlotContainer
#  Written by: David C. Morrill
#  Date: 01/26/2007
#  (c) Copyright 2007 by Enthought, Inc.
#----------------------------------------------------------------------------


from enthought.etsconfig.api import ETSConfig

from enthought.traits.ui.api import BasicEditorFactory

if ETSConfig.toolkit == 'wx':
    from enthought.traits.ui.wx.editor import Editor
    from enthought.enable2.wx_backend.api import Window
elif ETSConfig.toolkit == 'qt4':
    from enthought.traits.ui.qt4.editor import Editor
    from enthought.enable2.qt4_backend.api import Window
else:
    Editor = object
    Window = None

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

