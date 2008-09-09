""" Envisage 3 plugin for Chaco functionality.
"""

from enthought.envisage.api import Plugin
from enthought.traits.api import List


ID = 'enthought.chaco'
ICHACO_SESSION = ID + '.plugin.session_service.SessionService'


class ChacoPlugin(Plugin):
    """ Envisage 3 plugin for Chaco functionality.
    """

    id = ID
    name = 'Chaco plugin'

    #### Contributions to extension points made by this plugin #################

    # Extension point Ids.
    COMMANDS = 'enthought.plugins.python_shell.commands'
    

    contributed_commands = List(contributes_to=COMMANDS)

    def _contributed_commands_default(self):
        commands = [
            "from enthought.chaco.shell.commands import *",
        ]
        return commands

    #### Plugin interface ######################################################

    def start(self):
        """ Monkeypatch the Chaco shell subsystem.
        """
        from enthought.chaco import shell
        from enthought.chaco.shell import commands
        from enthought.chaco.plugin.workbench_session import WorkbenchSession

        commands.session = shell.session = WorkbenchSession(
            application=self.application)

        def show():
            """ Shows all the figure windows that have been created thus far, and
            creates a GUI main loop.  This function is useful in scripts to show plots and
            keep their windows open, and has no effect when used from the interpreter
            prompt.

            Inside Envisage, just raise the current window.
            """
            win = commands.session.active_window
            win.raise_window()

        commands.show = show

