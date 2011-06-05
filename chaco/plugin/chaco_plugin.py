""" Envisage 3 plugin for Chaco functionality.
"""

from envisage.api import Plugin
from traits.api import List


ID = 'chaco'
ICHACO_SESSION = ID + '.plugin.session_service.SessionService'


class ChacoPlugin(Plugin):
    """ Envisage 3 plugin for Chaco functionality.
    """

    id = ID
    name = 'Chaco plugin'

    #### Contributions to extension points made by this plugin #################

    # Extension point Ids.
    COMMANDS = 'envisage.plugins.python_shell.commands'


    contributed_commands = List(contributes_to=COMMANDS)

    def _contributed_commands_default(self):
        commands = [
            "from chaco.shell.commands import *",
        ]
        return commands

    #### Plugin interface ######################################################

    def start(self):
        """ Monkeypatch the Chaco shell subsystem.
        """
        from chaco import shell
        from chaco.shell import commands
        from chaco.plugin.workbench_session import WorkbenchSession

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

