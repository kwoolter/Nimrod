import collections
import copy
import csv
import logging
import os

import pygame

import utils
import utils.trpg as trpg
from .derived_stats import *


class Objects:
    EMPTY = "empty"
    TREE = "tree"
    PLAYER = "player"
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    HEART = "heart"
    BLOCK = "block"
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
    SQUOID = "squoid"
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
        self.name = name
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


class Monster(FloorObject):
    def __init__(self, name: str,
                 rect: pygame.Rect,
                 height: int = 30):
        super(Monster, self).__init__(name=name, rect=rect, height=height)


class Floor:
    EXIT_NORTH = "NORTH"
    EXIT_SOUTH = "SOUTH"
    EXIT_EAST = "EAST"
    EXIT_WEST = "WEST"
    EXIT_UP = "UP"
    EXIT_DOWN = "DOWN"

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
        self.players = {}
        self.objects = []
        self.monsters = []
        self.layers = {}
        self.floor_plans = {}
        self.exits = {}

    def __str__(self):
        return "Floor {0}: rect={1}, objects={2}, monsters={3}".format(self.name, self.rect, self.object_count,
                                                                       len(self.monsters))

    @property
    def object_count(self):
        count = 0
        for layer in self.layers.values():
            count += len(layer)
        return count

    def add_player(self, new_player: Player, position: str = None):

        self.players[new_player.name] = new_player

        #self.add_object(new_player)

        print("Adding player at {0},{1}".format(new_player.rect.x, new_player.rect.y))


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

    def is_player_collide(self, target: FloorObject):

        collide = False

        for player in self.players.values():
            if target.is_colliding(player):
                collide = True
                break

        return collide

    def colliding_objects(self, target: FloorObject):

        objects = self.layers[target.layer]

        # print("colliding check {0} objects".format(len(objects)))

        colliding = []

        for object in objects:
            if object.is_colliding(target):
                colliding.append(object)

        return colliding

    def touching_objects(self, target: FloorObject):

        objects = self.layers[target.layer]

        touching = []

        for object in objects:
            if object.is_touching(target):
                touching.append(object)

        return touching

    def get_layer(self, layer_id):

        if layer_id not in self.layers.keys():
            raise Exception("Layer {0} not found in Floor {0}".format(layer_id, self.name))

        layer = self.layers[layer_id]

        return layer

    def get_floor_tile(self, x : int, y: int, layer_id : int, is_raw : bool = False):

        layer = self.floor_plans[layer_id]
        floor_object = layer[x][y]
        if is_raw is False and floor_object is None:
            for player in self.players.values():
                if (x,y,layer_id) == (player.rect.x, player.rect.y, player.layer):
                    floor_object = player
                    break

        return floor_object


    def move_player(self, name: str, dx: int = 0, dy: int = 0):

        if name not in self.players.keys():
            raise Exception("{0}:move_player() - Player {1} is not on floor (2).".format(__class__, name, self.name))

        selected_player = self.players[name]

        selected_player.move(dx, dy)
        x,y = selected_player.rect.x, selected_player.rect.y

        if x >= self.rect.width or x < 0:
            selected_player.back()
        elif y >= self.rect.height or y < 0:
            selected_player.back()
        else:
            tile = self.get_floor_tile(x, y, selected_player.layer, is_raw=True)
            if tile is not None:
                if tile.name in (Objects.BLOCK_LEFT_SLOPE, Objects.BLOCK_RIGHT_SLOPE):
                    selected_player.layer += 1
                else:
                    print("You hit a {0}".format(tile.name))
                    selected_player.back()




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


class Character(trpg.RPGCharacter):
    def __init__(self, name: str, x: int = 1, y: int = 1, width: int = 1, height: int = 1, HP: int = 20):
        # super(trpg.RPGCharacter, self).__init__(name, race, rpg_class)

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

    def tick(self):

        if self.state != Game.PLAYING:
            return

        self.tick_count += 1

        if self.tick_count % 4 == 0:
            self.events.add_event(Event(Event.TICK, "Tick", Event.GAME))

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

        self.hst.load()

        new_player = Player(name=Objects.SQUOID, rect=(19,19,0,0))

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

    def move_player(self, dx : int, dy : int):

        self.current_floor.move_player(self.player.name, dx, dy)




class Event():
    # Event Types
    QUIT = "quit"
    DEFAULT = "default"
    STATE = "state"
    GAME = "game"

    # Events
    TICK = "Tick"
    PLAYING = "playing"

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



