__author__ = 'U394198'

import csv
from copy import deepcopy
from operator import attrgetter

from .RPGObject import *


class Character(RPGObject):
    CHARACTER_TYPES = {0: "PC", 1: "NPC", 2: "Vendor", 3: "Enemy", 4: "Thief", 5: "Trainer", 6: "Banker"}
    CHARACTERS = 0
    INVENTORY_ID = -1000
    # PLAYER_CHARACTER_INVENTORY_ID = ItemFactory.INVENTORY
    NPC_TYPE = "NPCType"
    TYPE_PC = 0
    TYPE_NPC = 1
    TYPE_VENDOR = 2
    TYPE_ENEMY = 3
    TYPE_THIEF = 4
    TYPE_TRAINER = 5
    TYPE_BANKER = 6

    # CORE_STAT_NAMES = ("Dexterity", "Intelligence", "Strength", "Wisdom", "Charisma", "Constitution")
    CORE_STAT_STANDARD_ARRAY = (15, 14, 13, 12, 10, 8)

    '''
    Class for storing the details about a character as well as their game state
    '''

    def __init__(self, name: str, race: str, rpg_class: str, is_player_character: bool = False):

        super(Character, self).__init__(name + " the " + race + " " + rpg_class, "Character")

        self.name = name
        self.race = race
        self.rpg_class = rpg_class
        self.create_time = datetime.datetime.now()
        self.is_player_character = is_player_character

        Character.CHARACTERS += 1
        self.id = Character.CHARACTERS

        # Create an empty dictionary to store non-numeric attributes
        self._attributes = {}

    @property
    def inventory_id(self):
        if self.is_player_character:
            return Character.PLAYER_CHARACTER_INVENTORY_ID
        else:
            stat = self.get_stat("InventoryID")
            if stat is None:
                return Character.INVENTORY_ID - self.id
            else:
                return stat.value

    @property
    def type(self):
        stat = self.get_stat(Character.NPC_TYPE)
        if stat is None:
            return Character.TYPE_NPC
        else:
            return stat.value

    # Roll the core stats for this Character
    def roll(self):
        '''
        Roll some random stats for this character
        '''

        # Load in some core stats using the standard array to randomly assign scores
        core_stat_values = set(Character.CORE_STAT_STANDARD_ARRAY)
        for core_stat in Character.CORE_STAT_NAMES:
            self.add_stat(CoreStat(core_stat, "Abilities", core_stat_values.pop()))

            # self.add_derived_stats()

    # Convert a Character object to a string
    def __str__(self):
        text = self.name + " the " + self.race + " " + self.rpg_class
        return text

    # Print the details of this Character object
    def print(self):
        text = str(self)
        text += " (created " + self.create_time.strftime("%d/%m/%Y %X") + ")"
        type = self.get_stat("NPCType")

        if type is not None:
            text += " type=" + Character.CHARACTER_TYPES[type.value]
        else:
            text += " type=" + Character.CHARACTER_TYPES[0]

        print(text)

    # Examine a character
    def examine(self):
        text = str(self)
        text += " (created " + self.create_time.strftime("%d/%m/%Y %X") + ")"
        text += " inventory id=%i" % self.inventory_id
        type = self.get_stat("NPCType")
        if type is not None:
            text += " type=" + Character.CHARACTER_TYPES[type.value]
        else:
            text += " type=" + Character.CHARACTER_TYPES[0]

        # Build list of all attributes in the private and public stats
        categories = list(self._private_data.get_category_names())
        categories.sort()

        for category in categories:
            text += "\n%s" % category
            stats = list(self._private_data.get_stats_by_category(category))
            stats.sort(key=attrgetter("name"))
            for stat in stats:
                text += "\n\t%s:%i" % (stat.name, stat.value)

        text += "\nDescriptors"
        descriptors = list(self._attributes.keys())
        descriptors.sort()
        for descriptor in descriptors:
            text += "\n\t%s:%s" % (descriptor, self._attributes[descriptor])

        text += "\nStats"

        # attributes = ["Age", "XP", "Level", "XPToLevel", "LevelUp","Damage", "HP", "Max HP", "Gold", "LoadPct"]
        # attributes = ["Age", "XP", "Level", "XPToLevel"]
        attributes = []

        for attribute_name in attributes:
            stat = self.get_stat(attribute_name)
            if stat is not None and stat.value is not None:
                text += "\n\t%s:%i" % (attribute_name, stat.value)

        stats = self._public_data.get_stats_by_owner(self)

        for stat in stats:
            text += "\n\t%s:%i" % (stat.name, stat.value)

        return text

    # Get a named non-numeric attribute
    def get_attribute(self, attribute_name: str):
        if attribute_name in self._attributes.keys():
            return self._attributes[attribute_name]
        else:
            return None

    # Load in a dictionary of attributes
    def load_attributes(self, new_attributes: dict, overwrite: bool = True):
        if new_attributes is not None:
            self._attributes.update(new_attributes)

    # Do a tick on all stats and other actions
    def tick(self):
        # tick all of the stats
        self.private_data.tick()

        # See if the character needs to move?
        location_route = self.get_attribute("LocationRoute")

        if location_route is not None:

            # Build a list of the locations that this character follows
            locations = location_route.split("/")

            logging.info("%s.tick(): Moving %s along route %s", __class__, self.name, locations)

            # Find out where on the route they current are.
            route_position_stat = self.get_stat("RoutePosition")
            if route_position_stat is None:
                route_position_stat = CoreStat("RoutePosition", "Map", 0)
                self.add_stat(route_position_stat)

            # Find out what position we are on the route
            route_position = route_position_stat.value

            # If the positions is valid...
            if route_position >= 0 and route_position < len(locations):

                # Get the Location ID of the current position
                current_location = int(locations[route_position])

                # Move along to the next position in the route looping back to the start if we have reached the end
                route_position += 1
                if route_position == len(locations):
                    route_position = 0

                # Get the ID of the new location
                new_location = int(locations[route_position])

                # Store the old and new location and new position on the route in the stat engine
                self.update_stat("OldLocation", current_location)
                self.update_stat("Location", new_location)
                self.update_stat("RoutePosition", route_position)

                logging.info("%s.tick(): Moving %s to %i.", __class__, self.name, new_location)
            else:
                logging.info("%s.tick(): Can't move %s as route position %i out of range",
                             __class__, self.name, route_position)


class Player(object):
    '''
    Class to capture the basic details of a player and which characters they own
    '''

    # Create the basic details of a Player
    def __init__(self, name):
        self.name = name
        self.create_time = datetime.datetime.now()
        self._characters = set()

    # Convert a Player object to a string
    def __str__(self):
        text = "Player " + self.name
        text += " (created " + self.create_time.strftime("%d/%m/%Y %X") + ")"

        # If this Player has some characters then add some details of these:-
        if len(self._characters) > 0:
            text += " owns these character(s) :-"
            for character in self._characters:
                text += "\n\t- " + str(character)

        return text

    # Register a character as belonging to this player
    def add_character(self, new_character: Character):
        self._characters.add(new_character)

    # Get all of the characters owned by this player
    def get_characters(self):
        return self._characters


class RPGCSVFactory(object):
    '''
    Factory class for loading in all of the stats associated with a class
    '''

    def __init__(self, name: str, file_name: str, stat_category: str = "Abilities"):
        self.name = name
        self.file_name = file_name
        self.stat_category = stat_category
        self._rpg_object_stats = {}
        self._rpg_object_attributes = {}

    def load(self):
        '''
        Read in the content of the CSV file and load it into a dictionary key by the value in the first column
        '''

        logging.info(("%s.load(): Loading %s from %s"), __class__, self.name, self.file_name)

        # Attempt to open the file
        with open(self.file_name, 'r') as rpg_object_file:

            # Load all row in as a dictionary
            reader = csv.DictReader(rpg_object_file)

            # Get the list of column headers
            header = reader.fieldnames

            # For each row in the file....
            for row in reader:

                # The RPG object name to use is in the first column
                rpg_object_name = row.get(header[0])

                # loop through all of the header fields except the first column...
                for i in range(1, len(header)):

                    # Get the next field value from the header row
                    field = header[i]
                    value = row.get(field)

                    # If the vield value is numeric...
                    if is_numeric(value) is not None:

                        # if we don't already have a set of stats for this RPG object in the dictionary then create one
                        if rpg_object_name not in self._rpg_object_stats.keys():
                            new_rpg_object_stats = []
                            self._rpg_object_stats[rpg_object_name] = new_rpg_object_stats

                        # Get the set of stats for this RPG object
                        rpg_object_stats = self._rpg_object_stats[rpg_object_name]

                        # Create a new core stat from the field name and the value of this field in the row
                        new_stat = CoreStat(field, self.stat_category, int(value))

                        # ...and add it to the list of stats for this RPG object
                        rpg_object_stats.append(new_stat)

                        logging.info("%s.load: RPG %s %s - loaded stats %s=%i", __class__, \
                                     self.name, rpg_object_name, new_stat.name, new_stat.value)
                    else:

                        # if we don't already have a set of attributes for this RPG object in the dictionary then create one
                        if rpg_object_name not in self._rpg_object_attributes.keys():
                            new_rpg_object_attributes = {}
                            self._rpg_object_attributes[rpg_object_name] = new_rpg_object_attributes

                        # Get the set of stats for this RPG object
                        rpg_object_attributes = self._rpg_object_attributes[rpg_object_name]

                        # Add the new field/value to the list of attributes
                        rpg_object_attributes[field] = value

                        logging.info("%s.load: RPG %s %s - loaded attribute %s=%s", __class__, \
                                     self.name, rpg_object_name, field, value)

            # Close the file
            rpg_object_file.close()

    # Return the list of object names for which stats are available
    def get_rpg_object_names(self):
        return self._rpg_object_stats.keys()

    # Return the list of stats for the specified object name
    def get_stats_by_name(self, object_name: str):
        if object_name in self._rpg_object_stats.keys():
            return deepcopy(self._rpg_object_stats[object_name])
        else:
            return None

    # Return the list of attributes for the specifed object name
    def get_attributes_by_name(self, object_name: str):
        if object_name in self._rpg_object_attributes.keys():
            return deepcopy(self._rpg_object_attributes[object_name])
        else:
            return None

    # Return a list of objects that have a stats that matches the one specified
    def get_matching_objects(self, stat: BaseStat):

        matches = []

        stat_name = stat.name
        stat_value = stat.value

        # For each object in the dictionary...
        for rpg_object_name in self._rpg_object_stats.keys():
            # Loop through it's stats...
            for rpg_stat in self._rpg_object_stats[rpg_object_name]:
                # ...and if a matching stats is found add the name of the object to the list of matches...
                if rpg_stat.name == stat_name and rpg_stat.value == stat_value:
                    matches.append(rpg_object_name)

        return sorted(matches)


class CharacterFactory(object):
    '''
    Load in some characters from a character CSV file
    '''

    def __init__(self, file_name: str, game_state: StatEngine = None):
        self.file_name = file_name
        self._characters = {}
        self.public_data = game_state

    @property
    def count(self):
        return len(self._characters)

    def load(self):
        logging.info(("%s.load(): Loading Characters from %s"), __class__, self.file_name)

        # Attempt to open the file
        with open(self.file_name, 'r') as rpg_character_file:

            # Load all row in as a dictionary
            reader = csv.DictReader(rpg_character_file)

            # Get the list of column headers
            header = reader.fieldnames

            # For each row in the file....
            for row in reader:
                new_character = Character(row.get("Name"), \
                                          row.get("Race"), \
                                          row.get("Class"))

                new_character.public_data = self.public_data
                self._characters[new_character.name] = new_character

                logging.info("%s.load(): Character %s the %s %s loaded.", __class__, \
                             new_character.name, new_character.race, new_character.rpg_class)

                other_header_names = set(header) - set(["Name", "Race", "Class"])
                new_stat_list = []

                # For each column header name
                for stat_name in other_header_names:

                    # Get the value of the field
                    stat_value = row.get(stat_name)

                    # If the value of the field is numeric then create a stat and add it to the list of stats to be loaded
                    if is_numeric(stat_value) is not None:
                        stat_value = is_numeric(stat_value)
                        new_stat_list.append(CoreStat(stat_name, "Attributes", stat_value, owner=new_character))

                    # else if the field is not empty add to the list of non-numeric attributes
                    elif stat_value is not "":
                        new_character._attributes[stat_name] = stat_value

                new_character.load_stats(new_stat_list, global_stat=False)

                logging.info("%s.load(): Now getting stats %s...", __class__, str(other_header_names))

            rpg_character_file.close()

    def get_character_names(self):
        return self._characters.keys()

    def get_characters(self):
        return self._characters.values()

    def get_matching_characters(self, stat: BaseStat):
        matches = set()
        stat_name = stat.name
        stat_value = stat.value
        for character in self._characters.values():
            character_stat = character.get_stat(stat_name)
            if character_stat is not None and character_stat.value == stat_value:
                matches.add(character)

        return matches

    def print(self):
        for npc in self._characters.values():
            npc.print()

    def get_character_by_name(self, character_name: str):
        if character_name in self._characters.keys():
            return self._characters[character_name]
        else:
            return None


def is_numeric(s):
    try:
        x = int(s)
    except:
        try:
            x = float(s)
        except:
            x = None
    return x
