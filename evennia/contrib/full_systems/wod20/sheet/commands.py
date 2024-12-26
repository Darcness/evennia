import evennia

from django.conf import settings  # type: ignore

from evennia.objects.objects import DefaultCharacter
from evennia.server.sessionhandler import SESSION_HANDLER
from evennia.utils import utils


COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdSheet(COMMAND_DEFAULT_CLASS):
    """
    Displays your sheet

    Usage:
      +sheet

    """

    key = "+sheet"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args

        if not caller:
            return ""

        sessions = caller.sessid.split(',')

        width = SESSION_HANDLER.get(int(sessions[0] or -1), {}).__dict__.get('protocol_flags', {}
                                                                             ).get('SCREENWIDTH', {0: 78})[0] if len(sessions) > 0 else 78

        target = caller
        if len(args) > 0:
            if args != caller.name and not caller.permissions.check("Admin"):
                self.msg("You do not have permission to view other character's sheets")
                return

            target = evennia.search_object(args, typeclass="typeclasses.character.Character")

            if target is None:
                self.msg("Could not find character: " + args)
                return

        self.msg(target.sheet.get_formatted_display(target, width))

class CmdSetStat(COMMAND_DEFAULT_CLASS):
    """
    Sets stats on a player.

    Usage:
      +setstat <player>/<statType>=<statName>/<statValue>

      <player> -- Player to edit
      <statType> -- Type of stat to edit.  Valid types: vitals, attributes, talents, skills, knowledges
      <statName> -- Name of the stat to edit
      <statValue> -- Value
    """

    key = "+setstat"
    locks = "cmd:perm(setstat) or perm(Admin)"

    def func(self):
        caller = self.caller
        args = self.args
