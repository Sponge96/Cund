from evennia import EvMenu
from commands.command import Command
from world.items import ITEMS
from world.mudcombat.c_skills import SKILLS
from world.mudcombat.misc import PREFIX, error_colour, highlight_colour, cooldown_colour

"""
COMMANDS
"""


class Skills(Command):
    key = "Skills"

    def func(self):
        to_check = self.caller.db.skills_known

        if to_check:
            EvMenu(self.caller, "world.menu_commands", startnode="skill_menu", cmd_on_exit=None)
        else:
            self.caller.msg(f"{highlight_colour}{PREFIX}|n {error_colour}You don't currently have any known skills!|n")


class Inventory(Command):
    key = "Inventory"

    def func(self):
        to_check = self.caller.db.inventory

        if to_check:
            EvMenu(self.caller, "world.menu_commands", startnode="inventory_menu", cmd_on_exit=None)
        else:
            self.caller.msg(f"{highlight_colour}{PREFIX}|n {error_colour}Your inventory is currently empty!|n")


class PickUp(Command):
    key = "Pickup"

    def func(self):
        to_check = self.caller.location.attributes.get("inventory")

        if to_check:
            EvMenu(self.caller, "world.menu_commands", startnode="pickup_menu", cmd_on_exit=None)
        else:
            self.caller.msg(f"{highlight_colour}{PREFIX}|n {error_colour}There is nothing to pickup!|n")


class Drop(Command):
    key = "Drop"

    def func(self):
        to_check = self.caller.db.inventory

        if to_check:
            EvMenu(self.caller, "world.menu_commands", startnode="drop_menu", cmd_on_exit=None)
        else:
            self.caller.msg(f"{highlight_colour}{PREFIX}|n {error_colour}You don't have any items you can drop!|n")


class Gear(Command):
    key = "Gear"

    def func(self):
        if self.caller.db.weapon or self.caller.db.armour:
            EvMenu(self.caller, "world.menu_commands", startnode="gear_menu", cmd_on_exit=None)
        else:
            self.caller.msg(f"{highlight_colour}{PREFIX}|n {error_colour}You have no items equipped!|n")


"""
MENUS
"""


def skill_menu(caller):
    text = "Skills"
    options = []
    for thing in caller.db.skills_known:
        options.append({"desc": f"{thing}",
                        "goto": ("skill_description", {"selected": thing})})
    options.append({"desc": "Quit",
                    "goto": "close_menu"})
    return text, options


def skill_description(caller, raw_string, **kwargs):
    skill = kwargs.get("selected")
    skilldata = SKILLS[skill]["description"]
    text = f"{skill}:{skilldata}"
    option = ({"desc": "Back", "goto": "skill_menu"})
    return text, option


def inventory_menu(caller):
    text = "Inventory"
    options = []
    for thing in caller.db.inventory:
        options.append(
            {"desc": f"{thing}",
             "goto": ("inventory_description", {"selected": thing})})
    options.append(
        {"desc": "Quit",
         "goto": "close_menu"}
    )
    return text, options


def inventory_description(caller, raw_string, **kwargs):
    item = kwargs.get("selected")
    itemdata = ITEMS[item]
    colour = "|W"
    if itemdata["stat"] == "dex" and caller.db.dex < 20:
        colour = cooldown_colour
    if itemdata["stat"] == "int" and caller.db.int < 20:
        colour = cooldown_colour
    if itemdata["stat"] == "str" and caller.db.str < 20:
        colour = cooldown_colour
    text = f"{item}: {itemdata['desc']}"
    options = ({"desc": f"{colour}Equip|n", "goto": ("equip_menu", {"selected": item})}, return_option)
    return text, options


def equip_menu(caller, raw_string, **kwargs):
    item = kwargs.get("selected")
    itemdata = ITEMS[item]

    if itemdata["stat"] == "dex" and caller.db.dex < 20:
        text = f"{PREFIX} You do not have enough dexterity to equip {item}"
        options = return_option
        return text, options
    if itemdata["stat"] == "int" and caller.db.int < 20:
        text = f"{PREFIX} You do not have enough intelligence to equip {item}"
        options = return_option
        return text, options
    if itemdata["stat"] == "str" and caller.db.str < 20:
        text = f"{PREFIX} You do not have enough strength to equip {item}"
        options = return_option
        return text, options

    if itemdata["type"] == "weapon":
        if caller.db.weapon:
            text = f"Would you like to swap this with {caller.db.weapon}?"
            options = ({"key": ("1", "Yes", "y"),
                        "desc": "Yes",
                        "goto": ("swap_weapon", {"selected": item})},
                       {"key": ("2", "No", "n"),
                        "desc": "No",
                        "goto": "inventory_menu"})
            return text, options
        else:
            caller.db.weapon.append(item)
            caller.db.inventory.remove(item)
            caller.refresh_resources()

    if itemdata["type"] == "armour":
        if caller.db.armour:
            text = f"Would you like to swap this with {caller.db.armour}?"
            options = ({"key": ("1", "Yes", "y"),
                        "desc": "Yes",
                        "goto": ("swap_armour", {"selected": item})})
            return text, options
        else:
            caller.db.armour.append(item)
            caller.db.inventory.remove(item)
            caller.refresh_resources()


def pickup_menu(caller):
    text = "What would you like to pickup"
    options = []
    for thing in caller.location.attributes.get("inventory"):
        options.append(
            {"desc": f"{thing}",
             "goto": ("pickup_resolve", {"selected": thing})})
    options.append(
        {"desc": "CLOSE MENU",
         "goto": "close_menu"}
    )
    return text, options


def drop_menu(caller):
    text = "What would you like to drop"
    options = []
    for thing in caller.db.inventory:
        options.append(
            {"desc": f"{thing}",
             "goto": ("drop_resolve", {"selected": thing})})
    options.append(
        {"desc": "CLOSE MENU",
         "goto": "close_menu"}
    )
    return text, options


def gear_menu(caller):
    text = "Gear Overview"
    options = []
    if caller.db.weapon:
        options.append({"desc": caller.db.weapon[0],
                        "goto": ("gear_description", {"selected": caller.db.weapon[0]})})
    if caller.db.armour:
        options.append({"desc": caller.db.armour[0],
                        "goto": ("gear_description", {"selected": caller.db.armour[0]})})
    options.append({"desc": "Quit"})
    return text, options


def gear_description(caller, raw_input, **kwargs):
    item = kwargs.get("selected")
    itemdata = ITEMS[item]
    text = f"{item}: {itemdata['desc']}"
    options = ({"desc": "Unequip", "goto": ("unequip_menu", {"selected": item})},
               {"key": ("2", "Return", "Back"),
                "desc": "Return",
                "goto": "gear_menu"})
    return text, options


def unequip_menu(caller, raw_string, **kwargs):
    item = kwargs.get("selected")
    text = f"Are you sure you would like to UNEQUIP {item}?"
    options = ({"key": ("1", "Yes", "y"),
                "desc": "Yes",
                "goto": ("unequip_item", {"selected": item})},
               {"key": ("2", "No", "n"),
                "desc": "No",
                "goto": "gear_menu"})
    return text, options


"""
RESOLVES
"""


def swap_weapon(caller, raw_string, **kwargs):
    item = kwargs.get("selected")
    caller.db.inventory.append(caller.db.weapon)
    caller.db.weapon.append(item)
    caller.refresh_resources()


def swap_armour(caller, raw_string, **kwargs):
    item = kwargs.get("selected")
    caller.db.inventory.append(caller.db.armour)
    caller.db.armour.append(item)
    caller.refresh_resources()


def pickup_resolve(caller, raw_string, **kwargs):
    thing = kwargs.get("selected")
    caller.db.inventory.append(thing)
    caller.location.attributes.get("inventory").remove(thing)


def drop_resolve(caller, raw_string, **kwargs):
    thing = kwargs.get("selected")
    caller.db.inventory.remove(thing)
    caller.location.attributes.get("inventory").append(thing)


def unequip_item(caller, raw_string, **kwargs):
    item = kwargs.get("selected")
    itemdata = ITEMS[item]
    if itemdata["type"] == "weapon":
        caller.db.inventory.append(caller.db.weapon[0])
        caller.db.weapon.remove(item)
        caller.refresh_resources()
    if itemdata["type"] == "armour":
        caller.db.inventory.append(caller.db.armour[0])
        caller.db.armour.remove(item)
        caller.refresh_resources()


def close_menu(caller):
    text = ""
    options = []
    return text, options


return_option = ({"desc": "Return",
                  "goto": "inventory_menu"})
