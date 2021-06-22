"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from world.mudcombat import c_functions, misc
from world.items import ITEMS


class Character(DefaultCharacter):
    """
    A character able to participate in turn-based combat. Has attributes for current
    and maximum HP, and access to combat commands.
    """

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
        """
        self.db.inventory = []
        self.db.range = 1
        self.db.armour = []
        self.db.av = 0
        self.db.weapon = []
        self.db.wv = 0
        self.db.visible = True
        self.db.con = 10
        self.db.str = 10
        self.db.dex = 10
        self.db.int = 10
        self.db.health = 10
        self.db.max_health = 10
        self.db.mana = 10
        self.db.max_mana = 10
        self.db.stamina = 10
        self.db.max_stamina = 10

    def set_stats(self):
        self.db.max_con = self.db.con
        self.db.max_str = self.db.str
        self.db.max_dex = self.db.dex
        self.db.max_int = self.db.int

    def refresh_resources(self):
        # HP
        self.db.max_health = int(self.db.con * 100)
        self.db.health = int(self.db.con * 100)
        # Stamina
        self.db.max_stamina = int(self.db.dex + self.db.str * 10)
        self.db.stamina = int(self.db.dex + self.db.str * 10)
        # MP
        self.db.max_mana = int(self.db.int * 200)
        self.db.mana = int(self.db.int * 200)
        # Dodge
        self.db.dodge = int(self.db.dex / 2)
        misc.refresh_prompt(self)
        # Armour
        if self.db.armour:
            itemdata = ITEMS[str(self.db.armour[0])]
            self.db.av = int(itemdata["value"])
        # Weapon
        if self.db.weapon:
            itemdata = ITEMS[str(self.db.weapon[0])]
            self.db.wv = int(itemdata["value"])

    def refresh_stats(self):
        self.db.con = self.db.max_con
        self.db.str = self.db.max_str
        self.db.dex = self.db.max_dex
        self.db.int = self.db.max_int
        self.refresh_resources()

    def at_before_move(self, destination):
        """
        Called just before starting to move this object to
        destination.

        Args:
            destination (Object): The object we are moving to

        Returns:
            shouldmove (bool): If we should move or not.

        Notes:
            If this method returns False/None, the move is cancelled
            before it is even started.

        """
        # Keep the character from moving if at 0 HP or in combat.
        if c_functions.is_in_combat(self):
            self.msg("You can't exit a room while in combat!")
            return False  # Returning false keeps the character from moving.
        if self.db.health <= 0:
            self.msg("You can't move, you've been defeated!")
            return False
        return True
