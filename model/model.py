import collections
import logging
import utils
import utils.trpg as trpg
import os
from .derived_stats import *


class Character(trpg.RPGCharacter):
    def __init__(self, name: str, x: int = 1, y: int = 1, width: int = 1, height: int = 1, HP: int = 20):
        #super(trpg.RPGCharacter, self).__init__(name, race, rpg_class)

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


class Player(Character):
    def __init__(self, name: str, x: int = 1, y: int = 1, HP: int = 10):
        super(Player, self).__init__(name=name, x=x, y=y, HP=HP)
        self.initialise()

    # Set player's attributes back to starting values
    def initialise(self):
        super(Player, self).initialise()
        self.keys = 0
        self.treasure = 0
        self.kills = 0

    @property
    def score(self):
        return self.kills + self.treasure


class Game():
    LOADED = "LOADED"
    READY = "READY"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME OVER"
    END = "END"

    SAVE_GAME_DIR = os.path.dirname(__file__) + "\\saves\\"
    GAME_DATA_DIR = os.path.dirname(__file__) + "\\data\\"

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

        self._stats = utils.StatEngine(self.name)
        self.hst = utils.HighScoreTable(self.name)



    def __str__(self):
        return "{0}. Events({1}).".format(self.name, self.events.size())

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

        self.load_characters("characters.csv")
        self.load_map("locations.csv", "maplinks.csv")
        self.load_items("items.csv")

        self._stats.print()

        self.hst.load()

    def load_map(self, location_file_name : str, map_links_file_name : str):

        # Load in locations
        self._locations = trpg.LocationFactory(Game.GAME_DATA_DIR + location_file_name)
        self._locations.load()

        # Load in level maps
        self._maps = trpg.MapFactory(self._locations)
        self._maps.load("Level1",1,Game.GAME_DATA_DIR + map_links_file_name)

    def load_characters(self, character_file_name : str):
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
            character.load_stats(rpg_classes.get_stats_by_name(character.rpg_class))
            character.load_stats(rpg_races.get_stats_by_name(character.race))
            add_core_stats(character)
            add_derived_stats(character)

    def load_items(self, item_file_name : str):
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


class Objects:
    TREE = "tree"
    PLAYER = "player"
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    HEART = "heart"
    DIRECTIONS = (NORTH, SOUTH, EAST, WEST)
