import copy
import csv
import logging

import pygame


class Objects:
    PLAYER = "player"
    TREE1 = "tree1"
    TREE2 = "tree2"
    GRASS = "grass"
    TILE1 = "tile1"
    TILE2 = "tile2"
    CRATE = "crate"
    BUSH = "bush"
    WALL = "wall"
    PLAYER = "player"
    TREASURE = "treasure"
    TREASURE_CHEST = "treasure chest"
    DOOR = "door"
    DOOR_NORTH = "door north"
    DOOR_OPEN = "open_door"
    KEY = "key"
    BOSS_KEY = "boss key"
    TRAP = "trap"
    BOSS = "boss"
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    WALL_CORNER_TL = "wall corner tl"
    WALL_CORNER_TR = "wall corner tr"
    WALL_CORNER_BL = "wall corner bl"
    WALL_CORNER_BR = "wall corner br"
    WALL_TOP_HORIZONTAL = "wall top horizontal"
    WALL_BOTTOM_HORIZONTAL = "wall bottom horizontal"
    WALL_LEFT_VERTICAL = "wall left vertical"
    WALL_RIGHT_VERTICAL = "wall right vertical"
    WALL_TL = "wall tl"
    WALL_TR = "wall tr"
    WALL_BL = "wall bl"
    WALL_BR = "wall br"
    WALL_TOP = "wall top"
    WALL_BLOCK = "wall block"

    DIRECTIONS = (NORTH, SOUTH, EAST, WEST)
    DOORS = (DOOR_NORTH, DOOR)


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

        if position in self.exits.keys():
            exit_rect = self.exits[position].rect
            player_rect = new_player.rect
            x = exit_rect.centerx - int(player_rect.width / 2)
            y = exit_rect.centery - int(player_rect.height / 2)

            if position == Floor.EXIT_NORTH:
                y = exit_rect.bottom + FloorObject.TOUCH_FIELD_Y + 1
            elif position == Floor.EXIT_SOUTH:
                y = exit_rect.top - new_player.rect.height - FloorObject.TOUCH_FIELD_Y - 1
            elif position == Floor.EXIT_WEST:
                x = exit_rect.right + FloorObject.TOUCH_FIELD_X + 1
            elif position == Floor.EXIT_EAST:
                x = exit_rect.left - new_player.rect.width - FloorObject.TOUCH_FIELD_X - 1
        else:
            x = (self.rect.width / 2)
            y = (self.rect.height / 2)

        print("Adding player at {0},{1}".format(x, y))
        new_player.set_pos(x, y)

    def add_object(self, new_object: FloorObject):

        if new_object.layer not in self.layers.keys():
            self.layers[new_object.layer] = []

        objects = self.layers[new_object.layer]
        objects.append(new_object)
        self.rect.union_ip(new_object.rect)

        self.layers[new_object.layer] = sorted(objects, key=lambda obj: obj.layer * 1000 + obj.rect.y, reverse=False)

        if new_object.name in Objects.DIRECTIONS:
            self.exits[Floor.OBJECT_TO_DIRECTION[new_object.name]] = new_object

        logging.info("Added {0} at location ({1},{2})".format(new_object.name, new_object.rect.x, new_object.rect.y))

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

    def move_player(self, name: str, dx: int = 0, dy: int = 0):

        if name not in self.players.keys():
            raise Exception("{0}:move_player() - Player {1} is not on floor (2).".format(__class__, name, self.name))

        selected_player = self.players[name]

        objects = self.layers[selected_player.layer]

        selected_player.move(dx, dy)

        if self.rect.contains(selected_player.rect) == False:
            selected_player.back()
        else:
            for object in objects:
                if object.is_colliding(selected_player):
                    selected_player.back()
                    break
                    # if dy != 0:
                    #     selected_player.move(0, dy)
                    #
                    #     if self.rect.contains(selected_player.rect) == False:
                    #         selected_player.back()
                    #     else:
                    #         for object in objects:
                    #             if object.is_colliding(selected_player):
                    #                 selected_player.back()
                    #                 break


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

    DEFAULT_OBJECT_WIDTH = 32
    DEFAULT_OBJECT_DEPTH = 32

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
