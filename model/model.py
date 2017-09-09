class Model():
    def __init__(self, name : str):
        self.name = name
        self.events = EventQueue()

    def __str__(self):
        return self.name


class Event():
    def __init__(self, name : str, type : str):
        self.name = name
        self.type = type


class EventQueue():
    def __init__(self):
        pass

    def add_event(self, new_event : Event):
        pass


