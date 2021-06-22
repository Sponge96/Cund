def refreshstats(caller):
    caller.db.health = caller.db.max_health
    caller.db.stamina = caller.db.max_stamina
    caller.db.mana = caller.db.max_mana


def race_node_dwarf(caller, raw_string, **kwargs):
    if not caller.db.race:
        caller.db.race = "dwarf"
        caller.db.max_health = 1250
        caller.db.max_stamina = 20
        caller.db.max_mana = 10
        refreshstats(caller)
    else:
        caller.msg("You have already selected a race")


def race_node_elf(caller, raw_string, **kwargs):
    if not caller.db.race:
        caller.db.race = "elf"
        caller.db.max_health = 800
        caller.db.max_stamina = 30
        caller.db.max_mana = 20
        refreshstats(caller)
    else:
        caller.msg("You have already selected a race")


def race_node_human(caller, raw_string, **kwargs):
    if not caller.db.race:
        caller.db.race = "human"
        caller.db.max_health = 1000
        caller.db.max_stamina = 10
        caller.db.max_mana = 30
        refreshstats(caller)
    else:
        caller.msg("You have already selected a race")


def race_select_node(caller, raw_string, **kwargs):
    if not caller.db.race:
        text = "Please choose from one of the following races!"
        options = (
            {"key": ("1", "dwarf"),
             "desc": "Dwarf:"
                     "\nStone Skin - Small chance to reduce damage with your tough skin"
                     "\nAdditional health but reduce mana",
             "goto": "race_node_dwarf"},

            {"key": ("2", "elf"),
             "desc": "Elf:"
                     "\nQuick Step - Small chance to dodge an attack with your nimble feet"
                     "\nAdditional stamina but reduced health",
             "goto": "race_node_elf"},

            {"key": ("3", "human"),
             "desc": "Human:"
                     "\nRetaliate - Small chance to reflex some damage."
                     "\nAdditional mana but reduced stamina",
             "goto": "race_node_human"}
        )
        return text, options
    else:
        caller.msg("Race has been reset, you can now choose a new race")
        caller.db.race = ""
        caller.db.max_health = 100
        caller.db.max_stamina = 20
        caller.db.max_mana = 20
        refreshstats(caller)
