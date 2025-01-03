from django.conf import settings  # type: ignore
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdJob(COMMAND_DEFAULT_CLASS):
    """
    Take action on a job

    Usage:
      +job <#>                               Show a job number <#>
      +job/create <category>/<title>=<text>  Creates a job in <category> with
                                             <title> and <text>
      +job/assign <#>=[<player>]             Assigns job number <#> to staff 
                                             <player> (or unassigns if none 
                                             specified)
      +job/claim <#>                         Claims job number <#>
      +job/addplayer <#>=<player>            Adds <player> to job number <#>
      +job/comment <#>=<text>                Add a <text> as a comment to job
                                             number <#>
      +job/complete <#>=<text>               Adds <text> as a final comment on
                                             job number <#> then complete the 
                                             job.
      +job/delete <#>                        Deletes job number <#>
      


    Talk to those in your current location OOCly, sending either <message> with 'say' or <pose> as a pose.
    """

    key = "+job"
    locks = locks = "cmd:perm(job) or perm(Admin)"

    def func(self):
        switches = self.switches
        args = self.args

        if len(switches) < 1:
            # do +job
            pass
        elif len(switches) > 1:
            self.msg(f"|rERROR:|n Invalid syntax. see help +job for help.")
            return
        else:
            match switches[0]:
                case 'create':
                    pass
                case 'assign':
                    pass
                case 'claim':
                    pass
                case 'addplayer':
                    pass
                case 'comment':
                    pass
                case 'complete':
                    pass
                case 'delete':
                    pass
                case default:
                    self.msg(f"|rERROR:|n invalid switch: {switches[0]}")
                    return
