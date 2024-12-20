from django.conf import settings  # type: ignore

from evennia.commands.default import account
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdPlusOOC(account.CmdOOC):
    """
    stop puppeting and go ooc

    Usage:
      +ooc

    Go out-of-character (OOC).

    This will leave your current character and put you in a incorporeal OOC state.
    """

    key = "+ooc"


class CmdOOC(COMMAND_DEFAULT_CLASS):
    """
    OOCly speak as your character

    Usage:
      ooc <message>
      ooc :<pose>

    Talk to those in your current location OOCly, sending either <message> with 'say' or <pose> as a pose.
    """

    key = "ooc"
    locks = "cmd:all()"

    def func(self):
        """Run the ooc command"""

        caller = self.caller

        if not self.args:
            caller.msg("Say what?")
            return

        speech = "|r<OOC>|n {name}".format(name=caller.get_display_name(caller))

        if self.args[0] == ":":
            speech += " " + self.args[1:]
        elif self.args[0] == ";":
            speech += self.args[1:]
        else:
            speech += " says, \"{}\".".format(caller.at_pre_say(self.args))

        self.caller.location.msg_contents(text=(speech, {"type": "ooc"}), from_obj=self.caller)
