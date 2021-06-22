from commands.command import Command
from world.mudcombat import c_functions, misc
from evennia import default_cmds
from evennia.commands.default.help import CmdHelp


PREFIX = misc.PREFIX


class CmdFight(Command):
    """
    Starts a fight with everyone in the same room as you.

    Usage:
      fight

    When you start a fight, everyone in the room who is able to
    fight is added to combat, and a turn order is randomly rolled.
    When it's your turn, you can attack other characters.
    """

    key = "fight"
    help_category = "combat"

    def func(self):
        """
        This performs the actual command.
        """
        here = self.caller.location
        fighters = []

        if not self.caller.db.health:  # If you don't have any hp
            self.caller.msg(PREFIX + "You can't start a fight if you've been defeated!")
            return
        if c_functions.is_in_combat(self.caller):  # Already in a fight
            self.caller.msg(PREFIX + "You're already in a fight!")
            return
        for thing in here.contents:  # Test everything in the room to add it to the fight.
            if thing.db.health:  # If the object has HP...
                fighters.append(thing)  # ...then add it to the fight.
        if len(fighters) <= 1:  # If you're the only able fighter in the room
            self.caller.msg("There's nobody here to fight!")
            return
        if here.db.combat_turnhandler:  # If there's already a fight going on...
            here.msg_contents(PREFIX + "%s joins the fight!" % self.caller)
            here.db.combat_turnhandler.join_fight(self.caller)  # Join the fight!
            return
        here.msg_contents(PREFIX + "%s starts a fight!" % self.caller)
        # Add a turn handler script to the room, which starts combat.
        here.scripts.add("world.mudcombat.c_turnhandler.TurnHandler")


class CmdRest(Command):
    """
    Recovers damage.

    Usage:
      rest

    Resting recovers your HP to its maximum, but you can only
    rest if you're not in a fight.
    """

    key = "rest"
    help_category = "combat"

    def func(self):
        "This performs the actual command."

        if c_functions.is_in_combat(self.caller):  # If you're in combat
            self.caller.msg("You can't rest while you're in combat.")
            return

        self.caller.db.health = self.caller.db.max_health  # Set current HP to maximum
        self.caller.db.mana = self.caller.db.max_mana
        self.caller.db.stamina = self.caller.db.max_stamina
        self.caller.db.con = self.caller.db.max_con
        self.caller.db.str = self.caller.db.max_str
        self.caller.db.dec = self.caller.db.max_dec
        self.caller.db.int = self.caller.db.max_int
        self.caller.location.msg_contents("%s rests to recover health." % self.caller)
        misc.refresh_prompt(self.caller)
        self.caller.refresh_resources()
        """
        You'll probably want to replace this with your own system for recovering HP.
        """


class CmdCombatHelp(CmdHelp):
    """
    View help or a list of topics

    Usage:
      help <topic or command>
      help list
      help all

    This will search for help on commands and other
    topics related to the game.
    """

    # Just like the default help command, but will give quick
    # tips on combat when used in a fight with no arguments.

    def func(self):
        if c_functions.is_in_combat(self.caller) and not self.args:  # In combat and entered 'help' alone
            self.caller.msg(
                "Available combat commands:|/"
                + "|wAttack:|n Attack a target, attempting to deal damage.|/"
                + "|wSkill:|n Use a skill to attack a target, attempting to deal damage.|/"
                + "|wPass:|n Pass your turn without further action.|/"
                + "|wDisengage:|n End your turn and attempt to end combat.|/"
            )
        else:
            super().func()  # Call the default help command




class BattleCmdSet(default_cmds.CharacterCmdSet):
    """
    This command set includes all the commmands used in the battle system.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        self.add(CmdFight())
        self.add(CmdRest())
        self.add(CmdCombatHelp())
