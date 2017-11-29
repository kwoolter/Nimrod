import collections
import copy
import csv
import logging
import math
import os
import random
from operator import attrgetter

import pygame

import utils
import utils.trpg as trpg
from .derived_stats import *


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
    SQUOID_GREEN = "squoid_green"
    SQUOID2 = "squoid2"
    KEY = "key1"
    LAVA = "lava"
    CYLINDER = "cylinder"

    DIRECTIONS = (NORTH, SOUTH, EAST, WEST)


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

    def move(self, dx: int, dy: int):
        self._old_rect = self._rect.copy()
        self.rect.x += dx
        self.rect.y += dy

    def set_pos(self, x: int, y: int):
        self._old_rect = self._rect.copy()
        self.rect.x = x
        self.rect.y = y

    def get_pos(self):
        return self._rect.x, self._rect.y


class Player(FloorObject):
    def __init__(self, name: str,
                 rect: pygame.Rect,
                 height: int = 40):
        super(Player, self).__init__(name=name, rect=rect, height=height)

        self.treasure = 0
        self.keys = 0
        self.boss_keys = 0
        self.HP = 10
        self.layer = 1
        self.AP = 1
        self._name = name

    def __str__(self):
        return ("Player {0}: HP={1},AP={2},({3},{4},{5}),Dead={6}".format(self.name, self.HP, self.AP,
                                                                             self.rect.x, self.rect.y, self.layer,
                                                                             self.is_dead()))

    def is_dead(self):
        return self.HP <= 0

    @property
    def name(self):
        if self.is_dead():
            return Objects.SKULL
        else:
            return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name


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

    def choose_player(self, tactic: int = TACTIC_RANDOM, other_player: Player = None):

        print("Choosing player based on {0}".format(tactic))

        available_players = []
        for player in self.players:
            if player.is_dead() is False:
                if other_player is not None:
                    player.distance = math.sqrt((player.rect.x - other_player.rect.x) ** 2 +
                                                (player.rect.x - other_player.rect.y) ** 2 +
                                                (player.layer - other_player.layer) ** 2)
                else:
                    player.distance = 0
                available_players.append(player)

        # for player in available_players:
        #     print(player, player.distance)

        if tactic == Team.TACTIC_RANDOM:
            chosen_player = random.choice(available_players)

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

    def __str__(self):
        return "Floor {0}: rect={1},layer={4} objects={2}, monsters={3}".format(self.name, self.rect, self.object_count,
                                                                       len(self.monsters), len(self.floor_plans.keys()))

    @property
    def object_count(self):
        count = 0
        for layer in self.layers.values():
            count += len(layer)
        return count

    def add_player(self, new_player: Player, position: str = None):

        self.players.append(new_player)

        # self.add_object(new_player)

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

    def remove_object(self, object: FloorObject):
        objects = self.layers[object.layer]
        objects.remove(object)

    def swap_object(self, object: FloorObject, new_object_type: str):

        objects = self.layers[object.layer]

        x, y = object.get_pos()

        swap_object = FloorObjectLoader.get_object_copy_by_name(new_object_type)
        swap_object.set_pos(x, y)
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
        if is_raw is False and floor_object is None:
            for player in self.players:
                if (x, y, layer_id) == (player.rect.x, player.rect.y, player.layer):
                    floor_object = player
                    break

        return floor_object

    def set_floor_tile(self, x: int, y: int, layer_id: int, new_object: FloorObject = None):

        layer = self.floor_plans[layer_id]
        layer[x][y] = new_object

    def move_player(self, name: str, dx: int = 0, dy: int = 0):

        if name not in self.players.keys():
            raise Exception("{0}:move_player() - Player {1} is not on floor (2).".format(__class__, name, self.name))

        selected_player = self.players[name]

        selected_player.move(dx, dy)
        x, y = selected_player.rect.x, selected_player.rect.y

        if x >= self.rect.width or x < 0 or y >= self.rect.height or y < 0:
            selected_player.back()
            Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.BLOCKED, description="You hit an edge!"))
        else:
            tile = self.get_floor_tile(x, y, selected_player.layer, is_raw=True)
            if tile is not None:
                if tile.name in (Objects.BLOCK_LEFT_SLOPE, Objects.BLOCK_RIGHT_SLOPE):
                    selected_player.layer += 1
                elif tile.name in (Objects.SQUOID):
                    Floor.EVENTS.add_event(
                        Event(type=Event.FLOOR, name=Event.COLLIDE, description="You hit a {0}".format(tile.name)))
                elif tile.name == Objects.SPHERE_GREEN:
                    selected_player.treasure += 1
                    self.set_floor_tile(x, y, selected_player.layer, None)
                    Floor.EVENTS.add_event(
                        Event(type=Event.FLOOR, name=Event.TREASURE, description="You found a {0}".format(tile.name)))
                elif tile.name == Objects.SPHERE_BLUE:
                    selected_player.HP += 1
                    self.set_floor_tile(x, y, selected_player.layer, None)
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.GAIN_HEALTH,
                                                 description="You found a {0}".format(tile.name)))
                elif tile.name == Objects.KEY:
                    selected_player.keys += 1
                    self.set_floor_tile(x, y, selected_player.layer, None)
                    Floor.EVENTS.add_event(
                        Event(type=Event.FLOOR, name=Event.KEY, description="You found a {0}".format(tile.name)))
                else:
                    selected_player.back()
                    Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.BLOCKED,
                                                 description="You are blocked by a {0}".format(tile.name)))

        # Check what the player is standing on...
        base_tile = self.get_floor_tile(selected_player.rect.x, selected_player.rect.y, selected_player.layer - 1)
        # If standing on nothing move back
        if base_tile is None:
            selected_player.back()
            Floor.EVENTS.add_event(Event(type=Event.FLOOR, name=Event.BLOCKED,
                                         description="You can't go that way"))

        # If standing on lava lose health
        elif base_tile.name == Objects.LAVA:
            selected_player.HP -= 1
            Floor.EVENTS.add_event(Event(type=Event.FLOOR,
                                         name=Event.LOSE_HEALTH,
                                         description="{0} stood on {1}".format(selected_player.name, base_tile.name)))

    def tick(self):

        # For each player...
        for selected_player in self.players.values():

            x, y, layer = selected_player.rect.x, selected_player.rect.y, selected_player.layer

            # Check what the player is standing on...
            base_tile = self.get_floor_tile(x, y, layer - 1)
            if base_tile.name == Objects.LAVA:
                selected_player.HP -= 1
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
                print("loading {0}".format(row))

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
        for team in self.teams:
            team.print()

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

    def get_current_player(self):
        current_player = self.order_of_play[0]

        if current_player.AP <= 0:
            old_player = self.order_of_play.pop(0)
            old_player.AP = 1
            current_player = self.order_of_play[0]
            self.set_current_target(tactic=Team.TACTIC_NEAREST)
            self.order_of_play.append(old_player)
            self.turns += 1

        return current_player

    def set_current_target(self, tactic : str = Team.TACTIC_NEAREST):

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

    def do_turn(self):
        current_player = self.get_current_player()
        current_team = self.get_player_team(current_player)

        #print("Player {0}'s turn from the {1} team".format(current_player.name, current_team.name))

        opponent_team = self.get_opposite_team(current_team)
        # opponent = opponent_team.choose_player(tactic=random.choice((Team.TACTIC_WEAKEST, Team.TACTIC_STRONGEST, Team.TACTIC_RANDOM)))
        #opponent = opponent_team.choose_player(tactic=Team.TACTIC_WEAKEST)
        #opponent = opponent_team.choose_player(tactic=Team.TACTIC_NEAREST, other_player=current_player)
        opponent = opponent_team.choose_player(tactic=Team.TACTIC_FURTHEST, other_player=current_player)

        print("Player {0} attacks Player {1} from the {2} team".format(current_player.name,
                                                                       opponent.name,
                                                                       opponent_team.name))
        opponent.HP -= random.randint(1, 3)
        if opponent.is_dead() is True:
            print("Player {0} killed Player {1}".format(current_player.name, opponent.name))
            self.order_of_play.remove(opponent)

        current_player.AP -= 1

    def do_attack(self):

        current_player = self.get_current_player()
        opponent = self.get_current_target()

        if opponent is not None:

            damage = random.randint(1, 3)
            opponent.HP -= damage
            current_player.AP -= 1

            print("Player {0} attacks Player {1} and does {2} damage".format(current_player.name,
                                                                             opponent.name,
                                                                             damage))

            if opponent.is_dead() is True:
                print("Player {0} killed Player {1}".format(current_player.name, opponent.name))
                self.order_of_play.remove(opponent)
                self.set_current_target(tactic=Team.TACTIC_NEAREST)


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
        for i in range(0, 5):
            team1.add_player(Player(name=Objects.SQUOID, rect=(i*2+3, 3, 32, 32)))
            team2.add_player(Player(name=Objects.SQUOID2, rect=(i*2+3, 11, 32, 32)))

        battle_floor = self.floor_factory.floors[self._battle_floor_id]

        self.battle = Battle(team1, team2, battle_floor)
        self.battle.start()

        # for i in range(1, 20):
        #     self.battle.do_turn()
        #
        # print(str(self.battle))
        # self.battle.print()


    def tick(self):

        if self.state != Game.PLAYING:
            return

        self.tick_count += 1

        if self.tick_count % 4 == 0:
            self.events.add_event(Event(Event.TICK, "Tick", Event.GAME))
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

        self._stats.print()

        self.floor_factory = FloorBuilder(Game.GAME_DATA_DIR)
        self.floor_factory.initialise()
        self.floor_factory.load_floors()

        Floor.EVENTS = self.events

        self.hst.load()

        new_player = Player(name=Objects.SQUOID, rect=(19, 19, 0, 0))

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
            character.load_stats(rpg_classes.get_stats_by_name(character.rpg_class), overwrite=False)
            character.load_stats(rpg_races.get_stats_by_name(character.race), overwrite=False)
            add_core_stats(character)
            add_derived_stats(character)

    def load_items(self, item_file_name: str):
        self._items = trpg.ItemFactory(Game.GAME_DATA_DIR + item_file_name, self._stats)
        self._items.load()

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

        self.current_floor.move_player(self.player.name, dx, dy)


class Event():
    # Event Types
    QUIT = "quit"
    DEFAULT = "default"
    STATE = "state"
    GAME = "game"
    FLOOR = "floor"

    # Events
    TICK = "Tick"
    PLAYING = "playing"
    COLLIDE = "collide"
    BLOCKED = "blocked"
    TREASURE = "treasure"
    KEY = "key"
    GAIN_HEALTH = "gain health"
    LOSE_HEALTH = "lose health"

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
