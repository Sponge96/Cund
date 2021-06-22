from evennia import EvMenu
MAGE_SKILLS = ["ember", "wall of flame"]
FIGHTER_SKILLS = ["slash", "bash"]


def class_node(caller, raw_string, **kwargs):
    text = "Please choose from one of the following classes!"
    options = (
        {"key": ("1", "fighter"),
         "desc": "Fighter",
         "goto": ("node_2", {"class": "fighter"})},

        {"key": ("2", "mage"),
         "desc": "Mage",
         "goto": ("node_2", {"class": "mage"})},
    )
    return text, options


def node_2(caller, raw_string, **kwargs):
    character = caller.db._last_puppet
    player_class = kwargs.get("class")
    character.db.p_class = player_class
    text = "Who would you like to target?"
    options = []
    if caller.db.p_class == "mage":
        for skill in MAGE_SKILLS:
            options.append({"desc": "%s" % skill,
                            "goto": ("skill_1", {"selected": skill})})
    return text, options


def skill_1(caller, raw_string, **kwargs):
    character = caller.db._last_puppet
    character.db.skills_known = []
    skill1 = kwargs.get("selected")
    character.db.skills_known = skill1
    character.msg(caller.db.skills_known)
    caller.msg(caller.db.p_class)



# EvMenu(self, "world.character_creation_menu", startnode="class_node", cmd_on_exit=None)
