'''
    This module contains the framework classes for the stat engine:
    - BaseStat - basic stat details
    - CoreStat - a core stat that auto updates listeners when its value changes
    - DerivedStat - a stat derived from other stats
    - StatEngine - the container for all of the stats and manages stat listeners
'''

import datetime
import logging

'''
The basic details of a stat
'''


class BaseStat(object):
    # magic numbers for a time dependencies stat
    EVERGREEN = -1
    DEAD = 0

    # Initiation of BaseStat, and parameters
    def __init__(self, name: str, category: str, value: float, owner=0, lifetime: int = EVERGREEN):
        self.name = name
        self.category = category
        self._value = value
        self._old_value = value
        self._owner = owner
        self._lifetime = lifetime
        self.create_time = datetime.datetime.now()
        self.update_time = datetime.datetime.now()

    # convert to string
    def __str__(self):
        return self.name + "(" + self.category + ")" + "=" + str(self._value)

    # A property style getter
    @property
    def value(self):
        return self._value

    # a property style setter
    @value.setter
    def value(self, new_value: float):
        self._old_value = self._value
        self._value = (new_value)
        self.update_time = datetime.datetime.now()


class CoreStat(BaseStat):
    """
    A core stat is one that is not derived from other stats but other stats can listen to it for updates
    """

    # Constructor
    def __init__(self, name: str, category: str, value: float, owner=0, lifetime=BaseStat.EVERGREEN):

        # Initialise the parent class
        super(CoreStat, self).__init__(name, category, value, owner, lifetime)

        # Define an protected empty set that will contain the listeners for this stat
        self._listeners = set()

        # There are no stats that a core stat is dependent on
        self._baseStatNames = None

    # Convert to a string
    def __str__(self):
        text = super(CoreStat, self).__str__()

        if len(self._listeners) > 0:
            text += ", listeners(" + str(len(self._listeners)) + ")"

        if self._owner != 0:
            text += ", owner(" + str(self._owner) + ")"

        if self._lifetime != BaseStat.EVERGREEN:
            text += ", lifetime(" + str(self._lifetime) + ")"

        return text

    # Registers a derived stat as being dependent on this stat by adding it to the list of listeners
    def add_listener(self, new_listener):

        # add the new listener to the list for this stat
        self._listeners.add(new_listener)

        # and then ping the new listener with the latest details of this stat by calling the update method
        new_listener.update(self)

    # Method called to tell listeners that this stat no longer wants to be listened to
    def remove_all_listeners(self):
        for listener in self._listeners:
            logging.debug("%s.remove_all_listeners(): Telling %s that %s is not publishing anymore", \
                          __class__, listener.name, self.name)
            listener.remove(self)

    # Change the value of this stat and let all listeners know the new state
    def set_value(self, new_value: float):
        self._value = new_value

        for listener in self._listeners:
            listener.update(self)

    # A property style getter
    @property
    def value(self):
        return self._value

    # a property style setter
    @value.setter
    def value(self, new_value: float):
        self.set_value(new_value)

    # Increment the current stat value by the specified amount
    def increment_value(self, increment):
        self.set_value(self.value + increment)

    # Do a tick on the stat to update its lifetime
    @property
    def tick(self):

        # if this is an time dependent stat then decrement its life
        if self._lifetime != BaseStat.EVERGREEN and self._lifetime > 0:
            self._lifetime -= 1

        # If the stat has come to the end of its life then stop it publishing
        if self._lifetime == 0:
            self.remove_all_listeners()

        # return how long this stat has to live
        return self._lifetime


'''
A derived stat is one that is based on one or more other base stats.
Base stats can be core stats or other derived stats
This class is an abstract class so you need to inherit from it and:-
1. Register which stat names you want to be notified about using add_dependency(...)
2. Implement the calculate(...) method to calculate the new value of your stat from its dependencies
'''


class DerivedStat(CoreStat):
    # Constructor
    def __init__(self, name: str, category: str):

        # Initialise the parent class
        super(DerivedStat, self).__init__(name, category, None)

        # This set stores the names of the stats that the derived class ins interested in
        self._baseStatNames = set()

        # This dictionary stores the actual dependencies key by the name of the stat
        self._baseStats = {}

        # This dictionary stores any defaults for optional dependencies
        self._baseStatDefaults = {}

    # Convert to string
    def __str__(self):
        text = super(DerivedStat, self).__str__()

        # Add how many dependent stats the derived stat has
        if len(self._baseStatNames) > 0:
            text += ", dependencies(" + str(len(self._baseStatNames)) + ")"

        # Add if we are missing any dependent stats...
        missing_stats = self.get_missing_dependencies()

        # Only one missing dependency?
        if len(missing_stats) == 1:
            text += ", missing(" + missing_stats.pop() + ")"

        # More than one missing dependency...?
        elif len(missing_stats) > 1:
            text += ", missing(" + missing_stats.pop()
            for stat in missing_stats:
                text += "," + stat
            text += ")"

        return text

    # This method is called when a dependent stat changes
    # The input parameter is the actual stat object that has changed which is optional
    def update(self, changed_stat=None):

        # If we got an update because of a change to a specific stat then log this
        if changed_stat is not None:

            logging.debug("%s.update(): %s got an update to %s.", __class__, self.name, changed_stat.name)

            # Store the new stat in the local dictionary
            self._baseStats[changed_stat.name] = changed_stat

        # Else log a generic update request
        else:
            logging.debug("%s.update(): %s got a general update request.", __class__, self.name)

        # If we have all of the dependent stats in the local dictionary then go ahead and recalculate the value
        # of the derived stat
        if len(self.get_missing_dependencies()) == 0:

            try:

                logging.debug("%s.update(): Calculating %s from %s", __class__, self.name, str(self._baseStatNames))

                # calculate the new value and call the parent set_value to make sure all derived stats are updated
                super(DerivedStat, self).set_value(self.calculate())

                logging.debug("%s.update(): New calculated value=%s", __class__, str(self._value))

            except Exception as err:

                logging.warning("%s.update(): Calculating %s exception (%s).", __class__, self.name, str(err))

        else:
            logging.info("%s.update(): Not got all of the dependencies yet for stat %s - missing %s.", \
                         __class__, self.name, str(self.get_missing_dependencies()))

    # This method is called when a dependent stat is being destroyed
    def remove(self, removed_stat):

        logging.debug("%s.remove(): Removing %s from %s.", __class__, removed_stat.name, self.name)

        # Remove the stat entry from the local dictionary
        if removed_stat.name in self._baseStats.keys():
            del self._baseStats[removed_stat.name]

        # Recalculate this derived stat using a generic update request
        self.update()

    # return a set of the stat names that we are still waiting for in our local dictionary
    def get_missing_dependencies(self):
        # Look at what are required stats and see if these are either in the local dictionary of in teh default list
        missing_stats = self._baseStatNames - set(self._baseStats.keys()) - set(self._baseStatDefaults)
        return missing_stats

    # This is a pure virtual function that needs to be overridden by a derived stat
    # It should return the newly calculate value of the stat
    def calculate(self):
        logging.error("%s.calculate(): No calculate() method defined for derived stat %s.", __class__, self.name)
        return None

    # Add the name of a dependency stat to the list of stat names
    # If the stat is optional then load in a default stat into the local dictionary with the specified default
    def add_dependency(self, dependent_stat, optional: bool = False, default_value: float = 0) -> object:

        self._baseStatNames.add(dependent_stat)
        if optional:
            self._baseStatDefaults[dependent_stat] = default_value

    # Retrieve the value of a specified dependency stat
    # Try the local dictionary, then defaults list else raise exception
    def get_dependency_value(self, dependency_stat_name):

        stat_value = None

        # Firstly see if we have the requested stat in our local dictionary
        if dependency_stat_name in self._baseStats.keys():
            stat_value = self._baseStats[dependency_stat_name].value

            logging.debug("%s.get_dependency_value(): Found local value %s=%s.", \
                          __class__, dependency_stat_name, str(stat_value))

        # We have a non-None value
        if stat_value is not None:
            pass
        # Next see if we have a default value for the requested stat....
        elif dependency_stat_name in self._baseStatDefaults:
            stat_value = self._baseStatDefaults[dependency_stat_name]

            logging.debug("%s.get_dependency_value(): Found default value %s=%s.", \
                          __class__, dependency_stat_name, str(stat_value))

        # Can't find it so see if the requested stat was ever registered as a dependency
        elif dependency_stat_name not in self._baseStatNames:
            logging.error(
                "%s.get_dependency_value(): %s trying to get stat %s that was never registered as a dependency", \
                __class__, self.name, dependency_stat_name)
            raise Exception(dependency_stat_name + " was never registered.")

        # Else finally we currently don't have a copy of the dependency in the local dictionary so log an error
        else:
            logging.warning("%s.get_dependency_value(): Can't find dependency %s for stat %s.", \
                            __class__, dependency_stat_name, self.name)

            raise Exception("Not got %s in local dictionary" % dependency_stat_name)

        return stat_value

    # Log an error if you try to directly set the value of a derived stat as a derived stat can only change if
    # a dependent stat changes
    def set_value(self, new_value: float):
        logging.error("%s.set_value(): Can't call set_value on derived stat %s.", __class__, self.name)


'''
The main container for stats.
'''


class StatEngine:
    # Initialises to create a name and empty dictionary
    def __init__(self, name):
        self.name = name

        # Create an empty dictionary that will store all of the stats
        self._stats = {}

    # Add a new stat to the container and sync up all listeners
    def add_stat(self, new_stat):

        logging.debug("%s.add_stat(): Adding new stat %s.", __class__, new_stat.name)

        # Adds a new stat to the dictionary using the stat name as the key
        self._stats[new_stat.name] = new_stat

        # If there are some dependencies for the new stat....
        if new_stat._baseStatNames is not None:

            # Look at the dependencies, retrieve each one from the dictionary
            # and register the new stat as a listener on each
            for base_stat_name in new_stat._baseStatNames:

                logging.debug("%s.add_stat(): Adding listener %s to %s.", __class__, new_stat.name, base_stat_name)

                base_stat = self.get_stat(base_stat_name)

                if base_stat is not None:
                    base_stat.add_listener(new_stat)
                else:
                    logging.warning("%s.add_stat(): Couldn't find dependency %s for stat %s.", \
                                    __class__, base_stat_name, new_stat.name)

        # Look through all stats in the container and see if any are dependent on the new stat
        # If they are then add the existing stat as a listener to the new stat
        for stat in self._stats.values():
            if stat._baseStatNames is not None and new_stat.name in stat._baseStatNames:
                logging.debug("%s.add_stat(): Adding listener %s to %s.", __class__, stat.name, new_stat.name)
                new_stat.add_listener(stat)

    # Load in stats from a provided list
    # Default is to overwrite what is there already with option to increment
    def load_stats(self, stat_list: list, overwrite: bool = True):

        if stat_list is None:
            return

        for stat in stat_list:
            # If we are overwriting or the stat does not exist then add the stat
            if overwrite is True or self.get_stat(stat.name) is None:
                self.add_stat(stat)
            # Else increment the existing stat
            else:
                self.increment_stat(stat.name, stat.value)

    # Get a named stat from the container
    def get_stat(self, stat_name: str):
        if stat_name not in self._stats.keys():
            logging.info("%s.get_stat(): Couldn't find stat %s in the container.", __class__, stat_name)
            return None
        else:
            return self._stats[stat_name]

    # Update a named stat in the container
    def update_stat(self, stat_name: str, new_value: float):
        # Look to see if the specified stat exists in the local dictionary and update if it is found
        if (stat_name in self._stats.keys()):
            stat = self._stats[stat_name]
            stat.set_value(new_value)
        # else log an error
        else:
            logging.warning("%s.update_stat(): Couldn't find stat %s in the container", __class__, stat_name)

    # Increment a named stat in the container
    def increment_stat(self, stat_name: str, increment: float):
        # Look to see if the specified stat exists in the local dictionary and increment if it is found
        if (stat_name in self._stats.keys()):
            stat = self._stats[stat_name]
            stat.increment_value(increment)
        # else log an error
        else:
            logging.warning("%s.increment_stat(): Couldn't find stat %s in the container", __class__, stat_name)

    # Get all of the stats for a specified category
    def get_stats_by_category(self, category_name: str):
        stats = set()
        for stat in self._stats.values():
            if stat.category == category_name:
                stats.add(stat)
        return stats

    def get_all_stats(self):
        return list(self._stats.values())

    # Get a list of all of the stat categories currently in the container
    def get_category_names(self):
        categories = set()
        for stat in self._stats.values():
            categories.add(stat.category)
        return categories

    # Get a list of all of the stat names currently in the container
    def get_stat_names(self):
        return set(self._stats.keys())

    # Create a new dictionary
    def remove_all(self):
        self._stats = {}

    # Remove all stats that are owned by a specified owner
    def remove_stats_by_owner(self, owner: int):

        logging.debug("%s.remove_stats_by_owner(): Going to remove stats owned by %s.", __class__, str(owner))

        stat_names_to_delete = set()
        for stat in self._stats.values():
            if stat._owner == owner:
                stat_names_to_delete.add(stat.name)

        logging.debug("%s.remove_stats_by_owner(): About to remove %s.", __class__, str(stat_names_to_delete))

        for stat_name in stat_names_to_delete:
            stat = self._stats[stat_name]
            stat.remove_all_listeners()
            del self._stats[stat_name]

    # Get a list of stats owned by a specified ID
    def get_stats_by_owner(self, owner):

        logging.debug("%s.get_stats_by_owner(): Going to get stats owned by %s.", __class__, str(owner))

        stats = set()
        for stat in self._stats.values():
            if stat._owner == owner:
                stats.add(stat)

        logging.debug("%s.get_stats_by_owner(): %i stats found for owned by %s.", __class__, len(stats), str(owner))

        return stats

    #
    # Do a tick on all stats in the container and remove any dead ones
    #
    def tick(self):

        logging.debug("%s.tick(): Doing a tick on all stats in %s.", __class__, self.name)

        # Set to collect the names of dead stats
        dead_stat_names = set()

        # Loop through all stats doing a tick and recording dead ones
        for stat in self._stats.values():

            life_left = stat.tick

            # If a stat is dead then remove it
            if life_left == BaseStat.DEAD:
                dead_stat_names.add(stat.name)

        if len(dead_stat_names) > 0:
            logging.debug("%s.tick(): Removing dead stats %s", __class__, str(dead_stat_names))

        # Go through the collection of dead stats and remove them from the container
        for stat_name in dead_stat_names:
            stat = self._stats[stat_name]
            stat.remove_all_listeners()
            del self._stats[stat.name]

    #
    # Print out the contents of the container
    #
    def print(self):
        output_width = 70

        # Create an empty dictionary that will hold the stats keyed by category
        stats_by_category = {}

        # Loop through all of the stats in the container...
        for stat in self._stats.values():

            # Get the category of the stat...
            category = stat.category

            # If there is not already an entry in the dictionary then add one with an empty list
            if category not in stats_by_category.keys():
                stats_by_category[category] = []

            # Add the stat to the appropriate category stat list
            stats_by_category[category].append(stat)

        # Now loop through the categories in alphabetical order...
        for key in sorted(stats_by_category.keys()):
            # Print the category and the stats that belong to it
            print((" " + key + " (" + str(len(stats_by_category[key])) + ") ").center(output_width, "-"))
            stats = {}
            for stat in stats_by_category[key]:
                stats[stat.name] = stat

            for stat_name in sorted(stats.keys()):
                stat = stats[stat_name]
                # print("\t"+ stat.name + "=" + str(stat.value))
                print("\t" + str(stat))
