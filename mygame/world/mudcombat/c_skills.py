from world.mudcombat import c_functions, c_menu
from random import randint
from world.mudcombat import misc
from evennia.utils import delay, inherits_from
from evennia import create_object

PREFIX = misc.PREFIX
DELAY = misc.DELAY

"""
Main Functions
"""


def att_skill(caster, skill_name):
    skilldata = SKILLS[skill_name]
    modi = get_modi(caster, skill_name)
    min_damage = skilldata["damage_range"][0]
    max_damage = skilldata["damage_range"][1]
    if skilldata["targets"] == "aoe":
        for target in caster.location.contents:
            if target.db.health:
                if not target == caster:
                    # TODO ADD RANGE CHECK FOR AOE!!!
                    damage = value_roll(min_damage, max_damage, modi)
                    att_display(caster, skill_name, target, damage)
                    c_functions.apply_damage(target, damage)

    else:
        for target in caster.db.combat_targets:
            damage = value_roll(min_damage, max_damage, modi)
            att_display(caster, skill_name, target, damage)
            c_functions.apply_damage(target, damage)
        caster.db.combat_targets = []


def heal_skill(caster, skill_name):
    skilldata = SKILLS[skill_name]
    modi = get_modi(caster, skill_name)
    min_healing = skilldata["healing_range"][0]
    max_healing = skilldata["healing_range"][1]
    if skilldata["targets"] == "aoe":
        for target in caster.location.contents:
            if target.db.health:
                healing = value_roll(min_healing, max_healing, modi)
                heal_display(caster, skill_name, target, healing)
                c_functions.apply_healing(target, healing)

    if skilldata["targets"] == "self":
        healing = value_roll(min_healing, max_healing, modi)
        heal_display(caster, skill_name, caster, healing)
        c_functions.apply_healing(caster, healing)

    else:
        for target in caster.db.combat_targets:
            healing = value_roll(min_healing, max_healing, modi)
            heal_display(caster, skill_name, target, healing)
            c_functions.apply_healing(target, healing)
        caster.db.combat_targets = []


def summon_skill(caster, skill_name):
    skilldata = SKILLS[skill_name]
    obj_key = skilldata["obj_key"]
    obj_typeclass = skilldata["obj_typeclass"]

    delay(DELAY, create_object, obj_typeclass, key=obj_key, location=caster.location)
    summon_display(caster, skill_name)


"""
Display Functions
"""


def att_display(caster, skill_name, target, damage):
    skill_msg = f"\n{caster} uses {misc.skillname_colour}{skill_name}!|n"
    skill_msg += f" and hit {target} for {misc.damage_colour}{damage} damage!|n"
    caster.location.msg_contents(skill_msg)


def heal_display(caster, skill_name, target, healing):
    skill_msg = f"\n{caster} uses {misc.healing_colour}{skill_name}!|n"
    skill_msg += f" and healed {target} for {healing}!|n"
    caster.location.msg_contents(skill_msg)


def summon_display(caster, skill_name):
    skill_msg = f"\n{caster} uses {misc.summonskill_colour}{skill_name}!|n"
    caster.location.msg_contents(skill_msg)


"""
MISC
"""


def value_roll(min, max, modi):
    roll = randint(min, max)
    damage = roll * modi
    return int(damage)


def get_modi(caster, skill_name):
    skilldata = SKILLS[skill_name]
    modi = 0
    if skilldata["stat"] == "int":
        modi = caster.db.int
    if skilldata["stat"] == "str":
        modi = caster.db.str
    if skilldata["stat"] == "dex":
        modi = caster.db.dex
    return int(modi)


"""
SKILLS
"""

SKILLS = {
    """
    ROGUE SKILLS
    """
    
    "Backstab": {
        "skillfunc": att_skill,
        "targets": 3,
        "cost": 1,
        "resource": "stamina",
        "stat": "dex",
        "damage_range": (1, 2),
        "range": 2,
        "cooldown": 1,
        "description": "Teleport behind 1-3 targets and strike them from behind.\n"
                       "Cost: 1, Stat: Dex, Range: 2, Cooldown: 1"
    },

    "Vital Strike": {
        "skillfunc": att_skill,
        "targets": 1,
        "cost": 2,
        "resource": "stamina",
        "stat": "dex",
        "damage_range": (2, 3),
        "range": 1,
        "cooldown": 2,
        "description": "Aim for targets vitals, dealing large amounts of damage.\n"
                       "Cost: 2, Stat: Dex, Range: 1, Cooldown: 2"
    },

    "Fan of Knifes": {
        "skillfunc": att_skill,
        "targets": "aoe",
        "cost": 2,
        "resource": "stamina",
        "stat": "dex",
        "damage_range": (1, 2),
        "range": 1,
        "cooldown": 2,
        "description": "Throw knifes out in all directions dealing medium amount of damage to everyone close by.\n"
                       "Cost: 2, Stat: Dex, Range: 1, Cooldown: 2"
    },


    "bite": {
        "skillfunc": att_skill,
        "targets": 1,
        "cost": 0,
        "resource": "stamina",
        "stat": "dex",
        "damage_range": (10, 50),
        "cooldown": 0,
        "range": 1,
        "description": "Attack a target from behind blah blah Targets: 2, Cost: 20 Stamina"
    },

}
#     "Summon Rat": {
#         "skillfunc": summon_skill,
#         "skilltype": "summon",
#         "cost": 1,
#         "resource": "stamina",
#         "noncombat_skill": False,
#         "obj_typeclass": "typeclasses.mobs.Rat",
#         "obj_key": "Rat"
#     }
# }
