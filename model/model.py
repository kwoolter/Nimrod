import collections
import copy
import csv
import logging
import math
import os
import random
from operator import attrgetter
from operator import itemgetter

import pygame

import utils
import utils.trpg as trpg
from .derived_stats import *


class Attack:
    # Attack Types
    MELEE = "Melee"
    RANGED = "Ranged"
    MAGIC = "Magic"
    UNKNOWN = "UNKNOWN"

    TYPES = (MELEE, RANGED, MAGIC)

    # Attack attributes
    STRENGTH = "Strength"
    DEXTERITY = "Dexterity"
    INTELLIGENCE = "Intelligence"
    WISDOM = "Wisdom"

    # Attack Stats
    NUMBER_OF_DICE = "Number of Dice"
    DICE_SIDES = "Dice Sides"
    BONUS = "Attack Bonus"
    RANGE = "Range"
    AP = "AP"
    EFFECT = "Effect"
    IMAGE = "Image"

    ATTACK_ATTRIBUTES = {STRENGTH: "STR", DEXTERITY: "DEX", INTELLIGENCE: "INT", WISDOM: "WIS"}

    # Defence types
    AC = "AC"
    FORTITIUDE = "Fortitude"
    REFLEX = "Reflex"
    WILL = "Will"

    DEFENCE_TYPES = {AC: "AC", FORTITIUDE: "FORT", REFLEX: "REF", WILL: "WILL"}

    def __init__(self, name: str, description: str, type: str, attack_attribute: str, defence_attribute: str,
                 effect: str, image: str):
        self.name = name
        self.description = description
        self.effect = effect
        self.image = image

        if type in Attack.TYPES:
            self.type = type
        else:
            self.type = Attack.UNKNOWN

        if attack_attribute in Attack.ATTACK_ATTRIBUTES.keys():
            self.attack_attribute = attack_attribute
        else:
            self.attack_attribute = Attack.UNKNOWN

        if defence_attribute in Attack.DEFENCE_TYPES:
            self.defence_attribute = defence_attribute
        else:
            self.defence_attribute = Attack.UNKNOWN

        self.stats = {}

    def add_stat(self, new_stat: trpg.BaseStat):
        self.stats[new_stat.name] = copy.copy(new_stat)

    def get_stat(self, stat_name: str):
        if stat_name not in self.stats.keys():
            raise Exception("Stat {0} is not set for attack {1}:{2}".format(stat_name, self.name, self.description))

        return self.stats[stat_name]

    def print(self):
        print("{0}:{1} - type({2}) - {3} vs. {4}".format(self.name,
                                                         self.description,
                                                         self.type,
                                                         self.attack_attribute,
                                                         self.defence_attribute))
        for stat in self.stats.values():
            print("\t{0}={1}".format(stat.name, stat.value))


class Character(trpg.RPGCharacter):
    def __init__(self, name: str, rpg_race: str, rpg_class: str,
                 x: int = 1, y: int = 1, width: int = 1, height: int = 1, HP: int = 20):
        super(trpg.RPGCharacter, self).__init__(name, rpg_race, rpg_class)

        self.name = name
        self._HP = HP
        self._x = x
        self._y = y
        self.height = height
        self.width = width
        self.old_x = x
        self.old_y = y
        self.initialise()

    def initialise(self):
        self.HP = self._HP

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self.old_x = self._x
        self._x = new_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self.old_y = self._y
        self._y = new_y

    def moved(self):
        return (self._x, self._y) != (self.old_x, self.old_y)

    # Go back to old position
    def back(self):
        self._x = self.old_x
        self._y = self.old_y


class Objects:
    EMPTY = "empty"
    TEST = "Q"
    TREE = "tree"
    RED_FLAG = "red_flag"
    PLAYER = "player"
    SKULL = "skull"
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    UP = "up"
    DOWN = "down"
    HEART = "heart"
    BASE = "base"
    BASE_RED = "base_red"
    BASE_YELLOW = "base_yellow"
    BASE_GREEN = "base_green"
    BASE_SHADOW = "base_shadow"
    BASE_FLAG_STONES = "flag_stones"
    BLOCK_SECRET = "secret"
    BLOCK = "block"
    BLOCK1 = "block1"
    BLOCK2 = "block2"
    BLOCK3 = "block3"
    BRICK = "brick"
    BLOCK_ORNATE = "block_ornate"
    BLOCK_HEXAGON = "block_hexagon"
    BLOCK_TOP = "block_top"
    BLOCK_BOTTOM = "block_bottom"
    BLOCK_RIGHT = "block_right"
    BLOCK_RIGHT_SLOPE = "block_right_slope"
    BLOCK_RIGHT_BACK_SLOPE = "block_right_back_slope"
    BLOCK_LEFT = "block_left"
    BLOCK_LEFT_SLOPE = "block_left_slope"
    BLOCK_LEFT_BACK_SLOPE = "block_left_back_slope"
    BLOCK_ARCH_NW = "block_arch_NW"
    BLOCK_ARCH_NE = "block_arch_NE"
    BLOCK_ARCH_SW = "block_arch_SW"
    BLOCK_ARCH_SE = "block_arch_SE"
    BLUE = "blue"
    PYRAMID1 = "pyramid1"
    PYRAMID2 = "pyramid2"
    SPHERE = "sphere"
    SPHERE_GREEN = "sphere_green"
    SPHERE_BLUE = "sphere_blue"
    SPHERE_RED = "sphere_red"
    OCTOPUS_RED = "octopus_red"
    OCTOPUS_BLUE = "octopus_blue"
    SHARK_RED = "shark_red"
    SHARK_BLUE = "shark_blue"
    SQUOID = "squoid"
    CRAB_GREEN = "crab"
    CRAB_RED = "crab_red"
    CRAB_BLUE = "crab_blue"
    SQUOID_GREEN = "squoid_green"
    SQUOID_RED = "squoid_red"
    SQUOID_BLUE = "squoid_blue"
    POLAR_BEAR_RED = "polar_bear_red"
    POLAR_BEAR_BLUE = "polar_bear_blue"
    SKELETON_LEFT = "skeleton_blue"
    SKELETON_RIGHT = "skeleton_red"
    KEY = "key1"
    SWITCH = "switch"
    SWITCH_LIT = "switch_lit"
    SWITCH_TILE = "switch_tile"
    DOORH = "doorh"
    DOORV = "doorv"
    CHEST = "chest"
    LAVA = "lava"
    ICE = "ice"
    SPIKE = "spike"
    CYLINDER = "cylinder"
    RED_DOT = "red dot"
    GREEN_DOT = "green_dot"
    BUBBLES = "bubbles"
    TELEPORT = "teleport"
    TELEPORT2 = "teleport2"
    SEAWEED = "seaweed"
    FIRE = "fire"
    POISON = "poison"
    INK = "ink"
    HIT = "hit"
    SHOCK = "shock"
    ASLEEP = "asleep"
    FROZEN = "frozen"
    SWORD_SMALL = "sword_small"
    DAGGER = "Dagger"
    SPEAR = "Spear"
    SWORD = "Sword"
    POTION = "potion"
    BOW = "Bow"
    MAGIC = "Magic"
    HAMMER = "Hammer"
    AXE = "Axe"

    DIRECTIONS = (NORTH, SOUTH, EAST, WEST)
    SQUOIDS = (SQUOID, SQUOID_BLUE, SQUOID_GREEN, SQUOID_RED, CRAB_GREEN, CRAB_RED, SKELETON_LEFT, SKELETON_RIGHT)

    SWAP_TILES = {BLOCK_SECRET: EMPTY, SWITCH: SWITCH_LIT, SWITCH_LIT: SWITCH}


class FloorObject(object):
    TOUCH_FIELD_X = 3
    TOUCH_FIELD_Y = 3

    def __init__(self, name: str,
                 rect: pygame.Rect,
                 layer: int = 1,
                 height: int = None,
                 solid: bool = True,
                 visible: bool = True,
                 interactable: bool = True,
                 occupiable: bool = False):

        self._name = name
        self._rect = pygame.Rect(rect)
        self._origin = self._rect.copy()

        self.layer = layer
        self._old_rect = self._rect.copy()
        if height is None:
            height = self._rect.height
        self.height = height
        self.is_solid = solid
        self.is_visible = visible
        self.is_interactable = interactable
        self._is_occupiable = occupiable
        self.dx = 0
        self.dy = 0
        self.d2x = 0
        self.d2y = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, new_rect):
        self._old_rect = self._rect.copy()
        self._rect = new_rect

    @property
    def xyz(self):
        return (self.rect.x, self.rect.y, self.layer)

    def set_origin(self, new_origin: pygame.Rect = None):
        if new_origin is None:
            self._origin = self._rect.copy()
        else:
            self._origin = new_origin.copy()

    def back(self):
        logging.info("Moving Player {0} back from {1} to {2}".format(self.name, self._rect, self._old_rect))
        self._rect = self._old_rect.copy()

    def is_colliding(self, other_object):
        return self.rect.colliderect(other_object.rect) and \
               self != other_object

    def is_touching(self, other_object):
        touch_field = self._rect.inflate(FloorObject.TOUCH_FIELD_X, FloorObject.TOUCH_FIELD_Y)

        return self.is_visible and \
               self.is_interactable and \
               self != other_object and \
               touch_field.colliderect(other_object.rect)

    def is_occupiable(self):
        return self._is_occupiable

    def has_moved(self):
        return self.rect != self._old_rect

    def distance_from_origin(self):
        return abs(self.rect.x - self._origin.x) + abs(self.rect.y - self._origin.y)

    def distance_from_point(self, point_x: int, point_y: int):
        return math.sqrt(math.pow(self.rect.x - point_x, 2) + pow(self.rect.y - point_y, 2))

    def move(self, dx: int, dy: int):
        self._old_rect = self._rect.copy()
        self.rect.x += dx
        self.rect.y += dy

    def set_pos(self, x: int, y: int, z: int):
        self._old_rect = self._rect.copy()
        self.rect.x = x
        self.rect.y = y
        self.layer = z

    def get_pos(self):
        return self._rect.x, self._rect.y, self.layer

    def __str__(self):
        return "{0}:{1}, {2}".format(self.name, self.rect, self.is_occupiable())


class Player(FloorObject):
    # Effects
    EVERGREEN = -999
    EFFECT_LIFETIME = 40
    HIT = "hit"
    DEAD = "dead"
    POISONED = "poisoned"
    ASLEEP = "asleep"
    BURNED = "burned"
    FROZEN = "frozen"
    INKED = "inked"
    SHOCKED = "shocked"
    ASLEEP = "asleep"
    FROZEN = "frozen"
    ATTACKING = "attacking"

    def __init__(self, name: str,
                 rect: pygame.Rect,
                 layer=1,
                 height: int = 40,
                 character: Character = None):
        super(Player, self).__init__(name=name, rect=rect, height=height, solid=True, visible=True, interactable=False)

        self.treasure = 0
        self.keys = 0
        self.boss_keys = 0
        self.layer = layer

        self._name = name
        self.character = character
        self.AP = self.MaxAP
        self._attacks = {}
        self.effects = {}

    def __str__(self):
        return ("Player {0}: HP={1},AP={2},({3},{4},{5}),Dead={6}, Effects={7}".format(self.name, self.HP, self.AP,
                                                                                       self.rect.x, self.rect.y,
                                                                                       self.layer,
                                                                                       self.is_dead(),
                                                                                       len(self.effects)))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name

    # @property
    # def xyz(self):
    #     return (self.rect.x, self.rect.y, self.layer)

    @property
    def HP(self):
        return self.character.get_stat("HP").value

    @property
    def MaxAP(self):
        return self.character.get_stat("MaxAP").value

    @property
    def XP(self):
        return self.character.get_stat("XP").value

    @XP.setter
    def XP(self, xp_gained: int):

        self.character.increment_stat("XP", xp_gained)

    def get_stat(self, stat_name: str):
        return self.character.get_stat(stat_name).value

    def increment_stat(self, stat_name: str, new_value: float):
        self.character.increment_stat(stat_name, new_value)

    def do_damage(self, new_value):
        self.character.increment_stat("Damage", new_value)
        if self.HP <= 0:
            self.effects = {}
            self.do_effect(Player.DEAD)
            self.is_solid = False

    def do_heal(self, new_value):
        self.character.increment_stat("Damage", new_value * -1)

    @property
    def kills(self):
        return self.character.get_stat("Kills").value

    @kills.setter
    def kills(self, new_value):
        self.character.update_stat("Kills", new_value)

    def is_dead(self):

        return self.HP <= 0

    def add_attack(self, attack: Attack):
        self._attacks[attack.name] = copy.deepcopy(attack)

    def get_attack(self):
        attack_name = list(self._attacks.keys())[0]

        return self._attacks[attack_name]

    def is_effect(self, effect_name: str):
        if effect_name in self.effects.keys():
            return True
        else:
            return False

    def do_effect(self, effect_name: str):
        self.effects[effect_name] = Player.EFFECT_LIFETIME

    def tick(self):
        expired_effects = []
        for effect in self.effects.keys():
            count = self.effects[effect]
            if count <= 0:
                expired_effects.append(effect)
            elif count != Player.EVERGREEN:
                self.effects[effect] = count - 1

        for effect in expired_effects:
            print("Effect {0} on player {1} expired.".format(effect, self.character.name))
            del self.effects[effect]


class Monster(FloorObject):
    def __init__(self, name: str,
                 rect: pygame.Rect,
                 height: int = 30):
        super(Monster, self).__init__(name=name, rect=rect, height=height)


class Team:
    # Team types
    PLAYER = "player"
    COMPUTER = "Computer"

    # Targeting Tactics
    TACTIC_RANDOM = "random"
    TACTIC_WEAKEST = "weakest"
    TACTIC_STRONGEST = "strongest"
    TACTIC_NEAREST = "nearest"
    TACTIC_FURTHEST = "furthest"
    TACTIC_SPECIFIED = "specified"

    def __init__(self, name: str, colour=(255, 0, 0), type: str = PLAYER):
        self.name = name
        self.colour = colour
        self.type = type
        self.players = []

    def add_player(self, new_player: Player):
        self.players.append(new_player)

    def is_player_in_team(self, selected_player: Player):

        if selected_player in self.players:
            return True
        else:
            return False

    def is_dead(self):
        is_dead = True
        for player in self.players:
            if player.is_dead() == False:
                is_dead = False
                break

        return is_dead

    def choose_player(self, tactic: int = TACTIC_RANDOM, other_player: Player = None, target_player: Player = None):

        print("Choosing player based on {0}".format(tactic))

        if self.is_dead():
            raise Exception("Team {0} are all dead!".format(self.name))

        available_players = []
        for player in self.players:
            if player.is_dead() is False:
                if other_player is not None:
                    player.distance = math.sqrt((player.rect.x - other_player.rect.x) ** 2 +
                                                (player.rect.y - other_player.rect.y) ** 2 +
                                                (player.layer - other_player.layer) ** 2)
                else:
                    player.distance = 9999
                    print("Choose Player Tactic {0}: defaulting distance to 999".format(tactic))
                available_players.append(player)

        if tactic == Team.TACTIC_RANDOM:
            chosen_player = random.choice(available_players)

        elif tactic == Team.TACTIC_SPECIFIED:

            if self.is_player_in_team(target_player) is True:
                chosen_player = target_player
            else:
                chosen_player = None

        elif tactic == Team.TACTIC_WEAKEST:
            chosen_player = sorted(available_players, key=attrgetter("HP"), reverse=False)[0]

        elif tactic == Team.TACTIC_STRONGEST:
            chosen_player = sorted(available_players, key=attrgetter("HP"), reverse=True)[0]

        elif tactic == Team.TACTIC_NEAREST:
            if other_player is not None:
                chosen_player = sorted(available_players, key=attrgetter("distance"), reverse=False)[0]
            else:
                chosen_player = random.choice(available_players)

        elif tactic == Team.TACTIC_FURTHEST:
            if other_player is not None:
                chosen_player = sorted(available_players, key=attrgetter("distance"), reverse=True)[0]
            else:
                chosen_player = random.choice(available_players)

        return chosen_player

    def __str__(self):
        return "Team {0}: {1} player(s)".format(self.name, len(self.players))

    def print(self):
        print("Team {0} has {1} members:".format(self.name, len(self.players)))
        for player in self.players:
            print(player)


class Floor:
    EXIT_NORTH = "NORTH"
    EXIT_SOUTH = "SOUTH"
    EXIT_EAST = "EAST"
    EXIT_WEST = "WEST"
    EXIT_UP = "UP"
    EXIT_DOWN = "DOWN"

    EVENTS = None

    OBJECT_TO_DIRECTION = {Objects.WEST: EXIT_WEST,
                           Objects.EAST: EXIT_EAST,
                           Objects.NORTH: EXIT_NORTH,
                           Objects.SOUTH: EXIT_SOUTH,
                           Objects.UP: EXIT_UP,
                           Objects.DOWN: EXIT_DOWN}

    DIRECTION_TO_OBJECT = {EXIT_WEST: Objects.WEST,
                           EXIT_EAST: Objects.EAST,
                           EXIT_NORTH: Objects.NORTH,
                           EXIT_SOUTH: Objects.SOUTH,
                           EXIT_UP: Objects.UP,
                           EXIT_DOWN: Objects.DOWN}

    REVERSE_DIRECTION = {EXIT_WEST: EXIT_EAST,
                         EXIT_EAST: EXIT_WEST,
                         EXIT_NORTH: EXIT_SOUTH,
                         EXIT_SOUTH: EXIT_NORTH,
                         EXIT_UP: EXIT_DOWN,
                         EXIT_DOWN: EXIT_UP}

    def __init__(self, id: int, name: str, rect: pygame.Rect, skin_name: str = "default"):

        self.id = id
        self.name = name
        self.skin_name = skin_name
        self.rect = pygame.Rect(rect)
        self.players = []
        self.objects = []
        self.monsters = []
        self.bots = []
        self.layers = {}
        self.floor_plans = {}
        self.exits = {}
        self.teleports = {}
        self.details = None
        self.start_positions = [None, None]
        self.start_layers = [None, None]
        self.start_layer = 1
        self.potions = 0
        self.chests = 0
        self.switch_on = False
        self.switch_tiles = None

    def __str__(self):
        return "Floor {0}: rect={1},layer={4} objects={2}, monsters={3}, potions={4}, chests={5}".format(self.name,
                                                                                                         self.rect,
                                                                                                         self.object_count,
                                                                                                         len(
                                                                                                             self.monsters),
                                                                                                         self.potions,
                                                                                                         self.chests)

    @property
    def object_count(self):
        count = 0
        for layer in self.layers.values():
            count += len(layer)
        return count

    def add_player_at_entrance(self, new_player: Player, direction: str):

        x, y, z = new_player.xyz

        matching_entrances = self.get_matching_objects((Floor.DIRECTION_TO_OBJECT[direction], ""), layer_id=z)
        if len(matching_entrances) > 0:
            selected = random.choice(matching_entrances)
            x, y, z = selected.xyz
            new_player.set_pos(x, y, z)
            self.players.append(new_player)

        else:

            new_player.set_pos(10, 10, z)
            self.players.append(new_player)

        print("Adding player at {0},{1},{2}".format(new_player.rect.x, new_player.rect.y, new_player.layer))

    def add_player(self, new_player: Player, auto_position: bool = False, team: int = 0):

        if auto_position is True:
            min_x, min_y, max_x, max_y = self.start_positions[team]
            start_layer = self.start_layers[team]
            placed = False
            for i in range(1, 20):
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)

                if self.get_floor_tile(x, y, start_layer) is None and self.is_occupiable(x, y, start_layer) is True:
                    new_player.set_pos(x, y, start_layer)
                    placed = True
                    break

            if placed is False:
                print("Failed to auto position player {0}".format(new_player.character.name))

        self.players.append(new_player)

        print("Adding player at {0},{1},{2}".format(new_player.rect.x, new_player.rect.y, new_player.layer))

    def add_enemy(self, new_player: Player, auto_position: bool = False, is_bot: bool = True, team: int = 1):

        if auto_position is True:
            min_x, min_y, max_x, max_y = self.start_positions[team]
            start_layer = self.start_layers[team]
            placed = False
            # Try 20 times
            for i in range(1, 20):
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)

                if self.get_floor_tile(x, y, start_layer) is None and self.is_occupiable(x, y, start_layer) is True:
                    new_player.set_pos(x, y, start_layer)
                    placed = True
                    break

            if placed is False:
                print("Failed to auto position enemy {0}".format(new_player.character.name))

        self.monsters.append(new_player)

        if is_bot is True:
            ai = AIBot2(player=new_player, floor=self)
            ai.set_path(((min_x, min_y, start_layer), (max_x, min_y, start_layer), (max_x, max_y, start_layer),
                         (min_x, max_y, start_layer)))

            self.bots.append(ai)

        #print("Adding enemy at {0},{1},{2}".format(new_player.rect.x, new_player.rect.y, new_player.layer))

    def add_items(self, item_type, item_count: int = 1):

        #print("Adding {0} {1} items into rect {2}".format(item_count, item_type, self.rect))

        new_object = FloorObjectLoader.get_object_copy_by_name(item_type)
        if new_object is not None:

            for i in range(0, item_count):
                placed = False
                for tries in range(0, 20):
                    x = random.randint(self.rect.x, self.rect.width - 1)
                    y = random.randint(self.rect.y, self.rect.height - 1)
                    z = random.choice(self.start_layers)
                    if self.get_floor_tile(x, y, z) is None:
                        base_tile = self.get_floor_tile(x, y, z - 1)
                        if base_tile is not None and base_tile.is_occupiable() is True:
                            new_object.set_pos(x, y, z)
                            self.add_object(new_object)
                            new_object = FloorObjectLoader.get_object_copy_by_name(item_type)
                            placed = True
                            #print("Added {0} item at {1},{2},{3}".format(item_type, x, y, z))
                            break

                if placed is False:
                    print("Failed to place item {0}".format(new_object.name))


        else:
            raise Exception("add_items: Could not find object {0}".format(item_type))

    def add_object(self, new_object: FloorObject):

        if new_object.layer not in self.layers.keys():
            self.layers[new_object.layer] = []

        objects = self.layers[new_object.layer]
        objects.append(new_object)
        self.rect.width = max(new_object.rect.x + 1, self.rect.width)
        self.rect.height = max(new_object.rect.y + 1, self.rect.height)

        if new_object.name in Objects.DIRECTIONS:
            self.exits[Floor.OBJECT_TO_DIRECTION[new_object.name]] = new_object

        logging.info("Added {0} at location ({1},{2})".format(new_object.name, new_object.rect.x, new_object.rect.y))

    def build_floor_plan(self):

        for layer_id in sorted(self.layers.keys(), reverse=True):
            if layer_id not in self.floor_plans.keys():
                new_plan = [[None for x in range(self.rect.height)] for x in range(self.rect.width)]
                self.floor_plans[layer_id] = new_plan

            for floor_object in self.layers[layer_id]:

                object_x, object_y, object_z = floor_object.xyz

                width = floor_object.rect.width
                depth = floor_object.rect.height
                height = floor_object.height

                for x in range(object_x, object_x + width):
                    for y in range(object_y, object_y + depth):
                        for z in range(layer_id, layer_id + height):
                            new_object = FloorObjectLoader.get_object_copy_by_name(floor_object.name)
                            try:
                                self.set_floor_tile(x, y, z, new_object)
                            except Exception as e:
                                print("Error:{0}".format(str(new_object)))


                if floor_object.name in (Objects.TELEPORT, Objects.TELEPORT2):
                    if floor_object.name not in self.teleports.keys():
                        self.teleports[floor_object.name] = []
                    self.teleports[floor_object.name].append(
                        (floor_object.rect.x, floor_object.rect.y, floor_object.layer))

    def get_camera_position(self):
        return (self.rect.width, self.rect.height, len(self.layers.keys()))

    def distance_to_camera(self, a):
        ax, ay, az = a
        bx, by, bz = self.get_camera_position()
        d = math.sqrt(math.pow(ax - bx, 2) + math.pow(ay - by, 2) + math.pow(az - bz, 2))
        return d

    def set_details(self, floor_details):

        self.details = floor_details
        self.name, self.start_layers[0], self.start_positions[0], self.start_layers[1], self.start_positions[
            1], self.potions, self.chests, self.switch_tiles = floor_details

        self.add_items(Objects.POTION, self.potions)
        self.add_items(Objects.CHEST, self.chests)
        self.build_floor_plan()


    def swap_object(self, object: FloorObject, new_object_type: str):

        x,y,z = object.xyz
        swap_object = FloorObjectLoader.get_object_copy_by_name(new_object_type)

        self.set_floor_tile(x,y,z,swap_object)


    def switch(self, setting=None):

        if setting is None:
            self.switch_on = not self.switch_on
        else:
            self.switch_on = setting

        return self.switch_on

    def add_monster(self, new_object: Monster):

        self.monsters.append(new_object)

    def get_layer(self, layer_id):

        if layer_id not in self.layers.keys():
            raise Exception("Layer {0} not found in Floor {0}".format(layer_id, self.name))

        layer = self.layers[layer_id]

        return layer

    def get_floor_tile(self, x: int, y: int, layer_id: int, is_raw: bool = False):

        layer = self.floor_plans[layer_id]
        floor_object = layer[x][y]

        if floor_object is not None and floor_object.name == Objects.SWITCH_TILE and self.switch_tiles is not None:
            if self.switch_on is True:
                tile = self.switch_tiles[1]
            else:
                tile = self.switch_tiles[0]

            x, y, z = floor_object.xyz
            floor_object = FloorObjectLoader.get_object_copy_by_name(tile)
            floor_object.set_pos(x,y,z)


        if is_raw is False:

            for player in self.players:
                if (x, y, layer_id) == player.xyz:
                    floor_object = player
                    break

            for enemy in self.monsters:
                if (x, y, layer_id) == enemy.xyz:
                    floor_object = enemy
                    break

        return floor_object

    def set_floor_tile(self, x: int, y: int, layer_id: int, new_object: FloorObject = None):

        if new_object is not None:
            new_object.set_pos(x, y, layer_id)

        layer = self.floor_plans[layer_id]
        layer[x][y] = new_object

    def get_matching_objects(self, types: list, layer_id: int = None):
        matches = []
        types = list(types)

        if layer_id is not None:
            start_layer = layer_id
            end_layer = layer_id
        else:
            start_layer = min(self.layers.keys())
            end_layer = max(self.layers.keys())

        print("looking for objects {0} in layers {1} to {2}".format(types, start_layer, end_layer))

        for selected_layer_id in range(start_layer, end_layer + 1):
            if selected_layer_id in self.layers.keys():
                for x in range(0, self.rect.width):
                    for y in range(0, self.rect.height):
                        tile = self.get_floor_tile(x, y, selected_layer_id, is_raw=True)
                        if tile is not None and tile.name in types:
                            matches.append(tile)

        print("{0} matches for tile type {1}".format(len(matches), types))

        return matches

    def is_occupiable(self, x, y, z):

        result = True

        # Is the position out of bounds?
        if x >= self.rect.width or x < 0 or y >= self.rect.height or y < 0:
            result = False
        else:

            tile = self.get_floor_tile(x, y, z - 1)

            # Is the base of the new position occupied?
            if tile is None or tile.is_occupiable() is False:
                result = False

        return result

    def is_dangerous(self, x, y, z):

        result = False

        tile = self.get_floor_tile(x, y, z)

        # Is the tile dangerous?
        if tile is not None and tile.name in (Objects.SPIKE):
            result = True
        else:

            base_tile = self.get_floor_tile(x, y, z - 1)

            # Is the base tile dangerous?
            if base_tile is not None and base_tile.name in (Objects.LAVA, Objects.ICE):
                result = True

        return result

    def is_in_bounds(self, x: int, y: int, z: int):

        # Is the position out of bounds?
        if x >= self.rect.width or x < 0 or y >= self.rect.height or y < 0 or z < min(self.layers.keys()) or z > max(
                self.layers.keys()):
            return False
        else:
            return True

    def move_player(self, selected_player: Player, dx: int = 0, dy: int = 0):

        if selected_player not in self.players and selected_player not in self.monsters:
            raise Exception(
                "{0}:move_player() - Player {1} is not on floor (2).".format(__class__, selected_player.character.name,
                                                                             self.name))

        # Make player's last position the same as their current position
        selected_player.rect = selected_player.rect

        x, y, z = selected_player.rect.x, selected_player.rect.y, selected_player.layer
        new_x = x + dx
        new_y = y + dy

        # Is the new position out of bounds?
        if self.is_in_bounds(new_x, new_y, z) is False:

            Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.BLOCKED, description="You hit an edge!"))

        else:

            # Look at what tile is in the new position
            tile = self.get_floor_tile(new_x, new_y, z)

            # Is the new position is filled with a solid object?
            if tile is not None and tile.is_solid is True:

                # If you can interact with it...
                if tile.is_interactable is True:

                    Floor.EVENTS.add_event(
                        Event(type=Event.FLOOR, name=Event.INTERACT,
                              description="You interact with a {0}".format(tile.name)))

                    if tile.name == Objects.CHEST:
                        reward = random.choice((Objects.KEY, Objects.POTION, Objects.SPHERE_GREEN))
                        reward_object = FloorObjectLoader.get_object_copy_by_name(reward)
                        self.set_floor_tile(new_x, new_y, z, reward_object)
                        Floor.EVENTS.add_event(
                            Event(type=Event.FLOOR, name=Event.TREASURE, description="You find a {0}".format(reward)))

                    elif tile.name == Objects.BLOCK_SECRET:

                        self.set_floor_tile(new_x, new_y, z, None)
                        Floor.EVENTS.add_event(
                            Event(type=Event.FLOOR, name=Event.SECRET, description="You find a secret way"))


                    elif tile.name in (Objects.SWITCH, Objects.SWITCH_LIT):

                        new_state = self.switch()
                        if new_state == True:
                            self.swap_object(tile, Objects.SWITCH_LIT)
                        else:
                            self.swap_object(tile, Objects.SWITCH)

                        Floor.EVENTS.add_event(
                            Event(type=Event.FLOOR, name=Event.SWITCH, description="You operated a switch"))

                    elif tile.name in (Objects.DOORH, Objects.DOORV):
                        if selected_player.keys > 0:
                            self.set_floor_tile(new_x, new_y, z, None)
                            selected_player.keys -= 1
                            Floor.EVENTS.add_event(
                                Event(type=Event.FLOOR, name=Event.DOOR_OPEN, description="You opened a door"))

                        else:
                            Floor.EVENTS.add_event(
                                Event(type=Event.FLOOR, name=Event.DOOR_LOCKED, description="The door is locked"))

                    elif tile.name == Objects.RED_FLAG:
                        Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.FOUND_FLAG, description="You found a battle flag"))

                    else:
                        Floor.EVENTS.add_event( \
                            Event(type=Event.FLOOR, name=Event.COLLIDE, description="You hit a {0}".format(tile.name)))


            # Else move the player and see what happens next...
            else:

                selected_player.move(dx, dy)
                x, y, z = selected_player.xyz

                tile = self.get_floor_tile(x, y, z, is_raw=True)

                if tile is not None:

                    if tile.name == Objects.SPHERE_GREEN:
                        selected_player.treasure += 1
                        self.set_floor_tile(x, y, z, None)
                        Floor.EVENTS.add_event(
                            Event(type=Event.FLOOR, name=Event.TREASURE,
                                  description="You found a {0}".format(tile.name)))

                    elif tile.name == Objects.SPHERE_BLUE:
                        selected_player.do_heal(1)
                        self.set_floor_tile(x, y, z, None)
                        Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.GAIN_HEALTH,
                                                     description="You found a {0}".format(tile.name)))

                    elif tile.name == Objects.SPHERE_RED:
                        selected_player.do_heal(random.randint(1, 3))
                        self.set_floor_tile(x, y, z, None)
                        Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.GAIN_HEALTH,
                                                     description="You found a {0}".format(tile.name)))

                    elif tile.name == Objects.POTION:
                        selected_player.do_heal(random.randint(1, 3))
                        self.set_floor_tile(x, y, z, None)
                        Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.GAIN_HEALTH,
                                                     description="You found a {0}".format(tile.name)))

                    elif tile.name == Objects.SPIKE:
                        selected_player.do_damage(random.randint(1, 3))
                        self.set_floor_tile(x, y, z, None)
                        Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.LOSE_HEALTH,
                                                     description="You hit a {0}".format(tile.name)))

                    elif tile.name == Objects.KEY:
                        selected_player.keys += 1
                        self.set_floor_tile(x, y, z, None)
                        Floor.EVENTS.add_event(
                            Event(type=Event.FLOOR, name=Event.KEY, description="You found a {0}".format(tile.name)))

                    elif tile.name in (Objects.TELEPORT, Objects.TELEPORT2):

                        while True:
                            new_position = random.choice(self.teleports[tile.name])
                            if new_position != (x, y, z):
                                break
                        x, y, z = new_position
                        selected_player.set_pos(x, y, z)
                        Floor.EVENTS.add_event(
                            Event(type=Event.FLOOR, name=Event.TELEPORT,
                                  description="Teleporting {0}".format(selected_player.character.name)))

                # Check what the player is standing on...
                base_tile = self.get_floor_tile(selected_player.rect.x, selected_player.rect.y,
                                                selected_player.layer - 1)

                # If standing on nothing or standing on a non-occupiable tile move back
                if base_tile is None or base_tile.is_occupiable() is False:
                    selected_player.back()
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.BLOCKED,
                                                 description="You can't go that way"))
                    print(str(base_tile))

                # If standing on lava lose health
                elif base_tile.name == Objects.LAVA:
                    selected_player.do_damage(1)
                    selected_player.do_effect(Player.BURNED)
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR,
                                                 name=Event.LOSE_HEALTH,
                                                 description="{0} stood on {1}".format(selected_player.character.name,
                                                                                       base_tile.name)))

                # If standing on ice lose health and AP
                elif base_tile.name == Objects.ICE:
                    selected_player.do_damage(1)
                    selected_player.AP -= 1
                    selected_player.do_effect(Player.FROZEN)
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR,
                                                 name=Event.LOSE_HEALTH,
                                                 description="{0} stood on {1}".format(selected_player.character.name,
                                                                                       base_tile.name)))

            if selected_player.has_moved() is True:
                selected_player.AP -= 1

    def tick(self):

        # For each player...
        for selected_player in self.players:

            selected_player.tick()

            x, y, layer = selected_player.xyz

            # Check what the player is standing on...
            base_tile = self.get_floor_tile(x, y, layer - 1)
            if base_tile.name in (Objects.LAVA, Objects.ICE):
                selected_player.do_damage(1)
                Floor.EVENTS.add_event(Event(type=Event.FLOOR,
                                             name=Event.LOSE_HEALTH,
                                             description="{0} stood on {1}".format(selected_player.name,
                                                                                   base_tile.name)))

        # For each enemy do a tick
        for enemy in self.monsters:
            enemy.tick()

        self.do_auto()

    def do_auto(self):

        #print("Bot automation...")

        # for each bot do a tick
        for bot in self.bots:
            #bot.print()
            bot.do_tick()
            bot.player.AP = bot.player.MaxAP
            bot.reset()


class FloorBuilder():
    FLOOR_LAYOUT_FILE_NAME = "_floor_layouts.csv"
    FLOOR_OBJECT_FILE_NAME = "_floor_objects.csv"

    def __init__(self, data_file_directory: str):
        self.data_file_directory = data_file_directory
        self.floors = {}
        self.floor_details = {}


    def initialise(self, file_prefix: str = "default"):

        self.load_floor_details()

        self.floor_objects = FloorObjectLoader(
            self.data_file_directory + file_prefix + FloorBuilder.FLOOR_OBJECT_FILE_NAME)
        self.floor_objects.load()

        self.floor_layouts = FloorLayoutLoader(
            self.data_file_directory + file_prefix + FloorBuilder.FLOOR_LAYOUT_FILE_NAME)
        self.floor_layouts.load()

    def load_floors(self):

        for floor_id, new_floor in FloorLayoutLoader.floor_layouts.items():
            if floor_id in self.floor_details.keys():
                new_floor.build_floor_plan()
                new_floor.set_details(self.floor_details[floor_id])
            self.floors[floor_id] = new_floor

        for floor in self.floors.values():
            floor.build_floor_plan()
            print(str(floor))

    def load_floor_details(self):

        # Floor Details:-
        # - name
        # - player start layer
        # - team1 start locations rect
        # - team2 start locations rect
        # - potions
        # - chests

        new_floor_id = 0
        new_floor_details = ("The Trial", 1, (6, 1, 16, 3), 1, (5, 16, 14, 18), 4, 4, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 1
        new_floor_details = ("The Maze", 1, (6, 1, 16, 3), 1, (5, 16, 14, 18), 1, 1, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 2
        new_floor_details = ("The Bridge", 3, (5, 2, 12, 3), 3, (5, 16, 14, 18), 4, 4, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 3
        new_floor_details = ("The Whale Grave Yard", 1, (2, 0, 16, 2), 1, (3, 17, 16, 19), 2, 2, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 4
        new_floor_details = ("Sunken Wreck", 2, (1, 1, 10, 3), 2, (1, 13, 8, 15), 2, 2, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 5
        new_floor_details = ("Citadel", 6, (0, 0, 6, 6), 2, (11, 11, 16, 16), 2, 2, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 100
        new_floor_details = ("The Start", 1, (6, 1, 16, 3), 1, (5, 16, 14, 18), 5, 5, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 101
        new_floor_details = ("The Square", 1, (6, 1, 16, 3), 1, (5, 16, 14, 18), 5, 5, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 102
        new_floor_details = ("The Jigger", 1, (6, 1, 16, 3), 1, (5, 16, 14, 18), 3, 3, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 103
        new_floor_details = ("The Jigger", 1, (6, 1, 16, 3), 1, (5, 16, 14, 18), 2, 2, (Objects.BLOCK, Objects.EMPTY))
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 104
        new_floor_details = ("The Ancient Gate", 1, (9, 17, 12, 18), 1, (4, 4, 15, 8), 2, 2, None)
        self.floor_details[new_floor_id] = new_floor_details

        new_floor_id = 105
        new_floor_details = ("The Lava Crossing", 1, (16,2,19,12), 1, (1,2,4,12), 2, 2, None)
        self.floor_details[new_floor_id] = new_floor_details


class FloorLayoutLoader():
    floor_layouts = {}

    DEFAULT_OBJECT_WIDTH = 1
    DEFAULT_OBJECT_DEPTH = 1

    EMPTY_OBJECT_CODE = " "

    def __init__(self, file_name):
        self.file_name = file_name

    def load(self):

        # Attempt to open the file
        with open(self.file_name, 'r') as object_file:

            # Load all rows in as a dictionary
            reader = csv.DictReader(object_file)

            # Get the list of column headers
            header = reader.fieldnames

            current_floor_id = None
            current_floor_layer = None

            # For each row in the file....
            for row in reader:

                floor_id = int(row.get("ID"))
                floor_layout_name = row.get("Name")
                floor_skin_name = row.get("Skin")

                if floor_id != current_floor_id:
                    FloorLayoutLoader.floor_layouts[floor_id] = Floor(floor_id, floor_layout_name, (0, 0, 0, 0),
                                                                      skin_name=floor_skin_name)
                    current_floor_id = floor_id
                    y = 0

                floor = FloorLayoutLoader.floor_layouts[floor_id]

                floor_layer = int(row.get("Layer"))
                if floor_layer != current_floor_layer:
                    current_floor_layer = floor_layer
                    y = 0

                floor_layout = row.get("Layout")
                x = 0
                for object_code in floor_layout:
                    if object_code != FloorLayoutLoader.EMPTY_OBJECT_CODE:
                        new_floor_object = FloorObjectLoader.get_object_copy_by_code(object_code)
                        new_floor_object.rect.x = x
                        new_floor_object.rect.y = y
                        new_floor_object.layer = floor_layer
                        floor.add_object(new_floor_object)
                    x += FloorLayoutLoader.DEFAULT_OBJECT_WIDTH

                y += FloorLayoutLoader.DEFAULT_OBJECT_DEPTH


class FloorObjectLoader():
    floor_objects = {}
    map_object_name_to_code = {}

    BOOL_MAP = {"TRUE": True, "FALSE": False}

    def __init__(self, file_name: str):
        self.file_name = file_name

    def load(self):

        # Attempt to open the file
        with open(self.file_name, 'r') as object_file:
            # Load all rows in as a dictionary
            reader = csv.DictReader(object_file)

            # Get the list of column headers
            header = reader.fieldnames

            # For each row in the file....
            for row in reader:
                # print("loading {0}".format(row))

                object_code = row.get("Code")

                new_object = FloorObject(row.get("Name"), \
                                         rect=(0, 0, int(row.get("width")), int(row.get("depth"))), \
                                         height=int(row.get("height")), \
                                         solid=FloorObjectLoader.BOOL_MAP[row.get("solid").upper()], \
                                         visible=FloorObjectLoader.BOOL_MAP[row.get("visible").upper()], \
                                         interactable=FloorObjectLoader.BOOL_MAP[row.get("interactable").upper()], \
                                         occupiable=FloorObjectLoader.BOOL_MAP[row.get("occupiable").upper()] \
                                         )

                # Store the floor object in the code cache
                FloorObjectLoader.floor_objects[object_code] = new_object

                # Store mapping of object name to code
                FloorObjectLoader.map_object_name_to_code[new_object.name] = object_code

                logging.info("{0}.load(): Loaded Floor Object {1}".format(__class__, new_object.name))

    @staticmethod
    def get_object_copy_by_code(object_code: str):

        if object_code not in FloorObjectLoader.floor_objects.keys():
            raise Exception("Can't find object by code '{0}'".format(object_code))

        return copy.deepcopy(FloorObjectLoader.floor_objects[object_code])

    @staticmethod
    def get_object_copy_by_name(object_name: str):

        if object_name not in FloorObjectLoader.map_object_name_to_code.keys():
            raise Exception("Can't find object by name '{0}'".format(object_name))

        object_code = FloorObjectLoader.map_object_name_to_code[object_name]

        if object_code not in FloorObjectLoader.floor_objects.keys():
            raise Exception("Can't find object by code '{0}'".format(object_name))

        return FloorObjectLoader.get_object_copy_by_code(object_code)


class Battle:
    EVENTS = None
    READY = "ready"
    PLAYING = "playing"
    END = "end"

    TACTIC_NEXT = "next opponent"

    def __init__(self, team1: Team, team2: Team, battle_floor: Floor = None):
        self.teams = [team1, team2]
        self.turns = 0
        self._state = Battle.READY
        self.next_team = None
        self.battle_floor = battle_floor
        self.order_of_play = []
        self.current_target = None
        self.bots = {}

    def __str__(self):
        return "Battle between team {0} and team {1} ({5})\nRound {2}\n{3}\n{4}".format(self.teams[0].name,
                                                                                        self.teams[1].name,
                                                                                        self.turns,
                                                                                        self.teams[0],
                                                                                        self.teams[1],
                                                                                        self._state)

    def print(self):
        print("Team {0} vs. Team {1}: Round {2}".format(self.teams[0].name,
                                                        self.teams[1].name,
                                                        self.turns))
        for team in self.teams:
            team.print()

        print("Camera at {0}".format(self.battle_floor.get_camera_position()))

    @property
    def state(self):

        if self.teams[0].is_dead() or self.teams[1].is_dead():
            return Battle.END
        else:
            return self._state

    def start(self):
        self._state = Battle.PLAYING

        t1 = copy.copy(self.teams[0].players)
        t2 = copy.copy(self.teams[1].players)
        loop = True
        while loop is True:

            if len(t1) > 0:
                new_player = t1.pop(0)
                self.order_of_play.append(new_player)
                self.battle_floor.add_player(new_player, auto_position=True, team=0)

            if len(t2) > 0:
                new_player = t2.pop(0)
                self.order_of_play.append(new_player)
                self.battle_floor.add_player(new_player, auto_position=True, team=1)

            if len(t1) + len(t2) == 0:
                loop = False

        self.set_current_target(tactic=Team.TACTIC_NEAREST)

    def tick(self):
        for player in self.order_of_play:
            player.tick()

    def get_current_player(self):

        return self.order_of_play[0]

    def next_player(self):

        old_player = self.order_of_play.pop(0)
        old_player.AP = old_player.MaxAP
        self.order_of_play.append(old_player)
        current_player = self.get_current_player()
        current_player.set_origin()
        self.set_current_target(tactic=Team.TACTIC_NEAREST)
        self.turns += 1

        Battle.EVENTS.add_event(Event(type=Event.BATTLE, name=Event.NEXT_PLAYER,
                                      description="{0}'s turn.".format(
                                          current_player.character.name)))

        return current_player

    def set_current_target(self, tactic: str = Team.TACTIC_NEAREST, target: Player = None):

        current_player = self.get_current_player()
        current_team = self.get_player_team(current_player)
        opponent_team = self.get_opposite_team(current_team)

        if tactic == Team.TACTIC_SPECIFIED:
            self.current_target = opponent_team.choose_player(tactic=tactic, other_player=current_player,
                                                              target_player=target)
        else:
            self.current_target = opponent_team.choose_player(tactic=tactic, other_player=current_player)

        return self.current_target

    def get_current_target(self):

        return self.current_target

    def get_opposite_team(self, selected_team: Team):

        if selected_team == self.teams[0]:
            return self.teams[1]
        elif selected_team == self.teams[1]:
            return self.teams[0]
        else:
            return None

    def get_player_team(self, selected_player: Player):
        if self.teams[0].is_player_in_team(selected_player):
            return self.teams[0]
        elif self.teams[1].is_player_in_team(selected_player):
            return self.teams[1]
        else:
            return None

    def do_attack(self):

        if self._state != Battle.PLAYING:
            raise Exception("Battle in state '{0}' - not playing so can't do attack!".format(self._state))

        # Find out who is attacking who
        current_player = self.get_current_player()
        current_team = self.get_player_team(current_player)
        opposite_team = self.get_opposite_team(current_team)

        # If the opposition are all already dead then stop here
        if opposite_team.is_dead() is True:
            Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                          name=Event.VICTORY,
                                          description="Team {0} are all dead!".format(opposite_team.name)))

        # Otherwise...
        else:

            # Get the current target opponent
            opponent = self.get_current_target()

            if opponent is not None:

                attack = current_player.get_attack()

                # Get a load of stats about the selected attack that the attacker is going to use
                number_of_dice = attack.get_stat(Attack.NUMBER_OF_DICE).value
                dice_sides = attack.get_stat(Attack.DICE_SIDES).value
                attack_bonus = attack.get_stat(Attack.BONUS).value
                attack_range = attack.get_stat(Attack.RANGE).value
                attack_AP = attack.get_stat(Attack.AP).value
                attack_effect = attack.effect

                # Is the target too far away based on the range to the attack?
                distance_to_target = current_player.distance_from_point(opponent.rect.x, opponent.rect.y)

                if distance_to_target > attack_range:
                    Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                                  name=Event.MISSED_OPPONENT,
                                                  description="{0} is too far away (distance={1:.1f}), attack range={2:.1f}".format(
                                                      opponent.character.name, distance_to_target, attack_range)))

                # Does the attacker have too few AP to execute the attack?
                elif current_player.AP < attack_AP:
                    Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                                  name=Event.NO_AP,
                                                  description="{0} does not have enough AP to attack - {1:.0f} AP required!".format(
                                                      current_player.character.name, attack_AP)))

                # OK we are good to attempt an attack
                else:

                    #  Is there a clear path to the target?
                    attack_route = Navigator(self.battle_floor)
                    result = attack_route.navigate((current_player.rect.x, current_player.rect.y, current_player.layer),
                                                   (opponent.rect.x, opponent.rect.y, opponent.layer), direct=True)

                    # If path is not clear then we cannot proceed
                    if result is False:
                        Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                                      name=Event.MISSED_OPPONENT,
                                                      description="Target {0} is blocked".format(
                                                          opponent.character.name)))

                    else:

                        # Set the attacker's status
                        current_player.do_effect(Player.ATTACKING)

                        # Get some attacker and opponent stats
                        attacker_attack_bonus = current_player.get_stat(attack.attack_attribute + " Attack Bonus")
                        attacker_attack_modifier = current_player.get_stat(attack.attack_attribute + " Modifier")
                        attacker_layer = current_player.layer
                        opponent_defence = opponent.get_stat(attack.defence_attribute + " Defence")
                        opponent_layer = opponent.layer

                        # Roll a 20 sided dice and add and attacker bonuses to the roll

                        dice_roll = random.randint(1, 20)
                        attack_roll = (dice_roll + attacker_attack_bonus)

                        print("{0} ({1} v {2}): attack roll = {3} v defence {4}".format(attack.name,
                                                                                        attack.attack_attribute,
                                                                                        attack.defence_attribute,
                                                                                        attack_roll,
                                                                                        opponent_defence))

                        # Compare the attack roll to the opponent's defense stats to see if the attack was successful
                        if attack_roll > opponent_defence:

                            # If the dice roll was a natural 20 then this is a critical hit and does maximum damage
                            if dice_roll == 20:
                                print("critical hit!")
                                damage = (number_of_dice * dice_sides) + attack_bonus + attacker_attack_modifier

                            # Else roll the dice associated with the attack and calculate the damage
                            else:
                                damage = random.randint(number_of_dice,
                                                        number_of_dice * dice_sides) + attack_bonus + attacker_attack_modifier

                            # Add/remove 30% damage depending on height advantage over opponent
                            if attacker_layer > opponent_layer:
                                height_advantage_factor = 1.3
                            elif attacker_layer < opponent_layer:
                                height_advantage_factor = 0.7
                            else:
                                height_advantage_factor = 1.0

                            damage *= height_advantage_factor
                            damage = int(damage)

                            print(
                                "{0} ({1} v {2}): {3:.0f}d{4:.0f}+{5:.0f}+{6:.0f} did {7:.0f} damage. Height factor={8}".format(
                                    attack.name,
                                    attack.attack_attribute,
                                    attack.defence_attribute,
                                    number_of_dice,
                                    dice_sides,
                                    attack_bonus,
                                    attacker_attack_modifier,
                                    damage,
                                    height_advantage_factor
                                ))

                            # Apply the damage to the opponent and also the effect associated with the attack
                            opponent.do_damage(damage)
                            opponent.do_effect(attack_effect)

                            Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                                          name=Event.DAMAGE_OPPONENT,
                                                          description="{0} did {1:.0f} damage to {2} with {3} attack".format(
                                                              current_player.character.name,
                                                              damage,
                                                              opponent.character.name,
                                                              attack.name)))

                        # If the attack was not successful the log the event that the attack missed
                        else:
                            Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                                          name=Event.MISSED_OPPONENT,
                                                          description="{0} attacked {1} but missed".format(
                                                              current_player.character.name,
                                                              opponent.character.name)))

                        # Deduct the AP required to perform the attack
                        current_player.AP -= attack_AP

                        # if the opponent was killed...
                        if opponent.is_dead() is True:

                            # Update the attackers kills and XP stats
                            current_player.kills += 1
                            xp_gained = opponent.get_stat("XPReward")
                            if xp_gained is None:
                                xp_gained = 5

                            current_player.increment_stat("XP", xp_gained)

                            Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                                          name=Event.KILLED_OPPONENT,
                                                          description="{0} killed {1} and gained {2} XP".format(
                                                              current_player.character.name,
                                                              opponent.character.name, xp_gained)))

                            # If the whole opponent's team is dead then end the battle
                            if opposite_team.is_dead() is True:
                                self._state = Battle.END
                                Battle.EVENTS.add_event(Event(type=Event.BATTLE, name=Event.VICTORY,
                                                              description="Team {0} are all dead!".format(
                                                                  opposite_team.name)))

                            # Otherwise just remove the deaqd player from the order of play
                            else:
                                self.order_of_play.remove(opponent)
                                self.set_current_target(tactic=Team.TACTIC_NEAREST)

    def move_player(self, dx: int, dy: int):

        current_player = self.get_current_player()

        if current_player.AP > 0:
            self.battle_floor.move_player(current_player, dx, dy)
        else:
            Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                          name=Event.NO_AP,
                                          description="{0} does not have enough AP to move!".format(
                                              current_player.character.name)))

    def do_auto(self, override=False):

        if self.state != Battle.PLAYING:
            return

        if self.get_player_team(self.get_current_player()).type == Team.COMPUTER or override is True:

            # If no Bot exists for the current player then create one
            if self.get_current_player() not in self.bots.keys():
                new_bot = AIBot(self.get_current_player(), self)
                x, y, z = self.get_current_player().xyz
                new_bot.set_path(((10, 10, z), (10, 1, z)))
                self.bots[self.get_current_player()] = new_bot

            # Get the Bot for the current player and do a tick
            ai = self.bots[self.get_current_player()]
            ai.print()
            ai.do_tick()

            # If the Bot can't do anything else then reset it and move to the next player
            if ai.current_state == AIBot.FINISHED:
                self.next_player()
                ai.reset()

    def get_winning_team(self):

        winning_team = None

        if self.state == Battle.END:
            if self.teams[0].is_dead() is True:
                winning_team = self.teams[1]
            else:
                winning_team = self.teams[0]

        return winning_team


class Game:
    LOADED = "LOADED"
    READY = "READY"
    PLAYING = "PLAYING"
    BATTLE = "BATTLE"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME OVER"
    END = "END"

    SAVE_GAME_DIR = os.path.dirname(__file__) + "\\saves\\"
    GAME_DATA_DIR = os.path.dirname(__file__) + "\\Squoids_data\\"

    def __init__(self, name: str):

        self.name = name
        self.tick_count = 0
        self.player = None
        self.events = EventQueue()
        self.events.add_event(Event("{0} model created!".format(self.name)))
        self._state = Game.LOADED
        self._locations = None
        self._items = None
        self._maps = None
        self._locations = None
        self._npcs = None
        self._attacks = None
        self.floor_factory = None
        self.battle = None
        self._battle_floor_id = None

        self._stats = utils.StatEngine(self.name)
        self.hst = utils.HighScoreTable(self.name)

    def __str__(self):
        return "{0}. Events({1}).".format(self.name, self.events.size())

    @property
    def current_floor(self):
        return self.floor_factory.floors[self.current_floor_id]

    def get_current_floor(self):
        return self.current_floor

    @property
    def state(self):

        return self._state

    @state.setter
    def state(self, new_state):

        self._old_state = self.state
        self._state = new_state

        self.events.add_event(Event(self._state,
                                    "Game state change from {0} to {1}".format(self._old_state, self._state),
                                    Event.STATE))

    def print(self):
        print(self)
        self.events.print()

    def process_event(self, new_event):
        print("Default Game event process:{0}".format(new_event))
        if new_event.name == Event.FOUND_FLAG:
            print("Battle Mode!!!!")
            self.start_battle()

    def start_battle(self):
        self.state = Game.BATTLE
        self._battle_floor_id = random.choice((0, 2, 3, 4, 5, 100, 101, 102))

        # self._battle_floor_id = 101

        RED = (237, 28, 36)
        GREEN = (34, 177, 76)
        BLUE = (63, 72, 204)



        team1 = Team("Blue", BLUE, type=Team.COMPUTER)
        team2 = Team("Red", RED, type=Team.COMPUTER)

        team1 = Team("Blue", BLUE, type=Team.PLAYER)
        team2 = Team("Red", RED, type=Team.PLAYER)

        characters = list(self._npcs.get_characters())

        for i in range(0, 5):
            new_char = random.choice(characters)
            new_char_type = new_char.get_attribute("Image") + "_blue"
            new_player = Player(name=new_char_type, rect=(i * 2 + 8, 2, 32, 32), layer=3, character=new_char)
            attack_name = new_char.get_attribute("Attack")
            new_player.add_attack(self._attacks[attack_name])
            characters.remove(new_char)
            team1.add_player(new_player)

            new_char = random.choice(characters)
            new_char_type = new_char.get_attribute("Image") + "_red"
            new_player = Player(name=new_char_type, rect=(i * 2 + 8, 17, 32, 32), layer=3, character=new_char)
            attack_name = new_char.get_attribute("Attack")
            new_player.add_attack(self._attacks[attack_name])
            characters.remove(new_char)
            team2.add_player(new_player)

        battle_floor = self.floor_factory.floors[self._battle_floor_id]

        self.battle = Battle(team1, team2, battle_floor)
        self.battle.start()

    def tick(self):

        self.tick_count += 1
        # self.events.add_event(Event(Event.TICK, "Tick", Event.GAME))

        if self.state == Game.BATTLE:
            self.battle.tick()
        elif self.state == Game.PLAYING:
            if self.tick_count % 4 == 0:
                self.current_floor.tick()

    def get_next_event(self):

        next_event = None
        if self.events.size() > 0:
            next_event = self.events.pop_event()

        return next_event

    def initialise(self):

        self.state = Game.READY
        self.current_floor_id = 100

        self.load_characters("characters.csv")
        self.load_map("locations.csv", "maplinks.csv")
        self.load_items("items.csv")
        self.load_attacks("attacks.csv")

        self._stats.print()

        self.floor_factory = FloorBuilder(Game.GAME_DATA_DIR)
        self.floor_factory.initialise()
        self.floor_factory.load_floors()

        Floor.EVENTS = self.events
        Battle.EVENTS = self.events

        self.hst.load()

        characters = list(self._npcs.get_characters())
        new_char = random.choice(characters)
        new_char_type = new_char.get_attribute("Image") + "_red"
        new_player = Player(name=new_char_type, rect=(0, 10, 32, 32), layer=1, character=new_char)
        attack_name = new_char.get_attribute("Attack")
        new_player.add_attack(self._attacks[attack_name])

        characters.remove(new_char)

        self.add_player(new_player, auto_position=True)

        for i in range(0, 4):
            new_char = random.choice(characters)
            new_char_type = new_char.get_attribute("Image") + "_blue"
            new_player = Player(name=new_char_type, rect=(0, 10, 32, 32), layer=1, character=new_char)
            new_player.add_attack(self._attacks["Basic Attack"])

            self.add_enemy(new_player, auto_position=True)

            characters.remove(new_char)

        self.current_map = self._maps.get_map(1)
        self.current_map.print()

    def load_map(self, location_file_name: str, map_links_file_name: str):

        # Load in locations
        self._locations = trpg.LocationFactory(Game.GAME_DATA_DIR + location_file_name)
        self._locations.load()

        # Load in level maps
        self._maps = trpg.MapFactory(self._locations)
        self._maps.load("Level1", 1, Game.GAME_DATA_DIR + map_links_file_name)

    def load_characters(self, character_file_name: str):
        self._npcs = trpg.RPGCharacterFactory(Game.GAME_DATA_DIR + character_file_name, self._stats)
        self._npcs.load()
        self._npcs.print()

        rpg_classes = trpg.RPGCSVFactory("Classes", Game.GAME_DATA_DIR + "classes.csv")
        rpg_classes.load()

        rpg_races = trpg.RPGCSVFactory("Races", Game.GAME_DATA_DIR + "races.csv")
        rpg_races.load()

        character_names = self._npcs.get_character_names()

        for character_name in character_names:
            character = self._npcs.get_character_by_name(character_name)
            # character.roll()
            character.load_stats(rpg_classes.get_stats_by_name(character.rpg_class), overwrite=False)
            character.load_stats(rpg_races.get_stats_by_name(character.race), overwrite=False)
            character.load_attributes(rpg_races.get_attributes_by_name(character.race))
            add_core_stats(character)
            add_derived_stats(character)
            # character.examine()

    def load_items(self, item_file_name: str):
        self._items = trpg.ItemFactory(Game.GAME_DATA_DIR + item_file_name, self._stats)
        self._items.load()

    def load_attacks(self, attacks_file_name: str):

        self._attacks = {}

        attack_data = trpg.RPGCSVFactory(name="Attacks", file_name=Game.GAME_DATA_DIR + attacks_file_name,
                                         stat_category="Attacks")
        attack_data.load()

        attacks = attack_data.get_rpg_object_names()

        for attack in attacks:

            attributes = attack_data.get_attributes_by_name(attack)
            # print("Attributes for attack {0}:".format(attack))
            for attribute, value in attributes.items():
                # print("\t{0}={1}".format(attribute, value))

                new_attack = Attack(name=attack,
                                    description=attributes["Description"],
                                    type=attributes["Type"],
                                    attack_attribute=attributes["Attack Attribute"],
                                    defence_attribute=attributes["Defence Attribute"],
                                    effect=attributes["Effect"],
                                    image=attributes["Image"])

            stats = attack_data.get_stats_by_name(attack)

            for stat in stats:
                new_attack.add_stat(stat)

            self._attacks[attack] = new_attack

            new_attack.print()

    def start(self):

        self.state = Game.PLAYING

    def pause(self, is_paused: bool = True):

        if self.state == Game.PAUSED and is_paused is False:

            self.state = Game.PLAYING

        else:
            self.state = Game.PAUSED

    def get_scores(self):

        return [("Keith", 923)]

    def is_high_score(self, score: int):
        return self.hst.is_high_score(score)

    def game_over(self):

        if self._state != Game.GAME_OVER:
            logging.info("Game Over {0}...".format(self.name))

            self.hst.save()

            self.state = Game.GAME_OVER

    def end(self):

        logging.info("Ending {0}...".format(self.name))

        self.state = Game.END

        self.hst.save()

    def save(self):
        pass

    def load(self):
        pass

    def add_player(self, new_player: Player, auto_position: bool = False):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't add new players!".format(self.state))

        logging.info("Adding new player {0} to game {1}...".format(new_player.name, self.name))

        self.player = new_player
        self.current_floor.add_player(new_player, auto_position=auto_position)

    def add_enemy(self, new_player: Player, auto_position: bool = False):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't add new players!".format(self.state))

        logging.info("Adding new enemy {0} to game {1}...".format(new_player.name, self.name))

        self.current_floor.add_enemy(new_player, auto_position=auto_position)

    def move_player(self, dx: int, dy: int):

        self.current_floor.move_player(self.player, dx, dy)

        x, y, z = self.player.xyz

        tile = self.current_floor.get_floor_tile(x, y, z, is_raw=True)

        if tile is not None and tile.name in Floor.OBJECT_TO_DIRECTION.keys():

            try:
                print("You found the exit {}!".format(Floor.OBJECT_TO_DIRECTION[tile.name]))
                self.check_exit(Floor.OBJECT_TO_DIRECTION[tile.name])

            except Exception as err:
                print(err)
                self.player.back()

    def check_exit(self, direction):

        # Check if a direction was even specified
        if direction is "":
            raise (Exception("You need to specify a direction e.g. NORTH"))

        # Check if the direction is a valid one
        direction = direction.upper()
        if direction not in trpg.MapLink.valid_directions:
            raise (Exception("Direction %s is not valid" % direction.title()))

        # Now see if the map allows you to go in that direction
        links = self.current_map.get_location_links_map(self.get_current_floor().id)

        # OK stat direction is valid...
        if direction in links.keys():
            link = links[direction]

            # ..but see if it is currently locked...
            if link.is_locked() is True:
                raise (Exception("You can't go %s - %s" % (direction.title(), link.locked_description)))

            # If all good move to the new location
            print("You go %s %s..." % (direction.title(), link.description))

            self.current_floor_id = link.to_id
            self.get_current_floor().add_player_at_entrance(self.player, Floor.REVERSE_DIRECTION[direction])

        else:
            raise (Exception("You can't go {0} from here!".format(direction)))


class Event():
    # Event Types
    QUIT = "quit"
    DEFAULT = "default"
    STATE = "state"
    GAME = "game"
    FLOOR = "floor"
    BATTLE = "battle"

    # Events
    TICK = "Tick"
    PLAYING = "playing"
    COLLIDE = "collide"
    INTERACT = "interact"
    BLOCKED = "blocked"
    SECRET = "secret"
    TREASURE = "treasure"
    DOOR_OPEN = "door opened"
    DOOR_LOCKED = "door locked"
    SWITCH = "switch"
    FOUND_FLAG = "found_flag"
    KEY = "key"
    TELEPORT = "teleport"
    GAIN_HEALTH = "gain health"
    LOSE_HEALTH = "lose health"
    NO_AP = "No action points"
    KILLED_OPPONENT = "killed opponent"
    MISSED_OPPONENT = "missed opponent"
    DAMAGE_OPPONENT = "damaged opponent"
    VICTORY = "victory"
    NEXT_PLAYER = "next player"

    def __init__(self, name: str, description: str = None, type: str = DEFAULT):
        self.name = name
        self.description = description
        self.type = type

    def __str__(self):
        return "{0}:{1} ({2})".format(self.name, self.description, self.type)


class EventQueue():
    def __init__(self):
        self.events = collections.deque()

    def add_event(self, new_event: Event):
        self.events.append(new_event)

    def pop_event(self):
        return self.events.pop()

    def size(self):
        return len(self.events)

    def print(self):
        for event in self.events:
            print(event)


class Navigator:
    ALTERNATE_OPTION_DIFF = 4
    MAX_RECURSION_LEVEL = 100

    def __init__(self, floor: Floor):
        self.floor = floor
        self.route = []
        self.danger_count = 0

    def distance(self, a, b):
        ax, ay, az = a
        bx, by, bz = b
        d = math.sqrt(math.pow(ax - bx, 2) + math.pow(ay - by, 2) + math.pow(az - bz, 2))
        return d

    def navigate(self, start, finish, direct=False, walkable=False, safe=False, level=0, visited=[]):

        if level == 0:
            self.route = []
            visited = []
            self.danger_count = 0

        if start in visited:
            # print("Already been here on this navigation!")
            return False

        visited.append(start)

        if level >= Navigator.MAX_RECURSION_LEVEL:
            return False

        d = self.distance(start, finish)

        # print("{3}. navigating from {0} to {1} (direct={4}, walkable={5},safe={6}). {2:.2f} distance to travel".format(
        #   start, finish, d, level, direct, walkable, safe))
        finished = False

        if start == finish:
            #print("found the finish")
            self.route.append((start))
            finished = True
        else:
            startx, starty, startz = start

            if level > 0:

                tile = self.floor.get_floor_tile(startx, starty, startz)

                if tile is not None and tile.is_solid is True:
                    # print("Hit an obstacle at {0}".format(start))
                    return False

                elif walkable is True and self.floor.is_occupiable(startx, starty, startz) is False:
                    # print("Hit an unoccupiable place")
                    return False

                elif safe is True and self.floor.is_dangerous(startx, starty, startz) is True:
                    # print("Hit an unsafe place!")
                    return False

            finishx, finishy, finishz = finish

            options = []

            dx = startx - finishx
            dy = starty - finishy

            if dx > 0:

                option = (startx - 1, starty, startz)
                options.append((option, self.distance(option, finish)))

                # If you are not far off track also look at other options
                if direct is False and abs(dx) <= Navigator.ALTERNATE_OPTION_DIFF:
                    # print("Adding extra X options")
                    option = (startx + 1, starty, startz)
                    options.append((option, self.distance(option, finish)))

            elif dx < 0:

                option = (startx + 1, starty, startz)
                options.append((option, self.distance(option, finish)))

                # If you are not hurry and not far off track also look at other options
                if direct is False and abs(dx) <= Navigator.ALTERNATE_OPTION_DIFF:
                    # print("Adding extra X options")
                    option = (startx - 1, starty, startz)
                    options.append((option, self.distance(option, finish)))

            # If you are not hurry and bang on track also look at other options
            elif dx == 0 and direct is False:
                # print("Adding extra X options")
                option = (startx - 1, starty, startz)
                options.append((option, self.distance(option, finish)))
                option = (startx + 1, starty, startz)
                options.append((option, self.distance(option, finish)))

            if dy > 0:

                option = (startx, starty - 1, startz)
                options.append((option, self.distance(option, finish)))

                # If you are not far off track also look at other options
                if direct is False and abs(dy) <= Navigator.ALTERNATE_OPTION_DIFF:
                    # print("Adding extra Y options")
                    option = (startx, starty + 1, startz)
                    options.append((option, self.distance(option, finish)))

            elif dy < 0:

                option = (startx, starty + 1, startz)
                options.append((option, self.distance(option, finish)))

                # If you are not far off track also look at other options
                if direct is False and abs(dy) <= Navigator.ALTERNATE_OPTION_DIFF:
                    # print("Adding extra Y options")
                    option = (startx, starty - 1, startz)
                    options.append((option, self.distance(option, finish)))

            # If you are bang on track still look at other options
            elif dy == 0 and direct is False:
                # print("Adding extra Y options")
                option = (startx, starty - 1, startz)
                options.append((option, self.distance(option, finish)))
                option = (startx, starty + 1, startz)
                options.append((option, self.distance(option, finish)))

            if startz > finishz:

                option = (startx, starty, startz - 1)
                options.append((option, self.distance(option, finish)))

            elif startz < finishz:

                option = (startx, starty, startz + 1)
                options.append((option, self.distance(option, finish)))

            options.sort(key=itemgetter(1))
            option, min_distance = options[0]

            # print(str(options))

            for option in options:
                direction, d = option

                if direct is True and d > min_distance:
                    continue

                if self.navigate(direction, finish, direct=direct, walkable=walkable, safe=safe, level=level + 1,
                                 visited=visited) is True:
                    self.route.insert(0, start)
                    finished = True
                    break

        return finished


class AIBot:
    HUNTING = "Hunting"
    TRACKING = "Tracking"
    ATTACKING = "Attacking"
    FLEEING = "Fleeing"
    FINISHED = "Finished"
    TELEPORTING = "Teleporting"

    def __init__(self, player: Player, battle: Battle):

        self.player = player
        self.battle = battle
        self.player_team = self.battle.get_player_team(self.player)
        self.opposition_team = self.battle.get_opposite_team(self.player_team)
        self.navigator = Navigator(battle.battle_floor)
        self.tick_count = 0
        self.view_range = 4
        self._path = None
        self._path_target = None
        self.current_state = AIBot.HUNTING
        self._actions = {}

        self.initialise()

    def reset(self):
        self.current_state = AIBot.HUNTING

    def set_path(self, path: list, start_pos: int = 0):
        self._path = list(path)
        self._path_target = start_pos

    def next_path_target(self):
        self._path_target += 1
        if self._path_target > len(self._path):
            self._path_target = 0

        return self._path[self._path_target]

    def do_tick(self):

        if self.current_state == AIBot.FINISHED:
            return

        self.tick_count += 1

        if self.player.AP <= 0:
            self.current_state = AIBot.FINISHED

        result = self._actions[self.current_state]()

        while result is False:
            result = self._actions[self.current_state]()

    def is_visible(self, direct: bool = True):
        opponents = []
        is_visible = False
        for player in self.opposition_team.players:

            if player.is_dead() is False:
                result = self.navigator.navigate(start=self.player.xyz,
                                                 finish=player.xyz,
                                                 direct=direct,
                                                 walkable=False,
                                                 safe=False)

                distance = self.navigator.distance(a=self.player.xyz, b=player.xyz)
                if result is True and distance < self.view_range:
                    opponents.append(
                        (player, distance, len(self.navigator.route)))
                    is_visible = True
                else:
                    print("Target at distance {0:.2f} beyond range {1}".format(distance, self.view_range))

        return is_visible, opponents

    def do_hunting(self):

        print("Hunting")

        action = False

        is_visible, opponents = self.is_visible()

        # If we can see a target then switch to Tracking mode
        if is_visible is True:
            print("Target spotted")
            self.current_state = AIBot.TRACKING

        # Else try to move around
        else:

            # Try and follow a set path
            if self._path is not None:
                action = self.do_path_following()

            # If that failed try to move around randomly
            if action is False:
                action = self.do_random_move()

            # Otherwise give-up
            if self.player.has_moved() is False:
                self.current_state = AIBot.FINISHED

        return action

    def do_tracking(self):

        action = False

        print("Tracking")

        is_visible, opponents = self.is_visible()

        # If we are tracking but have lost visibility of a target then switch to hunting
        if is_visible is False:
            self.current_state = AIBot.HUNTING

        # Else...
        else:
            # Look at the closest opponent that we can see
            opponents.sort(key=itemgetter(1))
            target, distance, route_length = opponents[0]
            self.battle.set_current_target(tactic=Team.TACTIC_SPECIFIED, target=target)

            print("Tracking nearest opponent {0} at distance {1}".format(target.character.name, distance))

            if target.layer != self.player.layer:
                print("No opponents on this level")
                self.current_state = AIBot.TELEPORTING
                return False

            # If they are close enough to attack then switch to attacking mode
            if distance <= self.player.get_attack().get_stat(Attack.RANGE).value:
                print("In range for attack!")
                self.current_state = AIBot.ATTACKING


            # Else navigate towards the target
            else:
                # Try to go via a safe route
                result = self.navigator.navigate(start=self.player.xyz,
                                                 finish=target.xyz,
                                                 direct=False,
                                                 walkable=True,
                                                 safe=True)
                print("Safe route = {0}: route = {1}".format(result, self.navigator.route))
                # If no safe route go direct!
                if result is False:
                    result = self.navigator.navigate(start=self.player.xyz,
                                                     finish=target.xyz,
                                                     direct=True,
                                                     walkable=True,
                                                     safe=False)

                    print("Direct route = {0}: route = {1}".format(result, self.navigator.route))

                # If there is a route to the target then move towards it
                if result is True:
                    x, y, z = self.player.xyz
                    newx, newy, newz = self.navigator.route[1]
                    print("from {0} to {1}".format(self.player.xyz, self.navigator.route[1]))
                    self.battle.battle_floor.move_player(self.player, newx - x, newy - y)
                    action = True

                # Else move randomly
                else:
                    action = self.do_random_move()

                    # If we failed to move after several attempts then give up
                    if self.player.has_moved() is False:
                        self.current_state = AIBot.FINISHED

        return action

    def do_teleporting(self):
        print("Teleporting")

        action = False

        x, y, z = self.player.xyz

        teleports = self.battle.battle_floor.get_matching_objects((Objects.TELEPORT, Objects.TELEPORT2), z)

        if len(teleports) == 0:
            self.current_state = AIBot.HUNTING
            return

        print(str(teleports))

        for teleport in teleports:
            result = self.navigator.navigate(start=self.player.xyz, finish=teleport.xyz, direct=False, walkable=True,
                                             safe=False)
            print(str(self.navigator.route))
            if result is True:

                if len(self.navigator.route) == 1:
                    next_xyz = self.navigator.route[0]
                else:
                    next_xyz = self.navigator.route[1]

                newx, newy, newz = next_xyz

                print("from {0} to {1}".format(self.player.xyz, next_xyz))
                self.battle.battle_floor.move_player(self.player, newx - x, newy - y)
                if self.player.has_moved() is True:
                    self.current_state = AIBot.HUNTING
                    action = True
                    break
            else:
                print("Can't find a route to the teleporter!")

        if self.player.has_moved() is False:
            self.current_state = AIBot.FINISHED

        return action

    def do_attacking(self):
        print("Attacking")

        action = False

        is_visible, opponents = self.is_visible()

        # If we have lost visibility of a target then switch to hunting
        if is_visible is False:
            self.current_state = AIBot.HUNTING

        # Else
        else:

            # Look at the nearest opponent
            opponents.sort(key=itemgetter(1))
            target, distance, route_length = opponents[0]

            # if they are close enough to attack...
            if distance <= self.player.get_attack().get_stat(Attack.RANGE).value:

                # .. and have enough AP...
                if self.player.AP >= self.player.get_attack().get_stat(Attack.AP).value:
                    self.battle.set_current_target(tactic=Team.TACTIC_SPECIFIED, target=target)
                    self.battle.do_attack()
                    print("Attacking {0}".format(self.battle.get_current_target().character.name))
                    action = True

                # Otherwise we have run out of options
                else:
                    self.current_state = AIBot.FINISHED

            # Else switch to tracking mode
            else:
                self.current_state = AIBot.TRACKING

        return action

    def do_fleeing(self):
        print("Fleeing")
        return True

    def do_finish(self):
        return True

    def do_random_move(self):
        print("Moving")
        action = False
        choices = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        x, y, z = self.player.xyz

        for i in range(0, 10):
            dx, dy = random.choice(choices)
            new_x = x + dx
            new_y = y + dy
            if self.battle.battle_floor.is_in_bounds(new_x, new_y, z) is True and self.battle.battle_floor.is_dangerous(
                    new_x, new_y, z) is False and \
                            self.battle.battle_floor.is_occupiable(new_x, new_y, z) is True:

                self.battle.battle_floor.move_player(self.player, dx, dy)
                if self.player.has_moved() is True:
                    action = True
                    break
            else:
                choices.remove((dx, dy))

        return action

    def do_path_following(self):

        print("Path Following")

        action = False

        target_position = self._path[self._path_target]
        if target_position == self.player.xyz:
            target_position = self.next_path_target()

        result = self.navigator.navigate(start=self.player.xyz,
                                         finish=target_position,
                                         direct=False,
                                         walkable=True,
                                         safe=True)

        print("Safe route = {0}: route = {1}".format(result, self.navigator.route))

        # If no safe route go unsafe route!
        if result is False:
            result = self.navigator.navigate(start=self.player.xyz,
                                             finish=target_position,
                                             direct=False,
                                             walkable=True,
                                             safe=False)

            print("Direct route = {0}: route = {1}".format(result, self.navigator.route))

        # If there is a route to the target then move towards it
        if result is True:
            x, y, z = self.player.xyz
            newx, newy, newz = self.navigator.route[1]
            print("from {0} to {1}".format(self.player.xyz, self.navigator.route[1]))
            self.battle.battle_floor.move_player(self.player, newx - x, newy - y)
            action = True

        return action

    def initialise(self):
        self._actions[AIBot.HUNTING] = self.do_hunting
        self._actions[AIBot.TRACKING] = self.do_tracking
        self._actions[AIBot.TELEPORTING] = self.do_teleporting
        self._actions[AIBot.ATTACKING] = self.do_attacking
        self._actions[AIBot.FLEEING] = self.do_fleeing
        self._actions[AIBot.FINISHED] = self.do_finish

    def print(self):
        print("AIBot for player {0} on team {1} vs team {2}: State={3}".format(self.player.character.name,
                                                                               self.player_team.name,
                                                                               self.opposition_team.name,
                                                                               self.current_state))


class AIBot2:
    HUNTING = "Hunting"
    TRACKING = "Tracking"
    ATTACKING = "Attacking"
    FLEEING = "Fleeing"
    FINISHED = "Finished"
    TELEPORTING = "Teleporting"

    def __init__(self, player: Player, floor: Floor):

        self.player = player
        self.floor = floor
        self.navigator = Navigator(floor)
        self.tick_count = 0
        self.view_range = 6
        self._path = None
        self._path_target = None
        self.current_state = AIBot.HUNTING
        self._actions = {}
        self.initialise()

    def reset(self):
        self.current_state = AIBot.HUNTING

    def set_path(self, path: list, start_pos: int = 0):
        self._path = list(path)
        self._path_target = start_pos

    def next_path_target(self):
        self._path_target += 1
        if self._path_target >= len(self._path):
            self._path_target = 0

        return self._path[self._path_target]

    def do_tick(self):

        if self.current_state == AIBot.FINISHED:
            return

        self.tick_count += 1

        if self.player.AP <= 0:
            self.current_state = AIBot.FINISHED

        result = self._actions[self.current_state]()

        while result is False:
            result = self._actions[self.current_state]()

    def is_visible(self, direct: bool = True):

        opponents = []
        is_visible = False
        for player in self.floor.players:

            if player.is_dead() is False:
                result = self.navigator.navigate(start=self.player.xyz,
                                                 finish=player.xyz,
                                                 direct=direct,
                                                 walkable=False,
                                                 safe=False)

                distance = self.navigator.distance(a=self.player.xyz, b=player.xyz)
                if result is True and distance < self.view_range:
                    opponents.append(
                        (player, distance, len(self.navigator.route)))
                    is_visible = True
                # else:
                #     print("Target at distance {0:.2f} beyond range {1}".format(distance, self.view_range))

        return is_visible, opponents

    def do_hunting(self):

        print("Hunting")

        action = False

        is_visible, opponents = self.is_visible()

        # If we can see a target then switch to Tracking mode
        if is_visible is True:
            #print("Target spotted")
            self.current_state = AIBot.TRACKING

        # Else try to move around
        else:

            # Try and follow a set path
            if self._path is not None:
                action = self.do_path_following()

            # If that failed try to move around randomly
            if action is False:
                action = self.do_random_move()

            # Otherwise give-up
            if self.player.has_moved() is False:
                self.current_state = AIBot.FINISHED

        return action

    def do_tracking(self):

        action = False

        print("Tracking")

        is_visible, opponents = self.is_visible()

        # If we are tracking but have lost visibility of a target then switch to hunting
        if is_visible is False:
            self.current_state = AIBot.HUNTING

        # Else...
        else:
            # Look at the closest opponent that we can see
            opponents.sort(key=itemgetter(1))
            target, distance, route_length = opponents[0]
            # self.floor.set_current_target(tactic=Team.TACTIC_SPECIFIED, target=target)

            #print("Tracking nearest opponent {0} at distance {1}".format(target.character.name, distance))

            if target.layer != self.player.layer:
                print("No opponents on this level")
                self.current_state = AIBot.TELEPORTING
                return False

            # If they are close enough to attack then switch to attacking mode
            if distance <= self.player.get_attack().get_stat(Attack.RANGE).value:
                print("In range for attack!")
                self.current_state = AIBot.ATTACKING


            # Else navigate towards the target
            else:
                # Try to go via a safe route
                result = self.navigator.navigate(start=self.player.xyz,
                                                 finish=target.xyz,
                                                 direct=False,
                                                 walkable=True,
                                                 safe=True)
                #print("Safe route = {0}: route = {1}".format(result, self.navigator.route))
                # If no safe route go direct!
                if result is False:
                    result = self.navigator.navigate(start=self.player.xyz,
                                                     finish=target.xyz,
                                                     direct=True,
                                                     walkable=True,
                                                     safe=False)

                    #print("Direct route = {0}: route = {1}".format(result, self.navigator.route))

                # If there is a route to the target then move towards it
                if result is True:
                    x, y, z = self.player.xyz
                    newx, newy, newz = self.navigator.route[1]
                    #print("from {0} to {1}".format(self.player.xyz, self.navigator.route[1]))
                    self.floor.move_player(self.player, newx - x, newy - y)
                    action = True

                # Else move randomly
                else:
                    action = self.do_random_move()

                    # If we failed to move after several attempts then give up
                    if self.player.has_moved() is False:
                        self.current_state = AIBot.FINISHED

        return action

    def do_teleporting(self):

        print("Teleporting")

        action = False

        x, y, z = self.player.xyz

        teleports = self.floor.get_matching_objects((Objects.TELEPORT, Objects.TELEPORT2), z)

        if len(teleports) == 0:
            self.current_state = AIBot.HUNTING
            return

        for teleport in teleports:
            result = self.navigator.navigate(start=self.player.xyz, finish=teleport.xyz, direct=False, walkable=True,
                                             safe=False)
            print(str(self.navigator.route))
            if result is True:

                if len(self.navigator.route) == 1:
                    next_xyz = self.navigator.route[0]
                else:
                    next_xyz = self.navigator.route[1]

                newx, newy, newz = next_xyz

                print("Moving from {0} to {1}".format(self.player.xyz, next_xyz))
                self.floor.move_player(self.player, newx - x, newy - y)
                if self.player.has_moved() is True:
                    self.current_state = AIBot.HUNTING
                    action = True
                    break
            else:
                print("Can't find a route to the teleporter!")

        if self.player.has_moved() is False:
            self.current_state = AIBot.FINISHED

        return action

    def do_attacking(self):
        print("Attacking")

        action = False

        is_visible, opponents = self.is_visible()

        # If we have lost visibility of a target then switch to hunting
        if is_visible is False:
            self.current_state = AIBot.HUNTING

        # Else
        else:

            # Look at the nearest opponent
            opponents.sort(key=itemgetter(1))
            target, distance, route_length = opponents[0]

            # if they are close enough to attack...
            if distance <= self.player.get_attack().get_stat(Attack.RANGE).value:

                # .. and we have enough AP...
                if self.player.AP >= self.player.get_attack().get_stat(Attack.AP).value:
                    # self.floor.set_current_target(tactic=Team.TACTIC_SPECIFIED, target=target)
                    # self.floor.do_attack()
                    print("Attacking {0}".format(target.character.name))
                    action = True

                # Otherwise we have run out of options
                else:
                    self.current_state = AIBot.FINISHED

            # Else switch to tracking mode
            else:
                self.current_state = AIBot.TRACKING

        return action

    def do_fleeing(self):
        print("Fleeing")
        return True

    def do_finish(self):
        return True

    def do_random_move(self):
        print("Moving")
        action = False
        choices = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        x, y, z = self.player.xyz

        for i in range(0, 10):
            dx, dy = random.choice(choices)
            new_x = x + dx
            new_y = y + dy
            if self.floor.is_in_bounds(new_x, new_y, z) is True and self.floor.is_dangerous(new_x, new_y,
                                                                                            z) is False and \
                            self.floor.is_occupiable(new_x, new_y, z) is True:

                self.floor.move_player(self.player, dx, dy)
                if self.player.has_moved() is True:
                    action = True
                    break
            else:
                choices.remove((dx, dy))

        return action

    def do_path_following(self):

        print("Path Following")

        action = False

        target_position = self._path[self._path_target]
        if target_position == self.player.xyz:
            target_position = self.next_path_target()

        result = self.navigator.navigate(start=self.player.xyz,
                                         finish=target_position,
                                         direct=False,
                                         walkable=True,
                                         safe=True)

        #print("Safe route = {0}: route = {1}".format(result, self.navigator.route))

        # If no safe route go unsafe route!
        if result is False:
            result = self.navigator.navigate(start=self.player.xyz,
                                             finish=target_position,
                                             direct=False,
                                             walkable=True,
                                             safe=False)

            #print("Direct route = {0}: route = {1}".format(result, self.navigator.route))

        # If there is a route to the target then move towards it
        if result is True:
            x, y, z = self.player.xyz
            newx, newy, newz = self.navigator.route[1]
            #print("Moving from {0} to {1}".format(self.player.xyz, self.navigator.route[1]))
            self.floor.move_player(self.player, newx - x, newy - y)
            action = True

        return action

    def initialise(self):
        self._actions[AIBot.HUNTING] = self.do_hunting
        self._actions[AIBot.TRACKING] = self.do_tracking
        self._actions[AIBot.TELEPORTING] = self.do_teleporting
        self._actions[AIBot.ATTACKING] = self.do_attacking
        self._actions[AIBot.FLEEING] = self.do_fleeing
        self._actions[AIBot.FINISHED] = self.do_finish

    def print(self):
        print("AIBot for player {0} : State={1}".format(self.player.character.name, self.current_state))
        print(str(self.player))
