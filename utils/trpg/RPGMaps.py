__author__ = 'JaneW'

from .RPGCharacter import *
import logging
'''
This module contains some framework classes for creating maps:-
    - Location - basic description of a location
    - LocationFactory - abstract factory class for storing Locations
    - MapLink - a class to define how two locations are linked together
    - LevelMap - defines a map by storing the MapLinks between all locations in the map
    - MapFactory - abstract factory class for creating LevelMaps
'''

'''
Basic details of a location
All locations need a unique ID which is used to access them from the Factory
as well as link them together using MapLinks
'''


class Location:
    LOCATION_STAT = "Location"

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    def __str__(self):
        return str(self.id) + ": " + self.name + " - " + self.description


'''
A factory for creating and storing location details for easy access by location ID
'''


class LocationFactory(object):
    def __init__(self, location_file_name: str):
        self.file_name = location_file_name

        # a dictionary of location ID to a location object
        self._locations = {}

    @property
    def count(self):
        return len(self._locations)

    def load(self):
        # Attempt to open the file
        with open(self.file_name, 'r') as location_file:
            # Load all rows in as a dictionary
            reader = csv.DictReader(location_file)

            # Get the list of column headers
            header = reader.fieldnames

            # For each row in the file....
            for row in reader:
                new_location = Location(int(row.get("ID")), \
                                        row.get("Name"), \
                                        row.get("Description"))

                self._locations[new_location.id] = new_location

                logging.info("%s.load(): Loaded Location %i. %s", __class__, new_location.id, new_location.name)

    # Returns the location with the specified ID
    def get_location(self, id):
        return self._locations[id]


class MapLink:
    '''
    MapLink - A link between two locations
    The link represents:
     - a "from" location ID
     - a "to" location ID
     - the direction of travel to get between from/to locations
     - an optional description of how you get from/to
     - an optional flag to indicate if the link is locked somehow
     - an optional description of why the link is locked
     - an optional flag for suppressing creation of the reverse map link i.e. for a one-way link
    '''

    # What directions are valid and what is their reverse equivalent
    valid_directions = ["NORTH", "SOUTH", "EAST", "WEST", "UP", "DOWN"]
    valid_reverse_directions = ["SOUTH", "NORTH", "WEST", "EAST", "DOWN", "UP"]
    valid_flags = {"TRUE": True, "FALSE": False}

    LOCKED = 0
    UNLOCKED = 1
    HIDDEN = 999
    UNHIDDEN = 1000
    HIDDEN_STAT = "Hidden"

    # Constructor
    def __init__(self, from_id, to_id, direction, description=None, \
                 is_lockable: bool = False, locked: bool = False, locked_description: str = None, \
                 reversible: bool = True, hidden: bool = False):

        self.from_id = from_id
        self.to_id = to_id
        self.description = description
        self.direction = direction
        self.locked = locked
        self.is_lockable = is_lockable
        self.locked_description = locked_description
        self.reversible = reversible
        self.hidden = hidden

        # If the direction supplied is not valid then log an error
        if direction not in MapLink.valid_directions:
            logging.warning((str(self) + ": Direction " + direction + " is not valid."))

    # Return a MapLink object that is the reverse of this one
    def get_reverse_link(self):
        return MapLink(self.to_id, self.from_id, self.get_reverse_direction(self.direction), self.description, \
                       is_lockable=self.is_lockable, locked=self.locked, \
                       locked_description=self.locked_description, reversible=self.reversible)

    # Given a valid direction look-up its reverse
    def get_reverse_direction(self, direction):
        i = MapLink.valid_directions.index(direction)
        return MapLink.valid_reverse_directions[i]

    # Check to see if this MapLink is valid
    def is_valid(self):
        return self.direction in MapLink.valid_directions

    # Check if the link is locked
    def is_locked(self, character: RPGCharacter = None):
        # If this link is not lockable then locked is always false
        if self.is_lockable == False:
            locked = False
        # If no game state provided then use local state
        elif character is None:
            locked = self.locked
        # Else determine if the link is locked from the game state
        else:
            # Look for the stat in the game stat
            stat_name = "%i:%i:%s" % (self.from_id, self.to_id, self.direction)
            stat = character.get_stat(stat_name)

            # If we couldn't find the stat in the game state then default to local state
            if stat is None:
                stat = CoreStat(stat_name, "Map", MapLink.UNLOCKED)
                if self.locked:
                    stat.value = MapLink.LOCKED
                character.add_stat(stat)

            logging.info("%s.is_locked(): Got stat %s.", __class__, stat_name)

            if stat.value == MapLink.LOCKED:
                locked = True
            else:
                locked = False

        return locked

    # lock/unlock a link
    def lock(self, is_locked, character: RPGCharacter = None):

        if character is None:
            self.locked = is_locked
        else:
            self.locked = is_locked
            stat_value = MapLink.LOCKED
            if is_locked == False:
                stat_value = MapLink.UNLOCKED

            stat_name = "%i:%i:%s" % (self.from_id, self.to_id, self.direction)
            new_stat = CoreStat(stat_name, "Map", stat_value)
            character.add_stat(new_stat)

            stat_name = "%i:%i:%s" % (self.to_id, self.from_id, self.get_reverse_direction(self.direction))
            new_stat = CoreStat(stat_name, "Map", stat_value)
            character.add_stat(new_stat)

    # Check if the link is hidden
    def is_hidden(self, character: RPGCharacter = None):
        # If no game stat provide then use local state value
        if character is None:
            hidden = self.is_hidden
        else:
            # Get the 'hidden' stat for this map link from the game state
            stat_name = "%i:%i:%s:%s" % (self.from_id, self.to_id, self.direction, MapLink.HIDDEN_STAT)
            stat = character.get_stat(stat_name)

            # If we couldn't find the stat in the game state then default to local state
            if stat is None:
                stat = CoreStat(stat_name, "Map", MapLink.UNHIDDEN)
                if self.hidden:
                    stat.value = MapLink.HIDDEN
                character.add_stat(stat)

            logging.info("%s.is_hidden(): Got stat %s.", __class__, stat_name)

            if stat.value == MapLink.HIDDEN:
                hidden = True
            else:
                hidden = False

        return hidden

    # hide/unhide a link
    def hide(self, is_hidden, character: RPGCharacter = None):

        if character is None:
            self.hidden = is_hidden
        else:
            self.hidden = is_hidden
            stat_value = MapLink.HIDDEN
            if is_hidden == False:
                stat_value = MapLink.UNHIDDEN

            stat_name = "%i:%i:%s:%s" % (self.from_id, self.to_id, self.direction, MapLink.HIDDEN_STAT)
            new_stat = CoreStat(stat_name, "Map", stat_value)
            character.add_stat(new_stat)

            stat_name = "%i:%i:%s%s:Hidden" % \
                        (self.to_id, self.from_id, self.get_reverse_direction(self.direction), MapLink.HIDDEN_STAT)
            new_stat = CoreStat(stat_name, "Map", stat_value)
            character.add_stat(new_stat)

    # Convert the MapLink object to a string
    def __str__(self):
        link_description = "Go " + self.direction + " from " + str(
            self.from_id) + " " + self.description + " to " + str(self.to_id) + "."
        if self.is_locked() == True and self.locked_description != None:
            link_description += self.locked_description
        if self.is_hidden() == True:
            link_description += "(Hidden)"
        return link_description


class LevelMap:
    '''
    The LevelMap class holds the details of how all of the locations in the map link together
    The map is stored as a dictionary that for each location ID stores the list of available MapLinks
    These MapLinks represent all of the directions that you can travel in from that location
    '''

    # Constructor
    def __init__(self, level, name):

        self.level = level
        self.name = name
        self._locations = None

        # A map to store the list of links for each location ID in the map
        self.mapLinks = {}

    def add_locations(self, locations):
        self._locations = locations

    # Add a new link to the map and also add the reverse link
    # e.g. if you can go East from 1 to 2, you can go West from 2 to 1
    def add_link(self, new_link):

        # First see if the link that you are trying to add is valid?
        if (new_link.is_valid() == False):
            logging.warning("Trying to add invalid link: " + str(new_link))
            return

        # See if there is already a list of links for the "from" location
        if new_link.from_id in self.mapLinks:
            list_links = self.mapLinks[new_link.from_id]
        # If not create a new blank list
        else:
            list_links = []

        # add the new link to the list
        list_links.append(new_link)

        # and store it back in the map of location IDs to links
        self.mapLinks[new_link.from_id] = list_links

        # add the reverse link as well if the link is reversible
        if new_link.reversible == True:
            # See if there is already a list of links for the "to" location
            if new_link.to_id in self.mapLinks:
                list_links = self.mapLinks[new_link.to_id]
            # If not create a new blank list
            else:
                list_links = []

            # add the reverse of the new link to the list
            list_links.append(new_link.get_reverse_link())

            # and store it back in the map of locations to links
            self.mapLinks[new_link.to_id] = list_links

    # Get the list of links for a specified location in the map
    def get_location_links(self, location_id):
        return self.mapLinks.get(location_id)

    # Get the map of links for a specified location in the map keyed by direction
    def get_location_links_map(self, location_id):
        link_map = {}
        for link in self.get_location_links(location_id):
            link_map[link.direction] = link
        return link_map

    # lock/unlock the specified link and its reverse link
    def lock(self, location_id, direction, is_locked):

        # get the map of links for the specified location
        link_map = self.get_location_links_map(location_id)

        # if specified direction has a link...
        if (direction in link_map.keys()):

            # get the link and lock/unlock it
            selected_link = link_map[direction]
            selected_link.lock(is_locked)

            # find out what the reverse link looks like
            reverse_link = selected_link.get_reverse_link()

            # loop through all of the links from the 'to' location
            for selected in self.mapLinks[selected_link.to_id]:

                # if we find the link that is the reverse then lock/unlock it
                if selected.to_id == location_id and selected.direction == reverse_link.direction:
                    selected.lock(is_locked)

        # else the specified link could not be found to lock it
        else:
            logging.warning(
                "Lock(" + str(is_locked) + "): No link found " + direction + " from location " + str(location_id))

    # Print a specified location
    def print_location(self, location_id: int, character: RPGCharacter = None):
        print(self.location_to_string(location_id, character))

    # Convert a specified Location to string describing the location in detail
    def location_to_string(self, location_id: int, character: RPGCharacter = None):

        # For the current location ID get the full details of the location from the LocationFactory and print...
        location = self._locations.get_location(location_id)
        location_description = "You are " + location.description + "."

        # Get the full list of links for the current location ID...
        full_list_links = self.mapLinks[location_id]

        # Create a new list with any hidden links removed
        list_links = []
        for link in full_list_links:
            if link.is_hidden(character) == False:
                list_links.append(link)

        if len(list_links) == 1:
            location_description += "  There is an exit "
        elif len(list_links) > 1:
            location_description += "  There are exits "

        # For each link in the list print the link...
        for i in range(len(list_links)):

            # Get the link
            map_link = list_links[i]

            # Get the details of the "to" location
            to_location = self._locations.get_location(map_link.to_id)

            # Build the basic link description
            location_description += map_link.direction.title()

            # If the direction is not locked then ok to say where the link leads to.
            if map_link.is_locked(character) is False:
                location_description += " to " + to_location.name

            if map_link.description != None and map_link.description != "":
                location_description += " " + map_link.description

            # If the link is locked add this to the description
            if map_link.is_locked(character) == True and map_link.locked_description != None:
                location_description += " (but " + map_link.locked_description + ")"

            # Indicate that there is no way back if a link is not reversible
            if map_link.reversible == False:
                location_description += ", but there is no way back"

            # Decide what test needs to be added to continue the list of links...
            if i == len(list_links) - 2 and len(list_links) > 1:
                location_description += " and "
            elif i < len(list_links) - 1:
                location_description += ", "
            else:
                location_description += "."

        return location_description

    # Print out all of the locations in the Level Map
    def print(self):

        output_width = 60

        print("\n\n")
        print((" Welcome to Level " + str(self.level) + " : " + self.name + " ").center(output_width, "-"))

        # For each of the location IDs in the map...
        for location_id in self.mapLinks.keys():
            print(self.location_to_string(location_id))


'''
A factory class to load in level maps and store them
'''


class MapFactory(object):
    def __init__(self, locations: LocationFactory):

        # A dictionary of level ID to LevelMap
        self._maps = {}

        self._locations = locations

    @property
    def count(self):
        return len(self._locations)

    def load(self, map_name: str, map_level: int, map_file_name: str):

        # Create a map of level and add it to the Factory
        new_map = LevelMap(map_level, map_name)
        self._maps[new_map.level] = new_map

        logging.info("%s.load(): Loading new map %s from '%s'.", __class__, new_map.name, map_file_name)

        # Attempt to open the map file
        with open(map_file_name, 'r') as data_file:

            # Load all rows in as a dictionary
            reader = csv.DictReader(data_file)

            # Get the list of column headers
            header = reader.fieldnames

            # For each row in the file....
            for row in reader:

                from_loc_id = int(row.get("FromID"))
                to_loc_id = int(row.get("ToID"))
                direction = row.get("Direction").upper()

                if direction not in MapLink.valid_directions:
                    logging.error("%s.load(): %s not a valid direction.", __class__, direction)
                    break

                description = row.get("Description")

                is_lockable = row.get("Lockable").upper()
                if is_lockable in MapLink.valid_flags.keys():
                    is_lockable = MapLink.valid_flags[is_lockable]
                elif is_lockable == "":
                    is_lockable = False
                else:
                    logging.warning("%s.load(): Lockable flag '%s' for location %i to %i not recognised", \
                                    __class__, is_lockable, from_loc_id, to_loc_id)
                    is_lockable = False

                locked = row.get("Locked").upper()
                if locked in MapLink.valid_flags.keys():
                    is_locked = MapLink.valid_flags[locked]
                elif locked == "":
                    is_locked = False
                else:
                    logging.warning("%s.load(): Locked flag %s not recognised", __class__, locked)
                    is_locked = False

                locked_description = row.get("LockedDescription")

                reversible = row.get("Reversible").upper()
                if reversible in MapLink.valid_flags.keys():
                    is_reversible = MapLink.valid_flags[reversible]
                elif reversible == "":
                    is_reversible = True
                else:
                    logging.warning("%s.load(): Reversible flag %s not recognised", __class__, reversible)
                    is_reversible = False

                hidden = row.get("Hidden").upper()
                if hidden in MapLink.valid_flags.keys():
                    is_hidden = MapLink.valid_flags[hidden]
                elif hidden == "":
                    is_hidden = False
                else:
                    logging.warning("%s.load(): Hidden flag %s not recognised", __class__, hidden)
                    is_hidden = False

                new_map_link = MapLink(from_loc_id, to_loc_id, direction, description, \
                                       is_lockable, is_locked, locked_description, is_reversible, is_hidden)

                logging.info("%s.load(): Loaded map link From %i %s to %i", \
                             __class__, new_map_link.from_id, new_map_link.direction, new_map_link.to_id)

                new_map.add_link(new_map_link)
                new_map.add_locations(self._locations)

    # Return the LevelMap with the specified ID
    def get_map(self, id):
        return self._maps[id]
