from commands.command import Command
from evennia.utils import delay


def refreshstats(caller):
    caller.db.con = caller.db.base_con
    caller.db.str = caller.db.base_str
    caller.db.dec = caller.db.base_dec
    caller.db.int = caller.db.base_int


def class_node_fighter(caller, raw_string, **kwargs):
    if not caller.db.p_class:
        caller.db.p_class = "fighter"
        caller.db.base_con = 20
        caller.db.base_str = 22
        caller.db.base_dex = 18
        caller.db.base_int = 10
        caller.db.skills_known = ["slam", "multi strike", ]

        caller.db.con = caller.db.base_con
        caller.db.str = caller.db.base_str
        caller.db.dex = caller.db.base_dex
        caller.db.int = caller.db.base_int

        caller.db.base_health = caller.db.con * 100
        caller.db.base_mana = caller.db.int * 10
        caller.db.base_stamina = caller.db.dex * 10

    else:
        caller.msg("You have already selected a class")


def class_node_mage(caller, raw_string, **kwargs):
    if not caller.db.p_class:
        caller.db.p_class = "mage"
        caller.db.con = 20
        caller.db.str = 10
        caller.db.dex = 18
        caller.db.int = 22
        caller.db.skills_known = ["bolt of flame", "flame whip", ]
        caller.set_stats()
        caller.refresh_resources()

    else:
        caller.msg("You have already selected a class")


def class_node_rogue(caller, raw_string, **kwargs):
    if not caller.db.p_class:
        caller.db.p_class = "Rogue"
        caller.db.con = 20
        caller.db.str = 10
        caller.db.dex = 20
        caller.db.int = 10
        caller.db.skills_known = ["Backstab", "Vital Strike", "Fan of Knifes"]
        caller.set_stats()
        caller.refresh_resources()

    else:
        caller.msg("You have already selected a class")


def class_select_node(caller, raw_string, **kwargs):
    if not caller.db.p_class:
        text = "Please choose from one of the following races!"
        options = (
            {"key": ("1", "fighter"),
             "desc": "Fighter"
                     "\nSkills:"
                     "\nSlam - Low cost, medium damage "
                     "\nMulti Strike - high cost, high damage, multiple targets",
             "goto": "class_node_fighter"},

            {"key": ("2", "mage"),
             "desc": "Mage"
                     "\nSkills:"
                     "\n- Bold of Flame - Low cost, medium damage"
                     "\n- Flame Whip - high cost, high damage",
             "goto": "class_node_mage"},

            {"key": ("3", "rogue"),
             "desc": "Rogue"
                     "\nSkills:"
                     "\n- Backstab: Low cost, Low damage, Single"
                     "\n- Vital Strike: Medium Cost, High Damage, Single"
                     "\n- Fan of Knifes: High Cost, High Damage, AOE"
                     "\n- Precision: Medium Cost, N/A, Self",
             "goto": "class_node_rogue"}
        )
        return text, options
    else:
        caller.msg("class has been reset")
        caller.db.p_class = ""
        caller.db.skills_known = []
        caller.db.con = 1
        caller.db.str = 1
        caller.db.dex = 1
        caller.db.int = 1
        caller.set_stats()
        caller.refresh_resources()
