__author__ = 'KeithW'

from .RPGCharacter import *
from .RPGItems import *


class Inventory(object):

    MAX_LOAD = "Max Load"
    TOTAL_ITEM_WEIGHT = "Item Weight"
    LOAD_PERCENTAGE = "Load Pct"

    def __init__(self, character : RPGCharacter, items : ItemFactory):
        self._character = character
        self._items = items
        self._inventory = []

        # Populate the inventory for the specified character
        self.__get_inventory_items()

    @property
    def total_weight(self):
        self.__get_inventory_items()
        total = 0
        for item in self._inventory:
            total += item.weight

        # Update the stat for the current total weight
        self._character.update_stat(Inventory.TOTAL_ITEM_WEIGHT, total)

        return total

    @property
    def total_value(self):
        self.__get_inventory_items()
        total = 0
        for item in self._inventory:
            total += item.value
        return total

    @property
    def total_items(self):
        self.__get_inventory_items()
        return len(self._inventory)

    @property
    def max_load(self):
        stat = self._character.get_stat(Inventory.MAX_LOAD)
        if stat is None:
            return 0
        else:
            return stat.value

    @property
    def load_pct(self):
        stat = self._character.get_stat(Inventory.LOAD_PERCENTAGE)
        if stat is None:
            return 0
        else:
            return stat.value

    @property
    def items(self):
        return self._inventory

    # Try and add the specified item to the inventory
    # Vendors can carry ALL items regardless
    # Other character types are restricted by "Max Load"
    def add_item(self, item : Item):

        # If...
        # You are not a vendor...
        # ...and the weight of the item is heavier that your maximum load then you are never going to pick it up!
        if self._character.type != RPGCharacter.TYPE_VENDOR and item.weight > self.max_load:
            raise Exception("%s is too big for %s to pick up." % (item.name, self._character.name))
        # Else If...
        # ...you are not a vendor...
        # ...and you can't carry the additional weight
        elif self._character.type != RPGCharacter.TYPE_VENDOR and item.weight + self.total_weight > self.max_load:
            raise Exception("%s can't get %s as they are carrying too much." % (self._character.name, item.name))
        # Else add the item to the inventory.
        else:
            item.update_stat("Location", self._character.inventory_id)

            # forces total weight stat to be recalculated
            new_total_weight = self.total_weight

            logging.info("%s.add_item(): %i", __class__, new_total_weight)


    # Drop a specified item
    def drop_item(self, item : Item):

        current_location = self._character.get_stat("Location")
        item.update_stat("Location", current_location.value)

        # forces total weight stat to be recalculated
        new_total_weight = self.total_weight

        logging.info("%s.drop_item(): %i", __class__, new_total_weight)


    # Look through the list of all items and populate local list items that belong to this character
    def __get_inventory_items(self):
        # Get any items that are in the inventory of the specified character and store them
        self._inventory = self._items.get_matching_items(BaseStat("Location","None",self._character.inventory_id))

    def print(self):

        # Print out the items
        if len(self._inventory) > 0:
            print("%s is holding %i items:" % (self._character.name, self.total_items))
            for item in self._inventory:
                 print("\t%s - %s : weight(%i), value(%i)" % (item.name, item.description, item.weight, item.value))

            print("Total weight=%i (%.0f%% of max weight=%i), total value=%i." % \
                  (self.total_weight, self.load_pct, self.max_load, self.total_value))
        else:
            print("%s has no items." % self._character.name)
