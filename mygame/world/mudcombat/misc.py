from evennia import EvMenu

TURN_TIMEOUT = 30
ACTIONS_PER_TURN = 1
DELAY = 1
PREFIX = ">  "
max_health_colour = "|130"
half_health_colour = "|y"
low_health_colour = "|r"
playername_colour = "|550"
skillname_colour = "|310"
debuff_colour = "|104"
summonskill_colour = "|440"
damage_colour = "|300"
highlight_colour = "|555"
healing_colour = "|025"
cooldown_colour = "|111"
error_colour = "|410"


def refresh_prompt(caller):
    health_colour = max_health_colour

    if caller.db.health < int(caller.db.max_health / 2):
        health_colour = half_health_colour
    if caller.db.health < int(caller.db.max_health / 4):
        health_colour = low_health_colour

    prompt = f"|555Health|n:{health_colour}{caller.db.health}/{caller.db.max_health}|n, " \
             f"|555Stamina|n:|230{caller.db.stamina}/{caller.db.max_stamina}|n, " \
             f"|555Mana|n:|014{caller.db.mana}/{caller.db.max_mana}|n"
    caller.msg(prompt=prompt)
