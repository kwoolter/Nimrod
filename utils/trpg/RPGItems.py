__author__ = 'KeithW'

import csv

from .RPGObject import *


class Item(RPGObject):

    WEIGHT = "Weight"
    VALUE = "Value"
    LOCATION = "Location"

    def __init__(self, name : str, category : str, description):
        
        super(Item,self).__init__(name, "Item")
        
        self._private_attributes = set([Item.WEIGHT,Item.VALUE])
        self.category = category
        self.description = description

    def __str__(self):
        text = "%s - %s" % (self.name, self.description)
        return text

    @property
    def location(self):
        location_stat_name = "Location"
        location_id = int(self.get_stat(location_stat_name).value)
        return location_id

    @location.setter
    def location(self, new_location_id : int):
        location_stat_name = "Location"
        location_stat = CoreStat(location_stat_name, "Map", new_location_id)
        stat_list = [location_stat]
        self.load_stats(stat_list)

    @property
    def weight(self):
        weight = self.get_stat(Item.WEIGHT)
        if weight is None:
            return 0
        else:
            return weight.value

    @property
    def value(self):
        value = self.get_stat(Item.VALUE)
        if value is None:
            return 0
        else:
            return value.value

    def print(self):
        print(str(self))
        self.private_data.print()

class ItemFactory(object):
    '''
    Load in some items from a character CSV file
    '''

    INVENTORY = -999
    NOWHERE = 0

    def __init__(self, file_name : str, game_state : StatEngine):
        self.file_name = file_name
        self._items = {}
        self.public_data = game_state

    @property
    def count(self):
        return len(self._items)

    def get_item_names(self):
        return self._items.keys()

    def get_items(self):
        return self._items.values()

    def get_item(self, item_name):
        if item_name in self._items.keys():
            return self._items[item_name]
        else:
            return None

    # get all items that have a stat that matches that specified stat
    def get_matching_items(self, stat : BaseStat):
        matches = []
        stat_name = stat.name
        stat_value = stat.value
        for item in self._items.values():
            item_stat = item.get_stat(stat_name)
            if item_stat is not None and item_stat.value == stat_value:
                matches.append(item)
                logging.info("%s.get_matching_items(): %s matches.", __class__, item.name)

        return matches

    # Print all of the items in the factory
    def print(self):
        for item in self._items.values():
            item.print()

    # Get all of the item locations
    def get_item_locations(self):
        item_location_stats = []

        for item in self._items.values():
            location = item.get_stat(Item.LOCATION)
            new_stat = CoreStat(item.name, "ItemLocation", location.value)
            if location is not None:
                item_location_stats.append(new_stat)

        return item_location_stats

    def load(self):
        logging.info(("%s.load(): Loading items from %s"), __class__, self.file_name)

        # Attempt to open the file
        with open(self.file_name, 'r') as rpg_character_file:

            # Load all row in as a dictionary
            reader = csv.DictReader(rpg_character_file)

            # Get the list of column headers
            header = reader.fieldnames

            # For each row in the file....
            for row in reader:
                new_item = Item(row.get("Name"),row.get("Category"), row.get("Description"))
                new_item.public_data = self.public_data
                self._items[new_item.name] = new_item

                logging.info("%s.load(): Item %s is created.", __class__, new_item.name)

                other_header_names = set(header) - set(["Name", "Category", "Description"])

                logging.info("%s.load(): Now getting stats %s...", __class__, str(other_header_names))
                new_stat_list = []

                for stat_name in other_header_names:

                    stat_value = row.get(stat_name)

                    if is_numeric(stat_value) is not None:
                        stat_value = is_numeric(stat_value)
                        new_stat_list.append(CoreStat(stat_name,new_item.category, stat_value))

                new_item.load_stats(new_stat_list)

            logging.info("%s.load(): Finished loading item %s", __class__, new_item.name)


def is_numeric(s):

    try:
        x = int(s)
    except:
        try:
            x = float(s)
        except:
            x = None
    return x
