__author__ = 'user'

from utils.trpg import RPGObject
from utils.trpg import RPGCharacter
from utils.trpg import CoreStat
from utils.trpg import DerivedStat



class RPGDerivedStat(DerivedStat):

    def __init__(self, name: str, category: str, owner: RPGObject):
        super(RPGDerivedStat, self).__init__(name, category)
        self._owner = owner

    def add_dependency(self, dependent_stat, optional: bool = False, default_value: float = 0):
        stat_name = self._owner.get_public_stat_name(dependent_stat)
        super(RPGDerivedStat, self).add_dependency(stat_name, optional, default_value)

    def get_dependency_value(self, dependency_stat_name):
        stat_name = self._owner.get_public_stat_name(dependency_stat_name)
        value = super(RPGDerivedStat, self).get_dependency_value(stat_name)
        return value


class elemental_attack_dark(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(elemental_attack_dark, self).__init__(name="Dark Attack", category="ATTACK", owner=owner)
        self.add_dependency("Faith")

    def calculate(self):
        faith = self.get_dependency_value("Faith")
        return 10 + faith


class elemental_attack_fire(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(elemental_attack_fire, self).__init__(name="Fire Attack", category="ATTACK", owner=owner)
        self.add_dependency("Dexterity")

    def calculate(self):
        dex = self.get_dependency_value("Dexterity")
        return 10 + dex


class elemental_attack_magic(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(elemental_attack_magic, self).__init__(name="Magic Attack", category="ATTACK", owner=owner)
        self.add_dependency("Intelligence")

    def calculate(self):
        intelligence = self.get_dependency_value("Intelligence")
        return 10 + intelligence

class attribute_modifier(RPGDerivedStat):

    def __init__(self, owner: RPGObject, attribute_name : str):
        super(attribute_modifier, self).__init__(name=attribute_name+" Modifier", category="Abilities", owner=owner)
        self.attribute_name = attribute_name
        self.add_dependency(self.attribute_name)

    def calculate(self):
        attribute_value = self.get_dependency_value(self.attribute_name)

        return round((attribute_value - 10)/2)

class strength_attack_bonus(RPGDerivedStat):

    def __init__(self, owner: RPGObject):
        super(strength_attack_bonus, self).__init__(name="Strength Attack Bonus", category="ATTACK", owner=owner)
        self.add_dependency("Strength Modifier")
        self.add_dependency("Level")

    def calculate(self):
        strength_mod = self.get_dependency_value("Strength Modifier")
        level = self.get_dependency_value("Level")
        return round(strength_mod + level/2)

class dexterity_attack_bonus(RPGDerivedStat):

    def __init__(self, owner: RPGObject):
        super(dexterity_attack_bonus, self).__init__(name="Dexterity Attack Bonus", category="ATTACK", owner=owner)
        self.add_dependency("Dexterity Modifier")
        self.add_dependency("Level")

    def calculate(self):
        dex_mod = self.get_dependency_value("Dexterity Modifier")
        level = self.get_dependency_value("Level")
        return round(dex_mod + level/2)

class intelligence_attack_bonus(RPGDerivedStat):

    def __init__(self, owner: RPGObject):
        super(intelligence_attack_bonus, self).__init__(name="Intelligence Attack Bonus", category="ATTACK",
                                                     owner=owner)
        self.add_dependency("Intelligence Modifier")
        self.add_dependency("Level")

    def calculate(self):
        int_mod = self.get_dependency_value("Intelligence Modifier")
        level = self.get_dependency_value("Level")
        return round(int_mod + level / 2)


class wisdom_attack_bonus(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(wisdom_attack_bonus, self).__init__(name="Wisdom Attack Bonus", category="ATTACK",
                                                        owner=owner)
        self.add_dependency("Wisdom Modifier")
        self.add_dependency("Level")

    def calculate(self):
        wis_mod = self.get_dependency_value("Wisdom Modifier")
        level = self.get_dependency_value("Level")
        return round(wis_mod + level / 2)

class AC_defence(RPGDerivedStat):

    def __init__(self, owner: RPGObject):
        super(AC_defence, self).__init__(name="AC Defence", category="DEFENCE", owner=owner)
        self.add_dependency("Level")
        self.add_dependency("Race AC Bonus")
        self.add_dependency("Class AC Bonus")

    def calculate(self):
        race_bonus = self.get_dependency_value("Race AC Bonus")
        class_bonus = self.get_dependency_value("Class AC Bonus")

        level = self.get_dependency_value("Level")
        return round(10 + race_bonus + class_bonus + (level/2))

class reflex_defence(RPGDerivedStat):

    def __init__(self, owner: RPGObject):
        super(reflex_defence, self).__init__(name="Reflex Defence", category="DEFENCE", owner=owner)
        self.add_dependency("Level")
        self.add_dependency("Race Reflex Bonus")
        self.add_dependency("Class Reflex Bonus")
        self.add_dependency("Dexterity Modifier")
        self.add_dependency("Intelligence Modifier")


    def calculate(self):
        race_bonus = self.get_dependency_value("Race Reflex Bonus")
        class_bonus = self.get_dependency_value("Class Reflex Bonus")
        dex_mod = self.get_dependency_value("Dexterity Modifier")
        int_mod = self.get_dependency_value("Intelligence Modifier")
        level = self.get_dependency_value("Level")
        return round(10 + race_bonus + class_bonus + max(dex_mod, int_mod) + (level/2))

class fortitude_defence(RPGDerivedStat):

    def __init__(self, owner: RPGObject):
        super(fortitude_defence, self).__init__(name="Fortitude Defence", category="DEFENCE", owner=owner)
        self.add_dependency("Level")
        self.add_dependency("Race Fortitude Bonus")
        self.add_dependency("Class Fortitude Bonus")
        self.add_dependency("Strength Modifier")
        self.add_dependency("Constitution Modifier")


    def calculate(self):
        race_bonus = self.get_dependency_value("Race Fortitude Bonus")
        class_bonus = self.get_dependency_value("Class Fortitude Bonus")
        str_mod = self.get_dependency_value("Strength Modifier")
        con_mod = self.get_dependency_value("Constitution Modifier")
        level = self.get_dependency_value("Level")
        return round(10 + race_bonus + class_bonus + max(str_mod, con_mod) + (level/2))

class will_defence(RPGDerivedStat):

    def __init__(self, owner: RPGObject):
        super(will_defence, self).__init__(name="Will Defence", category="DEFENCE", owner=owner)
        self.add_dependency("Level")
        self.add_dependency("Race Will Bonus")
        self.add_dependency("Class Will Bonus")
        self.add_dependency("Wisdom Modifier")
        self.add_dependency("Charisma Modifier")

    def calculate(self):
        race_bonus = self.get_dependency_value("Race Will Bonus")
        class_bonus = self.get_dependency_value("Class Will Bonus")
        wis_mod = self.get_dependency_value("Wisdom Modifier")
        cha_mod = self.get_dependency_value("Charisma Modifier")
        level = self.get_dependency_value("Level")
        return round(10 + race_bonus + class_bonus + max(wis_mod, cha_mod) + (level/2))

class elemental_defence_magic(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(elemental_defence_magic, self).__init__(name="Magic Defence", category="ELEMENTAL DEFENCE", owner=owner)
        self.add_dependency("Dexterity")

    def calculate(self):
        dex = self.get_dependency_value("Dexterity")
        return 10 + dex


class elemental_defence_fire(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(elemental_defence_fire, self).__init__(name="Fire Defence", category="ELEMENTAL DEFENCE", owner=owner)
        self.add_dependency("Strength")

    def calculate(self):
        strength = self.get_dependency_value("Strength")
        return 10 + strength


class elemental_defence_lightning(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(elemental_defence_lightning, self).__init__(name="Lightning Defence", category="ELEMENTAL DEFENCE",
                                                          owner=owner)
        self.add_dependency("Stamina")

    def calculate(self):
        stamina = self.get_dependency_value("Stamina")
        return 10 + stamina


class resistance_bleed(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(resistance_bleed, self).__init__(name="Bleed Resistance", category="RESISTANCE", owner=owner)
        self.add_dependency("Vitality")

    def calculate(self):
        vitality = self.get_dependency_value("Vitality")
        return 10 + vitality


class resistance_poison(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(resistance_poison, self).__init__(name="Poison Resistance", category="RESISTANCE", owner=owner)
        self.add_dependency("Stamina")

    def calculate(self):
        stamina = self.get_dependency_value("Stamina")
        return 10 + stamina


class resistance_curse(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(resistance_curse, self).__init__(name="Curse Resistance", category="RESISTANCE", owner=owner)
        self.add_dependency("Faith")

    def calculate(self):
        faith = self.get_dependency_value("Faith")
        return 10 + faith


class item_discovery(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(item_discovery, self).__init__(name="Item Discovery", category="Skills", owner=owner)
        self.add_dependency("Intelligence")
        self.add_dependency("Luck")

    def calculate(self):
        intelligence = self.get_dependency_value("Intelligence")
        luck = self.get_dependency_value("Luck")
        return 10 + (intelligence + luck) / 2


class XPToLevel(RPGDerivedStat):
    _xp_levels = [10, 15, 20, 25, 30, 35]

    def __init__(self, owner: RPGObject):
        super(XPToLevel, self).__init__(name="XPToLevel", category="Attributes", owner=owner)
        self.add_dependency("XP")

    def calculate(self):
        xp = self.get_dependency_value("XP")
        level = 1

        for i in range(0, len(XPToLevel._xp_levels)):
            if xp < XPToLevel._xp_levels[i]:
                break
            else:
                level += 1

        return level


class LevelUP(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(LevelUP, self).__init__("LevelUp", "Attributes", owner=owner)
        self.add_dependency("XPToLevel")
        self.add_dependency("Level")

    def calculate(self):
        xp_level = self.get_dependency_value("XPToLevel")
        current_level = self.get_dependency_value("Level")

        return xp_level - current_level


class MaxHP(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(MaxHP, self).__init__("MaxHP", "Attributes", owner=owner)
        self.add_dependency("Constitution")
        self.add_dependency("Level")
        self.add_dependency("Class_HP_Per_Level")

    def calculate(self):
        con = self.get_dependency_value("Constitution")
        lvl  = self.get_dependency_value("Level")
        hp_per_lvl =  self.get_dependency_value("Class_HP_Per_Level")

        return con + ((lvl - 1)*hp_per_lvl)

class MaxAP(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(MaxAP, self).__init__("MaxAP", "Attributes", owner=owner)
        self.add_dependency("Dexterity")
        self.add_dependency("Speed")

    def calculate(self):
        dex = self.get_dependency_value("Dexterity")
        speed = self.get_dependency_value("Speed")
        return 5 + dex // 11 + (speed - 1)


class HP(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(HP, self).__init__("HP", "Attributes", owner=owner)
        self.add_dependency("MaxHP")
        self.add_dependency("Damage", optional=True, default_value=0)

    def calculate(self):
        max_HP = self.get_dependency_value("MaxHP")
        dmg = self.get_dependency_value("Damage")
        return max_HP - dmg

class XPReward(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(XPReward, self).__init__("XPReward", "Attributes", owner=owner)
        self.add_dependency("MaxHP")
        self.add_dependency("XPToLevel")

    def calculate(self):
        xp_level = self.get_dependency_value("XPToLevel")
        max_HP = self.get_dependency_value("MaxHP")

        return xp_level * 5 + max_HP


class MaxLoad(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(MaxLoad, self).__init__("MaxLoad", "Attributes", owner=owner)
        self.add_dependency("Stamina")
        self.add_dependency("Level")

    def calculate(self):
        con = self.get_dependency_value("Stamina")
        lvl = self.get_dependency_value("Level")
        return 10 + con + lvl


class TotalWeight(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(TotalWeight, self).__init__("TotalWeight", "Attributes", owner=owner)
        self.add_dependency("Weight")
        self.add_dependency("ItemWeight", optional=True, default_value=0)

    def calculate(self):
        weight = self.get_dependency_value("Weight")
        item_weight = self.get_dependency_value("ItemWeight")
        return weight + item_weight


class LoadPct(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(LoadPct, self).__init__("LoadPct", "Attributes", owner=owner)
        self.add_dependency("ItemWeight", optional=True, default_value=0)
        self.add_dependency("MaxLoad")

    def calculate(self):
        max_load = self.get_dependency_value("MaxLoad")
        item_weight = self.get_dependency_value("ItemWeight")
        return item_weight * 100 / max_load


class Score(RPGDerivedStat):
    def __init__(self, owner: RPGObject):
        super(Score, self).__init__("Score", "Attributes", owner=owner)
        self.add_dependency("Kills", optional=True, default_value=0)
        self.add_dependency("Treasure", optional=True, default_value=0)
        self.add_dependency("Trophies", optional=True, default_value=0)

    def calculate(self):
        kills = self.get_dependency_value("Kills")
        treasure = self.get_dependency_value("Treasure")
        trophies = self.get_dependency_value("Trophies")
        return kills + treasure + (trophies * 50)


def add_core_stats(character: RPGCharacter):
    character.add_stat(CoreStat("Damage", "Attributes", 0, owner=character))
    character.add_stat(CoreStat("Level", "Attributes", 1, owner=character))
    character.add_stat(CoreStat("ItemWeight", "Attributes", 0, owner=character))
    character.add_stat(CoreStat("Keys", "Inventory", 0, owner=character))
    character.add_stat(CoreStat("ExitKeys", "Inventory", 0, owner=character))
    character.add_stat(CoreStat("BossKeys", "Inventory", 0, owner=character))
    character.add_stat(CoreStat("Treasure", "Inventory", 0, owner=character))
    character.add_stat(CoreStat("Trophies", "Inventory", 0, owner=character))
    character.add_stat(CoreStat("Sword", "Inventory", 0, owner=character))
    character.add_stat(CoreStat("Shield", "Inventory", 0, owner=character))
    character.add_stat(CoreStat("Kills", "Attributes", 0, owner=character))
    character.add_stat(CoreStat("XP", "Attributes", 0, owner=character))

    return


def add_derived_stats(character: RPGCharacter):

    # Add core attribute modifiers
    attribute_names = ("Strength", "Intelligence", "Dexterity", "Constitution", "Wisdom", "Charisma")
    for attribute in attribute_names:
        character.add_stat(attribute_modifier(owner=character, attribute_name=attribute))


    character.add_stat(XPToLevel(character))
    # character.add_stat(physical_attack_chop(character))
    # character.add_stat(physical_attack_regular(character))
    # character.add_stat(physical_attack_thrust(character))
    # character.add_stat(physical_attack_swing(character))

    # Add attack bonuses
    character.add_stat(strength_attack_bonus(character))
    character.add_stat(dexterity_attack_bonus(character))
    character.add_stat(intelligence_attack_bonus(character))
    character.add_stat(wisdom_attack_bonus(character))

    #Add defence stats
    character.add_stat(AC_defence(character))
    character.add_stat(reflex_defence(character))
    character.add_stat(fortitude_defence(character))
    character.add_stat(will_defence(character))

    # character.add_stat(physical_defence_thrust(character))
    # character.add_stat(physical_defence_swing(character))
    # character.add_stat(physical_defence_chop(character))
    # character.add_stat(elemental_attack_dark(character))
    # character.add_stat(elemental_attack_fire(character))
    # character.add_stat(elemental_attack_magic(character))
    # character.add_stat(elemental_attack_miracle(character))
    # character.add_stat(elemental_defence_fire(character))
    # character.add_stat(elemental_defence_lightning(character))
    # character.add_stat(elemental_defence_dark(character))
    # character.add_stat(elemental_defence_magic(character))
    # character.add_stat(resistance_bleed(character))
    # character.add_stat(resistance_curse(character))
    # character.add_stat(resistance_poison(character))
    # character.add_stat(item_discovery(character))

    character.add_stat(LevelUP(character))
    character.add_stat(MaxHP(character))
    character.add_stat(MaxAP(character))
    character.add_stat(HP(character))
    character.add_stat(XPReward(character))
    #character.add_stat(MaxLoad(character))
    #character.add_stat(TotalWeight(character))
    #character.add_stat(LoadPct(character))
    character.add_stat(Score(character))




    return
