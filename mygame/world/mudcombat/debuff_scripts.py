from typeclasses.scripts import Script


class AllStatDebuff(Script):

    def at_script_creation(self):
        self.key = "AllStatDebuff"
        self.persistent = True
        self.obj.db.combat_all_stat_debuff = self
        self.stacks = 0
        self.max_stacks = 5
        self.obj.db.con -= 1
        self.obj.db.str -= 1
        self.obj.db.dex -= 1
        self.obj.db.int -= 1

    def new_stack(self):
        self.stacks += 1
        if self.stacks >= self.max_stacks:
            pass
        else:
            self.obj.db.con -= 1
            self.obj.db.str -= 1
            self.obj.db.dex -= 1
            self.obj.db.int -= 1

    def at_stop(self):
        self.obj.db.combat_all_stat_debuff = None