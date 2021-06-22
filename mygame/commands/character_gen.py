from commands.command import Command
from evennia import EvMenu


class CmdRaceMenu(Command):
    key = "race"

    def func(self):
        EvMenu(self.caller, "world.racemenu", startnode="race_select_node")


class CmdClassMenu(Command):
    key = "class"

    def func(self):
        EvMenu(self.caller, "world.classmenu", startnode="class_select_node")
