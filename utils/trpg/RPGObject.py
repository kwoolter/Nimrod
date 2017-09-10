__author__ = 'KeithW'

from .StatEngine import *


class RPGStateProxy(object):
    def __init__(self, subject):
        self.__subject = subject

    def __getattr__(self, name):
        return getattr(self.__subject, name)

    def set_reference(self, new_real_object):
        self.__subject = new_real_object


class RPGObject(object):
    DELIMITER = ":"

    def __init__(self, name: str, category: str, public_data: StatEngine = None):

        self.name = name
        self.category = category
        self._public_data = public_data
        self._private_data = StatEngine(self.name + ":" + self.category)
        self._private_attributes = set()

    @property
    def private_data(self):
        return self._private_data

    @property
    def public_data(self):
        return self._public_data

    @public_data.setter
    def public_data(self, new_stat_engine: StatEngine):
        self._public_data = new_stat_engine

    def get_public_stat_name(self, stat_name: str):
        return self.category + RPGObject.DELIMITER + self.name + RPGObject.DELIMITER + stat_name

    def get_stat(self, stat_name: str, global_stat: bool = False):

        logging.info("%s.get_stat():%s global=%r", __class__, stat_name, global_stat)

        stat = None

        if global_stat is True:
            if self._public_data is None:
                raise Exception("%s.get_stat(): Tried to get a global stat from %s which has no public data." % (
                __class__, self.name))
            stat = self._public_data.get_stat(stat_name)
            logging.info("%s.get_stat():getting global data %s.", __class__, stat_name)
        elif stat_name in self._private_attributes or self._public_data is None:
            stat = self._private_data.get_stat(stat_name)
            logging.info("%s.get_stat():getting private data %s.", __class__, stat_name)
        else:
            stat_name = self.category + RPGObject.DELIMITER + self.name + RPGObject.DELIMITER + stat_name
            stat = self._public_data.get_stat(stat_name)
            logging.info("%s.get_stat():getting public data %s.", __class__, stat_name)

        return stat

    def add_stat(self, new_stat: BaseStat, global_stat: bool = False):

        logging.info("%s.add_stat():%s global=%r", __class__, new_stat.name, global_stat)

        if global_stat is True:
            if self._public_data is None:
                raise Exception("%s.add_stat(): Tried to add a global stat from %s which has no public data." % (
                __class__, self.name))
            self._public_data.add_stat(new_stat)
        elif new_stat.name in self._private_attributes or self._public_data is None:
            self._private_data.add_stat(new_stat)
        else:
            new_stat.name = self.category + RPGObject.DELIMITER + self.name + RPGObject.DELIMITER + new_stat.name
            self._public_data.add_stat(new_stat)

    def update_stat(self, stat_name: str, new_value: float, global_stat: bool = False):

        logging.info("%s.update_stat():%s global=%r", __class__, stat_name, global_stat)

        stat = self.get_stat(stat_name, global_stat)

        if stat is None:
            self.add_stat(CoreStat(stat_name, "AUTO", new_value), global_stat)
        else:
            stat.value = new_value

    def increment_stat(self, stat_name: str, increment: float, global_stat: bool = False):

        logging.info("%s.increment_stat():%s global=%r", __class__, stat_name, global_stat)

        stat = self.get_stat(stat_name, global_stat)
        if stat is not None:
            stat.value += increment

    # Load in stats from a provided list
    # Default is to overwrite what is there already with option to increment
    def load_stats(self, stat_list: list, overwrite: bool = True, global_stat: bool = False):

        if stat_list is None:
            logging.info("%s.load_stats:Tried to load a 'None' list of stats.", __class__)
            return

        for stat in stat_list:
            # If we are overwriting or the stat does not exist then add the stat
            if overwrite is True or self.get_stat(stat.name) is None:
                self.add_stat(stat, global_stat)
            # Else increment the existing stat
            else:
                self.increment_stat(stat.name, stat.value)

    def add_private_attributes(self, new_attributes: set):
        self._private_attributes |= new_attributes

    def print(self):
        print("%s (%s)" % (self.name, self.category))

        if self._private_data is not None:
            self._private_data.print()

        if self._public_data is not None:
            self._public_data.print()

    @staticmethod
    def is_numeric(s):
        try:
            x = int(s)
        except:
            try:
                x = float(s)
            except:
                x = None
        return x
