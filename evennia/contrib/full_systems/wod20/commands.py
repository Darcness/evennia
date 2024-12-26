from evennia.commands.cmdset import CmdSet
from .overrides import *
from .sheet import *

class Wod20CmdSet(CmdSet):
    key = "Wod20"
    priority = 1

    def at_cmdset_creation(self):
        super().at_cmdset_creation()

        self.add(CmdSheet)
        self.add(CmdPlusOOC)
        self.add(CmdSetStat)
        self.add(CmdOOC)