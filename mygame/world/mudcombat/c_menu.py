from evennia import EvMenu
from world.mudcombat import c_functions, c_skills, misc
from evennia.utils import delay

PREFIX = misc.PREFIX
DELAY = misc.DELAY
default_options = ({"key": ("1", "attack", "att"),
                    "desc": "Attack - Use your weapon to attack a target.",
                    "goto": "att_target"},

                   {"key": ("2", "skill", "cast"),
                    "desc": "Skills - Use a skill.",
                    "goto": "skill_select"},

                   # TODO!!
                   {"key": ("3", "item", "use"),
                    "desc": "Items - Use an item.",
                    "goto": "TODO"},

                   {"key": ("4", "flee", "run", "disengage"),
                    "desc": "Disengage - Attempt to flee from combat",
                    "goto": "disengage"},

                   {"key": ("5", "pass", "end"),
                    "desc": "End - End your turn without spending remaining actions.\n",
                    "goto": "end_turn"})

return_option = ({"desc": "Return",
                  "goto": "combat_menu"})

"""
Menu's
"""


def att_target(caller, raw_string, **kwargs):
    text = "Who would you like to attack?"
    options = []
    for target in caller.location.contents:
        if target.attributes.has("health"):
            if target.db.health > 0 and not target == caller:
                options.append(
                    {"desc": f"{target} - {get_health_colour(caller)}{target.db.health}/{target.db.max_health}|n",
                     "goto": ("att_resolve", {"selected": target})})

    options.append(return_option)
    return text, options


def skill_select(caller):
    text = "Select a Skill"
    options = []
    for skill in caller.db.skills_known:
        colour = "|W"
        if skill in caller.db.combat_oncooldown:
            colour = misc.cooldown_colour
        options.append({"desc": f"{colour}{skill}",
                        "goto": ("skill_check", {"selected": skill})})
    options.append({"desc": "Details", "goto": "skill_detail_view"})
    options.append(return_option)
    return text, options


def skill_detail_view(caller):
    text = "Select a Skill"
    options = []
    for skill in caller.db.skills_known:
        colour = "|W"
        if skill in caller.db.combat_oncooldown:
            colour = misc.cooldown_colour
        description = c_skills.SKILLS[skill]["description"]
        options.append({"desc": f"{colour}{skill}:\n{description}",
                        "goto": ("skill_check", {"selected": skill})})
    options.append(return_option)
    return text, options


def skill_check(caller, raw_string, **kwargs):
    skill_to_use = kwargs.get("selected")
    caller.db.combat_skill_to_use = skill_to_use
    skilldata = c_skills.SKILLS[skill_to_use]

    if skill_to_use in caller.db.combat_oncooldown:
        available = caller.db.combat_oncooldown[skill_to_use] - caller.db.combat_turn + 1
        text = PREFIX + f"{skill_to_use} is on cooldown for {available} more turns"
        options = default_options
        return text, options

    if skilldata["resource"] == "mana":
        if skilldata["cost"] > caller.db.mana:
            need = skilldata["cost"] - caller.db.mana
            text = PREFIX + f"You need {need} more mana to cast {skill_to_use}"
            options = default_options
            return text, options
        else:
            EvMenu(caller, "world.mudcombat.c_menu", startnode="skill_target", cmd_on_exit=None, **kwargs)

    if skilldata["resource"] == "stamina":
        if skilldata["cost"] > caller.db.stamina:
            need = skilldata["cost"] - caller.db.stamina
            text = PREFIX + f"You need {need} more stamina to cast {skill_to_use}"
            options = default_options
            return text, options
        else:
            EvMenu(caller, "world.mudcombat.c_menu", startnode="skill_target", cmd_on_exit=None)


def skill_target(caller, raw_string, **kwargs):
    skill_to_use = caller.db.combat_skill_to_use
    skilldata = c_skills.SKILLS[skill_to_use]
    if skilldata["targets"] in ("aoe", "self", "none"):
        skill_resolve(caller)

    else:
        if kwargs.get("selected"):
            to_check = kwargs.get("selected")
            if skilldata["range"] == 1 and (to_check.db.range == 2 or caller.db.range == 2):
                text = PREFIX + f"{to_check} is out of range, please try another target or skill."
                options = default_options
                return text, options
            else:
                caller.db.combat_targets.append(kwargs.get("selected"))

        if len(caller.db.combat_targets) < skilldata["targets"]:
            text = "Who would you like to target?"
            options = []
            for target in caller.location.contents:
                colour = "|W"
                if target.db.health and target.db.visible:
                    if not target == caller:
                        if skilldata["range"] == 1 and (target.db.range == 2 or caller.db.range == 2):
                            colour = misc.cooldown_colour
                        options.append(
                            {
                                "desc": f"{colour}{target}|n - {get_health_colour(caller)}{target.db.health}/{target.db.max_health}|n",
                                "goto": ("skill_target", {"selected": target})})
            options.append(return_option)
            return text, options
        else:
            skill_resolve(caller)


"""
RESOLVES
"""


def att_resolve(caller, raw_string, **kwargs):
    target = kwargs.get("selected")
    c_functions.spend_action(caller, 1, action_name="attack")
    delay(DELAY, c_functions.resolve_attack, caller, target)
    delay(DELAY + 1, refresh_menu, caller)


def skill_resolve(caller):
    skilldata = c_skills.SKILLS[caller.db.combat_skill_to_use]
    spend_resource(caller, skilldata)
    c_functions.spend_action(caller, 1, action_name="skill")
    caller.db.combat_cooldowns.get_info()
    delay(DELAY, refresh_menu, caller)

    if skilldata["targets"] in ("self", "none"):
        skilldata["skillfunc"](caller)
    else:
        skilldata["skillfunc"](caller, caller.db.combat_skill_to_use)


def disengage(caller):
    caller.location.msg_contents(f"{caller} attempts to disengage.")
    c_functions.spend_action(caller, "all", action_name="disengage")  # Spend all remaining actions.


def end_turn(caller):
    caller.location.msg_contents(f"{caller} takes no further action, ending the turn.")
    c_functions.spend_action(caller, "all", action_name="pass")  # Spend all remaining actions.


"""
MISC
"""


def refresh_menu(caller):
    EvMenu(caller, "world.mudcombat.c_menu", startnode="combat_menu", cmd_on_exit=None)


def combat_menu(caller):
    text = ""
    options = None

    if caller.db.health > 0 and caller.db.combat_actionsleft > 0:
        text = "----- COMBAT MENU -----"
        options = default_options
    return text, options


def get_health_colour(caller):
    health_colour = misc.max_health_colour
    if caller.db.health < int(caller.db.max_health / 2):
        health_colour = misc.half_health_colour
    if caller.db.health < int(caller.db.max_health / 4):
        health_colour = misc.low_health_colour
    return health_colour


def spend_resource(caller, skilldata):
    if skilldata["resource"] == "mana":
        caller.db.mana -= skilldata["cost"]
    if skilldata["resource"] == "stamina":
        caller.db.stamina -= skilldata["cost"]


def out_of_time(caller):
    text = ""
    options = []
    return text, options
