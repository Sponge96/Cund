"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from evennia import DefaultScript
from evennia.utils import delay
from world.mudcombat import misc, c_functions, c_skills

PREFIX = misc.PREFIX


class Script(DefaultScript):
    """
    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.

    """

    pass


class CDScript(Script):
    # Script that manages cool downs for skills
    def at_script_creation(self):
        self.obj.db.combat_cooldowns = self
        self.obj.db.combat_oncooldown = {}

    def get_info(self):
        # get information on skill being used and calculate when it will be OFF cool down (based on turn)
        cooldown = c_skills.SKILLS[self.obj.db.combat_skill_to_use]["cooldown"] + self.obj.db.combat_turn
        self.add_info(cooldown)

    def add_info(self, cooldown):
        # Add information about when skill will be OFF cool down to dictionary
        self.obj.db.combat_oncooldown[self.obj.db.combat_skill_to_use] = cooldown

    def check_cooldown(self):
        # check if skill is OFF cool down and remove from list if TRUE
        for key, value in self.obj.db.combat_oncooldown.items():
            if value < self.obj.db.combat_turn:
                del self.obj.db.combat_oncooldown[key]


class CheckRoom(Script):
    def at_script_creation(self):
        self.key = "CheckRoom"
        self.interval = 20
        self.persistent = True
        self.obj.db.CheckRoom = self

    def at_stop(self):
        self.obj.db.CheckRoom = None

    def at_repeat(self):
        if self.obj.db.health <= 0:
            self.stop()

        elif c_functions.is_in_combat(self.obj):
            pass

        else:
            self.join_combat()

    def join_combat(self):
        here = self.obj.location
        fighters = []

        for thing in here.contents:  # Test everything in the room to add it to the fight.
            if thing.db.health:  # If the object has HP...
                fighters.append(thing)  # ...then add it to the fight.
        if len(fighters) <= 1:  # If you're the only able fighter in the room
            self.obj.msg("There's nobody here to fight!")
            return
        if here.db.combat_turnhandler:  # If there's already a fight going on...
            here.msg_contents(PREFIX + "%s joins the fight!" % self.obj)
            here.db.combat_turnhandler.join_fight(self.obj)  # Join the fight!
            return
        here.msg_contents(PREFIX + "%s starts a fight!" % self.obj)
        # Add a turn handler script to the room, which starts combat.
        here.scripts.add("world.mudcombat.c_turnhandler.TurnHandler")


class NPCAttack(Script):
    def at_script_creation(self):
        self.key = "NPCAttack"
        self.interval = 10
        self.persistent = True
        self.obj.db.NPCAttack = self

    def at_repeat(self):
        if self.obj.db.combat_actionsleft > 0:
            self.obj.find_target()
        else:
            self.stop()

    def at_stop(self):
        self.db.NPCAttack = None
