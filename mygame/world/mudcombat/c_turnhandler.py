from typeclasses.scripts import DefaultScript
from world.mudcombat import c_functions
from evennia import EvMenu
from evennia.utils import delay, inherits_from
from world.mudcombat import misc, c_menu, c_skills

"""
OPTIONS
"""

TURN_TIMEOUT = misc.TURN_TIMEOUT
ACTIONS_PER_TURN = misc.ACTIONS_PER_TURN
DELAY = misc.DELAY
PREFIX = misc.PREFIX

"""
SCRIPT
"""


class TurnHandler(DefaultScript):
    def at_script_creation(self):

        self.key = "Combat Turn Handler"
        self.interval = 5
        self.persistent = True
        self.db.fighters = []

        for thing in self.obj.contents:
            if thing.db.health and thing.db.visible:
                self.db.fighters.append(thing)

        for fighter in self.db.fighters:
            self.initialize_for_combat(fighter)

        self.obj.db.combat_turnhandler = self
        delay(DELAY, self.starting_combat())

    def initialize_for_combat(self, character):
        c_functions.combat_cleanup(character)
        character.db.combat_actionsleft = 0
        character.db.combat_turnhandler = self
        character.db.combat_lastaction = "null"
        character.db.combat_targets = []
        character.db.combat_turn = 0
        character.scripts.add("typeclasses.scripts.CDScript")

    def starting_combat(self):
        self.obj.msg_contents("""
          XX                                   XX
        XX..X                                 X..XX
      XX.....X                               X.....XX
 XXXXX.....XX                                 XX.....XXXXX
X |......XX%,.@                             @#%,XX......| X
X |.....X  @#%,.@                         @#%,.@  X.....| X
X \\...X     @#%,.@                     @#%,.@     X.../  X
 X#\\.X        @#%,.@                 @#%,.@        X./  #
  ##  X          @#%,.@             @#%,.@          X   #
   # #X            @#%,.@         @#%,.@            X ##
    ###X             @#%,.@     @#%,.@             ####
      ###              @#%.,@ @#%,.@              ###
         #              @.,@#%,@,.@              #
                          @#%,@,@                   
                          @@@ @@@\n                             
""" + PREFIX + "Combat Starting...")
        delay(DELAY, self.roll_init_msg)

    def roll_init_msg(self):
        self.obj.msg_contents(PREFIX + "Rolling for initiative...")
        delay(DELAY, self.roll_result)

    def roll_result(self):
        ordered_by_roll = sorted(self.db.fighters, key=c_functions.roll_init, reverse=True)
        self.db.fighters = ordered_by_roll
        delay(DELAY, self.turn_order)

    def turn_order(self):
        self.obj.msg_contents(PREFIX + "Turn order is: %s " % ", ".join(obj.key for obj in self.db.fighters))
        delay(DELAY, self.turn_start)

    def turn_start(self):
        self.db.turn = 0
        self.db.timer = TURN_TIMEOUT

        self.start_turn(self.db.fighters[0])

    def start_turn(self, character):
        if character.db.health == 0:
            self.obj.msg_contents(PREFIX + f"{misc.highlight_colour}{character} has been defeated!|n")
            c_functions.spend_action(character, "all", action_name="dead")

        else:
            character.db.combat_turn += 1
            character.db.combat_cooldowns.check_cooldown()
            character.db.combat_actionsleft += ACTIONS_PER_TURN
            self.status_msg()
            if inherits_from(character, "typeclasses.mobs.HostileNPC") and character.db.health:
                character.scripts.add("typeclasses.scripts.NPCAttack")
            else:
                character.msg("It's your turn!\n")
                delay(DELAY, c_menu.refresh_menu, character)

    def at_repeat(self):
        currentchar = self.db.fighters[self.db.turn]
        self.db.timer -= self.interval

        if self.db.timer <= 0:
            self.obj.msg_contents("%s's turn timed out!" % currentchar)
            c_functions.spend_action(currentchar, "all", action_name="disengage")
            EvMenu(currentchar, "world.mudcombat.c_menu", startnode="out_of_time", cmd_on_exit=None)
            return
        elif self.db.timer <= 10 and not self.db.timeout_warning_given:
            currentchar.msg(PREFIX + "|RWARNING: About to run out of time!|n")
            self.db.timeout_warning_given = True

    def next_turn(self):
        disengage_check = True
        for fighter in self.db.fighters:
            if fighter.db.combat_lastaction != "disengage":
                disengage_check = False
        if disengage_check:
            self.obj.msg_contents(PREFIX + "All fighters have disengaged! Combat is over!")
            self.stop()
            return

        defeated_characters = 0
        for fighter in self.db.fighters:
            if fighter.db.health == 0:
                defeated_characters += 1
        if defeated_characters == (
                len(self.db.fighters) - 1):
            for fighter in self.db.fighters:
                if fighter.db.health != 0:
                    LastStanding = fighter
                    self.obj.msg_contents(PREFIX + f"Only {LastStanding} remains! Combat is over!")
                    self.stop()
                    return

        currentchar = self.db.fighters[self.db.turn]
        self.db.turn += 1
        if self.db.turn > len(self.db.fighters) - 1:
            self.db.turn = 0
            self.remove_dead()
        newchar = self.db.fighters[self.db.turn]
        self.db.timer = TURN_TIMEOUT + self.time_until_next_repeat()
        self.db.timeout_warning_given = False
        self.obj.msg_contents(f"{currentchar}'s|n turn ends - {newchar}'s|n turn begins!")
        self.start_turn(newchar)

    def status_msg(self):
        self.obj.msg_contents(f"\n{misc.highlight_colour}COMBAT OVERVIEW|n")
        for fighter in self.db.fighters:
            health_colour = misc.max_health_colour
            if fighter.db.health < int(fighter.db.max_health / 2):
                health_colour = misc.half_health_colour
            if fighter.db.health < int(fighter.db.max_health / 4):
                health_colour = misc.low_health_colour

            prompt = f"{fighter} - {health_colour}{fighter.db.health}/{fighter.db.max_health}|n"
            self.obj.msg_contents(prompt)
        self.obj.msg_contents("\n")

    def turn_end_check(self, character):
        if not character.db.combat_actionsleft:
            delay(DELAY, self.next_turn)
            return

    def join_fight(self, character):
        self.db.fighters.insert(self.db.turn, character)
        self.db.turn += 1
        self.initialize_for_combat(character)

    def remove_dead(self):
        for fighter in self.db.fighters:
            if fighter.db.health == 0:
                self.db.fighters.remove(fighter)
                c_functions.combat_cleanup(fighter)

    def at_stop(self):
        for fighter in self.db.fighters:
            fighter.refresh_stats()
            c_functions.combat_cleanup(fighter)
        self.obj.db.combat_turnhandler = None
