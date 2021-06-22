from random import randint
from world.mudcombat import misc, c_turnhandler

PREFIX = misc.PREFIX


def roll_init(caller):
    max_roll = int(caller.db.dex)
    roll = randint(1, max_roll)
    caller.location.msg_contents(PREFIX + f"{caller}|n rolled: {misc.highlight_colour}{roll}|n")
    return roll


def get_attack(caller):
    # TODO WORK WITH WEAPONS AND STATS
    min_damage = 1
    max_damage = int(caller.db.wv)
    attack_value = randint(min_damage, max_damage)
    return attack_value


def get_defense(defender):
    # TODO WORK WITH ARMOUR AND STATS
    defense_value = randint(1, int(defender.db.av))
    return defense_value


def get_damage(attacker, defender):
    """
    Returns a value for damage to be deducted from the defender's HP after abilities
    successful hit.

    Args:
        attacker (obj): Character doing the attacking
        defender (obj): Character being damaged

    Returns:
        damage_value (int): Damage value, which is to be deducted from the defending
            character's HP.

    Notes:
        By default, returns a random integer from 15 to 25 without using any
        properties from either the attacker or defender.

        Again, this can be expanded upon.
    """
    # For this example, just generate a number between 15 and 25.
    damage_value = randint(1000, 1000)
    return damage_value


def apply_damage(target, value):
    target.db.health -= value
    if target.db.health <= 0:
        target.db.health = 0
    misc.refresh_prompt(target)


def apply_healing(target, value):
    target.db.health += value
    if target.db.health + value > target.db.max_health:
        target.db.health = target.db.max_health
    misc.refresh_prompt(target)


def resolve_attack(attacker, defender):
    attacker.location.msg_contents(f"{1}")
    attack_value = attacker.db.wv
    defense_value = defender.db.av

    if defense_value < 1:
        defense_value = 1

    damage_value = attack_value // defense_value

    # Announce damage dealt and apply damage.
    attacker.location.msg_contents(f"\n{attacker} hits {defender} for {misc.damage_colour}{damage_value} damage!|n")
    apply_damage(defender, damage_value)


def combat_cleanup(character):
    """
    Cleans up all the temporary combat-related attributes on a character.

    Args:
        character (obj): Character to have their combat attributes removed

    Notes:
        Any attribute whose key begins with 'combat_' is temporary and no
        longer needed once a fight ends.
    """
    for attr in character.attributes.all():
        if attr.key[:7] == "combat_":  # If the attribute name starts with 'combat_'...
            character.attributes.remove(key=attr.key)  # ...then delete it!


def is_in_combat(character):
    """
    Returns true if the given character is in combat.

    Args:
        character (obj): Character to determine if is in combat or not

    Returns:
        (bool): True if in combat or False if not in combat
    """
    return bool(character.db.combat_turnhandler)


def is_turn(character):
    """
    Returns true if it's currently the given character's turn in combat.

    Args:
        character (obj): Character to determine if it is their turn or not

    Returns:
        (bool): True if it is their turn or False otherwise
    """
    turnhandler = character.db.combat_turnhandler
    currentchar = turnhandler.db.fighters[turnhandler.db.turn]
    return bool(character == currentchar)


def spend_action(character, actions, action_name=None):
    """
    Spends a character's available combat actions and checks for end of turn.

    Args:
        character (obj): Character spending the action
        actions (int) or 'all': Number of actions to spend, or 'all' to spend all actions

    Keyword Args:
        action_name (str or None): If a string is given, sets character's last action in
        combat to provided string
    """
    if action_name:
        character.db.combat_lastaction = action_name
    if actions == "all":  # If spending all actions
        character.db.combat_actionsleft = 0  # Set actions to 0
    else:
        character.db.combat_actionsleft -= actions  # Use up actions.
        if character.db.combat_actionsleft < 0:
            character.db.combat_actionsleft = 0  # Can't have fewer than 0 actions
    character.db.combat_turnhandler.turn_end_check(character)  # Signal potential end of turn.
    misc.refresh_prompt(character)
