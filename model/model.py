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

    ATTACK_ATTRIBUTES = {STRENGTH: "STR", DEXTERITY: "DEX", INTELLIGENCE: "INT", WISDOM: "WIS"}

    # Defence types
    AC = "AC"
    FORTITIUDE = "Fortitude"
    REFLEX = "Reflex"
    WILL = "Will"

    DEFENCE_TYPES = {AC: "AC", FORTITIUDE: "FORT", REFLEX: "REF", WILL: "WILL"}

    def __init__(self, name: str, description: str, type: str, attack_attribute: str, defence_attribute: str,
                 effect: str):
        self.name = name
        self.description = description
        self.effect = effect

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
    TREE = "tree"
    PLAYER = "player"
    SKULL = "skull"
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    HEART = "heart"
    BASE = "base"
    BASE_RED = "base_red"
    BASE_YELLOW = "base_yellow"
    BASE_SHADOW = "base_shadow"
    BLOCK = "block"
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
    SQUOID = "squoid"
    CRAB_GREEN = "crab"
    CRAB_RED = "crab_red"
    SQUOID_GREEN = "squoid_green"
    SQUOID_RED = "squoid_red"
    SQUOID2 = "squoid2"
    SKELETON_LEFT = "skeleton_left"
    SKELETON_RIGHT = "skeleton_right"
    KEY = "key1"
    CHEST = "chest"
    LAVA = "lava"
    ICE = "ice"
    CYLINDER = "cylinder"
    RED_DOT = "red dot"
    GREEN_DOT = "green_dot"
    BUBBLES = "bubbles"
    TELEPORT = "teleport"
    SEAWEED = "seaweed"
    FIRE = "fire"
    POISON = "poison"
    INK = "ink"
    HIT = "hit"
    SHOCK = "shock"
    ASLEEP = "asleep"
    FROZEN = "frozen"

    DIRECTIONS = (NORTH, SOUTH, EAST, WEST)
    SQUOIDS = (SQUOID, SQUOID2, SQUOID_GREEN, SQUOID_RED, CRAB_GREEN, CRAB_RED, SKELETON_LEFT, SKELETON_RIGHT)


class FloorObject(object):
    TOUCH_FIELD_X = 3
    TOUCH_FIELD_Y = 3

    def __init__(self, name: str,
                 rect: pygame.Rect,
                 layer: int = 1,
                 height: int = None,
                 solid: bool = True,
                 visible: bool = True,
                 interactable: bool = True):
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
                 height: int = 40,
                 character: Character = None):
        super(Player, self).__init__(name=name, rect=rect, height=height)

        self.treasure = 0
        self.keys = 0
        self.boss_keys = 0
        self.layer = 1

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
        if self.is_dead():
            return Objects.SKULL
        else:
            return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name

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

    def add_attack(self, attack : Attack):
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
    TACTIC_RANDOM = "random"
    TACTIC_WEAKEST = "weakest"
    TACTIC_STRONGEST = "strongest"
    TACTIC_NEAREST = "nearest"
    TACTIC_FURTHEST = "furthest"

    def __init__(self, name: str):
        self.name = name
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

    def choose_player(self, tactic: int = TACTIC_RANDOM, other_player: Player = None):

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
                    print("defaulting distance to 999")
                available_players.append(player)

        if tactic == Team.TACTIC_RANDOM:
            chosen_player = random.choice(available_players)

        elif tactic == Team.TACTIC_WEAKEST:
            chosen_player = sorted(available_players, key=attrgetter("HP"), reverse=False)[0]

        elif tactic == Team.TACTIC_STRONGEST:
            chosen_player = sorted(available_players, key=attrgetter("HP"), reverse=True)[0]

        elif tactic == Team.TACTIC_NEAREST:
            if other_player is not None:
                chosen_player = sorted(available_players, key=attrgetter("distance"), reverse=False)[0]
                # print("Attacker at ({0},{1},{2})".format(other_player.rect.x,other_player.rect.y,other_player.layer))
                # for player in available_players:
                #      print(player, player.distance)
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
        self.layers = {}
        self.floor_plans = {}
        self.exits = {}
        self.teleports = []

    def __str__(self):
        return "Floor {0}: rect={1},layer={4} objects={2}, monsters={3}".format(self.name, self.rect, self.object_count,
                                                                                len(self.monsters),
                                                                                len(self.floor_plans.keys()))

    @property
    def object_count(self):
        count = 0
        for layer in self.layers.values():
            count += len(layer)
        return count

    def add_player(self, new_player: Player, position: str = None):

        self.players.append(new_player)

        print("Adding player at {0},{1},{2}".format(new_player.rect.x, new_player.rect.y, new_player.layer))

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

        for layer_id in self.layers.keys():
            if layer_id not in self.floor_plans.keys():
                new_plan = [[None for x in range(self.rect.height)] for x in range(self.rect.width)]
                self.floor_plans[layer_id] = new_plan
            floor_plan = self.floor_plans[layer_id]
            for floor_object in self.layers[layer_id]:
                floor_plan[floor_object.rect.x][floor_object.rect.y] = floor_object
                if floor_object.name == Objects.TELEPORT:
                    self.teleports.append((floor_object.rect.x, floor_object.rect.y, floor_object.layer))

    def remove_object(self, object: FloorObject):
        objects = self.layers[object.layer]
        objects.remove(object)

    def swap_object(self, object: FloorObject, new_object_type: str):

        objects = self.layers[object.layer]

        x, y, z = object.get_pos()

        swap_object = FloorObjectLoader.get_object_copy_by_name(new_object_type)
        swap_object.set_pos(x, y, z)
        objects.remove(object)
        objects.append(swap_object)

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
        if is_raw is False:
            for player in self.players:
                if (x, y, layer_id) == (player.rect.x, player.rect.y, player.layer):
                    floor_object = player
                    break

        return floor_object

    def set_floor_tile(self, x: int, y: int, layer_id: int, new_object: FloorObject = None):

        layer = self.floor_plans[layer_id]
        layer[x][y] = new_object

    def is_occupiable(self, x, y, z):

        result = True

        # Is the position out of bounds?
        if x >= self.rect.width or x < 0 or y >= self.rect.height or y < 0:
            result = False
        else:

            tile = self.get_floor_tile(x, y, z)

            # Is the new position occupied?
            if tile is not None and tile.is_solid is True:
                result = False

        return result

    def move_player(self, selected_player: Player, dx: int = 0, dy: int = 0):

        if selected_player not in self.players:
            raise Exception(
                "{0}:move_player() - Player {1} is not on floor (2).".format(__class__, selected_player.character.name,
                                                                             self.name))

        # Make player's last position the same as their current position
        selected_player.rect = selected_player.rect

        x, y, z = selected_player.rect.x, selected_player.rect.y, selected_player.layer
        new_x = x + dx
        new_y = y + dy

        # Is the new position out of bounds?
        if new_x >= self.rect.width or new_x < 0 or new_y >= self.rect.height or new_y < 0:

            Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.BLOCKED, description="You hit an edge!"))
            # raise Exception("{0}:move_player() - out of bounds!".format(__class__, selected_player.character.name))

        else:

            # Look at what tile is in the new position
            tile = self.get_floor_tile(new_x, new_y, z)

            # Is the new position filled with a solid object?
            if tile is not None and tile.is_solid is True:

                Floor.EVENTS.add_event(
                    Event(type=Event.FLOOR, name=Event.COLLIDE, description="You hit a {0}".format(tile.name)))

            # Else move the player and see what happens next...
            else:

                selected_player.move(dx, dy)
                x, y, z = selected_player.rect.x, selected_player.rect.y, selected_player.layer

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
                    elif tile.name == Objects.KEY:
                        selected_player.keys += 1
                        self.set_floor_tile(x, y, z, None)
                        Floor.EVENTS.add_event(
                            Event(type=Event.FLOOR, name=Event.KEY, description="You found a {0}".format(tile.name)))

                    elif tile.name == Objects.TELEPORT:

                        while True:
                            new_position = random.choice(self.teleports)
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

                # If standing on nothing move back
                if base_tile is None or base_tile.is_solid is False:
                    selected_player.back()
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.BLOCKED,
                                                 description="You can't go that way"))

                # If standing on lava lose health
                elif base_tile.name == Objects.LAVA:
                    selected_player.do_damage(1)
                    selected_player.do_effect(Player.BURNED)
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR,
                                                 name=Event.LOSE_HEALTH,
                                                 description="{0} stood on {1}".format(selected_player.character.name,
                                                                                       base_tile.name)))

                # If standing on ice lose health
                elif base_tile.name == Objects.ICE:
                    selected_player.do_damage(1)
                    selected_player.do_effect(Player.FROZEN)
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR,
                                                 name=Event.LOSE_HEALTH,
                                                 description="{0} stood on {1}".format(selected_player.character.name,
                                                                                       base_tile.name)))

    def tick(self):

        # For each player...
        for selected_player in self.players:

            selected_player.tick()

            x, y, layer = selected_player.rect.x, selected_player.rect.y, selected_player.layer

            # Check what the player is standing on...
            base_tile = self.get_floor_tile(x, y, layer - 1)
            if base_tile.name == Objects.LAVA:
                selected_player.do_damage(1)
                Floor.EVENTS.add_event(Event(type=Event.FLOOR,
                                             name=Event.LOSE_HEALTH,
                                             description="{0} stood on {1}".format(selected_player.name,
                                                                                   base_tile.name)))


class FloorBuilder():
    FLOOR_LAYOUT_FILE_NAME = "_floor_layouts.csv"
    FLOOR_OBJECT_FILE_NAME = "_floor_objects.csv"

    def __init__(self, data_file_directory: str):
        self.data_file_directory = data_file_directory
        self.floors = {}

    def initialise(self, file_prefix: str = "default"):

        self.floor_objects = FloorObjectLoader(
            self.data_file_directory + file_prefix + FloorBuilder.FLOOR_OBJECT_FILE_NAME)
        self.floor_objects.load()

        self.floor_layouts = FloorLayoutLoader(
            self.data_file_directory + file_prefix + FloorBuilder.FLOOR_LAYOUT_FILE_NAME)
        self.floor_layouts.load()

    def load_floors(self):

        for floor_id, new_floor in FloorLayoutLoader.floor_layouts.items():
            self.floors[floor_id] = new_floor

        for floor in self.floors.values():
            print(str(floor))


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

        for floor in self.floor_layouts.values():
            floor.build_floor_plan()


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
                                         interactable=FloorObjectLoader.BOOL_MAP[row.get("interactable").upper()] \
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

    def __init__(self, team1: Team, team2: Team, battle_floor: Floor = None):
        self.teams = [team1, team2]
        self.turns = 0
        self._state = Battle.READY
        self.next_team = None
        self.battle_floor = battle_floor
        self.order_of_play = []
        self.current_target = None

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
                self.battle_floor.add_player(new_player)

            if len(t2) > 0:
                new_player = t2.pop(0)
                self.order_of_play.append(new_player)
                self.battle_floor.add_player(new_player)

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

    def set_current_target(self, tactic: str = Team.TACTIC_NEAREST):

        current_player = self.get_current_player()
        current_team = self.get_player_team(current_player)

        opponent_team = self.get_opposite_team(current_team)

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

        # Find out who is ttacking who
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
                        opponent_defence = opponent.get_stat(attack.defence_attribute + " Defence")

                        # Roll a 20 sided dice and add and attacker bonuses to the roll
                        dice_roll = random.randint(1, 20)
                        attack_roll = dice_roll + attacker_attack_bonus

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

                            print("{0} ({1} v {2}): {3:.0f}d{4:.0f}+{5:.0f}+{6:.0f} did {7:.0f} damage".format(
                                attack.name,
                                attack.attack_attribute,
                                attack.defence_attribute,
                                number_of_dice,
                                dice_sides,
                                attack_bonus,
                                attacker_attack_modifier,
                                damage))

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
            if current_player.has_moved() is True:
                current_player.AP -= 1
        else:
            Battle.EVENTS.add_event(Event(type=Event.BATTLE,
                                          name=Event.NO_AP,
                                          description="{0} does not have enough AP to move!".format(
                                              current_player.character.name)))

    def get_winning_team(self):

        winning_team = None

        if self.state == Battle.END:
            if self.teams[0].is_dead() is True:
                winning_team = self.teams[1]
            else:
                winning_team = self.teams[0]

        return winning_team


class Game():
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

    def start_battle(self):
        self.state = Game.BATTLE
        self._battle_floor_id = 0

        team1 = Team("Blue")
        team2 = Team("Red")

        characters = list(self._npcs.get_characters())

        for i in range(0, 5):
            new_char = random.choice(characters)
            new_char_type = random.choice((Objects.SQUOID, Objects.CRAB_GREEN, Objects.SKELETON_LEFT))
            new_player = Player(name=new_char_type, rect=(i * 2 + 3, 3, 32, 32), character=new_char)
            attack_name = new_char.get_attribute("Attack")
            new_player.add_attack(self._attacks[attack_name])
            characters.remove(new_char)
            team1.add_player(new_player)

            new_char = random.choice(characters)
            new_char_type = random.choice((Objects.SQUOID_RED, Objects.CRAB_RED, Objects.SKELETON_RIGHT))
            new_player = Player(name=new_char_type, rect=(i * 2 + 3, 14, 32, 32), character=new_char)
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
        self.current_floor_id = 1

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

        new_char = random.choice(list(self._npcs.get_characters()))
        new_player = Player(name=Objects.SQUOID, rect=(19, 19, 0, 0), character=new_char)

        self.add_player(new_player)

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
            #character.roll()
            character.load_stats(rpg_classes.get_stats_by_name(character.rpg_class), overwrite=False)
            character.load_stats(rpg_races.get_stats_by_name(character.race), overwrite=False)
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
                                    effect=attributes["Effect"])

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

    def add_player(self, new_player: Player):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't add new players!".format(self.state))

        logging.info("Adding new player {0} to game {1}...".format(new_player.name, self.name))

        self.player = new_player
        self.current_floor.add_player(new_player)

    def move_player(self, dx: int, dy: int):

        self.current_floor.move_player(self.player, dx, dy)


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
    BLOCKED = "blocked"
    TREASURE = "treasure"
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
    def __init__(self, floor: Floor):
        self.floor = floor
        self.route = []

    def distance(self, a, b):
        ax, ay, az = a
        bx, by, bz = b
        d = math.sqrt(math.pow(ax - bx, 2) + math.pow(ay - by, 2) + math.pow(az - bz, 2))
        return d

    def navigate(self, start, finish, direct=False, level=0):

        if level == 0:
            self.route = []

        d = self.distance(start, finish)

        print("{3}. navigating from {0} to {1}. {2:.2f} distance to travel".format(start, finish, d, level))
        finished = False

        if start == finish:
            print("found the finish")
            finished = True
        else:
            startx, starty, startz = start

            if level > 0 and self.floor.is_occupiable(startx, starty, startz) is False:
                print("Hit an obstacle at {0}".format(start))
                return False

            finishx, finishy, finishz = finish

            options = []

            if startx > finishx:

                option = (startx - 1, starty, startz)
                options.append((option, self.distance(option, finish)))

            elif startx < finishx:

                option = (startx + 1, starty, startz)
                options.append((option, self.distance(option, finish)))

            if starty > finishy:

                option = (startx, starty - 1, startz)
                options.append((option, self.distance(option, finish)))

            elif starty < finishy:

                option = (startx, starty + 1, startz)
                options.append((option, self.distance(option, finish)))

            options.sort(key=itemgetter(1))
            option, min_distance = options[0]

            # print(str(options))

            for option in options:
                direction, d = option

                if direct is True and d > min_distance:
                    continue

                if self.navigate(direction, finish, direct, level + 1) is True:
                    self.route.insert(0, start)
                    finished = True
                    break

        return finished
