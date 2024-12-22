from django.conf import settings  # type: ignore

from evennia.commands.default import account
from evennia.server.sessionhandler import SESSION_HANDLER
from evennia.utils import utils


COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdSheet(COMMAND_DEFAULT_CLASS):
    """
    Displays your sheet

    Usage:
      sheet
      
    """

    key = "sheet"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        if not caller:
            return ""
        
        sessions = caller.sessid.split(',')

        if len(sessions) == 0:
            width = 78
        else:
            width = SESSION_HANDLER.get(int(sessions[0] or -1),{}).__dict__.get('protocol_flags',{}).get('SCREENWIDTH', {0:78})[0]
        
        self.msg(caller.sheet.get_formatted_display(width))