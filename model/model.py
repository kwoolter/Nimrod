import collections

class Game():

    LOADED = "LOADED"
    READY = "READY"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME OVER"
    END = "END"

    def __init__(self, name : str):
        self.name = name
        self.tick_count = 0
        self.events = EventQueue()
        self.events.add_event(Event("{0} model created!".format(self.name)))
        self._state = Game.LOADED

    def __str__(self):
        return "{0}. Events({1}).".format(self.name, self.events.size())

    @property
    def state(self):

        return self._state

    def print(self):
        print(self)
        self.events.print()

    def tick(self):
        self.tick_count += 1
        # self.events.add_event(Event("tick"))
        #
        # if self.tick_count > 100:
        #     self.events.add_event(Event("Time do die", Event.QUIT))

    def get_next_event(self):

        next_event = None
        if self.events.size() > 0:
            next_event = self.events.pop_event()

        return next_event


class Event():

    QUIT = "quit"
    DEFAULT = "default"

    def __init__(self, name : str, type : str = DEFAULT):
        self.name = name
        self.type = type

    def __str__(self):
        return "{0} ({1})".format(self.name, self.type)


class EventQueue():
    def __init__(self):
        self.events = collections.deque()

    def add_event(self, new_event : Event):
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
    DIRECTIONS = (NORTH, SOUTH, EAST, WEST)
