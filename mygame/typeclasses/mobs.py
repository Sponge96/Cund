from typeclasses.characters import Character
from world.mudcombat import misc, c_functions, c_skills
from evennia.utils import inherits_from, delay
import random

PREFIX = misc.PREFIX
DELAY = misc.DELAY


class HostileNPC(Character):

    def at_object_creation(self):
        super().at_object_creation()
        self.scripts.add("typeclasses.scripts.CheckRoom")

    def find_target(self):
        target_list = []
        for target in self.location.contents:
            if target.db.health and not target == self:
                target_list.append(target)

        rand_target = random.choice(target_list)
        target = self.search(rand_target)
        self.attack_target(target)

    def attack_target(self, target):
        self.db.combat_targets = [target]
        roll = random.randint(1, 2)
        if roll == 1:
            c_functions.resolve_attack(self, target)
            c_functions.spend_action(self, 1, action_name="attack")
        if roll == 2:
            skills_list = self.db.skills_known
            rand_skill = random.choice(skills_list)
            skill_to_use = rand_skill
            skilldata = c_skills.SKILLS[skill_to_use]
            skilldata["skillfunc"](self, skill_to_use)


class Rat(HostileNPC):

    def at_object_creation(self):
        super().at_object_creation()
        self.db.skills_known = ["bite", ]
        self.db.max_health = 300
        self.db.health = 300

    def find_target(self):
        target_list = []
        for target in self.location.contents:
            if target.db.health and target.db.visible and not inherits_from(target, "typeclasses.mobs.Rat"):
                target_list.append(target)

        if target_list:
            rand_target = random.choice(target_list)
            target = self.search(rand_target)
            self.attack_target(target)
        else:
            c_functions.spend_action(self, "all", action_name="end")
